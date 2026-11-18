"""
BEEST 2 history builder.

Extends the emissions series back to 1 September 2019 so the long chart runs
seamlessly into the live one. Writes history.json. From 1 December 2025 the
rows are exactly those of build_series.py (the live method); before that the
inputs come from BEEST 1 and Cambridge, as set out in methodology.md.

Per day, the chain is the same as the live chart:
    TWh/yr = hashrate (EH/s) x efficiency (J/TH) x 8.76
    gross  = TWh/yr x intensity (gCO2e/kWh) / 1000
    net    = gross - emission mitigation (gas)

How each input is built before 1 December 2025:
  Efficiency (facility level) = 1.0884 x grid-fleet efficiency, the same structure
    as the live method (1.05 overhead; one tenth of hashrate on older machines at
    1.366 times the grid fleet's J/TH). The grid-fleet figure comes from:
      - 1 Jun 2022 to 1 Dec 2025: Cambridge survey anchors 40.7 (Jun 2022), 36.9
        (Jun 2023), 28.2 (Jun 2024) and 20.5 (Dec 2025, the mean of Cambridge's
        20.8 and Luxor's 20.2), interpolated on a log scale between anchors.
      - Before 1 Jun 2022: a straight log-scale line from September 2019 to the
        June 2022 anchor. The September 2019 level is CBECI's hardware-efficiency
        figure for that month (86.0 J/TH) scaled by the same factor that brings
        CBECI's June 2022 figure onto the survey (40.7 / 48.4 = 0.841), giving
        72.3 J/TH. CBECI's month-to-month shape between those dates is not used:
        its hardware model before the August 2023 update produced swings (such
        as the 2020 dip) that reflect its price-driven machine selection rather
        than the fleet. The implied improvement, 19 percent a year, matches the
        18 percent a year the survey anchors show for 2022 to 2025.
  Intensity (gross, gCO2e/kWh): BEEST 1's Scope 2 series, straight lines between
    its dated points; from its last point (26 Oct 2024, 260.8) a straight line to
    Cambridge's 252 at 1 Dec 2025.
  Emission mitigation (gas): BEEST 1's (Scope 2 minus total) g/kWh times the
    electricity, rescaled by 82.5/84 to restate its GWP20 of 84 at the AR6 value;
    from 26 Oct 2024 a straight line in Mt to Cambridge's 4.69 at 1 Dec 2025.
  Clean (sustainable) energy share: BEEST 1's series, then a straight line to
    Cambridge's 59.4% at 1 Dec 2025, held after.
  Hashrate: 7-day average of the daily difficulty-implied figure (mempool.space).
  Price: Coin Metrics PriceUSD, context only.
"""
import csv
import json
import math
import os
import sys
import urllib.request
from datetime import date, timedelta

import build_series as live
from hashrate_feed import moving_average, _get

HERE = os.path.dirname(os.path.abspath(__file__))
START = date(2019, 9, 1)
LIVE_START = live.START                     # 1 December 2025
ANCHOR_SURVEY = {date(2022, 6, 1): 40.7, date(2023, 6, 1): 36.9, date(2024, 6, 1): 28.2, LIVE_START: live.E_GRID_START}
NETWORK_FACTOR = live.PUE * ((1 - live.S_OFF) + live.S_OFF * (live.E_OFF / live.E_GRID_START))  # 1.0884
GWP_RESCALE = 82.5 / 84.0                   # BEEST 1 used GWP20 84; the tracker uses AR6's 82.5
CAMBRIDGE_INTENSITY = live.CARBON_INTENSITY  # 252
CAMBRIDGE_CLEAN = 0.594


