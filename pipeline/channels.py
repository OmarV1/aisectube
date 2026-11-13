"""Step 1b: pull full upload catalogs from curated AI-security channels (needs YOUTUBE_API_KEY in .env).

mode "all"    -> AI-security-focused channel: keep every real video (drops shorts)
mode "ai"     -> general security conference: keep only talks whose title looks AI-related
mode "topic"  -> AI lab channel: keep only videos matching a safety/security topic (skip product videos)
Writes data/channel_videos.json. Uploads lists are cached in data/uploads_cache.json (delete to refresh).
"""
import json, re, sys
from pathlib import Path
from ytapi import call
from classify import AI_RE, TOPIC_RE, NOISE_RE

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "uploads_cache.json"
OUT = ROOT / "data" / "channel_videos.json"

CHANNELS = [
    ("UCBUw0vVET-kB7LPj_XsNQ9Q", "AI Village (DEF CON)", "all"),
    ("PLlrxD0HtieHhXnVUQM42aKRPrirbUIDdh", "Microsoft — AI Red Teaming 101", "all"),   # playlist
    ("UCmIY4lIVsotxeUDRCQb2ZXA", "CAMLIS", "all"),
    ("UC5GCrYGsm7EHQzQZj65A-5w", "[un]prompted", "all"),
    ("UCO3btvFeqGV8gzrw48wamhg", "[un]prompted AU", "all"),
    ("UCSwcJXQWE6GWu9IKc0QwO5g", "Embrace The Red", "all"),
    ("UCLB7AzTwc6VFZrBsO2ucBMg", "Robert Miles AI Safety", "all"),
    ("UCCV6kbjBZje3LPxRp0NHfxg", "FAR.AI", "all"),
    ("UC6Om9kAkl32dWlDSNlDS9Iw", "DEF CON", "ai"),
    ("UCuVGdZa_LvyW_lwp_Fj65Pg", "Policy @ DEF CON", "ai"),
    ("UCJ6q9Ie29ajGqKApbLqfBOg", "Black Hat", "ai"),
    ("UCMNvAtT4ak2azKNk6UlB1QQ", "OffensiveCon", "ai"),
    ("UC2TXq_t06Hjdr2g_KdKpHQg", "media.ccc.de", "ai"),
    ("UCHwLg2XZDZL3OvrwpzleKjw", "USENIX", "ai"),
    ("UC6pXMS7qre9GZW7A7FVM90Q", "IEEE S&P", "ai"),
    ("UCWemrSP6Aba171jXReCz_Qg", "BSides SF", "ai"),
    ("UC4s3tv0Qq_OSUBfR735Jc6A", "Microsoft Security", "ai"),
    ("UCe8j61ABYDuPTdtjItD2veA", "OWASP", "ai"),
    ("UCP7jMXSY2xbc3KCAE0MHQ-A", "Google DeepMind", "topic"),
    ("UCrDwWp7EBBv4NwvScIpBDOA", "Anthropic", "topic"),
]
# AI policy, regulation & standards: official bodies and established policy institutes (mode "reg": AI + policy titles only)
POLICY_CHANNELS = [
    ("UCelItQpbih_hBrNSA5cRZyw", "NIST", "reg", 40),
    ("UCMPaviJxybo1RTdzvYcU91A", "European Commission", "reg", 30),
    ("UCvU4p_w08osQsrNi_I4ZtDA", "European Parliament", "reg", 30),
    ("UCSzp1BZ6rLc5OZYUYTLR1vQ", "EU in the US", "reg", 15),
    ("UCR-Ja1yBcjkhuQblxnroZJg", "OECD", "reg", 30),
    ("UCqD5MdT9cw4LBQ2TaH1-fkw", "MITRE", "reg", 30),
    ("UChugFTK0KyrES9terTid8vA", "Stanford HAI", "reg", 60),
    ("UCC0d3h9rVlfBouk0WoKE1FQ", "CSET (Georgetown)", "reg", 60),
    ("UC-rCCy3FQ-GItDimSR9lhzw", "Future of Life Institute", "reg", 60),
    ("UCY_K5gXsXHtuiP8mj3BiWxA", "Center for AI Safety", "reg", 40),
    ("UCj6Sdo4tRaczDt30FNbMztg", "AI Now Institute", "reg", 40),
    ("UCFrzEv98T3Ee-zSc6aFvmWA", "Tech Policy Press", "reg", 40),
    ("UCh_9jgYqQNYlk8daCZFRD1A", "Lawfare", "reg", 50),
    ("UCr5jq6MC_VCe1c5ciIZtk_w", "CSIS", "reg", 50),
    ("UCi7jxgIOxcRaF4Q54U7lF3g", "Brookings", "reg", 50),
    ("UCDeDd29TrRzAkSKXBCtGhxA", "Carnegie Endowment", "reg", 40),
    ("UCoooV8TQKY3Llh_Llcp9Asg", "CNAS", "reg", 40),
]
REG_AI = re.compile(r"\b(ai|a\.i\.|artificial intelligence|llms?|chatgpt|generative|gen ?ai|frontier models?|"
                    r"machine learning|algorithm\w*|deep ?fakes?|automated decision|autonomous weapons?)\b", re.I)
