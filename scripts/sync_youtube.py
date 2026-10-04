"""Synchronize all regular videos from the UltrablackXL YouTube channel.

Source is the channel's /videos tab, not /shorts, so Shorts are intentionally
excluded. Existing editorial fields are preserved when a video can be matched
by YouTube ID or normalized title.

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

CYR = str.maketrans({
    "а":"a","б":"b","в":"v","г":"h","ґ":"g","д":"d","е":"e","ё":"yo","є":"ye","ж":"zh","з":"z",
    "и":"y","і":"i","ї":"yi","й":"y","к":"k","л":"l","м":"m","н":"n","о":"o","п":"p","р":"r",
    "с":"s","т":"t","у":"u","ф":"f","х":"kh","ц":"ts","ч":"ch","ш":"sh","щ":"shch","ъ":"",
    "ы":"y","ь":"","э":"e","ю":"yu","я":"ya",
})

def translit(text: str) -> str:
    return "".join(ch.translate(CYR) if ch.lower() in CYR else ch for ch in text.lower())

def slugify(text: str, video_id: str = "") -> str:
    s = translit(unicodedata.normalize("NFKC", text or ""))
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    if not s:
        s = "recipe"
    return f"{s[:72]}-{video_id[:8]}" if video_id else s[:80]

def norm_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", translit(text or ""))

def guess_category(title: str) -> str:
    t = translit(title)
    rules = [
        ("Салати", ["salat"]),
        ("Супи", ["sup", "borsh", "solyank"]),
        ("Риба", ["ryb", "losos", "skumb", "karp", "seld", "tunts", "forel"]),
        ("Випічка", ["piro", "khleb", "buloc", "blin", "pitsa", "pizza", "keks"]),
        ("Десерти", ["tort", "desert", "pechen", "krem", "tiramisu", "napoleon"]),
        ("Птиця", ["kur", "indey", "kryl", "utk"]),
        ("М’ясо", ["myas", "svinin", "govyad", "buzhen", "shashlyk", "kotlet", "pechenk", "yazyk"]),
        ("Закуски", ["zakusk", "buter", "kanape", "rulet", "shampinon"]),
        ("Гарніри", ["kartof", "kartopl", "ris", "grechk", "makaron"]),
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

    old = json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else []
    by_id = {x.get("youtube_id"): x for x in old if x.get("youtube_id")}
    by_title = {norm_key(x.get("title", "")): x for x in old if x.get("title")}

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
        previous = by_id.get(vid) or by_title.get(norm_key(title)) or {}
        row = {
            "slug": previous.get("slug") or slugify(title, vid),
            "title": title,
            "category": previous.get("category") or guess_category(title),
            "youtube_id": vid,
            "youtube_url": f"https://www.youtube.com/watch?v={vid}",
            "thumbnail": e.get("thumbnail") or f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
            "description": previous.get("description") or e.get("description") or "",
            "duration": e.get("duration"),
            "upload_date": e.get("upload_date"),
            "source_url": previous.get("source_url", ""),
            "status": "published",
        }
        rows.append(row)

    if not rows:
        print("No regular videos were returned; refusing to overwrite the catalog.", file=sys.stderr)
        sys.exit(2)

    DATA.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Synced {len(rows)} regular videos from {CHANNEL}; Shorts excluded")

if __name__ == "__main__":
    run()
