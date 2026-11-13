"""Discovery helper: list playlists of key channels + targeted searches, keep AI-related ones. Prints candidates."""
import html, re, json
from pathlib import Path
from ytapi import call, api_key

OUT = Path(__file__).resolve().parent.parent / "data" / "playlist_candidates.json"
CHANNELS = {
    "DEF CON": "UC6Om9kAkl32dWlDSNlDS9Iw", "Black Hat": "UCJ6q9Ie29ajGqKApbLqfBOg", "CAMLIS": "UCmIY4lIVsotxeUDRCQb2ZXA",
    "FAR.AI": "UCCV6kbjBZje3LPxRp0NHfxg", "OWASP": "UCe8j61ABYDuPTdtjItD2veA", "IEEE S&P": "UC6pXMS7qre9GZW7A7FVM90Q",
    "AI Village": "UCBUw0vVET-kB7LPj_XsNQ9Q", "Microsoft Security": "UC4s3tv0Qq_OSUBfR735Jc6A",
    "Google DeepMind": "UCP7jMXSY2xbc3KCAE0MHQ-A", "Anthropic": "UCrDwWp7EBBv4NwvScIpBDOA", "BSides SF": "UCWemrSP6Aba171jXReCz_Qg",
    "media.ccc.de": "UC2TXq_t06Hjdr2g_KdKpHQg", "Embrace The Red": "UCSwcJXQWE6GWu9IKc0QwO5g",
    "Robert Miles": "UCLB7AzTwc6VFZrBsO2ucBMg", "[un]prompted": "UC5GCrYGsm7EHQzQZj65A-5w", "USENIX": "UCHwLg2XZDZL3OvrwpzleKjw",
    "Stanford Online": "UCBa5G_ESCn8Yd4vw5U-gIcg", "3Blue1Brown": "UCYO_jab_esuFRV4b17AJtAw", "Karpathy": "UCXUPKJO5MZQN11PqgIvyuvQ",
    "StatQuest": "UCtYLUTtgS3k1Fg4y5tAhLbw", "Jeremy Howard": "UCX7Y2qWriXpqocG97SFW2OQ", "Alexander Amini": "UCtslD4DGH6PKyG_1gFAX7sg",
    "Steve Brunton": "UCm5mt-A4w61lknZ9lCsZtBw", "Umar Jamil": "UCtAcpQcYerN8xxZJYTfWBMw", "Serrano": "UCgBncpylJ1kiVaPyP-PZauQ",
    "Hugging Face": "UCHlNU7kIZhRgSbhHvFoy72w", "Sebastian Raschka": "UC_CzsS7UTjcxJ-xXp1ftxtA", "MIT OCW": "UCEBb1b_L6zDS3xTUrIALZOw",
    "Yannic Kilcher": "UCZHmQk67mSJgfCCTn7xBfew", "Neel Nanda": None,
}
SEARCHES = ["AI security conference talks", "LLM security talks playlist", "AI red teaming playlist", "AI safety lectures playlist",
            "AI alignment course lectures", "SaTML conference talks", "MLSecOps podcast", "NeurIPS AI safety workshop",
            "mechanistic interpretability lectures", "AI governance course lectures", "adversarial machine learning tutorial",
            "AI village DEF CON talks", "GenAI security OWASP talks", "AI agent security talks", "Alignment Workshop talks",
            "Stanford CS224N", "MIT 6.S191 introduction to deep learning", "Neural Networks Zero to Hero"]
AI = re.compile(r"\b(ai|a\.i\.|llms?|gpt|genai|machine learning|deep learning|ml|neural|transformer|nlp|alignment|"
                r"safety|interpretab\w*|red team\w*|adversarial|language model|agents?|agentic|artificial intelligence|"
                r"reinforcement|linear algebra|calculus|probability|statistics|cs\d{3}\w*|6\.s\d+)\b", re.I)


def channel_playlists(cid):
    out, tok = [], None
    while True:
        p = dict(part="snippet,contentDetails", channelId=cid, maxResults=50)
        if tok: p["pageToken"] = tok
        d = call("playlists", **p)
        out += d.get("items", [])
        tok = d.get("nextPageToken")
        if not tok: return out


cands = {}
for name, cid in CHANNELS.items():
    if not cid: continue
    for it in channel_playlists(cid):
        t = html.unescape(it["snippet"]["title"]); n = it["contentDetails"]["itemCount"]
        if n >= 3 and AI.search(t):
            cands[it["id"]] = {"title": t, "channel": it["snippet"]["channelTitle"], "n": n, "via": name}
for q in SEARCHES:
    d = call("search", part="snippet", type="playlist", q=q, maxResults=10)
    for it in d.get("items", []):
        pid = it["id"]["playlistId"]
        cands.setdefault(pid, {"title": html.unescape(it["snippet"]["title"]),
                               "channel": html.unescape(it["snippet"]["channelTitle"]), "n": None, "via": "search:" + q})
OUT.write_text(json.dumps(cands, indent=0, ensure_ascii=False), encoding="utf-8")
for pid, c in sorted(cands.items(), key=lambda x: x[1]["via"]):
    print(f"{pid} | {c['via'][:18]:18} | {c['channel'][:22]:22} | {c['n']} | {c['title'][:70]}")
