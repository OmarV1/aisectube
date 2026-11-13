# AISec Tube

AI security & safety videos that Hacker News kept recommending over ~20 years, with private, local recommendations.

## Use it
Open `site/index.html` in a browser (works offline from disk), or serve the `site/` folder anywhere static
(GitHub Pages, Netlify, an S3 bucket, a VPS with nginx). No backend, no logins: watch history and the
recommendation profile live in each viewer's browser (`localStorage`), with Export/Import in the sidebar.

## Hosting & weekly updates
- Live at **https://aisectube.com**, hosted on **Cloudflare Pages** (project `aisectube`, output directory `site`,
  no build command). Cloudflare deploys automatically on every push to `main` and gives each pull request a preview link.
- `.github/workflows/deploy.yml` only keeps the old `omarv1.github.io/aisectube` address redirecting to aisectube.com.
- `.github/workflows/weekly-update.yml` runs every Monday: it re-reads only the curated sources, applies the
  same filters, and opens a pull request listing new videos. **Merge it to publish; close it to skip.**
- Needs one repository secret: `YOUTUBE_API_KEY` (Settings -> Secrets and variables -> Actions).

## How the data is built
```
python pipeline/harvest.py         # HN Algolia API: comments/stories linking YouTube + AI-security keywords
python pipeline/enrich.py          # YouTube oEmbed: titles/channels, drops dead videos (cached)
python pipeline/channels.py        # curated channels (needs YOUTUBE_API_KEY in .env) - edit CHANNELS / FOUND_CHANNELS
python pipeline/courses.py         # courses & playlists (ordered episodes) - edit COURSES, mark "course" or "playlist"
python pipeline/make_decisions.py  # manual (Claude-reviewed) include/reject list
python pipeline/classify.py        # rule tagging + decisions -> site/data/videos.js
```
- Topics: prompt injection, LLM/agent security, adversarial ML, alignment, interpretability, AI risk, privacy,
  deepfakes/misuse, governance. Tweak regexes in `classify.py` (`TOPICS`) and keywords in `harvest.py`.
- `data/review_queue.txt` lists videos the rules did not match; add good ones to `INCLUDE` in `make_decisions.py`.
- Thumbnails use YouTube's auto-generated middle frame (`hq2.jpg`), not the uploader's thumbnail.
- Score = HN mentions + story points; the "Recommended" sort adds your topic/channel affinity, freshness and a
  small daily shuffle.
