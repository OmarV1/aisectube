"""Write a Markdown summary of what a pipeline run changed (used as the weekly pull-request description)."""
import json, sys
from collections import Counter


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


before, after = load(sys.argv[1]), load(sys.argv[2])
bv = {v["id"]: v for v in before["videos"]}
av = {v["id"]: v for v in after["videos"]}
added = [av[i] for i in av if i not in bv]
removed = [bv[i] for i in bv if i not in av]
bc = {c["id"]: c for c in before.get("courses", [])}
ac = {c["id"]: c for c in after.get("courses", [])}
grown = [(c, len(c["episodes"]) - len(bc[c["id"]]["episodes"])) for c in ac.values()
         if c["id"] in bc and len(c["episodes"]) > len(bc[c["id"]]["episodes"])]

print("## Proposed weekly update\n")
print(f"- **{len(added)} new videos**, {len(removed)} removed (deleted or made private on YouTube)")
print(f"- {len(grown)} courses/playlists gained new episodes")
print(f"- Catalog: {len(bv)} -> {len(av)} videos\n")
print("Merge this pull request to publish. Close it to skip this week.\n")
if added:
    print("### New videos by topic\n")
    for t, n in Counter(v["topics"][0] for v in added if v["topics"]).most_common():
        print(f"- {t}: {n}")
    print("\n### New videos\n")
    for v in sorted(added, key=lambda v: -v.get("views", 0))[:150]:
        print(f"- [{v['title']}](https://www.youtube.com/watch?v={v['id']}) - {v['channel']} - {', '.join(v['topics'])}")
    if len(added) > 150:
        print(f"\n...and {len(added) - 150} more.")
if grown:
    print("\n### Courses and playlists with new episodes\n")
    for c, n in grown:
        print(f"- {c['title']}: +{n}")
if removed:
    print("\n### Removed\n")
    for v in removed[:50]:
        print(f"- {v['title']} - {v['channel']}")
