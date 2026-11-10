#!/usr/bin/env python3
"""Convert source/landing-page.dc.html into dist/ (static site). Run: python3 -I tools/build.py"""
import re, json, html, pathlib
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "source"; DIST = ROOT / "dist"; A = DIST / "assets"
A.mkdir(parents=True, exist_ok=True)
ACCENT = "#CF202E"
SITE = "https://aiaudit.redcatmarketing.ca/"

# ---------- images ----------
def save(img, name, **kw):
    img.save(A / name, **kw); return img.size
logo = Image.open(SRC/"assets/red-cat-logo.png").convert("RGBA")
logo_s = logo.resize((int(88*logo.width/logo.height*2)//1, 176), Image.LANCZOS)  # 2x of 44px header
logo_w, logo_h = logo_s.size
logo_s.save(A/"red-cat-logo.png", optimize=True)
logo_s.save(A/"red-cat-logo.webp", quality=88)
hero = Image.open(SRC/"assets/hero-phone.jpg").convert("RGB")
h1 = hero.resize((1920, round(1920*hero.height/hero.width)), Image.LANCZOS)
h1.save(A/"hero-phone.jpg", quality=72, optimize=True, progressive=True)
h2 = hero.resize((900, round(900*hero.height/hero.width)), Image.LANCZOS)
h2.save(A/"hero-phone-sm.jpg", quality=72, optimize=True, progressive=True)
rep = Image.open(SRC/"assets/audit-report.jpg").convert("RGB")
rep_w = 1600; rep_h = round(rep_w*rep.height/rep.width)
r = rep.resize((rep_w, rep_h), Image.LANCZOS)
r.save(A/"audit-report.jpg", quality=78, optimize=True, progressive=True)
r.save(A/"audit-report.webp", quality=76)
# share image 1200x630 crop (center) for OG
og_h = round(rep.width*630/1200)
top = max(0,(rep.height-og_h)//2)
og = rep.crop((0,top,rep.width,top+og_h)).resize((1200,630), Image.LANCZOS)
og.save(A/"og-image.jpg", quality=80, optimize=True)
# favicon: red skewed slash on white (brand mark used in the page)
from PIL import ImageDraw
S=256; fav=Image.new("RGBA",(S,S),(255,255,255,0)); d=ImageDraw.Draw(fav)
d.rounded_rectangle((0,0,S-1,S-1),radius=40,fill=(17,17,17,255))
d.polygon([(48,150),(208,104),(208,152),(48,198)],fill=(207,32,46,255))
fav.resize((64,64),Image.LANCZOS).save(DIST/"favicon.png")
fav.save(DIST/"favicon.ico", sizes=[(16,16),(32,32),(48,48)])
fav.resize((180,180),Image.LANCZOS).save(DIST/"apple-touch-icon.png")

# ---------- html ----------
s = (SRC/"landing-page.dc.html").read_text()
helmet = re.search(r"<helmet>(.*?)</helmet>", s, re.S).group(1)
body = re.search(r"<x-dc>(.*?)</x-dc>", s, re.S).group(1)
body = re.sub(r"<helmet>.*?</helmet>", "", body, flags=re.S)
style = re.search(r"<style>(.*?)</style>", helmet, re.S).group(1)
fonts = re.search(r'<link href="(https://fonts[^"]+)"', helmet).group(1)

style = style.replace("url(/_blob/79fcdec79d7568266ce7f08752ee20aa)", "url(assets/hero-phone.jpg)", 1)
# mobile hero uses the smaller file
style = style.replace("url(/_blob/79fcdec79d7568266ce7f08752ee20aa)", "url(assets/hero-phone-sm.jpg)")
style += """
.icon-close{display:none}.menu-open .icon-close{display:block}.menu-open .icon-open{display:none}
a:focus-visible,button:focus-visible,summary:focus-visible{outline:2px solid #CF202E;outline-offset:2px}
input[type=radio]:focus-visible{outline:2px solid #CF202E;outline-offset:2px}
.hp{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
.form-error{display:none;background:#FDECEE;border:1px solid #CF202E;color:#7A0F18;padding:12px 14px;border-radius:2px;font-size:15px;font-weight:500}
.form-error.show{display:block}
html,body{max-width:100%;overflow-x:hidden}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
"""
body = body.replace("{{accent}}", ACCENT)
body = re.sub(r'\s*onClick="\{\{[^}]*\}\}"', "", body)
body = body.replace('class="nav-bar {{menuClass}}"', 'class="nav-bar" id="nav-bar"')
body = body.replace('aria-expanded="{{ariaExpanded}}"', 'id="nav-toggle" aria-expanded="false"')
body = body.replace('aria-label="{{toggleLabel}}"', 'aria-label="Open menu"')
body = re.sub(r'<sc-if value="\{\{menuOpen\}\}"[^>]*>(<svg )(.*?)</sc-if>', r'\1class="icon-close" \2', body, flags=re.S)
body = re.sub(r'<sc-if value="\{\{menuClosed\}\}"[^>]*>(<svg )(.*?)</sc-if>', r'\1class="icon-open" \2', body, flags=re.S)
assert "{{" not in body and "sc-if" not in body, re.findall(r"\{\{.*?\}\}", body)
# logo
body = body.replace('<img src="/_blob/a352247ed3e7de09f2bf2f9d72dc8c1c" alt="Red Cat Marketing" style="height: 44px; width: auto">',
  f'<img src="assets/red-cat-logo.png" alt="Red Cat Marketing" width="{round(44*logo_w/logo_h)}" height="44" style="height: 44px; width: auto">')
body = body.replace('<img src="/_blob/a352247ed3e7de09f2bf2f9d72dc8c1c" alt="Red Cat Marketing" style="height: 40px; width: auto">',
  f'<img src="assets/red-cat-logo.png" alt="Red Cat Marketing" width="{round(40*logo_w/logo_h)}" height="40" loading="lazy" style="height: 40px; width: auto">')
# report image
m = re.search(r'<img src="/_blob/2cb7e659b8b9c7aed230ce7f52887982" alt="([^"]*)" style="([^"]*)">', body)
body = body.replace(m.group(0),
  f'<picture><source srcset="assets/audit-report.webp" type="image/webp"><img src="assets/audit-report.jpg" alt="{m.group(1)}" width="{rep_w}" height="{rep_h}" loading="lazy" decoding="async" style="{m.group(2)}"></picture>')
assert "/_blob/" not in body + style

# form
form_open = re.search(r'<form style="([^"]*)" aria-label="([^"]*)">', body)
body = body.replace(form_open.group(0),
  f'<form id="audit-form" action="https://api.web3forms.com/submit" method="post" style="{form_open.group(1)}" aria-label="{form_open.group(2)}">\n'
  '<div id="form-error" class="form-error" role="alert" tabindex="-1">Sorry, something went wrong sending your request. Please check the required fields and try again, or email us directly.</div>\n'
  '<input type="hidden" name="access_key" value="f6058e88-d028-4f5f-b17e-cfb63106ab9c">\n'
  '<input type="hidden" name="subject" value="New AI Visibility Audit request">\n'
  '<input type="hidden" name="from_name" value="Red Cat AI Audit (aiaudit.redcatmarketing.ca)">\n'
  '<input type="hidden" name="redirect" value="https://aiaudit.redcatmarketing.ca/thank-you.html">\n'
  '<div class="hp" aria-hidden="true"><label>Leave this box unchecked<input type="checkbox" name="botcheck" tabindex="-1" autocomplete="off"></label></div>')
for nm in ("first_name","last_name","email","website"):
    body = body.replace(f'name="{nm}"', f'name="{nm}" id="f_{nm}" required', 1)
body = body.replace('name="geo_area"', 'name="geo_area" id="f_geo_area" autocomplete="off"')
body = body.replace('name="competitors"', 'name="competitors" id="f_competitors"')
body = body.replace('name="notes"', 'name="notes" id="f_notes"')
body = body.replace('name="website" id="f_website" required', 'name="website" id="f_website" required autocomplete="url"')

# FAQ for schema (exact text)
faq = re.findall(r'<h3 style="margin: 0; font-family: \'Playfair Display\', serif; font-weight: 500; font-size: 26px; line-height: 1.2">(.*?)</h3>\s*<p style="[^"]*">(.*?)</p>', body, re.S)
assert len(faq)==4, len(faq)
faq = [(html.unescape(q).strip(), html.unescape(a).strip()) for q,a in faq]

title = "AI Visibility Audit | Red Cat Marketing"
desc = "See where ChatGPT, Claude and Google's AI Overviews recommend your brand, where competitors beat you, and what to fix first. One-time $997 audit."
assert len(desc) <= 155, len(desc)
org = {"@type":"Organization","@id":"https://www.redcatmarketing.ca/#organization","name":"Red Cat Marketing","url":"https://www.redcatmarketing.ca",
       "logo":SITE+"assets/red-cat-logo.png","sameAs":["https://www.linkedin.com/company/redcatmarketing/"]}
service = {"@type":"Service","name":"AI Visibility Audit","description":desc,"serviceType":"AI search visibility audit",
  "provider":{"@id":"https://www.redcatmarketing.ca/#organization"},"areaServed":{"@type":"Country","name":"Canada"},
  "url":SITE,"offers":{"@type":"Offer","price":"997","priceCurrency":"CAD","url":SITE+"#get-audit"}}
faqp = {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faq]}
ld = json.dumps({"@context":"https://schema.org","@graph":[org,service,faqp]}, ensure_ascii=False, indent=1)

head = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{SITE}">
<meta name="theme-color" content="#111111">
<link rel="icon" href="favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="favicon.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Red Cat Marketing">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{SITE}">
<meta property="og:image" content="{SITE}assets/og-image.jpg">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{SITE}assets/og-image.jpg">
<link rel="preload" as="image" href="assets/hero-phone.jpg" media="(min-width: 761px)">
<link rel="preload" as="image" href="assets/hero-phone-sm.jpg" media="(max-width: 760px)">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{fonts}" rel="stylesheet">
<style>{style}</style>
<script type="application/ld+json">
{ld}
</script>
</head>
<body>"""

js = """
<script>
(function(){
  var bar=document.getElementById('nav-bar'),btn=document.getElementById('nav-toggle');
  function set(open){bar.classList.toggle('menu-open',open);btn.setAttribute('aria-expanded',open?'true':'false');btn.setAttribute('aria-label',open?'Close menu':'Open menu');}
  btn.addEventListener('click',function(){set(!bar.classList.contains('menu-open'));});
  document.querySelectorAll('#nav-bar a').forEach(function(a){a.addEventListener('click',function(){set(false);});});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&bar.classList.contains('menu-open')){set(false);btn.focus();}});
  window.addEventListener('resize',function(){if(window.innerWidth>760)set(false);});
  var form=document.getElementById('audit-form'),er0=document.getElementById('form-error');
  form.addEventListener('submit',function(e){
    e.preventDefault();
    var b=form.querySelector('button[type=submit]'),t=b.textContent;b.disabled=true;b.textContent='Sending...';er0.classList.remove('show');
    fetch(form.action,{method:'POST',headers:{'Accept':'application/json'},body:new FormData(form)})
      .then(function(r){return r.json();})
      .then(function(j){if(j&&j.success){window.location.href='thank-you.html';}else{throw new Error('fail');}})
      .catch(function(){b.disabled=false;b.textContent=t;er0.classList.add('show');er0.focus();});
  });
  if(/[?&]error=/.test(location.search)){var er=document.getElementById('form-error');if(er){er.classList.add('show');var f=document.getElementById('get-audit');if(f)f.scrollIntoView();er.focus();}}
})();
</script>
</body>
</html>
"""
(DIST/"index.html").write_text(head + "\n" + body.strip() + "\n" + js)

# ---------- thank you ----------
ty = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Thank you | Red Cat Marketing</title>
<meta name="robots" content="noindex">
<link rel="icon" href="favicon.ico" sizes="any"><link rel="icon" type="image/png" href="favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{fonts}" rel="stylesheet">
<style>body{{margin:0;background:#fff;color:#111;font-family:'Figtree',system-ui,sans-serif;font-size:17px;line-height:1.6}}
a{{color:#111}}a:hover{{color:#CF202E}}a:focus-visible{{outline:2px solid #CF202E;outline-offset:2px}}
header{{border-bottom:1px solid #E6E2DC;padding:18px 24px}}main{{max-width:680px;margin:0 auto;padding:96px 24px 120px}}
.slash{{display:block;width:56px;height:6px;background:#CF202E;transform:skewY(-24deg);margin-bottom:32px}}
h1{{font-family:'Playfair Display',Georgia,serif;font-weight:400;font-size:clamp(36px,6vw,56px);line-height:1.08;margin:0 0 20px}}
.btn{{display:inline-flex;align-items:center;min-height:52px;padding:0 28px;background:#111;color:#fff;text-decoration:none;font-weight:600;border-radius:2px;margin-top:16px}}.btn:hover{{color:#fff;background:#CF202E}}
</style></head><body>
<header><a href="/" aria-label="Red Cat Marketing home"><img src="assets/red-cat-logo.png" alt="Red Cat Marketing" width="{round(44*logo_w/logo_h)}" height="44" style="height:44px;width:auto"></a></header>
<main><span class="slash" aria-hidden="true"></span>
<h1>Thanks, your audit request is in.</h1>
<p>A Red Cat Marketing strategist will review your details and be in touch with next steps. Your audit is delivered within 3 business days of kickoff.</p>
<p>In the meantime, have a look at our <a href="https://www.redcatmarketing.ca/work">work</a>.</p>
<a class="btn" href="/">Back to the audit page</a></main></body></html>
"""
(DIST/"thank-you.html").write_text(ty)

# ---------- robots / sitemap ----------
bots = ["GPTBot","ClaudeBot","PerplexityBot","Google-Extended","OAI-SearchBot","ChatGPT-User","anthropic-ai","CCBot"]
robots = "User-agent: *\nAllow: /\n\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"Sitemap: {SITE}sitemap.xml\n"
(DIST/"robots.txt").write_text(robots)
(DIST/"sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>{SITE}</loc><lastmod>2026-11-10</lastmod></url>\n</urlset>\n')
(DIST/"CNAME").write_text("aiaudit.redcatmarketing.ca\n")
print("ok", logo_w, logo_h, rep_w, rep_h)
