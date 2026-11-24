"""Builds the Edusoft portal from catalog.json + data.json.

Outputs:  index.html (home) and software/<slug>.html (one page per product)

Usage:  python build.py            build
        python build.py --check    re-check every demo/APK link first, then build

Videos (optional, picked up automatically on the next build):
  home intro      assets/video/intro.mp4      or  "introVideo": "<YouTube link>" in catalog.json -> company
  each product    assets/video/<slug>.mp4     or  "video": "<YouTube link>" on that product in catalog.json
"""
import json, re, sys, subprocess, time
from html import escape as e
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).parent
cat = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8-sig"))
raw = {p["id"]: p for p in json.loads((ROOT / "data.json").read_text(encoding="utf-8-sig"))}
C = cat["company"]
INDS = {i["id"]: i for i in cat["industries"]}
# one accent colour per industry, used on cards, chips and product pages
COLORS = {"healthcare": "#0e8f9a", "education": "#5856d6", "retail": "#e2702a",
          "food": "#d9443a", "agri": "#6f9a1e", "enterprise": "#12884a", "fuel": "#1f6fb2", "distribution": "#b7791f", "invoicing": "#2b6cb0", "pharmacy": "#0e8f9a"}
YEAR = 2026
VER = int(time.time())  # cache-busting for css/js
LOGO = "assets/edusoft-logo-light.png"

def wa(text):
    return f"https://wa.me/{C['whatsapp']}?text={quote(text)}"
tel = lambda n: "tel:" + n.replace(" ", "")

products = []
for p in cat["products"]:
    r = raw[p["id"]]
    products.append({**p, "type": r["type"], "isNew": r["isNew"], "url": r["url"],
                     "username": r["username"], "password": r["password"],
                     "poster": p.get("image") or r.get("image") or "",
                     "image": (f"assets/covers/{p['slug']}.svg" if (ROOT / "assets" / "covers" / f"{p['slug']}.svg").exists() else p.get("image") or r.get("image") or ""),
                     "photo": (f"assets/photos/{p['slug']}.jpg" if (ROOT / "assets" / "photos" / f"{p['slug']}.jpg").exists() else None),
                     "linkStatus": r.get("linkStatus", 200)})

if "--check" in sys.argv:
    for p in products:
        u = p["url"] if p["url"].startswith("http") else C["demoBase"] + p["url"]
        out = subprocess.run(["curl", "-s", "-o", "NUL" if sys.platform == "win32" else "/dev/null", "-w", "%{http_code}", "-L", "-m", "20", u], capture_output=True, text=True)
        p["linkStatus"] = raw[p["id"]]["linkStatus"] = int(out.stdout or 0)
        print(f"{p['linkStatus']}  {u}")
    (ROOT / "data.json").write_text(json.dumps(list(raw.values()), indent=2, ensure_ascii=False), encoding="utf-8")

BYID = {p["id"]: p for p in products}
WEB = [p for p in products if p["type"] == "web"]
APPS = [p for p in products if p["type"] == "android"]
SUITE = [p for p in products if p.get("suite") == "hmis"]
APK_OK = lambda p: p["type"] != "android" or p["linkStatus"] == 200
SITE = C.get("siteUrl", C["demoBase"]).rstrip("/") + "/"   # public address, used for link previews

def video_for(name):
    """Local video file assets/video/<name>.mp4|webm, if present."""
    for ext in ("mp4", "webm"):
        if (ROOT / "assets" / "video" / f"{name}.{ext}").exists():
            return f"assets/video/{name}.{ext}", ext
    return None, None

def youtube_id(url):
    m = re.search(r"(?:youtu\.be/|v=|embed/|shorts/)([\w-]{11})", url or "")
    return m.group(1) if m else None

