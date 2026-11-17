// Draws the chart list on the right of every page from charts.json. Add a chart by adding a line to charts.json.
(function () {
  var here = location.pathname.split("/").pop() || "index.html";
  // Line icons, drawn in the link colour. "leaf" for emissions charts, "chart" for other series, "doc" for the methodology.
  var ICONS = {
    leaf: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19c0-7 4-12 14-13-1 10-6 14-13 14"/><path d="M5 19c2-4 6-7 10-9"/></svg>',
    chart: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19h16"/><path d="M5 15l4-5 4 3 6-8"/></svg>',
    doc: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/><path d="M9.5 13h5M9.5 17h5"/></svg>',
    articles: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v14H4z"/><path d="M7 9h10M7 12h10M7 15h6"/></svg>',
    mail: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18v12H3z"/><path d="M3 7l9 6 9-6"/></svg>',
    person: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="3.5"/><path d="M5 20c1-4 4-6 7-6s6 2 7 6"/></svg>'
  };
  // Links to Daniel's other sites. Kept below a divider so they are not read as more charts.
  var EXTERNAL = [
    { title: "Articles", href: "https://batcoinz.com/", icon: "articles" },
    { title: "Newsletter", href: "https://www.batcoinz.com/", icon: "mail" },
    { title: "Bitcoiner coaching", href: "https://www.danielbatten.co", icon: "person" }
  ];
  function link(href, icon, title) {
    var a = document.createElement("a");
    a.href = href;
    a.innerHTML = ICONS[icon] + "<span></span>";
    a.querySelector("span").textContent = title;
    return a;
  }
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
    // Divider: a rule styled inline so every page gets it without its own CSS.
    var hr = document.createElement("hr");
    hr.style.cssText = "border:0;border-top:1px solid rgba(238,238,238,0.18);margin:12px 0;width:100%;";
    nav.appendChild(hr);
    EXTERNAL.forEach(function (e) { nav.appendChild(link(e.href, e.icon, e.title)); });
  }).catch(function () {});
})();
