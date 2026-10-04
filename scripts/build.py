from pathlib import Path
import json
import html
import shutil

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "recipes.json"
recipes = json.loads(DATA.read_text(encoding="utf-8"))

def esc(x):
    return html.escape(str(x or ""))

def shell(title, body, extra="", depth=0):
    up = "../" * depth
    return f'''<!doctype html><html lang="uk"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | UltrablackXL Рецепти</title><meta name="description" content="Відеорецепти UltrablackXL"><link rel="stylesheet" href="{up}assets/style.css">{extra}</head><body><header class="top"><div class="wrap nav"><a class="brand" href="{up}">UltraBlack<span>XL</span><small style="display:block;font-size:9px;letter-spacing:4px;color:#aaa">РЕЦЕПТИ</small></a><nav class="navlinks"><a href="{up}">Головна</a><a href="{up}#recipes">Рецепти</a><a href="https://www.youtube.com/@ultrablackxl6205">YouTube</a></nav><a class="ytbtn" href="https://www.youtube.com/@ultrablackxl6205?sub_confirmation=1">▶ Підписатися</a></div></header>{body}<footer class="footer"><div class="wrap">UltrablackXL Рецепти · відео відтворюються з YouTube</div></footer></body></html>'''

recipes_dir = ROOT / "recipes"
if recipes_dir.exists():
    shutil.rmtree(recipes_dir)
recipes_dir.mkdir(parents=True, exist_ok=True)

for r in recipes:
    d = recipes_dir / r["slug"]
    d.mkdir(parents=True, exist_ok=True)
    if r.get("youtube_id"):
        player = f'''<iframe src="https://www.youtube-nocookie.com/embed/{esc(r['youtube_id'])}" title="{esc(r['title'])}" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>'''
    else:
        player = '''<div class="emptyvideo"><strong>🎬 Відео буде підв’язане автоматично</strong><span class="muted">Після синхронізації каналу тут буде оригінальний YouTube-плеєр UltrablackXL.</span></div>'''

    body = f'''<main class="recipe"><div class="wrap"><div class="crumb"><a href="../../">Головна</a> › {esc(r.get('category'))}</div><span class="status"><span class="dot"></span>{esc(r.get('status','draft'))}</span><h1>{esc(r['title'])}</h1><p class="muted" style="font-size:19px;max-width:780px">{esc(r.get('description'))}</p><div class="player">{player}</div><div class="twocol"><section class="box"><h2>Про рецепт</h2><p>{esc(r.get('description') or 'Відеорецепт UltrablackXL.')}</p></section><aside class="box"><h2>Категорія</h2><p>{esc(r.get('category'))}</p><a class="ytbtn" style="display:inline-block" href="{esc(r.get('youtube_url') or 'https://www.youtube.com/@ultrablackxl6205')}">▶ Відкрити YouTube</a></aside></div></div></main>'''

    ld = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": r["title"],
        "description": r.get("description", ""),
        "image": [r.get("thumbnail")] if r.get("thumbnail") else [],
        "author": {"@type": "Organization", "name": "UltrablackXL"},
    }
    extra = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    (d / "index.html").write_text(shell(r["title"], body, extra, depth=2), encoding="utf-8")

home = '''<main><section class="wrap hero"><div><div class="tag">ULTRABLACKXL · YOUTUBE РЕЦЕПТИ</div><h1>Прості рецепти.<br>Смачні моменти.</h1><p>Усі повноформатні відеорецепти UltrablackXL в одному зручному каталозі. Shorts не імпортуються.</p><a class="ytbtn" style="display:inline-block;margin-top:8px" href="#recipes">Дивитися рецепти ↓</a></div><div class="heroart"></div></section><section class="wrap section" id="recipes"><div class="sectionhead"><div><div class="tag">КАТАЛОГ</div><h2>Усі рецепти</h2></div><div class="muted" id="count"></div></div><div class="toolbar"><input class="search" id="q" placeholder="Пошук: курка, суп, пиріг…"><div class="chips" id="chips"></div></div><div class="grid" id="grid"></div></section></main><script src="assets/app.js"></script><script>initHome()</script>'''
(ROOT / "index.html").write_text(shell("Головна", home), encoding="utf-8")
(ROOT / "sitemap.txt").write_text("\n".join("recipes/" + r["slug"] + "/" for r in recipes), encoding="utf-8")
(ROOT / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
print(f"Built {len(recipes)} recipe pages")
