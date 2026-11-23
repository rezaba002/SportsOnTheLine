# Video 12 — Can CS2 Pick’Em Pay for Itself?

Singapore 2026 gave a Diamond coin holder 900 tokens. At $0.99 for 100
tokens, that's $8.91 of shop value versus a $9.99 pass. If stickers
resell at the open shop's prices, estimated Steam Wallet proceeds after
fees are about $7.75. This is a sticker scenario, not a guaranteed
ceiling outside those assumptions or a claim about real buyer returns.

## Check the figures

From this folder, with Python 3.11 or newer (no dependencies):

```sh
python analysis/check_pass_value.py
```

[`data/frozen_inputs.json`](data/frozen_inputs.json) contains only the
aggregate counts, prices, and matched sale medians behind the final cut.
The checker recomputes the comparisons **from those frozen aggregates**.
It does not scrape Steam or rerun the match simulator.

- **Coin odds:** 20,000 simulated Majors per strategy drawn from the same
  match model used in [Video 10](../10-singapore-major-contenders) and
  [Video 11](../11-singapore-pickem). Participants are assumed to activate
  the coin and place all four tickets. That gives five base challenges.
  The model then scores six challenges requiring correct picks. Gold
  requires three of those six, Diamond all six. Diamond occurred in
  133 model-pick, 20 seed-pick, and one random-pick simulation. One hit
  is not a precise estimate of the underlying random-pick rate.
- **Cologne stickers:** 390 Holo histories were reviewed. For the 197
  original Event Holos with paired medians, 161 were cheaper in the
  recent window (last 30 days of the snapshot through November 22) than
  in their first observed sale week. Medians are volume-weighted per
  sticker. This is a relative comparison, not a historical USD basket
  estimate: the older sticker cache does not consistently record currency.
- **Cologne souvenirs:** June 2–September 29, 2026 inclusive. Match
  normal and souvenir skins by name and wear and retain the EUR
  volume-weighted medians. Estimate incremental Wallet value as
  `souvenir median / 1.15 − normal purchase median`, before the pass,
  paid top-ups, or leftover rewards. Per-item fee rounding is not modeled.
  The Bone Mask and Blue Spruce quotes total 236 tokens; their paired
  comparisons add about €4.79 (summing the cent-rounded estimates).
  Their quotes are snapshots, not tracked
  trades. The Elite Build example adds about €16.36, but no matching
  craft quote was verified. Steam sales pool variants across events,
  autographs and floats; these are not identified individual crafts.
- **Scope:** Cologne's souvenir pricing depended on the selected stickers
  as well as rarity; Singapore prices by rarity. Cologne is historical
  context, not a Singapore forecast or a count of buyers who broke even.
  Steam Wallet credit is not cash.

## Sources

- [Valve — The Cobbled Road to Singapore](https://steamcommunity.com/ogg/730/announcements/detail/687522235410285289)
- [Valve game text via SteamDB GameTracking-CS2](https://github.com/SteamDatabase/GameTracking-CS2)
- [Steam Community Market](https://steamcommunity.com/market/)
- [SkinSniper — Cologne 2026 archived shop](https://skinsniper.com/events/iem-cologne-2026)
- [Valve — Cologne souvenir rules](https://store.steampowered.com/news/app/730/view/672869045073084949)
- June 2 craft quotes: [Bone Mask](https://www.youtube.com/watch?v=zPWjREB_8bc&t=407s) and [Blue Spruce](https://www.youtube.com/watch?v=zPWjREB_8bc&t=442s)

Repository [code](../../LICENSE) and [derived-data](../../LICENSE-data)
licenses apply. No downloaded pages, footage, narration, thumbnails,
source images, or renders are included.
