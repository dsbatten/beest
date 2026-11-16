"""
BEEST 2 hashrate feed.

Pulls daily difficulty-implied network hashrate from a public API that needs
no key, and returns the 7-day moving average in EH/s. This is the one live
input to the tracker; everything else is a static value in tracker-inputs.md.

Why mempool.space: it serves a daily series back to 2009 with no key or rate
plan, returns the current difficulty in the same call, and its figures match
blockchain.com and Coin Metrics to within a fraction of a percent (checked
15 November 2026: all three gave a 7-day average of 894 EH/s). The other two
are kept as fallbacks so a single outage does not blank the chart. Hashrate
Index (Luxor) also publishes this series, but its API needs a paid key.

Why a 7-day average: single-day figures swing by 10 percent or more on block
luck alone (811 to 984 EH/s in the week to 15 November 2026). Seven days is
the window Cambridge uses for its own hashrate figures, so the tracker's
check values line up with theirs.

Usage:
    python3 hashrate_feed.py            # prints today's 7-day average
    python3 hashrate_feed.py --series   # prints the daily series and rolling average as CSV
"""
import hashlib
import json
import os
import sys
import tempfile
import time
import urllib.request
from datetime import datetime, timezone

WINDOW = 7  # days in the moving average

# Each source: URL and a function turning its JSON into [(date, EH/s), ...]
def _mempool(days):
    # One endpoint for every span, so the live series and the history are built from the
    # same response. mempool.space runs several backends whose per-day averages can differ
    # by a few EH/s between calls (seen 16 November 2026: 946.3 against 940.4 EH/s for
    # 27 May 2026 on consecutive calls of /all), and two fetches of different spans gave
    # the two builders different 7-day averages for the same week.
    span = "3m" if days <= 90 else "all"
    data = _get(f"https://mempool.space/api/v1/mining/hashrate/{span}")
    return [(_day(h["timestamp"]), h["avgHashrate"] / 1e18) for h in data["hashrates"]]

def _blockchain_com(days):
    data = _get(f"https://api.blockchain.info/charts/hash-rate?timespan={days}days&format=json")
    return [(_day(v["x"]), v["y"] / 1e6) for v in data["values"]]  # TH/s -> EH/s

def _coinmetrics(days):
    url = ("https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
           f"?assets=btc&metrics=HashRate&frequency=1d&page_size={days}&paging_from=end")
    data = _get(url)["data"]
    return [(r["time"][:10], float(r["HashRate"]) / 1e6) for r in data]  # TH/s -> EH/s

SOURCES = [("mempool.space", _mempool), ("blockchain.com", _blockchain_com), ("Coin Metrics", _coinmetrics)]


CACHE_TTL = 3600  # seconds; one refresh run fetches each URL once and every builder reads the same bytes


def _get(url):
    """GET a JSON URL, caching the response on disk for CACHE_TTL seconds.

    build_series.py and build_history.py run back to back in the daily refresh and both
    need the same hashrate series; without the cache each makes its own request, and
    the upstream's backends do not always agree with each other to the last EH/s. The
    cache makes the two files consistent by construction, which is what the refresh
    workflow's cross-check asserts."""
    path = os.path.join(tempfile.gettempdir(), "beest-feed-" + hashlib.sha1(url.encode()).hexdigest() + ".json")
    try:
        if time.time() - os.path.getmtime(path) < CACHE_TTL:
            with open(path) as f:
                return json.load(f)
    except OSError:
        pass
    with urllib.request.urlopen(url, timeout=60) as r:
        data = json.load(r)
    try:
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f)
        os.replace(tmp, path)
    except OSError:
        pass
    return data


def _day(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d")


def daily_series(days=90):
    """Daily hashrate in EH/s from the first source that answers; returns (source name, series)."""
    last_error = None
    for name, fn in SOURCES:
        try:
            series = fn(days)
            if len(series) >= WINDOW:
                return name, series
        except Exception as e:  # network error, schema change, outage: try the next source
            last_error = e
    raise RuntimeError(f"no hashrate source answered; last error: {last_error}")


def moving_average(series, window=WINDOW):
    """Rolling mean over the trailing `window` days; the first window-1 days are left out."""
    out = []
    for i in range(window - 1, len(series)):
        vals = [v for _, v in series[i - window + 1:i + 1]]
        out.append((series[i][0], sum(vals) / window))
    return out


def current(window=WINDOW):
    """Latest 7-day average in EH/s, with its date and source."""
    name, series = daily_series()
    date, value = moving_average(series, window)[-1]
    return {"date": date, "ehs_7d": round(value, 1), "source": name}


if __name__ == "__main__":
    if "--series" in sys.argv:
        name, series = daily_series()
        print("date,daily_ehs,ma7_ehs  # source:", name)
        ma = dict(moving_average(series))
        for d, v in series:
            print(f"{d},{v:.1f},{ma.get(d, float('nan')):.1f}")
    else:
        print(json.dumps(current()))
