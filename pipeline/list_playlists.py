"""Discovery helper: print every playlist (4+ videos) on a set of channels, no keyword filter."""
import html
from ytapi import call


def pls(cid):
    out, tok = [], None
    while True:
        p = dict(part="snippet,contentDetails", channelId=cid, maxResults=50)
        if tok:
            p["pageToken"] = tok
        d = call("playlists", **p)
        out += d.get("items", [])
        tok = d.get("nextPageToken")
        if not tok:
            return out


ids = {"3Blue1Brown": "UCYO_jab_esuFRV4b17AJtAw", "Welch Labs": "UConVfxXodg78Tzh5nNu85Ew",
       "Umar Jamil": "UCtAcpQcYerN8xxZJYTfWBMw", "Mutual Information": "UCCcrR0XBH0aWbdffktUBEdw",
       "ritvikmath": "UCUcpVoi5KkJmnE3bvEhHR0Q", "Algorithmic Simplicity": "UC3sH8ShnMyB5MxavG1DaklA",
       "Neel Nanda": "UCBMJ0D-omcRay8dh4QT0doQ", "Robert Miles": "UCLB7AzTwc6VFZrBsO2ucBMg",
       "AI Coffee Break": "UCobqgqE4i5Kf7wrxRxhToQA", "Two Minute Papers": "UCbfYPyITQ-7l4upoX8nvctg",
       "Steve Brunton": "UCm5mt-A4w61lknZ9lCsZtBw", "Jia-Bin Huang": "UCkQS_dP6GJTmYnMlox-YiKQ",
       "CAMLIS": "UCmIY4lIVsotxeUDRCQb2ZXA", "Sasha Rush": "UCCnH8mxROOqii6gesCmMRzQ"}
for h in ["@Computerphile", "@IBMTechnology", "@MicrosoftDeveloper", "@ArtemKirsanov", "@OWASPGenAISecurityProject",
          "@VisuallyExplained"]:
    d = call("channels", part="snippet", forHandle=h)
    for i in d.get("items", []):
        ids[i["snippet"]["title"]] = i["id"]
for name, cid in ids.items():
    for it in pls(cid):
        n = it["contentDetails"]["itemCount"]
        if n >= 4:
            print(f"{it['id']} | {name[:18]:18} | {n:3} | {html.unescape(it['snippet']['title'])[:70]}")
