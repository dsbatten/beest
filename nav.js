// Draws the chart list on the right of every page from charts.json. Add a chart by adding a line to charts.json.
(function () {
  // Link text size, shared by every page. The panel keeps its 160px width; only the text grows.
  var st = document.createElement("style");
  st.textContent = ".nav a.nav-link { font-size: 17px !important; } .nav a.nav-link svg { width: 17px !important; height: 17px !important; }" +
    "@media (max-width: 900px) { .nav a.nav-link { font-size: 15px !important; } .nav a.nav-link svg { width: 15px !important; height: 15px !important; } }";
  document.head.appendChild(st);
  var here = location.pathname.split("/").pop() || "index.html";
  // Line icons, drawn in the link colour. "leaf" for emissions charts, "chart" for other series, "doc" for the methodology.
  var ICONS = {
    leaf: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19c0-7 4-12 14-13-1 10-6 14-13 14"/><path d="M5 19c2-4 6-7 10-9"/></svg>',
    chart: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19h16"/><path d="M5 15l4-5 4 3 6-8"/></svg>',
    doc: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/><path d="M9.5 13h5M9.5 17h5"/></svg>',
    articles: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v14H4z"/><path d="M7 9h10M7 12h10M7 15h6"/></svg>',
    mail: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18v12H3z"/><path d="M3 7l9 6 9-6"/></svg>',
    institute: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 9l9-5 9 5"/><path d="M5 10v8M9.5 10v8M14.5 10v8M19 10v8"/><path d="M3 20h18"/></svg>',
    person: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="3.5"/><path d="M5 20c1-4 4-6 7-6s6 2 7 6"/></svg>'
  };
  // Links to Daniel's other sites. Kept below a divider so they are not read as more charts.
  var EXTERNAL = [
    { title: "Articles", href: "https://batcoinz.com/", icon: "articles" },
    { title: "Newsletter", href: "https://www.batcoinz.com/", icon: "mail" },
    { title: "DARI", href: "https://www.da-ri.org/", icon: "institute" },
    { title: "Bitcoiner coaching", href: "https://www.danielbatten.co", icon: "person" }
  ];
  var TIP_ADDRESS = "soakedbobcat96@walletofsatoshi.com";
  // QR code for "lightning:" + TIP_ADDRESS, one hex string per row of 33 modules (1 = dark).
  var QR_ROWS = "1fc44047f 1057c9c41 1752bc15d 175e2015d 174d2415d 104551841 1fd55557f 001a44400 1053ec7ce 17b822632 04cd2584e 17165261d 1df6dfd69 06bfd9665 1fd006cda 09a12221d 0cf28e7b3 11a4bba6d 1245632a1 012e4ebbf 0beb31d13 1a3b95634 1363f9c9e 113bc43fc 18d9fb3f0 001777311 1fc835b56 104b6231d 174b269fa 17435141d 174b5d61f 1048b70cc 1fdf1a742".split(" ");
  var qrPath = QR_ROWS.map(function (row, y) {
    var bits = parseInt(row, 16).toString(2).padStart(33, "0"), d = "";
    for (var x = 0; x < 33; x++) if (bits[x] === "1") d += "M" + x + " " + y + "h1v1h-1z";
    return d;
  }).join("");
  var CHAI_SVG = '<svg viewBox="95 50 390 410" role="img" aria-label="Chai cup with a Lightning QR code" style="width:100%;max-width:150px;height:auto;display:block">' +
    '<g fill="none" stroke="#8FDCA6" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">' +
    '<path d="M200 70c-14 18 14 30 0 48M260 60c-14 18 14 30 0 48M320 70c-14 18 14 30 0 48" opacity="0.7"/>' +
    '<path d="M110 150h300l-26 270a30 30 0 0 1-30 27H166a30 30 0 0 1-30-27z"/>' +
    '<path d="M404 200h30a40 40 0 0 1 0 80h-38"/></g>' +
    '<rect stroke="none" x="180" y="190" width="160" height="160" rx="10" fill="#EEF2F5"/>' +
    '<g transform="translate(194 204) scale(4)"><path stroke="none" fill="#0A1A2F" d="' + qrPath + '"/></g>' +
    '<path d="M258 372l-12 22h12l-8 18 22-28h-12l8-12z" fill="#E4F060" stroke="none"/></svg>';
  function link(href, icon, title) {
    var a = document.createElement("a");
    a.className = "nav-link";
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
      a.className = "nav-link";
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
    // Lightning tip jar: the cup's QR code encodes the same lightning: address as the link.
    var tip = document.createElement("a");
    tip.className = "nav-tip";
    tip.href = "lightning:" + TIP_ADDRESS;
    tip.style.cssText = "display:block;margin-top:18px;";
    tip.innerHTML = CHAI_SVG + '<span style="display:block;margin-top:8px;font-size:13px;line-height:1.4;color:#F4F6F8;">If you got value from this research, buy me a chai</span>';
    nav.appendChild(tip);
  }).catch(function () {});
})();
