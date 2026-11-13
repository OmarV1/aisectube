"""Resolve candidate handles/search terms to channel IDs so we can pick the right ones."""
import sys
from ytapi import call

HANDLES = ["@DEFCONConference", "@AIVillage", "@aivillagedc", "@BlackHatOfficialYT", "@OffensiveCon", "@offensivecon",
           "@CAMLIS", "@camlis", "@mediacccde", "@USENIX", "@IEEESSP", "@ieeesymposiumonsecuritypr6219",
           "@SecurityBSidesSanFrancisco", "@BSidesSF", "@MicrosoftSecurity", "@OWASPGLOBAL", "@OWASP",
           "@googledeepmind", "@anthropic-ai", "@embracethered", "@RobertMilesAI", "@FARAIResearch", "@far-ai",
           "@unpromptedcon", "@unprompted", "@unprompted-con"]
SEARCH = ["AI Village DEF CON", "CAMLIS conference", "OffensiveCon", "unprompted AI security conference",
          "IEEE Symposium on Security and Privacy", "FAR.AI"]

seen = {}
for h in HANDLES:
    d = call("channels", part="snippet,statistics", forHandle=h)
    for it in d.get("items", []):
        seen[it["id"]] = (h, it["snippet"]["title"], it["statistics"].get("videoCount"))
for q in SEARCH:
    d = call("search", part="snippet", type="channel", q=q, maxResults=4)
    for it in d.get("items", []):
        cid = it["snippet"]["channelId"]
        seen.setdefault(cid, ("search:" + q, it["snippet"]["title"], "?"))
for cid, (src, title, n) in seen.items():
    print(f"{cid} | {title} | videos={n} | via {src}")
