"""Step 1: harvest Hacker News comments/stories that link YouTube videos about AI security & safety.

Uses the public HN Algolia API (no key). Writes data/raw_mentions.json.
"""
import html, json, re, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw_mentions.json"

KEYWORDS = [
    "prompt injection", "jailbreak llm", "jailbreak gpt", "jailbreaking", "ai safety", "ai alignment",
    "alignment problem", "red teaming", "adversarial examples", "adversarial attack", "adversarial machine learning",
    "data poisoning", "model extraction", "membership inference", "model stealing", "llm security", "ai security",
    "machine learning security", "backdoor neural", "deepfake", "ai risk", "existential risk", "x-risk",
    "superintelligence", "interpretability", "reward hacking", "specification gaming", "rlhf", "constitutional ai",
    "ai governance", "ai regulation", "ai act", "ai village", "defcon ai", "black hat ai", "owasp llm",
    "llm vulnerabilities", "prompt leaking", "agent security", "mcp security", "sleeper agents", "deceptive alignment",
    "robert miles", "rob miles", "yudkowsky", "stuart russell", "paul christiano", "carlini", "goodfellow",
    "differential privacy", "watermarking", "ai hacking", "ai pentest", "llm attack", "model poisoning",
    "ai misuse", "ai control problem", "mesa optimizer", "ai doom", "frontier ai", "eliciting latent knowledge",
    "anthropic safety", "openai safety", "ai cyber", "llm exploit", "ai model weights", "ai privacy",
]
YEARS = range(2007, 2027)
VID_RE = re.compile(
    r"(?:youtube\.com/(?:watch\?(?:[^\"'\s<>]*?&(?:amp;)?)?v=|embed/|shorts/|live/|v/)|youtu\.be/)([A-Za-z0-9_-]{11})"
)
TAG_RE = re.compile(r"<[^>]+>")


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.load(r)
        except Exception as e:  # rate limit / transient
            time.sleep(2 * (i + 1))
    print("FAILED", url, file=sys.stderr)
    return {"hits": [], "nbPages": 0}


def ts(y):
    return int(time.mktime((y, 1, 1, 0, 0, 0, 0, 0, 0)))


def search(kw, tag, year, yt_word):
    q = f"{kw} {yt_word}" if tag == "comment" else kw
    out, page = [], 0
    while True:
        params = {
            "query": q, "tags": tag, "hitsPerPage": 1000, "page": page,
            "numericFilters": f"created_at_i>={ts(year)},created_at_i<{ts(year + 1)}",
            "typoTolerance": "false",
        }
        if tag == "story":
            params["restrictSearchableAttributes"] = "title"
        d = get("https://hn.algolia.com/api/v1/search?" + urllib.parse.urlencode(params))
        out += d.get("hits", [])
        page += 1
        if page >= d.get("nbPages", 0):
            break
    return kw, out


def main():
    jobs = []
    for kw in KEYWORDS:
        for y in YEARS:
            jobs.append((kw, "comment", y, "youtube"))
            jobs.append((kw, "comment", y, "youtu"))
            jobs.append((kw, "story", y, ""))
    print(f"{len(jobs)} queries", file=sys.stderr)
    mentions = {}  # (video_id, hn_id) -> record
    with ThreadPoolExecutor(12) as ex:
        for n, (kw, hits) in enumerate(ex.map(lambda j: search(*j), jobs)):
            for h in hits:
                text = html.unescape(h.get("comment_text") or h.get("story_text") or "")
                url = h.get("url") or ""
                ids = set(VID_RE.findall(text + " " + url))
                for vid in ids:
                    key = (vid, h["objectID"])
                    rec = mentions.setdefault(key, {
                        "video_id": vid,
                        "hn_id": h["objectID"],
                        "type": "story" if "story" in h.get("_tags", []) and not h.get("comment_text") else "comment",
                        "story_id": h.get("story_id"),
                        "story_title": h.get("story_title") or h.get("title"),
                        "points": h.get("points") or 0,
                        "author": h.get("author"),
                        "created_at": h.get("created_at"),
                        "text": TAG_RE.sub(" ", text)[:600].strip(),
                        "keywords": [],
                    })
                    if kw not in rec["keywords"]:
                        rec["keywords"].append(kw)
            if n % 300 == 0:
                print(f"  {n}/{len(jobs)}  mentions={len(mentions)}", file=sys.stderr)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(list(mentions.values()), indent=1), encoding="utf-8")
    vids = {m["video_id"] for m in mentions.values()}
    print(f"{len(mentions)} mentions, {len(vids)} unique videos -> {OUT}")


if __name__ == "__main__":
    main()
