# Are CS2 timeouts useless? I Checked all 430 timeouts from Cologne Major 2026

Video: https://youtu.be/pUSPR1zwcZc

Scripts as I ran them for the video. Paths are absolute to my machine (D:/Youtube/...), and footage, narration audio, logos and photos are not included. Scripts that go online have an **EDIT ME** proxy block at the top.

## Scripts

| File | What it does |
|---|---|
| [`analysis/work/assemble.py`](analysis/work/assemble.py) | Assemble video 03 from the section clips: whip transitions, one continuous music bed ducked under the voice, |
| [`analysis/work/engine.py`](analysis/work/engine.py) | Shared engine for video 03 section clips: canvas, palette, fonts, word timing, frame piping, captions, audio mix. |
| [`analysis/work/make_sheet.py`](analysis/work/make_sheet.py) | Recording sheet for video 03 (same layout as video 02's): one card per paragraph, emphasis + delivery cues + |
| [`analysis/work/sections.py`](analysis/work/sections.py) | Section clips for video 03. One function per section; render with:  python sections.py s01 [s02 ...] |
| [`analysis/work/thumbnail.py`](analysis/work/thumbnail.py) | Thumbnail for video 03 (1280x720): the frog coach in a headset + 'ARE TIMEOUTS USELESS?' + '430 TIMEOUTS'. |
| [`analysis/work/tts_narration.py`](analysis/work/tts_narration.py) | Narration for video 03 (timing guide until the owner records): Brian (Edge TTS), one file per script paragraph, with word timings. |

## Data

Derived tables behind the numbers on screen.

- [`data/coach_timeouts.csv`](data/coach_timeouts.csv)
- [`data/luck_sim.json`](data/luck_sim.json)
