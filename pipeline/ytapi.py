"""Tiny YouTube Data API v3 helper. Reads YOUTUBE_API_KEY from ../.env (never printed)."""
import json, os, sys, urllib.error, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def api_key():
    key = os.environ.get("YOUTUBE_API_KEY", "")
    env = ROOT / ".env"
    if not key and env.exists():
        for line in env.read_text(encoding="utf-8-sig").splitlines():
            if line.strip().startswith("YOUTUBE_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        sys.exit("No YOUTUBE_API_KEY found in .env")
    return key


def call(endpoint, **params):
    params["key"] = api_key()
    url = f"https://www.googleapis.com/youtube/v3/{endpoint}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = json.loads(e.read() or b"{}")
        msg = body.get("error", {}).get("message", str(e)).replace(params["key"], "***")
        raise RuntimeError(f"YouTube API error {e.code}: {msg}") from None


if __name__ == "__main__":  # self-test
    d = call("videos", part="snippet,contentDetails,statistics", id="pYXy-A4siMw")
    it = d["items"][0]
    print("OK - key works.", it["snippet"]["title"], "|", it["contentDetails"]["duration"],
          "|", it["statistics"].get("viewCount"), "views")
