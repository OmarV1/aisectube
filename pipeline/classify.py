"""Step 3: topic-tag videos and decide relevance.

Rules tag titles into an AI security/safety taxonomy. Videos whose title doesn't match are 'review'
candidates; manual (Claude) decisions live in data/review_decisions.json as {video_id: [topics] | []}.
Writes site/data/videos.json.
"""
import json, math, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IN = ROOT / "data" / "videos_enriched.json"
DECISIONS = ROOT / "data" / "review_decisions.json"
REVIEW = ROOT / "data" / "review_queue.txt"
OUT = ROOT / "site" / "data" / "videos.json"

TOPICS = {
    "prompt-injection": r"prompt.?injection|prompt leak|indirect injection|ignore (all )?previous|data exfiltration",
    "jailbreaks": r"jailbr[eo]a?k",
    "llm-security": r"llm (security|attack|vulnerab|hack|exploit)|(ai|ml|machine learning) security|security (of|for) (ai|llm|machine learning|ml)|hacking (ai|llm|gpt|chatgpt)|owasp|ai village|agent security|mcp security|secure ai|ai hack|llm hack|attacking (ai|llm|ml|machine)|pwn",
    "ai-cyber": r"cyber ?(security|attack|risk|defen[cs]e|grand challenge)|ransomware|malware|offensive (ai|security)|black.?hat llm|zero.?day|bug bount|vulnerability (research|discovery)|automating defen[cs]e",
    "red-teaming": r"red.?team|pyrit|garak|purple (ai|team)|(attack|pen(etration)?).?test\w* (llm|ai|gen)|testing (llm|ai|gen)\w*|"
                   r"(llm|ai|gen ?ai) (pen.?test|offensive testing)|hack(ing)? (ai|llm|chatgpt|gpt)|breaking (ai|llm)|"
                   r"attacking (ai|llm|ml|machine|gen)|evaluate it",
    "safety-evals": r"\bevals?\b|evaluat(e|ing|ion)s? (of )?(llm|ai|model|frontier|safety|adversarial|machine)|safety test|"
                    r"dangerous capabilit|capabilit(y|ies) eval|\bmetr\b|benchmark\w* (safety|ai risk|frontier)|"
                    r"responsible scaling|preparedness|model card|pre.?deployment|warning shot|measuring (ai|machine)",
    "adversarial-ml": r"adversarial|data poison|backdoor|model (extraction|stealing|inversion|poison)|membership inference|evasion attack|robustness|trojan",
    "alignment": r"align(ment|ed|ing)|reward (hack|model)|specification gaming|mesa.?optim|inner misalign|rlhf|corrigib|constitutional ai|deceptive|sleeper agent|goal misgeneral|scalable oversight|instrumental convergence|orthogonality|stop button|ai control",
    "interpretability": r"interpretab|explainab|mechanistic|superposition|sparse autoencoder|circuits|feature visuali|saliency|xai\b|probing",
    "ai-risk": r"existential|x.?risk|superintelligen|ai (risk|doom|safety|danger)|dangers? of (ai|artificial)|agi (risk|safety|ruin)|catastroph|extinction|singularity|intelligence explosion|pause ai|safe(ty)? (ai|agi)|unfriendly ai|friendly ai|paperclip|yudkowsky|bostrom",
    "privacy": r"privacy|differential(ly)? private|deanonym|federated|memoriz|training data extract|pii",
    "deepfakes-misuse": r"deep.?fake|voice clon|synthetic media|disinformation|misinformation|watermark|ai.generated (fake|scam)|scam|fraud|misuse|weaponi[sz]",
    # policy & governance: how labs, governments and the world steer AI (strategy, coordination, ethics)
    "governance": r"governance|polic(y|ies)|ethic|responsible ai|treaty|summit|geopolit|national security|"
                  r"international (cooperation|coordination)|ai race|compute governance|scaling policy|"
                  r"democracy|accountab|safe harbor|whistleblow",
    # regulation & standards: laws, regulators and formal frameworks
    "regulation": r"regulat\w*|\bai act\b|artificial intelligence act|eu ai|\bnist\b|ai rmf|risk management framework|"
                  r"iso ?/?iec|42001|legislat\w*|executive order|sb ?1047|sb ?53|congress|senate|hearing|testimony|"
                  r"parliament|lawmakers|\bai laws?\b|state ai laws?|compliance|\bstandards?\b|code of practice|"
                  r"ai office|liability|copyright|gdpr|mitre atlas|safety institute|\baisi\b|\bbill\b",
}
TOPIC_RE = {k: re.compile(v, re.I) for k, v in TOPICS.items()}
# A title must look AI-related unless it's an AI-specific term already
AI_RE = re.compile(r"\b(ai|a\.i\.|agi|asi|llms?|gpt|chatgpt|claude|gemini|openai|anthropic|deepmind|neural|machine learning|deep learning|ml|artificial intelligence|language models?|transformers?|chatbots?|copilot|diffusion|robot|agents?|superintelligen|yudkowsky|bostrom|deep.?fake)\b", re.I)
AI_SPECIFIC = {"prompt-injection", "interpretability"}


