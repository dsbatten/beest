"""Write each chart page's latest figure into its HTML as plain text.

The charts are drawn in the browser, so search engines cannot read the figures inside them.
This script, run by the daily refresh after the data files are rebuilt, writes the update date and
the day's headline figure into the line under each chart's title, so the text a search engine reads
changes every day along with the data. The same figures are drawn on the charts by label.js.
"""
import json
import re

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fmt_date(iso):
    y, m, d = iso.split("-")
    return f"{int(d)} {MONTHS[int(m) - 1]} {y}"


def same_day_years_ago(rows, years):
    last = rows[-1]["date"]
    target = f"{int(last[:4]) - years}{last[4:]}"
    best = None
    for r in rows:
        if r["date"] <= target:
            best = r
        else:
            break
    return best


def net_intensity(r):
    return r["net_mt"] * 1000 / r["electricity_twh_yr"]


def latest_texts(data):
    rows = data["rows"]
    now = rows[-1]
    then = same_day_years_ago(rows, 7)
    texts = {"index.html": f"net emissions {now['net_mt']:.1f} MtCO2e a year"}
    if then:
        pct = (now["net_mt"] / then["net_mt"] - 1) * 100
        texts["index.html"] += f", {'up' if pct >= 0 else 'down'} {abs(pct):.1f}% vs {fmt_date(then['date'])}"
    if then:
        pct = round((1 - net_intensity(now) / net_intensity(then)) * 100)
        word = "down" if pct >= 0 else "up"
        texts["intensity.html"] = (f"net carbon intensity {net_intensity(now):.0f} gCO2e/kWh, "
                                   f"{word} {abs(pct)}% vs {fmt_date(then['date'])}")
    share = 100 * now["mitigation_gas_mt_30d"] / now["gross_mt_30d"]
    texts["mitigated.html"] = (f"{share:.1f}% of total emissions mitigated "
                               f"({now['mitigation_gas_mt_30d']:.2f} MtCO2e a year)")
    return texts


def main():
    data = json.load(open("history.json"))
    updated = fmt_date(data["generated"])
    texts = latest_texts(data)
    for page in ["index.html", "intensity.html", "mitigated.html", "sustainable.html", "since-2019.html"]:
        html = open(page).read()
        # The update date, so the static page no longer shows a dash before the chart's code runs.
        html = re.sub(r'<span id="updated">[^<]*</span>', f'<span id="updated">{updated}</span>', html, count=1)
        if page in texts:
            latest = f'<span id="latest">{texts[page]}</span>'
            # The latest figure gets a line of its own under the source line.
            html = re.sub(r'(?: <span class="sep">\|</span> |<br>)<b>latest:</b> <span id="latest">[^<]*</span>', '', html, count=1)
            html = html.replace(f'<span id="updated">{updated}</span>',
                                f'<span id="updated">{updated}</span><br><b>latest:</b> {latest}', 1)
        open(page, "w").write(html)
        print(page, "->", texts.get(page, "(date only)"))


if __name__ == "__main__":
    main()
