from pathlib import Path
import json
import html
import shutil
import re
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "recipes.json"
CHANNEL_DATA = ROOT / "data" / "channel.json"
BASE_URL = "https://ultrablackxl.site.je"

recipes = json.loads(DATA.read_text(encoding="utf-8"))
channel = json.loads(CHANNEL_DATA.read_text(encoding="utf-8")) if CHANNEL_DATA.exists() else {}

def esc(x):
    return html.escape(str(x or ""), quote=True)

def clean_title(title):
    t = re.sub(r"\s+#\S+", "", str(title or "")).strip()
    t = re.sub(r"\s{2,}", " ", t)
    t = t.strip(" -–—|")
    return t or "Відеорецепт"

def short_desc(r):
    title = clean_title(r.get("title"))
    cat = r.get("category") or "Рецепти"
    return f'Відеорецепт «{title}» від UltraBlack XL. Дивіться повний процес приготування у відео та готуйте разом з нами.'

def fmt_duration(seconds):
    try:
        seconds = int(seconds or 0)
    except Exception:
        return ""
    if seconds <= 0:
        return ""
    m, s = divmod(seconds, 60)
    if m >= 60:
        h, m = divmod(m, 60)
        return f"{h} год {m:02d} хв"
    return f"{m} хв {s:02d} с"

def cat_slug(category):
    table = {
        "Гарніри":"garniry","Випічка":"vypichka","Закуски":"zakusky","М’ясо":"myaso",
        "Десерти":"deserty","Салати":"salaty","Риба":"ryba","Супи":"supy",
        "Птиця":"ptytsya","Напої":"napoyi","Інше":"inshe"
    }
    return table.get(category, re.sub(r"[^a-z0-9]+","-",category.lower()).strip("-") or "recipes")

def abs_url(path=""):
    return BASE_URL.rstrip("/") + "/" + path.lstrip("/")

def shell(title, body, description, canonical, image="", extra="", depth=0, noindex=False):
    up = "../" * depth
    avatar = channel.get("avatar") or ""
    robots = '<meta name="robots" content="noindex,nofollow">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large">'
    og_image = image or avatar
    return f'''<!doctype html>
<html lang="uk"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
{robots}
<link rel="canonical" href="{esc(canonical)}">
<link rel="stylesheet" href="{up}assets/style.css">
<meta property="og:type" content="website">
<meta property="og:site_name" content="UltraBlackXL Рецепти">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(canonical)}">
{f'<meta property="og:image" content="{esc(og_image)}">' if og_image else ''}
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0b0d0f">
{f'<link rel="icon" href="{esc(avatar)}">' if avatar else ''}
{extra}
</head><body>
<header class="top"><div class="wrap nav">
<a class="brand" href="{up}">UltraBlack<span>XL</span><small>РЕЦЕПТИ</small></a>
<nav class="navlinks"><a href="{up}">Головна</a><a href="{up}#recipes">Рецепти</a><a href="https://www.youtube.com/@ultrablackxl6205">YouTube</a></nav>
<a class="ytbtn" href="https://www.youtube.com/@ultrablackxl6205?sub_confirmation=1">▶ Підписатися</a>
</div></header>
{body}
<footer class="footer"><div class="wrap footergrid"><div><div class="brand">UltraBlack<span>XL</span></div><p>Відеорецепти з оригінального YouTube-каналу UltraBlack XL.</p></div><div><b>Категорії</b><div class="footerlinks">{''.join(f'<a href="{up}category/{cat_slug(c)}/">{esc(c)}</a>' for c in sorted(set(x.get("category") or "Інше" for x in recipes)))}</div></div></div></footer>
<script src="{up}assets/app.js"></script>
</body></html>'''

# Clean generated dirs
for folder in ("recipes","category"):
    p = ROOT / folder
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True, exist_ok=True)

