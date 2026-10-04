"""Synchronize all regular videos from the UltrablackXL YouTube channel.

The source is the channel's /videos tab, not /shorts, so Shorts are excluded.
Auto-generated fields are rebuilt from YouTube every run. Editorial overrides
will live separately, so a bad automatic value can never poison later syncs.

Requires: pip install -U yt-dlp
"""
from pathlib import Path
import subprocess
import json
import sys
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "recipes.json"
CHANNEL = "https://www.youtube.com/@ultrablackxl6205/videos"

CYR_MAP = {
    "а":"a","б":"b","в":"v","г":"h","ґ":"g","д":"d","е":"e","ё":"yo","є":"ye","ж":"zh","з":"z",
    "и":"y","і":"i","ї":"yi","й":"y","к":"k","л":"l","м":"m","н":"n","о":"o","п":"p","р":"r",
    "с":"s","т":"t","у":"u","ф":"f","х":"kh","ц":"ts","ч":"ch","ш":"sh","щ":"shch","ъ":"",
    "ы":"y","ь":"","э":"e","ю":"yu","я":"ya",
}

def translit(text: str) -> str:
    return "".join(CYR_MAP.get(ch, ch) for ch in (text or "").lower())

def slugify(text: str, video_id: str = "") -> str:
    s = translit(unicodedata.normalize("NFKC", text or ""))
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    if not s:
        s = "recipe"
    return f"{s[:72]}-{video_id[:8]}" if video_id else s[:80]

def guess_category(title: str) -> str:
    t = translit(title)
    rules = [
        ("Салати", ["salat"]),
        ("Супи", ["sup", "borsh", "solyank"]),
        ("Риба", ["ryb", "losos", "skumb", "karp", "seld", "tunts", "forel"]),
        ("Випічка", ["piro", "khleb", "buloc", "blin", "pitsa", "pizza", "keks"]),
        ("Десерти", ["tort", "desert", "pechen", "krem", "tiramisu", "napoleon"]),
        ("Птиця", ["kur", "indey", "kryl", "utk"]),
        ("М’ясо", ["myas", "svinin", "govyad", "buzhen", "shashlyk", "kotlet", "pechenk", "yazyk", "rulk"]),
        ("Закуски", ["zakusk", "buter", "kanape", "rulet", "shampinon", "hot-dog", "khod-dog"]),
        ("Гарніри", ["kartof", "kartopl", "batat", "ris", "grechk", "makaron"]),
        ("Напої", ["napit", "kokteyl", "limonad", "baileys", "beylis"]),
    ]
    for cat, words in rules:
        if any(w in t for w in words):
            return cat
    return "Інше"

def run():
    cmd = [
        "yt-dlp", "--flat-playlist", "--dump-json", "--skip-download",
        "--ignore-errors", "--no-warnings", CHANNEL,
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if p.returncode and not p.stdout.strip():
        print(p.stderr, file=sys.stderr)
        sys.exit(p.returncode)

    rows = []
    seen = set()
    for line in p.stdout.splitlines():
        try:
            e = json.loads(line)
        except Exception:
            continue
        vid = e.get("id")
        if not vid or vid in seen:
            continue
        seen.add(vid)
        url = e.get("webpage_url") or e.get("original_url") or e.get("url") or ""
        if "/shorts/" in str(url):
            continue
        title = e.get("title") or vid
        rows.append({
            "slug": slugify(title, vid),
            "title": title,
            "category": guess_category(title),
            "youtube_id": vid,
            "youtube_url": f"https://www.youtube.com/watch?v={vid}",
            "thumbnail": e.get("thumbnail") or f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
            "description": e.get("description") or "",
            "duration": e.get("duration"),
            "upload_date": e.get("upload_date"),
            "status": "published",
        })

    if not rows:
        print("No regular videos were returned; refusing to overwrite the catalog.", file=sys.stderr)
        sys.exit(2)

    DATA.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Synced {len(rows)} regular videos from {CHANNEL}; Shorts excluded")

if __name__ == "__main__":
    run()
