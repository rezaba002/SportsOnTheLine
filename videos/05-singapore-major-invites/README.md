# How the Singapore Major 2026 Invites Were Decided (and Who Dropped Out)

Video: https://youtu.be/YKWjoljq4JY

Scripts as I ran them for the video. Paths are absolute to my machine (D:/Youtube/...), and footage, narration audio, logos and photos are not included. Scripts that go online have an **EDIT ME** proxy block at the top.

## Scripts

| File | What it does |
|---|---|
| [`analysis/work/build_daily_race.py`](analysis/work/build_daily_race.py) | Daily ranking-race data per region (HLTV's daily Valve ranking, Oct 5 -> last day collected) for Remotion. |
| [`analysis/work/build_race_data.py`](analysis/work/build_race_data.py) | Build the Europe ranking-race data (Valve Regional Standings, monthly 2026 files) for the Remotion race chart. |
| [`analysis/work/build_transfers.py`](analysis/work/build_transfers.py) | Per-team roster moves since the Cologne Major, from the HLTV transfers list (top-30 teams, Jun 22 -> Nov 1). |
| [`analysis/work/fetch_logos.py`](analysis/work/fetch_logos.py) | Team logos from Liquipedia (same source as video 02): dark-mode version when there is one, 400 px wide. |
| [`analysis/work/master.py`](analysis/work/master.py) | Video 05 final audio: the Remotion render (Brian + sound effects) + one CC0 music bed, sidechain-ducked under the |
| [`analysis/work/receiver.py`](analysis/work/receiver.py) | Tiny local receiver: the HLTV tab in the built-in browser POSTs JSON here, it is saved under video05/research/hltv/. |
| [`analysis/work/sfx_variants.py`](analysis/work/sfx_variants.py) | Pitch variants of every sound effect, so repeated effects never sound identical (video 05 v4). |
| [`analysis/work/timeline.py`](analysis/work/timeline.py) | Video 05 timeline: Brian's narration (work/narration/narration.json, word timings) -> what is on screen and when. |
| [`analysis/work/tts05.py`](analysis/work/tts05.py) | Brian narration for video 05: one mp3 per "> [id]" block of script_v1.md -> work/narration/<id>.mp3 + narration.json. |

## Data

Derived tables behind the numbers on screen.

- [`data/qual_chances_1031p2.json`](data/qual_chances_1031p2.json)
- [`data/transfers_top30_2026-06-22_to_2026-11-01.tsv`](data/transfers_top30_2026-06-22_to_2026-11-01.tsv)
