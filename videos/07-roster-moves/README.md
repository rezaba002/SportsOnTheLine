# Which CS2 Transfer Actually Worked?

Video: https://youtu.be/zwpl93MQuU4

Scripts as I ran them for the video. Paths are absolute to my machine (D:/Youtube/...), and footage, narration audio, logos and photos are not included. Scripts that go online have an **EDIT ME** proxy block at the top.

## Scripts

| File | What it does |
|---|---|
| [`analysis/work/captions.py`](analysis/work/captions.py) | Video 07 English subtitles (SRT) from the narration's own word timings (script spellings, absolute frames in |
| [`analysis/work/eras.py`](analysis/work/eras.py) | Video 07: did the roster moves since the Cologne Major work? |
| [`analysis/work/lineups.py`](analysis/work/lineups.py) | Match-by-match lineups from Valve's ranking details (Nov 2 2026 files: every match since May with the five who played). |
| [`analysis/work/moves.py`](analysis/work/moves.py) | Video 07, precise version: each team judged on its REAL current five (stand-ins and loans left out). |
| [`analysis/work/timeline.py`](analysis/work/timeline.py) | Video 07 timeline: narration blocks back to back (longer pauses between sections), word timings for cues, and every |
| [`analysis/work/tts.py`](analysis/work/tts.py) | Brian narration for video 05: one mp3 per "> [id]" block of script_v1.md -> work/narration/<id>.mp3 + narration.json. |
| [`analysis/work/valve_rosters.py`](analysis/work/valve_rosters.py) | Lineup changes from Valve's monthly global standings (each row lists the team's five). Jun 1 -> Nov 2 2026. |

## Data

Derived tables behind the numbers on screen.

- [`data/eras.json`](data/eras.json)
- [`data/lineup_timeline.json`](data/lineup_timeline.json)
- [`data/moves_curated.json`](data/moves_curated.json)
- [`data/moves_verdict.json`](data/moves_verdict.json)
- [`data/net_moves.json`](data/net_moves.json)
