"""
BEEST 2 series builder.

Turns the live hashrate feed and the static inputs in tracker-inputs.md into the
daily series the chart draws, from 1 December 2025 (the date of the Cambridge
energy-mix survey behind the carbon intensity) to today. Writes series.json.

Chain, per day:
    electricity TWh/yr = hashrate (EH/s) x efficiency (J/TH) x 8,760 / 1,000
    gross MtCO2e/yr    = TWh/yr x carbon intensity (gCO2e/kWh) / 1,000
    net MtCO2e/yr      = gross - emission mitigation (gas) [- mitigation (landfills), when added]

Efficiency is not held flat across the window: the fleet improved through 2026
as the least efficient machines switched off. The series runs a straight line
from the 1 December 2025 figure to the November 2026 figure from
network-efficiency-proxy-method.md and holds flat after that until the method
is next refreshed. Both ends use the same formula, PUE x [(1-s) E_grid + s E_off]
with s = 0.10, E_off = 28, PUE = 1.05; only E_grid differs.

Usage:
    python3 build_series.py            # writes series.json beside this file
    python3 build_series.py --print    # also prints the last five rows
"""
import json
import os
import sys
import urllib.request
from datetime import date

from hashrate_feed import daily_series, moving_average
from grid_greening import Greening

START = date(2025, 12, 1)

# Static inputs; every value and its source is in tracker-inputs.md
CARBON_INTENSITY = 252.0      # gCO2e/kWh, Cambridge 2nd edition, December 2025 mix; moved after that with the world grid (grid_greening.py)
MITIGATION_GAS = 4.69         # MtCO2e/yr, Cambridge 2nd edition, 44 flare-gas respondents, 91.1% flare efficiency, GWP20
MITIGATION_LANDFILL = None    # MtCO2e/yr, to be added when a sourced figure exists

PUE, S_OFF, E_OFF = 1.05, 0.10, 28.0
E_GRID_START = 20.5           # 1 Dec 2025: mean of Luxor 20.2 and Cambridge 20.8, before the 2026 idling
E_GRID_END = 17.3             # Nov 2026: network-efficiency-proxy-method.md central case
E_GRID_END_DATE = date(2026, 11, 15)


def price_series(days=400):
    """Daily BTC price in USD as {date: price}: Coin Metrics community API first, blockchain.com as fallback.
    Context only; nothing in the emissions chain depends on it. Returns {} if neither source answers."""
    try:
        url = ("https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
               f"?assets=btc&metrics=PriceUSD&frequency=1d&page_size={days}&paging_from=end")
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.load(r)["data"]
        return {row["time"][:10]: float(row["PriceUSD"]) for row in data}
    except Exception:
        pass
    try:
        url = f"https://api.blockchain.info/charts/market-price?timespan={days}days&format=json"
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.load(r)["values"]
        from datetime import datetime, timezone
        return {datetime.fromtimestamp(v["x"], timezone.utc).strftime("%Y-%m-%d"): float(v["y"]) for v in data}
    except Exception:
        return {}


def network_jth(e_grid):
    return PUE * ((1 - S_OFF) * e_grid + S_OFF * E_OFF)


def efficiency_on(d):
    """Facility-level J/TH on a given date: linear between the two anchors, flat beyond them."""
    if d <= START:
        return network_jth(E_GRID_START)
    if d >= E_GRID_END_DATE:
        return network_jth(E_GRID_END)
    f = (d - START).days / (E_GRID_END_DATE - START).days
    return network_jth(E_GRID_START + f * (E_GRID_END - E_GRID_START))


def build():
    source, daily = daily_series(days=400)
    prices = price_series()
    last_price = None
    green = Greening()
    rows = []
    for day, ehs in moving_average(daily):
        d = date.fromisoformat(day)
        if d < START:
            continue
        jth = efficiency_on(d)
        gw = ehs * jth / 1000.0                       # EH/s x J/TH = 1e18 x 1e-12 W = 1e6 W x ... -> GW after /1000
        twh = gw * 8.760                              # GW x 8,760 h = TWh/yr
        intensity = green.intensity(d)                # gCO2e/kWh: Cambridge December 2025, on-grid part moved with the world grid
        gross = twh * intensity / 1000.0              # TWh x g/kWh = Mt / 1000
        mit = MITIGATION_GAS + (MITIGATION_LANDFILL or 0.0)
        last_price = prices.get(day, last_price)  # carry the last close forward over a missing day
        rows.append({
            "date": day,
            "hashrate_ehs_7d": round(ehs, 1),
            "efficiency_jth": round(jth, 2),
            "power_gw": round(gw, 2),
            "electricity_twh_yr": round(twh, 1),
            "gross_mt": round(gross, 2),
            "mitigation_gas_mt": round(MITIGATION_GAS, 2),
            "mitigation_landfill_mt": MITIGATION_LANDFILL,
            "net_mt": round(gross - mit, 2),
            "price_usd": round(last_price) if last_price else None,
            "intensity_g_kwh": round(intensity, 1),
            "clean_share": round(green.clean(d), 4),
        })
    return {
        "generated": date.today().isoformat(),
        "hashrate_source": source,
        "price_source": "Coin Metrics community API (PriceUSD), fallback blockchain.com" if prices else None,
        "inputs": {
            "carbon_intensity_gco2e_kwh": CARBON_INTENSITY,
            "mitigation_gas_mt": MITIGATION_GAS,
            "mitigation_landfill_mt": MITIGATION_LANDFILL,
            "efficiency_jth_start": round(network_jth(E_GRID_START), 2),
            "efficiency_jth_end": round(network_jth(E_GRID_END), 2),
            "efficiency_end_date": E_GRID_END_DATE.isoformat(),
            "grid_greening_latest_month": green.latest_month,
        },
        "rows": rows,
    }


if __name__ == "__main__":
    out = build()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "series.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {len(out['rows'])} rows to {path} from {out['hashrate_source']}")
    if "--print" in sys.argv:
        for r in out["rows"][-5:]:
            print(r)
