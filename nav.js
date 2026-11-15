// Draws the chart list on the right of every page from charts.json. Add a chart by adding a line to charts.json.
(function () {
  var here = location.pathname.split("/").pop() || "index.html";
  // Line icons, drawn in the link colour. "leaf" for emissions charts, "chart" for other series, "doc" for the methodology.
  var ICONS = {
    leaf: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19c0-7 4-12 14-13-1 10-6 14-13 14"/><path d="M5 19c2-4 6-7 10-9"/></svg>',
    chart: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19h16"/><path d="M5 15l4-5 4 3 6-8"/></svg>',
    doc: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/><path d="M9.5 13h5M9.5 17h5"/></svg>'
  };
  fetch("charts.json", { cache: "no-store" }).then(function (r) { return r.json(); }).then(function (charts) {
    var nav = document.getElementById("nav");
    if (!nav) return;
    var h = document.createElement("h2"); h.textContent = "BEEST 2 charts"; nav.appendChild(h);
    charts.forEach(function (c) {
      var a = document.createElement("a");
      a.href = c.file; a.title = c.description || "";
      a.innerHTML = (ICONS[c.icon] || ICONS.chart) + "<span></span>";
      a.querySelector("span").textContent = c.title;
      if (c.file === here) a.setAttribute("aria-current", "page");
      nav.appendChild(a);
    });
  }).catch(function () {});
})();
