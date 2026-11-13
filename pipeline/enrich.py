"""Step 2: fetch title/channel for each video via YouTube oEmbed (no API key). Drops dead videos.

Reads data/raw_mentions.json, writes data/videos_enriched.json (cached; re-runs only fetch new ids).
"""
import json, sys, time, urllib.parse, urllib.request, urllib.error
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw_mentions.json"
CACHE = ROOT / "data" / "oembed_cache.json"
OUT = ROOT / "data" / "videos_enriched.json"


def oembed(vid):
    url = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(f"https://www.youtube.com/watch?v={vid}")
    for i in range(3):
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                d = json.load(r)
                return vid, {"title": d.get("title"), "channel": d.get("author_name"), "channel_url": d.get("author_url")}
        except urllib.error.HTTPError as e:
            if e.code in (400, 401, 403, 404):
                return vid, None  # private / removed / embedding disabled
            time.sleep(2 * (i + 1))
        except Exception:
            time.sleep(2 * (i + 1))
    return vid, "retry"


def main():
    mentions = json.loads(RAW.read_text(encoding="utf-8"))
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    by_vid = defaultdict(list)
    for m in mentions:
        by_vid[m["video_id"]].append(m)
    todo = [v for v in by_vid if v not in cache]
    print(f"{len(by_vid)} videos, fetching {len(todo)}", file=sys.stderr)
    with ThreadPoolExecutor(8) as ex:
        for n, (vid, meta) in enumerate(ex.map(oembed, todo)):
            if meta != "retry":
                cache[vid] = meta
            if n % 200 == 0:
                print(f"  {n}/{len(todo)}", file=sys.stderr)
    CACHE.write_text(json.dumps(cache), encoding="utf-8")

    videos = []
    for vid, ms in by_vid.items():
        meta = cache.get(vid)
        if not meta:
            continue
        ms.sort(key=lambda m: m["created_at"] or "")
        kws = sorted({k for m in ms for k in m["keywords"]})
        videos.append({
            "id": vid, **meta,
            "mentions": len(ms),
            "points": sum(m["points"] for m in ms if m["type"] == "story"),
            "first_seen": ms[0]["created_at"], "last_seen": ms[-1]["created_at"],
            "keywords": kws,
            "hn": [{"id": m["hn_id"], "story_id": m["story_id"], "story_title": m["story_title"], "type": m["type"],
                    "points": m["points"], "date": (m["created_at"] or "")[:10], "text": m["text"][:300]} for m in ms[:5]],
        })
    OUT.write_text(json.dumps(videos, indent=1), encoding="utf-8")
    print(f"{len(videos)} live videos -> {OUT}")


if __name__ == "__main__":
    main()
