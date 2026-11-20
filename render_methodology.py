"""Render methodology.md to methodology.html in the chart's style. Standalone page (served beside the chart)."""
import markdown, re, sys
md = open("methodology.md", encoding="utf-8").read()
body = markdown.markdown(md, extensions=["tables", "sane_lists", "toc"])
body = re.sub(r'<a href="(http[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', body)
# Bare URLs (as in the References list) become links too; only text not already inside a tag or an existing link.
body = re.sub(r'(?<![="\'>/\w])(https?://[^\s<]+?)(?=[.,;)]?(?:\s|<|$))', r'<a href="\1" target="_blank" rel="noopener">\1</a>', body)
html = f"""<!doctype html>
<html lang="en"><head><link rel="canonical" href="https://batcoinz.com/beest/methodology.html"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>BEEST 2 methodology</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600&display=swap">
<style>
:root {{ --bg:#092142; --ink:#EEEEEE; --ink-title:#CCCCCC; --ink-muted:#B8C0CC; --link:#3B86C6; --rule:rgba(238,238,238,0.14); --tile:rgba(255,255,255,0.045); color-scheme:dark; }}
body {{ background:var(--bg); color:var(--ink); font-family:"Open Sans",-apple-system,"Segoe UI",Helvetica,Arial,sans-serif; font-weight:400; margin:0; padding-block:28px 48px; padding-left:max(16px,env(safe-area-inset-left,0px)); padding-right:max(16px,env(safe-area-inset-right,0px)); line-height:1.6; font-size:17px; }}
main {{ max-width:860px; margin:0 auto; }}
h1 {{ font-weight:300; color:var(--ink-title); font-size:clamp(30px,4.6vw,50px); line-height:1.1; margin:0 0 10px; text-wrap:balance; }}
h2 {{ font-weight:300; color:var(--ink-title); font-size:30px; margin:48px 0 10px; border-top:1px solid var(--rule); padding-top:22px; }}
h3 {{ font-weight:600; font-size:19px; margin:30px 0 6px; }}
p {{ margin:0 0 14px; }}
a {{ color:var(--link); text-decoration:none; }} a:hover, a:focus {{ text-decoration:underline; }}
code {{ font-family:ui-monospace,Menlo,Consolas,monospace; font-size:0.92em; background:var(--tile); padding:1px 5px; }}
.tablewrap {{ overflow-x:auto; margin:10px 0 18px; }}
table {{ border-collapse:collapse; font-size:15px; min-width:640px; }}
th, td {{ text-align:left; vertical-align:top; padding:8px 12px; border-bottom:1px solid var(--rule); }}
th {{ color:var(--ink-muted); font-weight:600; letter-spacing:0.02em; }}
ul {{ padding-left:22px; }} li {{ margin:0 0 8px; }}
.back {{ display:inline-block; margin-bottom:18px; font-size:15px; }}
</style></head><body><main>
<a class="back" href="index.html">&larr; Back to the chart</a>
{body}
</main><!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "56d83fe84b3246c2821499ad48e61025"}}'></script><!-- End Cloudflare Web Analytics --></body></html>"""
html = html.replace("<table>", '<div class="tablewrap"><table>').replace("</table>", "</table></div>")
open("methodology.html", "w", encoding="utf-8").write(html)
print("ok", len(html))
