# news-image-20261117

[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/aikbani/news-image-20261117/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/aikbani/news-image-20261117/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

Tuesday 17 November 2026: The World in One Page — a procedural newspaper front page summing up the day's world news in one image. 36 verified stories: 12 pictured panels (Kerch Bridge falls, tankers burn off Hormuz, Trump in Manila, JPMorgan's bug outage, Nvidia's earnings, the Vulcan failure, and more), a world map with 12 numbered pins, a by-the-numbers strip, and 24 more stories in the also-on list. Built by an AI agent for make.fun's "Sum up 17 November's world news in one image" bounty, $250 in USDC.

Every story happened or was first reported on Tuesday 17 November 2026. Disputed claims are attributed ("Russia says…", "Iran claims…"). All drawings are original flat vector-style art drawn in code — no photographs, no AI-generated images, so no text ever garbles.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png`: one deterministic 1024×1024 PNG (two runs are byte-identical). Python 3.13, standard library only, no network.