# Recipe pages
for r in recipes:
    d = ROOT / "recipes" / r["slug"]
    d.mkdir(parents=True, exist_ok=True)
    display = clean_title(r["title"])
    desc = r.get("seo_description") or short_desc(r)
    seo_title = r.get("seo_title") or display
    canonical = abs_url(f"recipes/{r['slug']}/")
    thumb = r.get("thumbnail") or (f"https://img.youtube.com/vi/{r.get('youtube_id')}/hqdefault.jpg" if r.get("youtube_id") else "")
    duration = fmt_duration(r.get("duration"))
    cat = r.get("category") or "Інше"
    cslug = cat_slug(cat)

    related = [x for x in recipes if x is not r and (x.get("category") or "Інше") == cat][:3]
    related_html = "".join(
        f'''<a class="relatedcard" href="../../recipes/{quote(x["slug"])}/">
        <img src="https://img.youtube.com/vi/{esc(x.get("youtube_id"))}/hqdefault.jpg" alt="{esc(clean_title(x.get("title")))}" loading="lazy">
        <div><span>{esc(x.get("category") or "Інше")}</span><strong>{esc(clean_title(x.get("title")))}</strong></div></a>'''
        for x in related
    )

    player = f'''<div id="yt-player"></div><script>
(function(){{
  var played=false, vid={json.dumps(r.get("youtube_id") or "")}, title={json.dumps(display, ensure_ascii=False)};
  function send(name){{try{{if(window.UltraTrack)window.UltraTrack(name,{{video_id:vid,title:title}})}}catch(e){{}}}}
  window.onYouTubeIframeAPIReady=function(){{
    new YT.Player('yt-player',{{videoId:vid,playerVars:{{rel:0,modestbranding:1}},events:{{onStateChange:function(e){{if(e.data===YT.PlayerState.PLAYING&&!played){{played=true;send('youtube_play')}}}}}}}});
  }};
  var s=document.createElement('script');s.src='https://www.youtube.com/iframe_api';document.head.appendChild(s);
}})();
</script>''' if r.get("youtube_id") else '<div class="emptyvideo">Відео тимчасово недоступне.</div>'

    body = f'''<main class="recipe">
<div class="wrap">
<div class="crumb"><a href="../../">Головна</a><span>›</span><a href="../../category/{cslug}/">{esc(cat)}</a></div>
<div class="recipehead">
<div>
<div class="tag">{esc(cat)}</div>
<h1>{esc(display)}</h1>
<p class="lead">{esc(desc)}</p>
<div class="recipefacts">
{f'<span>⏱ {esc(duration)}</span>' if duration else ''}
<span>🎬 Відеорецепт</span>
<span>▶ UltraBlack XL</span>
</div>
</div>
<img class="recipecover" src="{esc(thumb)}" alt="{esc(display)}" onerror="this.style.display='none'">
</div>

<div class="player">{player}</div>

<div class="recipeactions">
<a class="ytbtn" href="{esc(r.get('youtube_url') or 'https://www.youtube.com/@ultrablackxl6205')}">▶ Відкрити на YouTube</a>
<a class="ghostbtn" href="https://www.youtube.com/@ultrablackxl6205?sub_confirmation=1">Підписатися на канал</a>
</div>

<div class="twocol recipeinfo">
<section class="box"><div class="tag">ПРО РЕЦЕПТ</div><h2>{esc(display)}</h2><p>{esc(desc)}</p><p class="muted">Повний процес приготування показаний у відео вище.</p></section>
<aside class="box"><div class="tag">НАВІГАЦІЯ</div><h2>{esc(cat)}</h2><p>Ще більше страв цієї категорії.</p><a class="ghostbtn" href="../../category/{cslug}/">Усі рецепти категорії →</a></aside>
</div>

{f'<section class="related"><div class="sectionhead"><div><div class="tag">ЩЕ СПРОБУЙ</div><h2>Схожі рецепти</h2></div></div><div class="relatedgrid">{related_html}</div></section>' if related_html else ''}
</div></main>'''

    ld = {
        "@context":"https://schema.org",
        "@type":"Recipe",
        "name":display,
        "description":desc,
        "image":[thumb] if thumb else [],
        "author":{"@type":"Organization","name":"UltraBlack XL","url":"https://www.youtube.com/@ultrablackxl6205"},
        "video":{"@type":"VideoObject","name":display,"thumbnailUrl":[thumb] if thumb else [],"embedUrl":f"https://www.youtube.com/embed/{r.get('youtube_id')}","contentUrl":r.get("youtube_url")},
    }
    if r.get("duration"):
        ld["totalTime"] = f"PT{int(r['duration'])//60}M{int(r['duration'])%60}S"
    extra = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    (d/"index.html").write_text(shell(f"{seo_title} | UltraBlackXL", body, desc, canonical, thumb, extra, depth=2), encoding="utf-8")

