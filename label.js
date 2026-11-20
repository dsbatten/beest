/* BEEST 2 on-chart headline label: the day's figure, drawn large on the plot so a screenshot carries the
   figure and its date. Pages call beestLabel(...) and add the result to layout.annotations.
   big   - one headline string drawn in `color`, or a list of { text, color } lines given equal weight
   small - the muted supporting line (what the figure is, and its date)
   y     - optional vertical position (fraction of the plot); default near the bottom
   opts  - optional { size: desktop font size for the big lines, smallFirst: put the small line above the big ones } */
window.beestLabel = function (big, small, color, narrow, css, y, opts) {
  opts = opts || {};
  const bigPx = narrow ? Math.round((opts.size || 36) * 0.55) : (opts.size || 36);
  const smallPx = narrow ? 10 : 15;
  const lines = (Array.isArray(big) ? big : [{ text: big, color: color }])
    .map((l) => "<span style='font-size:" + bigPx + "px;font-weight:700;color:" + (l.color || color) + "'>" + l.text + "</span>");
  const smallLine = "<span style='font-size:" + smallPx + "px;color:" + css("--ink-muted") + "'>" + small + "</span>";
  return {
    xref: "paper", yref: "paper", x: 0.995, y: (y === undefined ? 0.02 : y), xanchor: "right", yanchor: "bottom", align: "right", showarrow: false,
    bgcolor: "rgba(0,0,0,0)", borderpad: 0,
    // Line spacing follows the annotation's base font size, so a stack of large lines needs it raised to match.
    font: { size: lines.length > 1 ? bigPx : undefined },
    text: opts.smallFirst ? [smallLine].concat(lines).join("<br>") : lines.concat([smallLine]).join("<br>"),
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
