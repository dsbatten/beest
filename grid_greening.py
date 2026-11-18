"""
Grid greening: moves the on-grid part of the December 2025 Cambridge energy mix with the world grid.

Cambridge measured the mining mix once, in December 2025 (59.4% low-carbon, 252 gCO2e/kWh). Between
surveys the grid-connected part of the network gets cleaner as the grids it draws from get cleaner.
This module applies that change, and only to the on-grid share; off-grid mining is held as surveyed.

    ratio_clean(d)     = world grid clean share (12 months to the latest month) / same for the 12 months to Dec 2025
    ratio_intensity(d) = world grid gCO2e/kWh (12 months to the latest month)   / same for the 12 months to Dec 2025

    clean(d)     = clean_off_part + ON_GRID x clean_on_grid_Dec2025 x ratio_clean(d)
    intensity(d) = 252 x [ (1 - ON_GRID) + ON_GRID x ratio_intensity(d) ]

Data: Ember monthly electricity data, world totals (CC BY 4.0). A copy of the derived monthly series is kept
in grid_greening.json so the daily build still runs if Ember cannot be reached.
"""
import csv
import io
import json
import os
import urllib.request
from datetime import date

EMBER_URL = "https://files.ember-energy.org/public-downloads/generation/outputs/release_generation_monthly_global.csv"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grid_greening.json")

BASE_MONTH = "2025-12"          # 12 months to December 2025 = the year of the Cambridge survey mix
CLEAN_DEC_2025 = 0.594          # Cambridge 2nd edition, December 2025
INTENSITY_DEC_2025 = 252.0      # gCO2e/kWh, Cambridge 2nd edition, December 2025
ON_GRID = 0.919                 # Cambridge, April 2025: 8.1% of mining power off-grid
OFF_GRID_CLEAN = 0.72 / 1.23    # Cambridge, April 2025: of 1.23 GW off-grid, 0.507 GW runs on flare gas; the rest on co-located, mostly renewable power
CLEAN_ON_GRID_DEC_2025 = (CLEAN_DEC_2025 - (1 - ON_GRID) * OFF_GRID_CLEAN) / ON_GRID


def _monthly_world():
    """{'YYYY-MM': (total TWh, clean TWh, MtCO2e)} for the world, from Ember."""
    req = urllib.request.Request(EMBER_URL, headers={"User-Agent": "beest2-refresh"})
    with urllib.request.urlopen(req, timeout=180) as r:
        text = r.read().decode("utf-8")
    out = {}
    for x in csv.DictReader(io.StringIO(text)):
        if x["Area"] != "World":
            continue
        m = x["Date"][:7]
        tot, cl, em = out.get(m, (None, None, None))
        if x["Electricity source"] == "Total generation":
            tot, em = float(x["Generation (TWh)"]), float(x["Emissions (MtCO2e)"])
        elif x["Electricity source"] == "Clean":
            cl = float(x["Generation (TWh)"])
        out[m] = (tot, cl, em)
    return {m: v for m, v in out.items() if None not in v}


def trailing_series():
    """[(month, clean share, gCO2e/kWh)], each on the 12 months to that month. Falls back to the cached copy."""
    try:
        w = _monthly_world()
        ms = sorted(w)
        rows = []
        for i in range(11, len(ms)):
            win = ms[i - 11:i + 1]
            T = sum(w[m][0] for m in win); C = sum(w[m][1] for m in win); E = sum(w[m][2] for m in win)
            rows.append((ms[i], round(C / T, 5), round(E * 1000 / T, 2)))
        with open(CACHE, "w") as f:
            json.dump({"source": EMBER_URL, "fetched": date.today().isoformat(), "rows": rows}, f, indent=0)
        return rows
    except Exception:
        with open(CACHE) as f:
            return [tuple(r) for r in json.load(f)["rows"]]


def _month_end(m):
    y, mo = map(int, m.split("-"))
    nxt = date(y + (mo == 12), mo % 12 + 1, 1)
    return date.fromordinal(nxt.toordinal() - 1)


class Greening:
    """Daily clean share and carbon intensity for dates from December 2025 on."""

    def __init__(self):
        rows = trailing_series()
        base = {m: (c, e) for m, c, e in rows}[BASE_MONTH]
        # Points at each month end from the base month on; linear between them, flat after the last.
        self.pts = [(_month_end(m), c / base[0], e / base[1]) for m, c, e in rows if m >= BASE_MONTH]
        self.latest_month = rows[-1][0]

    def ratios(self, d):
        p = self.pts
        if d <= p[0][0]:
            return 1.0, 1.0
        for (d0, c0, e0), (d1, c1, e1) in zip(p, p[1:]):
            if d <= d1:
                f = (d - d0).days / (d1 - d0).days
                return c0 + f * (c1 - c0), e0 + f * (e1 - e0)
        return p[-1][1], p[-1][2]

    def clean(self, d):
        rc, _ = self.ratios(d)
        return (1 - ON_GRID) * OFF_GRID_CLEAN + ON_GRID * CLEAN_ON_GRID_DEC_2025 * rc

    def intensity(self, d):
        _, ri = self.ratios(d)
        return INTENSITY_DEC_2025 * ((1 - ON_GRID) + ON_GRID * ri)


if __name__ == "__main__":
    g = Greening()
    for d in (date(2025, 12, 1), date(2026, 3, 31), date(2026, 6, 30), date(2026, 9, 30), date.today()):
        print(d, round(100 * g.clean(d), 2), "% clean", round(g.intensity(d), 1), "gCO2e/kWh")
    print("latest Ember month", g.latest_month)