# ------------------------------------------------------------------ shared pieces
def head(title, desc, pre, active="", page_url="", image="", accent=""):
    links = [("Software", f"{pre}index.html#software", "software"), ("Mobile apps", f"{pre}index.html#apps", "apps"),
             ("Clients", f"{pre}index.html#clients", "clients"), ("Contact", "#contact", "contact")]
    og_img = SITE + (image or BYID[15]["poster"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Edusoft System Solutions">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(SITE + page_url)}">
<meta property="og:image" content="{e(og_img)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f6f6f1">
<link rel="icon" href="{pre}assets/logo.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Inter+Tight:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<link rel="stylesheet" href="{pre}assets/css/edusoft.css?v={VER}">
</head>
<body{f' style="--c:{accent}"' if accent else ''}>
<nav class="nav"><div class="nav-in">
  <a class="logo" href="{pre}index.html"><img src="{pre}{LOGO}" alt="Edusoft System Solutions"></a>
  <div class="nav-links">{''.join(f'<a href="{h}" class="{"on" if k == active else ""}">{t}</a>' for t, h, k in links)}</div>
  <div class="nav-r">
    <a class="ic hide-s" href="{tel(C['mobile'])}" aria-label="Call"><i class="fas fa-phone"></i></a>
    <a class="ic hide-s" href="https://wa.me/{C['whatsapp']}" target="_blank" rel="noopener" aria-label="WhatsApp"><i class="fab fa-whatsapp"></i></a>
    <a class="btn btn-dark btn-sm" href="{wa('Hi Edusoft, I would like a demo.')}" target="_blank" rel="noopener">Book a demo</a>
    <button class="ic burger" aria-label="Menu"><i class="fas fa-bars"></i></button>
  </div>
</div></nav>
"""

def cta(title="Need help choosing software?"):
    return f"""<div class="wrap" style="padding-top:20px"><div class="cta">
  <div><h2>{e(title)}</h2><p>Multan office &middot; {C['mobile']} &middot; {C['email']}</p></div>
  <a class="btn" href="{wa('Hi Edusoft, I need help choosing software.')}" target="_blank" rel="noopener"><i class="fab fa-whatsapp"></i> Talk to us</a>
</div></div>"""

def foot(pre):
    def col(title, items):
        return f"<div><h5>{title}</h5><ul>" + "".join(f'<li><a href="{pre}software/{p["slug"]}.html">{e(p["name"])}</a></li>' for p in items) + "</ul></div>"
    hosp = [p for p in products if p["industry"] == "healthcare"]
    biz = [p for p in WEB if p["industry"] == "enterprise"]
    other = [p for p in WEB if p["industry"] in ("education", "retail", "agri")]
    return f"""
<footer id="contact"><div class="wrap"><div class="fcard">
  <div class="fgrid">
    <div class="fbrand">
      <a class="logo" href="{pre}index.html"><img src="{pre}{LOGO}" alt="Edusoft System Solutions"></a>
      <p>Business software for Pakistani companies since {C['since']}.</p>
      <ul>
        <li><i class="fas fa-location-dot"></i><span>{e(C['address'])}</span></li>
        <li><i class="fas fa-phone"></i><span><a href="{tel(C['mobile'])}">{C['mobile']}</a></span></li>
        <li><i class="fab fa-whatsapp"></i><a href="https://wa.me/{C['whatsapp']}" target="_blank" rel="noopener">{C['whatsappDisplay']}</a></li>
        <li><i class="fas fa-envelope"></i><a href="mailto:{C['email']}">{C['email']}</a></li>
      </ul>
    </div>
    {col("Hospitals", hosp)}
    {col("Business &amp; accounts", biz)}
    {col("Schools, shops &amp; farms", other)}
    <div><h5>Mobile apps</h5><ul>{''.join(f'<li><a href="{pre}software/{p["slug"]}.html">{e(p["name"])}</a></li>' for p in APPS)}</ul>
      <h5 style="margin-top:16px">Company</h5><ul><li><a href="{C['website']}" target="_blank" rel="noopener">edusoftsolutions.com</a></li><li><a href="{C['mapUrl']}" target="_blank" rel="noopener">Directions</a></li></ul></div>
  </div>
  <div class="fbot"><span>&copy; {YEAR} {e(C['name'])}. All rights reserved.</span><a href="{C['website']}/ContactUs" target="_blank" rel="noopener">Feedback &amp; complaints</a></div>
</div></div></footer>
<a class="wa-float" href="https://wa.me/{C['whatsapp']}" target="_blank" rel="noopener" aria-label="WhatsApp Edusoft"><i class="fab fa-whatsapp"></i></a>
<div class="toast" id="toast"><span></span></div>
<script src="{pre}assets/js/edusoft.js?v={VER}"></script>
</body>
</html>
"""

def demo_href(p, pre):
    """(href, label, extra attributes) for the main action of a product."""
    if p["type"] == "web" and not p["url"]:  # demo link not ready yet
        return wa("Hi Edusoft, I'd like a demo of " + p["name"] + "."), "Ask for a demo", 'target="_blank" rel="noopener"'
    if p["type"] == "web":
        return e(p["url"]), "Open demo", 'target="_blank" rel="noopener"'
    if APK_OK(p):
        return f"{pre}{e(p['url'])}", "Download APK", "download"
    return wa("Hi Edusoft, please send me the " + p["name"] + " APK."), "Get the APK", 'target="_blank" rel="noopener"'

def demo_btn(p, pre, cls="btn demo"):
    href, label, attrs = demo_href(p, pre)
    icon = "fa-arrow-up-right-from-square" if p["type"] == "web" else "fa-android"
    return f'<a class="{cls}" href="{href}" {attrs}>{label} <i class="{"fas" if p["type"] == "web" else "fab"} {icon}"></i></a>'

LOGIN_DL = lambda p: (f"<dt>Username</dt><dd><code>{e(p['username'])}</code></dd><dt>Password</dt><dd><code>{e(p['password'])}</code></dd>"
                      if p['username'] else '<dt>Demo</dt><dd>Link coming soon</dd>')

def creds(p):
    if not p["username"]:
        return '<span class="cred soon"><i class="far fa-clock"></i> Demo link coming soon</span>'
    return (f'<button class="cred" data-copy="{e(p["username"])}" title="Copy username">user <code>{e(p["username"])}</code> <i class="far fa-copy"></i></button>'
            f'<button class="cred" data-copy="{e(p["password"])}" title="Copy password">pass <code>{e(p["password"])}</code> <i class="far fa-copy"></i></button>')

def ind_badge(p):
    i = INDS[p["industry"]]
    return f'<span class="badge-ind"><i class="fas {p["icon"]}"></i>{e(i["label"])}</span>'

def card(p, pre=""):
    href = f"{pre}software/{p['slug']}.html" if pre == "" else f"{p['slug']}.html"
    img = ("" if pre == "" else "../") + (p["photo"] or p["image"])
    feats = "".join(f'<li><i class="fas fa-check"></i>{e(t)}</li>' for t, _ in p["features"][:4])
    return f"""<article class="card" data-type="{p['type']}" data-ind="{p['industry']}" style="--c:{COLORS[p['industry']]}">
  <a class="shot" href="{href}" tabindex="-1"><img src="{e(img)}" alt="{e(p['name'])}" loading="lazy">{ind_badge(p)}{'<span class="tag-new">New</span>' if p['isNew'] else ''}
    <div class="over"><ul>{feats}</ul></div></a>
  <button class="peek" data-peek="{p['id']}" aria-label="Quick look at {e(p['name'])}"><i class="far fa-eye"></i></button>
  <div class="body">
    <h3><a href="{href}">{e(p['name'])}</a></h3>
    <p>{e(p['tagline'])}</p>
    <div class="logrow">{creds(p)}</div>
    <div class="cardacts">{demo_btn(p, '' if pre == '' else '../', 'btn demo')}<a class="more" href="{href}">Details <i class="fas fa-arrow-right"></i></a></div>
  </div>
</article>"""

def peek_data():
    """Compact product data for the quick-look panel on the home page."""
    out = {}
    for p in products:
        href, label, attrs = demo_href(p, "")
        out[p["id"]] = {"name": p["name"], "tagline": p["tagline"], "intro": p["intro"][0], "img": p["photo"] or p["image"],
                        "page": f"software/{p['slug']}.html", "color": COLORS[p["industry"]], "icon": p["icon"],
                        "ind": INDS[p["industry"]]["label"], "user": p["username"], "pass": p["password"],
                        "demo": href, "demoLabel": label, "demoBlank": "_blank" in attrs, "apk": "download" in attrs,
                        "features": p["features"][:5]}
    return json.dumps(out, ensure_ascii=False).replace("</", "<\\/")

# ------------------------------------------------------------------ home page
INTRO_POSTER = "assets/video/intro-poster.jpg" if (ROOT / "assets/video/intro-poster.jpg").exists() else BYID[15]["poster"]

def intro_video():
    """Short intro video beside the one-line intro. File: assets/video/intro.mp4, or "introVideo" (YouTube) in catalog.json."""
    yt = youtube_id(C.get("introVideo"))
    vfile, vext = video_for("intro")
    poster = INTRO_POSTER
    if yt:
        inner = f'<iframe src="https://www.youtube-nocookie.com/embed/{yt}?rel=0&autoplay=1&mute=1&loop=1&playlist={yt}" title="Edusoft intro" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>'
        modal = f'<iframe data-src="https://www.youtube-nocookie.com/embed/{yt}?rel=0&autoplay=1" title="Edusoft intro" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>'
    elif vfile:
        inner = f'<video autoplay muted loop playsinline preload="metadata" poster="{poster}"><source src="{vfile}" type="video/{vext}"></video><button class="sound" aria-label="Play with sound"><i class="fas fa-volume-xmark"></i> Tap for sound</button>'
        modal = f'<video controls playsinline preload="none" poster="{poster}"><source src="{vfile}" type="video/{vext}"></video>'
    else:  # placeholder until a video is added
        inner = f'<img src="{poster}" alt=""><div class="vslot"><span><i class="fas fa-play"></i>Intro video</span></div>'
        modal = f'<img src="{poster}" alt="">'
    return inner, modal

def home():
    h = head("Edusoft | Software & mobile app demos",
             "Open live demos of Edusoft software and Android apps: pharmacy, school, restaurant, retail, fuel station, business ERP and FBR invoicing.", "", "software", "", INTRO_POSTER)
    counts = {i: sum(1 for p in WEB if p["industry"] == i) for i in INDS}
    vid, vmodal = intro_video()
    logos = "".join(f'<img src="assets/clients/{c.name}" alt="" loading="lazy">' for c in sorted((ROOT / "assets" / "clients").glob("*.png")))
    h += f"""
<main class="top" id="software"><div class="wrap">
  <div class="top-row">
    <div class="intro">
      <h1 class="oneline"><b>Edusoft <i>System Solutions</i></b> <span><em class="dot">&middot;</em> Business software &amp; Android apps since {C['since']}. Pick one below and open the live demo.</span></h1>
      <button class="watch" data-open-video><i class="fas fa-play"></i> Watch the intro</button>
      <div class="tabs" role="tablist" id="apps"><span class="ind-bar"></span>
        <button class="on" data-view="web" role="tab"><i class="fas fa-desktop"></i> Software <span>{len(WEB)}</span></button>
        <button data-view="android" role="tab"><i class="fab fa-android"></i> Mobile apps <span>{len(APPS)}</span></button>
      </div>
    </div>
    <div class="intro-video" data-open-video-desktop>{vid}</div>
  </div>
  <div class="chips" id="chips"><button class="chip on" data-filter="all">All software</button>{''.join(f'<button class="chip" data-filter="{i}" style="--c:{COLORS[i]}"><i class="fas {INDS[i]["icon"]}"></i>{e(INDS[i]["label"])}<span>{n}</span></button>' for i, n in counts.items() if n)}</div>
  <div class="grid" id="bento">{''.join(card(p) for p in products)}</div>
</div></main>

<dialog class="vmodal" id="vmodal"><button class="vclose" aria-label="Close"><i class="fas fa-xmark"></i></button>{vmodal}</dialog>

<div class="peekpanel" id="peek" aria-hidden="true">
  <div class="scrim" data-peek-close></div>
  <div class="pp" role="dialog" aria-modal="true" aria-label="Quick look">
    <div class="pp-img"><img alt=""><button class="pp-close" data-peek-close aria-label="Close"><i class="fas fa-xmark"></i></button></div>
    <div class="pp-body"></div>
    <div class="pp-acts"></div>
  </div>
</div>
<script id="peek-data" type="application/json">{peek_data()}</script>

<section><div class="wrap"><div class="glance">
  <h2>Edusoft at a glance.</h2>
  <div class="stats">
    <div><b>{C['since']}</b><small>In business since</small></div>
    <div><b data-count="{len(WEB)}">{len(WEB)}</b><small>Web systems with live demos</small></div>
    <div><b data-count="{len(APPS)}">{len(APPS)}</b><small>Android apps</small></div>
    <div><b data-count="{len(list((ROOT / 'assets' / 'clients').glob('*.png')))}" data-suffix="+">{len(list((ROOT / 'assets' / 'clients').glob('*.png')))}+</b><small>Client brands shown below</small></div>
  </div>
</div></div></section>

<section id="clients"><div class="wrap">
  <span class="kicker">Clients</span>
  <div class="sec-h"><h2>What our clients say.</h2></div>
  <div class="quotes">{''.join(f'<div class="quote"><span class="av"><i class="fas fa-quote-left"></i></span><div><small>{e(t["org"])}</small><p>{e(t["quote"])}</p><b>{e(t["name"])}</b></div></div>' for t in cat['testimonials'])}</div>
  <div class="marquee"><div class="marquee-in">{logos}{logos}</div></div>
</div></section>
{cta()}
"""
    return h + foot("")

# ------------------------------------------------------------------ product page
def product_page(p):
    pre = "../"
    is_app = p["type"] == "android"
    color = COLORS[p["industry"]]
    h = head(f"{p['name']} | Edusoft", f"{p['tagline']} {p['audience']}", pre, "apps" if is_app else "software",
             f"software/{p['slug']}.html", p["photo"] or p["poster"], color)
    # product video: a YouTube link in catalog.json ("video"), or a file at assets/video/<slug>.mp4
    yt = youtube_id(p.get("video"))
    vfile, vext = video_for(p["slug"])
    if yt:
        media = f'<div class="media vid"><iframe src="https://www.youtube-nocookie.com/embed/{yt}?rel=0" title="{e(p["name"])} video" loading="lazy" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>'
    elif vfile:
        media = f'<div class="media vid"><video controls preload="metadata" playsinline poster="{pre}{e(p["image"])}"><source src="{pre}{vfile}" type="video/{vext}"></video></div>'
    else:
        media = f'<div class="media"><img src="{pre}{e(p["image"])}" alt="{e(p["name"])}"><div class="chip-stat"><b>Free</b><small>live demo</small></div></div>'
    icons = ["fa-bolt", "fa-chart-line", "fa-shield-halved", "fa-layer-group", "fa-gears", "fa-file-lines", "fa-users", "fa-boxes-stacked"]
    body = "".join(f"<p>{e(x)}</p>" for x in p["intro"])
    if p.get("workflow"):
        body += '<h2>How it works</h2><ol class="steps-ol">' + "".join(f"<li>{e(s)}</li>" for s in p["workflow"]) + "</ol>"
    body += '<h2>What\'s included</h2><ul class="flist">' + "".join(f'<li><i class="fas {icons[n % len(icons)]}"></i><span><b>{e(t)}</b>{e(d)}</span></li>' for n, (t, d) in enumerate(p["features"])) + "</ul>"
    if p.get("modules"):
        body += '<h2>Modules in detail</h2><div class="mods">' + "".join(f'<div class="mod"><h3>{e(t)}</h3><ul>' + "".join(f"<li>{e(x)}</li>" for x in items) + "</ul></div>" for t, items in p["modules"]) + "</div>"
    if p.get("faq"):
        body += '<h2>Questions we get</h2><div class="faq">' + "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in p["faq"]) + "</div>"
    if p.get("suite") == "hmis":
        body += ('<h2>Other HMIS modules</h2><p>These run on the same hospital system. Each has its own demo login.</p><div class="modlist">'
                 + "".join(f'<a href="{x["slug"]}.html" class="{"cur" if x["id"] == p["id"] else ""}">{e(x["name"])}<small>{e(x["username"])} / {e(x["password"])}</small></a>' for x in SUITE) + "</div>")
    related = [x for x in products if x["industry"] == p["industry"] and x["id"] != p["id"]][:3]
    if not related or p.get("suite") == "hmis":
        related = [x for x in products if x["type"] == p["type"] and x["id"] != p["id"] and x.get("suite") != "hmis"][:3]
    demo_how = ("Download the APK and install it on an Android phone." if APK_OK(p) else "Ask us on WhatsApp and we'll send the APK.") if is_app else ("Opens in a new tab." if p["url"] else "The live demo link is coming soon. Message us and we'll show it to you.")
    h += f"""
<header class="phero"><div class="wrap">
  <div>
    <div class="crumbs"><a href="../index.html#software">All software</a> &rsaquo; {e(INDS[p['industry']]['label'])}</div>
    {ind_badge(p)}{' <span class="tag-new" style="position:static;display:inline-block;margin-left:6px">New</span>' if p['isNew'] else ''}
    <h1>{e(p['name'])}</h1>
    <p class="lead">{e(p['tagline'])} For {e(p['audience'][0].lower() + p['audience'][1:])}</p>
    <div class="acts">{demo_btn(p, pre, 'btn demo')}<a class="btn btn-light" href="{wa('Hi Edusoft, I would like the price of ' + p['name'] + '.')}" target="_blank" rel="noopener"><i class="fab fa-whatsapp"></i> Ask for a price</a></div>
    <div class="logrow">{"Demo login: " if p["username"] else ""}{creds(p)}</div>
  </div>
  {media}
</div></header>

<section><div class="wrap layout">
  <div class="prose">{body}</div>
  <aside class="side">
    <div class="panel">
      <h3>Trying the demo</h3>
      <dl><dt>Platform</dt><dd>{'Android' if is_app else 'Web browser'}</dd>{LOGIN_DL(p)}</dl>
      <p>{demo_how} The demo has sample data; your own copy is set up with your data.</p>
      {demo_btn(p, pre, 'btn demo')}
      <a class="btn btn-light" href="{tel(C['mobile'])}"><i class="fas fa-phone"></i> {C['mobile']}</a>
    </div>
  </aside>
</div></section>

<section><div class="wrap">
  <span class="kicker">More</span>
  <div class="sec-h"><h2>Related software.</h2><a href="../index.html#software">All software &rsaquo;</a></div>
  <div class="grid">{''.join(card(x, '../') for x in related)}</div>
</div></section>
{cta("Interested in " + p['name'] + "?")}
"""
    return h + foot(pre)

# ------------------------------------------------------------------ write
def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("wrote", path.relative_to(ROOT))

write(ROOT / "index.html", home())
for p in products:
    write(ROOT / "software" / f"{p['slug']}.html", product_page(p))
