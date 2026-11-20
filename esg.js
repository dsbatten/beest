/* BEEST 2 ESG charts: one renderer shared by every single-metric chart page.
   Each page sets window.ESG = { file, aria, traces(rows, css), yaxis(rows, narrow), price } before loading this file.
   Look and behaviour follow index.html: navy canvas, Open Sans, clickable legend, BTC price on a quiet log axis
   banded into the top fifth of the plot so it stays clear of the metric. */
(function () {
  const $ = (id) => document.getElementById(id);
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const spec = window.ESG;

  // Log band for a side axis: the series occupies the slice of the plot between fracBottom and fracTop.
  function band(values, fracTop, fracBottom) {
    const logs = values.filter((v) => v > 0).map((v) => Math.log10(v));
    const lo = Math.min(...logs), hi = Math.max(...logs), span = Math.max(hi - lo, 0.05);
    const full = span / (fracTop - fracBottom);
    const bottom = lo - fracBottom * full;
    return [bottom, bottom + full];
  }
  const nice = (lo, hi, steps) => { const out = []; for (let k = -2; k <= 7; k++) for (const s of steps) { const v = +(s * Math.pow(10, k)).toPrecision(6); if (v >= lo && v <= hi) out.push(v); } return out; };
  const within = (cands, vals) => { const lo = Math.min(...vals) * 0.97, hi = Math.max(...vals) * 1.03; return cands.filter((v) => v >= lo && v <= hi); };

  function render(data) {
    const rows = data.rows;
    const upd = new Date(data.generated + "T00:00:00Z");
    $("updated").textContent = upd.getUTCDate() + " " + MONTHS[upd.getUTCMonth()] + " " + upd.getUTCFullYear();

    const narrow = window.innerWidth < 700;
    const fs = narrow ? Math.max(7, Math.round(window.innerWidth * 0.029)) : 15;
    const lw = (w) => narrow ? Math.round(w * 0.55 * 10) / 10 : w;
    const x = rows.map((r) => r.date);
    const traces = spec.traces(rows, css, lw).map((t) => Object.assign({ x, mode: "lines" }, t));

    const showPrice = spec.price !== false && rows.some((r) => r.price_usd);
    const priceVals = rows.map((r) => r.price_usd || 0).filter((v) => v > 0);
    if (showPrice) traces.push({ name: "BTC price", x, y: rows.map((r) => r.price_usd), yaxis: "y3", mode: "lines", line: { color: css("--price"), width: lw(2) },
      hovertemplate: "$%{y:,.0f}<extra>BTC price</extra>" });

    const sideTick = { family: css("--font"), color: "rgba(184,192,204,0.7)", size: narrow ? 10 : 11, weight: 300 };
    const priceTicks = showPrice ? within(nice(1, 1e7, [1, 2, 5]), priceVals) : [];
    const y = spec.yaxis(rows, narrow);
    const layout = {
      paper_bgcolor: css("--bg"), plot_bgcolor: css("--bg"), font: { family: css("--font"), color: css("--ink"), size: fs },
      margin: { l: narrow ? Math.round(fs * 3.7) : 80, r: narrow ? 12 : 70, t: narrow ? 12 : 20, b: narrow ? Math.round(fs * 5.8) : 80 },
      hovermode: narrow ? false : "x unified",
      dragmode: narrow ? false : "zoom",
      hoverlabel: { bgcolor: "#0D2B55", bordercolor: "rgba(238,238,238,0.2)", font: { family: css("--font"), color: css("--ink"), size: narrow ? 12 : 14 } },
      legend: { orientation: "h", x: 0.5, xanchor: "center", y: narrow ? -0.13 : -0.16, yanchor: "top", font: { size: fs, color: css("--ink-muted") }, itemclick: "toggle", itemdoubleclick: "toggleothers", traceorder: "normal" },
      xaxis: { type: "date", showgrid: false, zeroline: false, tickformat: "%b %Y", ticks: "outside", tickcolor: css("--ink-muted"), tickfont: { color: css("--ink-muted") }, linecolor: css("--grid"), hoverformat: "%-d %b %Y" },
      yaxis: Object.assign({ gridcolor: css("--grid"), zeroline: false, tickfont: { color: css("--ink-muted") }, fixedrange: narrow,
        title: { text: narrow ? y.titleShort : y.title, font: { color: css("--ink-muted"), size: narrow ? Math.max(7, fs - 1) : 15 }, standoff: narrow ? 4 : 10 } }, y.axis),
      yaxis3: { type: "log", overlaying: "y", side: "right", showgrid: false, zeroline: false, showline: false, ticks: "",
        tickfont: sideTick, range: showPrice ? band(priceVals, 0.97, 0.45) : [0, 1], tickvals: priceTicks,
        ticktext: priceTicks.map((v) => v >= 1000 ? "$" + (v / 1000) + "k" : "$" + v), fixedrange: narrow, visible: showPrice && !narrow },
    };
    const config = { responsive: true, displaylogo: false, displayModeBar: !narrow, scrollZoom: false, doubleClick: narrow ? false : "reset",
      modeBarButtonsToRemove: ["select2d", "lasso2d", "autoScale2d", "toggleSpikelines"], toImageButtonOptions: { filename: spec.file, scale: 2 } };
    if (spec.label && window.beestLabel) { const L = spec.label(rows); if (L) layout.annotations = [window.beestLabel(L.big, L.small, css(L.color), narrow, css)]; }
    Plotly.react("chart", traces, layout, config);
  }

  fetch("history.json", { cache: "no-store" })
    .then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then((d) => { window.__beest = d; render(d); })
    .catch((e) => { $("status").hidden = false; $("status").textContent = "The series could not be loaded (" + e.message + "). The page is rebuilt daily; try again shortly."; });

  let t; window.addEventListener("resize", () => { clearTimeout(t); t = setTimeout(() => { if (window.__beest) render(window.__beest); }, 250); });
})();