REG_POLICY = re.compile(r"polic\w*|govern\w*|regulat\w*|\bact\b|\blaws?\b|legislat\w*|security|safety|risk\w*|"
                        r"standard\w*|compliance|oversight|ethic\w*|rights|national security|military|weapons?|"
                        r"treaty|summit|accountab\w*|audit\w*|trust\w*|framework|china|democracy|elections?|"
                        r"executive order|congress|senate|hearing|testimony|liability|copyright|privacy", re.I)


# off-topic policy-institute events (education, food, energy, careers, health care)
REG_NOISE = re.compile(r"ai\s?\+\s?education|education summit|educators|classroom|students|schools|food (in)?security|"
                       r"hungermap|energy|\boil\b|music|career|health ?care|healthcare|public health", re.I)


# AI & ML foundations: technical educators and paper explainers (no influencers).
# mode "fall" = keep every real video, "ffilter" = keep only titles about ML/AI/math. cap = top-N by views (+ last 18 months)
FOUND_CHANNELS = [
    ("UCYO_jab_esuFRV4b17AJtAw", "3Blue1Brown", "ffilter", 120),
    ("UCXUPKJO5MZQN11PqgIvyuvQ", "Andrej Karpathy", "fall", 50),
    ("UConVfxXodg78Tzh5nNu85Ew", "Welch Labs", "fall", 60),
    ("UCtYLUTtgS3k1Fg4y5tAhLbw", "StatQuest", "fall", 150),
    ("UCtAcpQcYerN8xxZJYTfWBMw", "Umar Jamil", "fall", 40),
    ("UC3sH8ShnMyB5MxavG1DaklA", "Algorithmic Simplicity", "fall", 20),
    ("UCgBncpylJ1kiVaPyP-PZauQ", "Luis Serrano Academy", "fall", 80),
    ("UCCcrR0XBH0aWbdffktUBEdw", "Mutual Information", "fall", 30),
    ("UCX7Y2qWriXpqocG97SFW2OQ", "Jeremy Howard", "ffilter", 80),
    ("UC_CzsS7UTjcxJ-xXp1ftxtA", "Sebastian Raschka", "ffilter", 80),
    ("UCCnH8mxROOqii6gesCmMRzQ", "Sasha Rush", "fall", 40),
    ("UCBMJ0D-omcRay8dh4QT0doQ", "Neel Nanda", "fall", 60),
    ("UCMLtBahI5DMrt0NPvDSoIRQ", "Machine Learning Street Talk", "fall", 120),
    ("UCZHmQk67mSJgfCCTn7xBfew", "Yannic Kilcher", "fall", 150),
    ("UCbfYPyITQ-7l4upoX8nvctg", "Two Minute Papers", "fall", 150),
    ("UCobqgqE4i5Kf7wrxRxhToQA", "AI Coffee Break with Letitia", "fall", 80),
    ("UCNIkB2IeJ-6AmZv7bQ1oBYg", "Arxiv Insights", "fall", 20),
    ("UCm5mt-A4w61lknZ9lCsZtBw", "Steve Brunton", "ffilter", 80),
    ("UCUcpVoi5KkJmnE3bvEhHR0Q", "ritvikmath", "ffilter", 80),
    ("UCtslD4DGH6PKyG_1gFAX7sg", "Alexander Amini (MIT 6.S191)", "fall", 60),
    ("UCBa5G_ESCn8Yd4vw5U-gIcg", "Stanford Online", "ffilter", 120),
    ("UCEBb1b_L6zDS3xTUrIALZOw", "MIT OpenCourseWare", "fml", 60),
]
FOUND_RE = re.compile(r"\b(ai|a\.i\.|llms?|gpt\S*|transformers?|attention|neural|deep learning|machine learning|ml|"
                      r"reinforcement learning|language models?|nlp|diffusion|backprop\w*|gradient|regression|"
                      r"classification|linear algebra|calculus|probability|statistic\w*|bayes\w*|matri(x|ces)|eigen\w*|"
                      r"optimization|data science|computer vision|cs ?(221|224n|229|230|231n|234|236|336)|artificial "
                      r"intelligence|agents?|alignment|interpretab\w*|embedding\w*|tokeni\w*)\b", re.I)