NOISE_RE = re.compile(r"generative adversarial|\bgans?\b|bill hader|tom cruise|harmonyos|introducing .* platform|"
                      r"\[deep ?fake\]|deepfake\b.*(song|movie|music video)|"
                      # entertainment: films, music, clips, trailers, parodies
                      r"short film|\bfilm\b|full film|trailer|movie clip|music video|official (video|audio)|lyric|"
                      r"\bsings?\b|\bsong\b|parody|remix|cover\b|\bvevo\b|sketch|episode \d+ -|\bsnl\b|south park", re.I)
# Channels that are entertainment regardless of title
NOISE_CHANNELS = re.compile(r"vevo|- topic$|movieclips|ctrl shift face|shamook|corridor|foregone films|"
                            r"dust$|stop autonomous weapon|diep nep|sassy justice|party in the ai lab|comedy central", re.I)
STRICT_PI = re.compile(r"prompt.?injection|prompt leak", re.I)


def tag(title):
    if NOISE_RE.search(title):
        return []
    ts = [k for k, r in TOPIC_RE.items() if r.search(title)]
    if not ts:
        return []
    if AI_RE.search(title) or STRICT_PI.search(title) or "interpretability" in ts:
        return ts
    return []


def main():
    vids = json.loads(IN.read_text(encoding="utf-8"))
    decisions = json.loads(DECISIONS.read_text(encoding="utf-8")) if DECISIONS.exists() else {}
    keep, queue = [], []
    dropped = []
    for v in vids:
        title = v["title"] or ""
        if NOISE_RE.search(title) or NOISE_CHANNELS.search(v["channel"] or ""):
            if v["id"] in decisions and decisions[v["id"]] or tag(title):
                dropped.append(title)
            continue
        if v["id"] in decisions:
            topics = decisions[v["id"]]
            if topics:  # manual include: also add any category whose regex matches the title
                topics = topics + [k for k, r in TOPIC_RE.items() if r.search(title) and k not in topics]
        else:
            topics = tag(v["title"] or "")
            if not topics:
                queue.append(v)
                continue
        if topics:
            v["topics"] = topics
            keep.append(v)
    print("entertainment filter dropped:", *dropped, sep="\n  ")
    queue.sort(key=lambda v: -v["mentions"])
    REVIEW.write_text("\n".join(
        f"{v['id']}|{v['title']}|{v['channel']}|{','.join(v['keywords'][:3])}|{(v['hn'][0]['story_title'] or '')[:60]}"
        for v in queue), encoding="utf-8")
    talk_re = re.compile(r"def ?con|black ?hat|usenix|\bccc\b|\d\dc3|media\.ccc|bsides|camlis|hitcon|ekoparty|owasp|"
                         r"symposium|neurips|nips|iclr|icml|keynote|lecture|seminar|talk|conference|summit|"
                         r"\[un\]prompted|workshop|mit 6\.|stanford|berkeley|ipam|simons institute|far\.ai|far․ai", re.I)
    for v in keep:
        v["talk"] = bool(talk_re.search(f"{v['title']} {v['channel']}"))
        v["source"] = ["hn"]
        for h in v["hn"]:
            h["text"] = h["text"][:220]
    keep = merge_channels(keep)
    add_details(keep)
    alias = {"defconconference": "DEF CON", "far․ai": "FAR.AI", "unprompted": "[un]prompted",
             "unprompted au": "[un]prompted AU", "ieee symposium on security and privacy": "IEEE S&P"}
    for v in keep:
        v["channel"] = alias.get((v["channel"] or "").strip().lower(), (v["channel"] or "").strip())
        hn = math.log1p(v["mentions"]) * 1.2 + math.log1p(v["points"]) / 5
        yt = math.log10(v.get("views", 0) + 10) * 0.45
        v["pop"] = round(max(hn, yt) + (0.3 if hn and "channel" in v["source"] else 0), 3)
        v["score"] = v["pop"]
    keep.sort(key=lambda v: -v["score"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    courses_file = ROOT / "data" / "courses.json"
    courses = json.loads(courses_file.read_text(encoding="utf-8")) if courses_file.exists() else []
    payload = json.dumps({"topics": list(TOPICS), "generated": __import__("datetime").date.today().isoformat(),
                          "videos": keep, "courses": courses}, ensure_ascii=False)
    OUT.write_text(payload, encoding="utf-8")
    OUT.with_suffix(".js").write_text("window.AISEC_DATA = " + payload + ";", encoding="utf-8")
    print(f"kept {len(keep)}, review queue {len(queue)} (undecided) -> {REVIEW}")


CHANNEL_FILE = ROOT / "data" / "channel_videos.json"
DETAILS_CACHE = ROOT / "data" / "details_cache.json"
CHANNEL_DEFAULT = {   # topic for 'all'-mode channel videos no rule matched
    "AI Village (DEF CON)": ["llm-security"], "CAMLIS": ["ai-cyber"], "[un]prompted": ["llm-security"],
    "[un]prompted AU": ["llm-security"], "Embrace The Red": ["prompt-injection", "llm-security"],
    "Robert Miles AI Safety": ["alignment"], "FAR.AI": ["alignment"],
    "Microsoft — AI Red Teaming 101": ["red-teaming", "llm-security"],
}
NOT_TALK = {"Robert Miles AI Safety", "Embrace The Red", "Microsoft — AI Red Teaming 101", "Google DeepMind",
            "Anthropic", "Microsoft Security"}
# AI used FOR security work (defense/offense tooling) rather than attacks ON AI systems
AI_FOR_SEC = re.compile(r"using (ai|llms?|ml|machine learning|deep learning|neural)|with (ai|llms?|machine learning)|"
                        r"llm.?(powered|empowered|based|assisted)|ai.?(assisted|augmented|powered|driven|enhanced)|"
                        r"(machine|deep) learning (for|approach|on|to)|threat (hunting|intel)|detect|fuzz|phish|osint|"
                        r"\bsoc\b|soc detection|malware|side.?channel|decompil|triage|security (operations|response|review|teams?)|"
                        r"automat|harness|forensic|honeypot|sast|vulnerability (repair|assessment|analysis)|"
                        r"\bctf\b|exploit develop|hack(ing|s)? with|taught ai to hack|hackbots|ai cyber challenge|"
                        r"influence ops|social engineering|cybercrime|adversaries have ai", re.I)


# AI & ML foundations topics: only applied to foundation-channel videos (so security talks stay in security topics)
FOUND_TOPICS = {
    "llms": r"\b(llms?|gpt\S*|transformers?|attention|tokeni[sz]\w*|language models?|chatgpt|llama|bert|fine.?tun\w*|lora|"
            r"rag|kv.?cache|mixture.of.experts|moe|reasoning models?|scaling laws?|nanogpt|next.token|post.?training|"
            r"pre.?training|rlhf|dpo|vllm|context window|chain.of.thought|nlp|word2vec|seq2seq)\b",
    "deep-learning": r"\b(neural|deep learning|backprop\w*|cnns?|convolution\w*|rnns?|lstm|machine learning|reinforcement "
                     r"learning|gans?|vaes?|diffusion|autoencoders?|regression|decision trees?|random forests?|svms?|"
                     r"clustering|xgboost|gradient boost\w*|classification|computer vision|q.?learning|policy gradient|"
                     r"ml|alphago|alphafold|backpropagation|activation|dropout|batch norm\w*|resnet|imagenet)\b",
    "math": r"\b(linear algebra|calculus|probability|statistic\w*|eigen\w*|matri(x|ces)|fourier|bayes\w*|derivatives?|"
            r"integrals?|optimization|information theory|entropy|topology|theorem|proofs?|math\w*|vectors?|geometry|"
            r"differential equations?|p.?values?|hypothesis|distributions?|variance|determinant|convex|stochastic|"
            r"markov|monte carlo|primes?|numbers?|series|limits?|logarithms?|complex)\b",
}
FOUND_RE_T = {k: re.compile(v, re.I) for k, v in FOUND_TOPICS.items()}
PAPER_CHANNELS = {"Yannic Kilcher", "Two Minute Papers", "AI Coffee Break with Letitia", "Arxiv Insights"}
FOUND_DEFAULT = {"3Blue1Brown": "math", "Mutual Information": "math", "ritvikmath": "math", "Steve Brunton": "math",
                 "Andrej Karpathy": "llms", "Umar Jamil": "llms", "Sasha Rush": "llms", "Sebastian Raschka": "llms",
                 "Neel Nanda": "interpretability"}


def found_topics(c):
    t = c["title"]
    ts = [k for k, r in FOUND_RE_T.items() if r.search(t)]
    # safety topics still apply (e.g. Neel Nanda -> interpretability, MLST alignment interviews)
    ts += [k for k in ("alignment", "interpretability", "ai-risk", "safety-evals") if TOPIC_RE[k].search(t)]
    if c["channel"] in PAPER_CHANNELS:
        ts.append("papers")
    if not ts:
        ts = [FOUND_DEFAULT.get(c["channel"], "deep-learning")]
    return list(dict.fromkeys(ts))


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def merge_channels(keep):
    if not CHANNEL_FILE.exists():
        return keep
    by_id = {v["id"]: v for v in keep}
    seen_titles = {}
    for c in json.loads(CHANNEL_FILE.read_text(encoding="utf-8")):
        key = (c["channel"], norm(c["title"]))
        if key in seen_titles and seen_titles[key]["views"] >= c["views"]:
            continue
        seen_titles[key] = c
    added = 0
    for c in seen_titles.values():
        t = c["title"]
        if c["mode"] in ("fall", "ffilter", "fml"):
            if c["id"] in by_id:
                continue   # already present from HN/security sources
            by_id[c["id"]] = {
                "id": c["id"], "title": t, "channel": c["channel"], "mentions": 0, "points": 0,
                "first_seen": c["published"], "last_seen": c["published"], "published": c["published"],
                "keywords": [], "hn": [], "topics": found_topics(c), "talk": False, "found": True,
                "duration_s": c["duration_s"], "views": c["views"], "source": ["channel"],
            }
            added += 1
            continue
        topics = list(c.get("topics", [])) + [k for k, r in TOPIC_RE.items() if r.search(t) and k not in c.get("topics", [])]
        if not topics:
            if c["mode"] == "reg":
                topics = ["governance"]
            elif c["mode"] == "all":
                topics = list(CHANNEL_DEFAULT.get(c["channel"], ["llm-security"]))
            else:
                topics = ["ai-cyber"] if AI_FOR_SEC.search(t) else ["llm-security"]
        if c["id"] in by_id:   # already found via HN: enrich
            v = by_id[c["id"]]
            v["source"].append("channel")
            v["topics"] = v["topics"] + [x for x in topics if x not in v["topics"]]
            v["talk"] = v["talk"] or c["channel"] not in NOT_TALK
            continue
        by_id[c["id"]] = {
            "id": c["id"], "title": t, "channel": c["channel"], "mentions": 0, "points": 0,
            "first_seen": c["published"], "last_seen": c["published"], "published": c["published"],
            "keywords": [], "hn": [], "topics": topics,
            "talk": c["mode"] not in ("curated", "reg") and c["channel"] not in NOT_TALK,
            "duration_s": c["duration_s"], "views": c["views"], "source": ["channel"],
        }
        added += 1
    print(f"channels: +{added} new videos")
    return list(by_id.values())


def add_details(vids):
    """Fill duration/views/published for HN-sourced videos via the YouTube API (cached; skipped without a key)."""
    cache = json.loads(DETAILS_CACHE.read_text(encoding="utf-8")) if DETAILS_CACHE.exists() else {}
    need = [v["id"] for v in vids if "duration_s" not in v and v["id"] not in cache]
    if need:
        try:
            from ytapi import call
            from channels import iso_dur
            for i in range(0, len(need), 50):
                d = call("videos", part="contentDetails,statistics,snippet", id=",".join(need[i:i + 50]))
                for it in d.get("items", []):
                    cache[it["id"]] = {"duration_s": iso_dur(it["contentDetails"].get("duration")),
                                       "views": int(it["statistics"].get("viewCount", 0) or 0),
                                       "published": it["snippet"].get("publishedAt", "")[:10]}
            DETAILS_CACHE.write_text(json.dumps(cache), encoding="utf-8")
        except (SystemExit, Exception) as e:
            print("details skipped:", e)
    for v in vids:
        if v["id"] in cache and "duration_s" not in v:
            v.update(cache[v["id"]])


if __name__ == "__main__":
    main()
