# Singapore Major: 3 Players You Shouldn't Overlook

Video: https://youtu.be/C_JbnVVSQGY

Round swing from bo3.gg 2D replays: which Major players win their teams' rounds, and when on the round clock they kill and die.

Scripts as I ran them for the video. Paths are absolute to my machine (D:/Youtube/...), and footage, narration audio, logos, photos, music and sound effects are not included. Lines marked **EDIT ME** point at tools or files you need to supply yourself.

## Scripts

| File | What it does |
|---|---|
| [`analysis/work/bo3.py`](analysis/work/bo3.py) | Small bo3.gg client: curl with retries, polite pacing, on-disk cache. |
| [`analysis/work/bo3_round_kills.py`](analysis/work/bo3_round_kills.py) | Kill times for one round from bo3.gg's 2D-replay file, without downloading all of it. |
| [`analysis/work/fetch_matches.py`](analysis/work/fetch_matches.py) | All finished CS2 matches on bo3.gg since the season start -> research/matches_2026.json |
| [`analysis/work/collect.py`](analysis/work/collect.py) | Collect round-clock data for the 32 Singapore Major teams, season 2026 (Jan 1 -> now). |
| [`analysis/work/analyze.py`](analysis/work/analyze.py) | Round clock per player: when do they die, when do they kill. |
| [`analysis/work/clock_stats.py`](analysis/work/clock_stats.py) | Round-clock stats in seconds per Major player (full-buy rounds) -> data/clock.json |
| [`analysis/work/win_check.py`](analysis/work/win_check.py) | Does dying early cost rounds? Team round-win % by how/when a player died (full-buy rounds). |
| [`analysis/work/swing.py`](analysis/work/swing.py) | Round swing (win probability added) per player, from our own 46K rounds. |
| [`analysis/work/swing_v4.py`](analysis/work/swing_v4.py) | Match-cross-fitted, bomb-aware kill/death swing. Objective counts are separate. |
| [`analysis/work/test_swing_v4.py`](analysis/work/test_swing_v4.py) | Tests for swing_v4.py. |
| [`analysis/work/bomb_context.py`](analysis/work/bomb_context.py) | Versioned objective context, kept separate from original round-clock inputs. |
| [`analysis/work/test_bomb_context.py`](analysis/work/test_bomb_context.py) | Tests for bomb_context.py. |
| [`analysis/work/igls.py`](analysis/work/igls.py) | IGLs of the Major teams from the saved Liquipedia team pages -> research/igls.json |
| [`analysis/work/fetch_liquipedia.py`](analysis/work/fetch_liquipedia.py) | Liquipedia team pages (wikitext) for the Major teams -> research/liquipedia/<team>.wiki |
| [`analysis/work/verify_claims_v4.py`](analysis/work/verify_claims_v4.py) | Release gate for the actual spoken statistical claims, independent of graphics. |
| [`analysis/work/captions.py`](analysis/work/captions.py) | Video 09 captions from Brian's own word timings (sotl-graphics/public/data/video09.json): script spellings (ropz, MongolZ, |
| [`analysis/work/timeline.py`](analysis/work/timeline.py) | Video 09 timeline: narration blocks back to back (longer pauses between sections, air after the intro), |

## Data

Derived tables behind the numbers on screen.

- [`data/clock.json`](data/clock.json)
- [`data/players.json`](data/players.json)
- [`data/swing_v4.json`](data/swing_v4.json)
- [`data/win_check.json`](data/win_check.json)
- [`data/claims_v4_verified.json`](data/claims_v4_verified.json)
- [`data/igls.json`](data/igls.json)
- [`data/major_teams_bo3.json`](data/major_teams_bo3.json)

## Production

Remotion source for the edit (code only; it expects assets that are not in this repo).

- [`production/src/video09/Video09V4.tsx`](production/src/video09/Video09V4.tsx)
- [`production/src/video09/EditorialCaptions.tsx`](production/src/video09/EditorialCaptions.tsx)
- [`production/src/video09/camera.ts`](production/src/video09/camera.ts)
