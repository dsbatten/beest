/* BEEST 2 on-chart headline label: the day's figure, drawn large in the bottom-right of the plot so a
   screenshot carries the figure and its date. Pages call beestLabel(...) and add the result to layout.annotations. */
window.beestLabel = function (big, small, color, narrow, css, y) {
  const bigPx = narrow ? 20 : 36, smallPx = narrow ? 10 : 15;
  return {
    xref: "paper", yref: "paper", x: 0.995, y: (y === undefined ? 0.02 : y), xanchor: "right", yanchor: "bottom", align: "right", showarrow: false,
    bgcolor: "rgba(0,0,0,0)", borderpad: 0,
    text: "<span style='font-size:" + bigPx + "px;font-weight:700;color:" + color + "'>" + big + "</span><br>" +
          "<span style='font-size:" + smallPx + "px;color:" + css("--ink-muted") + "'>" + small + "</span>",
  };
};
window.beestDate = function (iso) {
  const M = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  const d = new Date(iso + "T00:00:00Z"); return d.getUTCDate() + " " + M[d.getUTCMonth()] + " " + d.getUTCFullYear();
};
window.beestSameDayYearsAgo = function (rows, years) {
  const last = rows[rows.length - 1].date; const target = (parseInt(last.slice(0, 4), 10) - years) + last.slice(4);
  let best = null; for (const r of rows) { if (r.date <= target) best = r; else break; } return best;
};