# ML/AI only (no general math) - for MIT OCW single videos; full math courses come in via courses.py
FOUND_ML = re.compile(r"\b(ai|llms?|gpt\S*|transformers?|attention|neural|deep learning|machine learning|"
                      r"reinforcement learning|language models?|nlp|diffusion models?|artificial intelligence)\b", re.I)
# business webinars, industry series, marketing and off-topic lectures on big university channels
FOUND_NOISE = re.compile(r"webinar|ai in healthcare|healthcare series|reacts|myths|trends|top questions|startup|"
                         r"program (overview|info)|info session|graduate certificate|counterparty|musicolog|economist|"
                         r"in the age of ai\?|finance|marketing|leadership|business|frontier$|session \d+:|"
                         r"python in the age|career", re.I)
# For general security channels: a title must be clearly about AI (no bare "agent"/"robot", which hit "Agent X", ROBOT attack...)
STRICT_AI = re.compile(r"\b(ai|a\.i\.|agi|llms?|llm\w+|gpt\S*|chatgpt|claude|gemini|copilot|openai|anthropic|deepmind|"
                       r"machine learning|deep learning|neural|genai|gen ?ai|generative|language models?|agentic|a2a|"
                       r"mcp|prompt\w*|adversarial (ml|machine|examples?|inputs?|robust\w*|attacks? on)|deep ?fakes?|chatbots?|rag|ml|mlops|dnn|hackbots?|"
                       r"coding agents?|computer.use|vibe.?cod\w*)\b", re.I)
# The talk must also be about security / safety, not AI in general
SEC = re.compile(r"hack|exploit|attack|secur|vulnerab|threat|malic|phish|red.?team|offens|defen[cs]|adversar|abuse|break|"
                 r"own(ing|ed)? |pwn|\bbugs?\b|cve|rce\b|sandbox|evad|evasion|poison|leak|steal|exfil|\bc2\b|malware|fuzz|"
                 r"detect|\bsoc\b|osint|forensic|\bspy|influence|manipul|decept|deceiv|trust|risk|safe|privacy|private|"
                 r"harm|bias|surveil|cyber|incident|zero.?day|0.?day|honeypot|injection|backdoor|side.?channel|"
                 r"hijack|tamper|integrity|confidential|guardrail|govern|accountab|compromise|blind.?spot|taint|"
                 r"triage|hunting|apt\b|identity|zero trust|supply chain|appsec|sast|ctf|crime|fraud|scam", re.I)
TRANSLATION = re.compile(r"deutsche übersetzung|traduction|traducción|\(deu\)|\bdeu\b -|übersetzung", re.I)
# Vendor marketing / product how-tos (mostly Microsoft Security channel)
MARKETING = re.compile(r"security copilot|copilot for security|flight school|swimlane|promptbook|defender for cloud|"
                       r"\| microsoft (defender|purview|entra|intune|sentinel|365)|microsoft (defender|purview|entra|"
                       r"intune|sentinel) \||sentinel (mcp|ai-powered|webinar)|azure (ai foundry|essentials|sentinel)|"
                       r"customers|saves nearly|\bama\b|camp kickoff|campfire|trail tip|in the field|tech accelerator|"
                       r"better together|ignite 20|security forum at rsac|ecosystem in the ai era|raises certainty|"
                       r"avanade|configure an agent|consent prompts|built-in ml policies|it solutions simplified|"
                       r"purview|sentinel|azure|mdeasm|defender xdr|customer panel|public sector|highlights|"
                       r"dlp alert|unlock ai agents|stay secure", re.I)