def load_cbeci():
    rows = []
    with open(os.path.join(HERE, "sources", "cbeci-hardware-efficiency-monthly.csv"), encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or line.startswith("month"):
                continue
            m, e, _ = line.strip().split(",")
            y, mo = m.split("-")
            rows.append((date(int(y), int(mo), 1), float(e)))
    return rows


def load_beest1():
    rows = []
    with open(os.path.join(HERE, "sources", "beest1-emission-intensity.csv"), encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or line.startswith("date"):
                continue
            d, s2, tot, clean = line.strip().split(",")
            rows.append((date.fromisoformat(d), float(s2), float(tot), float(clean)))
    return rows


def interp(points, d, log=False):
    """Linear (or log-linear) interpolation of [(date, value), ...] at date d; flat beyond the ends."""
    if d <= points[0][0]:
        return points[0][1]
    if d >= points[-1][0]:
        return points[-1][1]
    for (d0, v0), (d1, v1) in zip(points, points[1:]):
        if d0 <= d <= d1:
            f = (d - d0).days / (d1 - d0).days
            if log:
                return math.exp(math.log(v0) + f * (math.log(v1) - math.log(v0)))
            return v0 + f * (v1 - v0)


def grid_efficiency(d, cbeci, scale):
    if d >= date(2022, 6, 1):
        return interp(sorted(ANCHOR_SURVEY.items()), d, log=True)
    start = dict(cbeci)[START] * scale                     # Sep 2019 level, CBECI scaled to the survey
    return interp([(START, start), (date(2022, 6, 1), 40.7)], d, log=True)


def hashrate_daily_all():
    data = _get("https://mempool.space/api/v1/mining/hashrate/all")["hashrates"]
    from datetime import datetime, timezone
    by_day = {}
    for h in data:
        by_day[datetime.fromtimestamp(h["timestamp"], timezone.utc).date()] = h["avgHashrate"] / 1e18
    days = sorted(by_day)
    # fill any missing day with the previous value so the 7-day window is always seven days
    out, cur = [], days[0]
    while cur <= days[-1]:
        if cur in by_day:
            last = by_day[cur]
        out.append((cur.isoformat(), last))
        cur += timedelta(days=1)
    return out


def price_all():
    url = ("https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
           "?assets=btc&metrics=PriceUSD&frequency=1d&start_time=2019-08-01&page_size=10000")
    try:
        data = _get(url)["data"]
        return {r["time"][:10]: float(r["PriceUSD"]) for r in data}
    except Exception:
        return {}


def supply_all():
    """Coins in circulation (Coin Metrics SplyCur), used for market cap on the per-dollar chart."""
    url = ("https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
           "?assets=btc&metrics=SplyCur&frequency=1d&start_time=2019-08-01&page_size=10000")
    try:
        data = _get(url)["data"]
        return {r["time"][:10]: float(r["SplyCur"]) for r in data}
    except Exception:
        return {}


def build():
    cbeci = load_cbeci()
    scale = 40.7 / dict(cbeci)[date(2022, 6, 1)]
    b1 = load_beest1()
    s2_pts = [(d, s2) for d, s2, _, _ in b1] + [(LIVE_START, CAMBRIDGE_INTENSITY)]
    mit_g_pts = [(d, s2 - tot) for d, s2, tot, _ in b1]            # g/kWh of mitigation, BEEST 1 basis
    # Data quality: a BEEST 1 row whose net figure equals its gross figure has an unfilled mitigation cell
    # (13 March 2023: 0.38 g/kWh between neighbours near 20). Such a point is dropped and the offset
    # interpolated across it; gross intensity and clean share from the same row are kept.
    kept = []
    for i, (d, g) in enumerate(mit_g_pts):
        nb = [mit_g_pts[j][1] for j in (i - 1, i + 1) if 0 <= j < len(mit_g_pts)]
        if nb and all(g < 0.5 * v for v in nb):
            print("dropped BEEST 1 mitigation point", d, round(g, 2), "g/kWh; neighbours", [round(v, 2) for v in nb])
            continue
        kept.append((d, g))
    mit_g_pts = kept
    clean_pts = [(d, c) for d, _, _, c in b1] + [(LIVE_START, CAMBRIDGE_CLEAN)]
    b1_last = b1[-1][0]

    daily = hashrate_daily_all()
    ma = moving_average(daily)
    prices = price_all()
    live_rows = {r["date"]: r for r in live.build()["rows"]}

    rows, last_price, mit_at_b1_last = [], None, None
    for day, ehs in ma:
        d = date.fromisoformat(day)
        if d < START:
            continue
        last_price = prices.get(day, last_price)
        if d >= LIVE_START and day in live_rows:
            r = dict(live_rows[day])
            r["basis"] = "BEEST 2"
            if r.get("price_usd") is None and last_price:
                r["price_usd"] = round(last_price)
            rows.append(r)
            continue
        e_grid = grid_efficiency(d, cbeci, scale)
        jth = NETWORK_FACTOR * e_grid
        gw = ehs * jth / 1000.0
        twh = gw * 8.76
        intensity = interp(s2_pts, d)
        gross = twh * intensity / 1000.0
        if d <= b1_last:
            mit = twh * interp(mit_g_pts, d) / 1000.0 * GWP_RESCALE
            mit_at_b1_last = mit
            basis = "BEEST 1"
        else:
            start_mit = mit_at_b1_last if mit_at_b1_last is not None else live.MITIGATION_GAS
            mit = interp([(b1_last, start_mit), (LIVE_START, live.MITIGATION_GAS)], d)
            basis = "BEEST 1"
        rows.append({
            "date": day,
            "hashrate_ehs_7d": round(ehs, 1),
            "efficiency_jth": round(jth, 2),
            "power_gw": round(gw, 2),
            "electricity_twh_yr": round(twh, 1),
            "intensity_g_kwh": round(intensity, 1),
            "gross_mt": round(gross, 2),
            "mitigation_gas_mt": round(mit, 2),
            "mitigation_landfill_mt": None,
            "net_mt": round(gross - mit, 2),
            "price_usd": round(last_price) if last_price else None,
            "clean_share": round(interp(clean_pts, d), 4),
            "basis": basis,
        })
    # Coins in circulation; the latest day carries the previous day's figure until Coin Metrics publishes it.
    supplies, last_supply = supply_all(), None
    for r in rows:
        last_supply = supplies.get(r["date"], last_supply)
        r["supply_btc"] = round(last_supply) if last_supply else None
    return {
        "generated": date.today().isoformat(),
        "hashrate_source": "mempool.space",
        "price_source": "Coin Metrics community API (PriceUSD)" if prices else None,
        "supply_source": "Coin Metrics community API (SplyCur)" if supplies else None,
        "inputs": {
            "network_factor": round(NETWORK_FACTOR, 4),
            "cbeci_scale_to_june_2022_survey": round(scale, 4),
            "sep_2019_grid_jth": round(dict(cbeci)[START] * scale, 2),
            "gwp_rescale_beest1_to_ar6": round(GWP_RESCALE, 4),
            "survey_anchors_jth": {k.isoformat(): v for k, v in sorted(ANCHOR_SURVEY.items())},
            "live_from": LIVE_START.isoformat(),
        },
        "rows": rows,
    }


if __name__ == "__main__":
    out = build()
    path = os.path.join(HERE, "history.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"wrote {len(out['rows'])} rows to {path}")
    if "--print" in sys.argv:
        for key in ["2019-09-01", "2020-07-01", "2021-07-01", "2022-06-01", "2023-06-01", "2024-06-01", "2024-10-26", "2025-06-01", "2025-11-30", "2025-12-01", out["rows"][-1]["date"]]:
            r = next((x for x in out["rows"] if x["date"] == key), None)
            if r:
                print(key, r["hashrate_ehs_7d"], "EH/s", r["efficiency_jth"], "J/TH", r["electricity_twh_yr"], "TWh", r["intensity_g_kwh"], "g/kWh", "gross", r["gross_mt"], "mit", r["mitigation_gas_mt"], "net", r["net_mt"], r["basis"][:20])
