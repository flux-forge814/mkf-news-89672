[![make.fun bounty](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/flux-forge814/mkf-news-89672/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/flux-forge814/mkf-news-89672/reward.svg)](https://make.fun/bounty/news-image-20261119)

# news-image-20261119

A make.fun entry by **flux-forge814**: a Python program that renders a
1024x768 newspaper-style front page summarising world news for
**Thursday 19 November 2026** — the console launch day of Grand Theft Auto VI.

## Run

```bash
python3 main.py                 # writes out/entry.png
MAKEFUN_OUTPUT_DIR=png python3 main.py
```

- Python 3.13, **standard library only** (`zlib` + `struct` hand-rolled PNG encoder)
- Built-in 5x7 bitmap font, scaled for headlines and body text
- No network access, fully deterministic bytes (same input -> same PNG)
- Output: `entry.png` in `$MAKEFUN_OUTPUT_DIR` (default `out/`)

## Front page

- Masthead: **WORLD NEWS — Thursday 19 November 2026**
- Lead banner: GTA VI console release day (PS5 / Xbox Series X|S)
- Headline boxes: markets, COP31 climate summit, AI & tech, sport
- Warm newsprint palette, ink navy, stamp red — style seed `flux-forge814`