# Individually reviewed rejects (off-topic, previews, duplicates)
REJECT_IDS = set("""90VeWekqHLQ 6Cedq6RnjZM 4ouNbLgJEHA sl-H4H1PX1A hJxRD4YX1RU t01tbbjJHbs tuJmvaLZOoI tLcSug8IHis
uDksY6ji-dk D6By-egAge0 Qgd3OK5DZWI 0ghzG14dT-w Nmt3uYrbNTs""".split())


# Hand-picked individual videos (id -> topics). AI policy: Jack Clark / Anthropic policy & frontier-AI governance.
GOV, CYBER = "governance", "ai-cyber"
CURATED = {
    "yGmvaOast_k": [GOV], "e0L29mGRKeo": [GOV], "xYTwgTRU4sM": [GOV], "b1-OuHWu88Y": [GOV], "U1ZMmKMMHgQ": [GOV],
    "PO8-fegV4X0": [GOV], "Ax0ddrP8_ho": [GOV], "7nz4cWEsPWc": [GOV], "riuB-hwY9Jo": [GOV], "PY8MOhlqC4U": [GOV],
    "QQSsMr4MUy8": [GOV], "GZ427GAGCz0": [GOV], "eMBc0Ps-CCs": [GOV, CYBER], "7JYb0JGz7rg": [GOV, CYBER],
    "om2lIWXLLN4": [GOV], "0Q5J8UB3mXE": [GOV], "aAPpQC-3EyE": [GOV], "lLv14fslvFU": [GOV], "6pnfVSrlFAw": [GOV],
    "f4T9BnnvhVs": [GOV],
    # Regulation & standards (official bodies and credible explainers only; no cert-prep / consultancy funnels)
    "O4iKEr5AIi4": ["regulation"],                      # ISO: What is ISO/IEC 42001?
    "0oeD2Wf25wY": ["regulation"],                      # IBM: NIST AI Risk Management Framework explained
    "eqKwuYCBlVE": ["regulation"],                      # SANS: Demystifying the NIST AI RMF
    "QhoG74PDFyc": ["regulation", "llm-security"],      # IBM: Anatomy of an AI attack - MITRE ATLAS
    "AGu8-v9EHlo": ["regulation", "llm-security"],      # MITRE ATLAS with MITRE's Steve Winterfeld
    "iO0nfxxeYjE": ["regulation"],                      # Fieldfisher: overview of the EU AI Act legal framework
    "oWHCyLfUgUw": ["regulation"],                      # Deloitte: EU AI Act explained
    "_LP_WFZ6aqA": ["regulation"],                      # The finalised EU AI Act: implications for builders
    "s_rxOnCt3HQ": ["regulation"],                      # The EU's AI Act explained
}


def curated_videos():
    out, ids = [], list(CURATED)
    for i in range(0, len(ids), 50):
        d = call("videos", part="snippet", id=",".join(ids[i:i + 50]))
        for it in d.get("items", []):
            s = it["snippet"]
            out.append({"id": it["id"], "title": s["title"], "published": s.get("publishedAt", "")[:10],
                        "desc": (s.get("description") or "")[:400], "channel": s["channelTitle"],
                        "channel_id": s["channelId"], "mode": "curated", "topics": CURATED[it["id"]]})
    return out


def uploads(cid, max_pages=None):
    """All uploads of a channel (or items of a playlist), newest first. max_pages=N reads only the newest N*50."""
    pl = cid if cid.startswith("PL") else "UU" + cid[2:]   # playlist id, or the channel's uploads playlist
    items, tok, pages = [], None, 0
    while True:
        pages += 1
        p = dict(part="snippet", playlistId=pl, maxResults=50)
        if tok:
            p["pageToken"] = tok
        d = call("playlistItems", **p)
        for it in d.get("items", []):
            s = it["snippet"]
            vid = s.get("resourceId", {}).get("videoId")
            if vid and s.get("title") not in ("Private video", "Deleted video"):
                items.append({"id": vid, "title": s["title"], "published": s.get("publishedAt", "")[:10],
                              "desc": (s.get("description") or "")[:400]})
        tok = d.get("nextPageToken")
        if not tok or (max_pages and pages >= max_pages):
            return items


def iso_dur(s):
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    if not m:
        return 0
    d, h, mi, se = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + se