# Category pages
categories = sorted(set(r.get("category") or "Інше" for r in recipes))
for cat in categories:
    rows = [r for r in recipes if (r.get("category") or "Інше") == cat]
    slug = cat_slug(cat)
    d = ROOT/"category"/slug
    d.mkdir(parents=True, exist_ok=True)
    cards = "".join(f'''<a class="card" href="../../recipes/{quote(r["slug"])}/"><div class="thumb"><img src="https://img.youtube.com/vi/{esc(r.get("youtube_id"))}/hqdefault.jpg" alt="{esc(clean_title(r.get("title")))}" loading="lazy"></div><div class="cardbody"><div class="tag">{esc(cat)}</div><h3>{esc(clean_title(r.get("title")))}</h3><div class="muted">Дивитися рецепт →</div></div></a>''' for r in rows)
    desc = f"{cat}: відеорецепти UltraBlack XL. {len(rows)} рецептів у категорії."
    body = f'''<main class="wrap categorypage"><div class="crumb"><a href="../../">Головна</a><span>›</span>Категорії</div><div class="categoryhero"><div class="tag">КАТЕГОРІЯ</div><h1>{esc(cat)}</h1><p>{esc(desc)}</p></div><div class="grid">{cards}</div></main>'''
    (d/"index.html").write_text(shell(f"{cat} | Рецепти UltraBlackXL", body, desc, abs_url(f"category/{slug}/"), depth=2), encoding="utf-8")

# Home
avatar = esc(channel.get("avatar") or "")
channel_title = esc(channel.get("title") or "UltraBlack XL")
hero_visual = f'''<aside class="channelcard">
<div class="channelavatar">{f'<img src="{avatar}" alt="{channel_title}">' if avatar else '<div class="avatarfallback">UBXL</div>'}</div>
<div class="channeltag">YOUTUBE КАНАЛ</div><h3>{channel_title}</h3>
<p>Домашня кухня, зрозумілі відеорецепти та нові страви.</p>
<a class="ytbtn" href="https://www.youtube.com/@ultrablackxl6205">▶ Відкрити YouTube</a>
</aside>'''

cat_links = "".join(f'<a class="hashtagcat" href="category/{cat_slug(c)}/">#{esc(c)}</a>' for c in categories)

home = f'''<main>
<section class="wrap hero"><div><div class="tag">ULTRABLACKXL · ВІДЕОРЕЦЕПТИ</div><h1>Прості рецепти.<br>Смачні моменти.</h1><p>Домашні рецепти без зайвої метушні. Обирай страву, відкривай відео та готуй разом з UltraBlackXL.</p><a class="ytbtn" style="display:inline-block;margin-top:8px" href="#recipes">Дивитися рецепти ↓</a></div>{hero_visual}</section>
<section class="wrap cats"><div class="sectionhead"><div><div class="tag">ШВИДКИЙ ВИБІР</div><h2>Що готуємо?</h2></div></div><div class="hashtagrow">{cat_links}</div></section>
<section class="wrap section" id="recipes"><div class="sectionhead"><div><div class="tag">КАТАЛОГ</div><h2>Усі рецепти</h2></div><div class="muted" id="count"></div></div><div class="toolbar"><input class="search" id="q" placeholder="Пошук: курка, суп, пиріг…"><div class="chips" id="chips"></div></div><div class="grid" id="grid"></div></section>
</main><script>document.addEventListener('DOMContentLoaded',()=>initHome())</script>'''

home_desc = "Відеорецепти UltraBlack XL: домашні страви, салати, супи, випічка, м’ясо, риба, закуски та десерти. Обирайте рецепт і дивіться оригінальне відео."
(ROOT/"index.html").write_text(shell("UltraBlackXL Рецепти | Домашні відеорецепти", home, home_desc, BASE_URL+"/", avatar, depth=0), encoding="utf-8")

# SEO files
urls = [(BASE_URL+"/","1.0")]
urls += [(abs_url(f"category/{cat_slug(c)}/"),"0.8") for c in categories]
urls += [(abs_url(f"recipes/{r['slug']}/"),"0.9") for r in recipes]
xml = ['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u,p in urls:
    xml.append(f'<url><loc>{esc(u)}</loc><changefreq>weekly</changefreq><priority>{p}</priority></url>')
xml.append('</urlset>')
(ROOT/"sitemap.xml").write_text("\n".join(xml), encoding="utf-8")
(ROOT/"sitemap.txt").write_text("\n".join(u for u,_ in urls), encoding="utf-8")
(ROOT/"robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /stats/\nDisallow: /api/\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")

print(f"Built {len(recipes)} recipe pages and {len(categories)} category pages")
