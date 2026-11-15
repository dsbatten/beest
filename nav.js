// Draws the chart list on the right of every page from charts.json. Add a chart by adding a line to charts.json.
(function () {
  var here = location.pathname.split("/").pop() || "index.html";
  fetch("charts.json", { cache: "no-store" }).then(function (r) { return r.json(); }).then(function (charts) {
    var nav = document.getElementById("nav");
    if (!nav) return;
    var h = document.createElement("h2"); h.textContent = "BEEST 2 charts"; nav.appendChild(h);
    charts.forEach(function (c) {
      var a = document.createElement("a");
      a.href = c.file; a.textContent = c.title; a.title = c.description || "";
      if (c.file === here) a.setAttribute("aria-current", "page");
      nav.appendChild(a);
    });
  }).catch(function () {});
})();