def details(ids):
    out = {}
    for i in range(0, len(ids), 50):
        d = call("videos", part="contentDetails,statistics", id=",".join(ids[i:i + 50]))
        for it in d.get("items", []):
            out[it["id"]] = {"duration_s": iso_dur(it["contentDetails"].get("duration")),
                             "views": int(it["statistics"].get("viewCount", 0) or 0)}
    return out


def keep(v, mode):
    t = v["title"]
    if v["id"] in REJECT_IDS or NOISE_RE.search(t) or TRANSLATION.search(t) or MARKETING.search(t):
        return False
    if mode in ("all", "fall"):
        return True
    if mode in ("ffilter", "fml") and FOUND_NOISE.search(t):
        return False
    if mode == "ffilter":
        return bool(FOUND_RE.search(t))
    if mode == "fml":
        return bool(FOUND_ML.search(t))
    if mode == "reg":
        return bool(REG_AI.search(t) and REG_POLICY.search(t)) and not REG_NOISE.search(t)
    if mode == "topic":
        return any(r.search(t) for k, r in TOPIC_RE.items() if k not in ("governance",))
    on_topic = any(r.search(t) for r in TOPIC_RE.values())
    return bool(STRICT_AI.search(t) and (SEC.search(t) or on_topic))


def recent_update(pages=2):
    """Quick weekly mode: read only each channel's newest uploads (pages*50) and merge them into the existing
    data/channel_videos.json. Existing entries are re-checked against the current filters; nothing is re-downloaded."""
    existing = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else []
    known = {v["id"] for v in existing}
    by_name = {name: mode for cid, name, mode, *cap in CHANNELS + POLICY_CHANNELS + FOUND_CHANNELS}
    kept = [v for v in existing if v.get("mode") == "curated" or (v["channel"] in by_name and keep(v, v["mode"]))]
    new = []
    for cid, name, mode, *cap in CHANNELS + POLICY_CHANNELS + FOUND_CHANNELS:
        ups = uploads(cid, max_pages=pages)
        k = [dict(v, channel=name, channel_id=cid, mode=mode) for v in ups if v["id"] not in known and keep(v, mode)]
        if k:
            print(f"{name:28} +{len(k)} new candidates", file=sys.stderr)
        new += k
    known_curated = {v["id"] for v in existing if v.get("mode") == "curated"}
    new += [v for v in curated_videos() if v["id"] not in known_curated and v["id"] not in known]
    det = details([v["id"] for v in new])
    added = [dict(v, **det[v["id"]]) for v in new if v["id"] in det and det[v["id"]]["duration_s"] >= 150]
    OUT.write_text(json.dumps(kept + added, indent=0, ensure_ascii=False), encoding="utf-8")
    print(f"quick update: {len(kept)} kept, {len(existing) - len(kept)} dropped by filters, {len(added)} new -> {OUT}")


def main():
    if "--recent" in sys.argv:
        return recent_update()
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    picked = []
    caps = {}
    for cid, name, mode, *cap in CHANNELS + POLICY_CHANNELS + FOUND_CHANNELS:
        if cid not in cache:
            cache[cid] = uploads(cid)
            CACHE.write_text(json.dumps(cache), encoding="utf-8")
        ups = cache[cid]
        k = [dict(v, channel=name, channel_id=cid, mode=mode) for v in ups if keep(v, mode)]
        print(f"{name:24} {len(ups):5} uploads -> {len(k):4} candidates", file=sys.stderr)
        picked += k
        if cap:
            caps[name] = cap[0]
    picked += curated_videos()
    det = details([v["id"] for v in picked])
    out = []
    for v in picked:
        d = det.get(v["id"])
        if not d or d["duration_s"] < 150:   # dead or shorts/teasers
            continue
        out.append(dict(v, **d))
    # cap big foundation channels: top-N by views, plus anything from the last ~18 months
    import datetime
    recent = (datetime.date.today() - datetime.timedelta(days=540)).isoformat()
    capped = []
    for name, n in caps.items():
        vs = sorted([v for v in out if v["channel"] == name], key=lambda v: -v["views"])
        keep_ids = {v["id"] for v in vs[:n]} | {v["id"] for v in vs if v["published"] >= recent}
        capped += [v for v in vs if v["id"] in keep_ids]
    out = [v for v in out if v["channel"] not in caps] + capped
    OUT.write_text(json.dumps(out, indent=0, ensure_ascii=False), encoding="utf-8")
    print(f"{len(out)} channel videos -> {OUT}")


if __name__ == "__main__":
    main()
