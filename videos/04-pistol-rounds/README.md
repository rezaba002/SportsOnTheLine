# Do Pistol Rounds Decide CS2 maps? I Checked Every Major

Video: https://youtu.be/Vjlev_o5zDY

Scripts as I ran them for the video. Paths are absolute to my machine (D:/Youtube/...), and footage, narration audio, logos and photos are not included. Scripts that go online have an **EDIT ME** proxy block at the top.

## Scripts

| File | What it does |
|---|---|
| [`analysis/work/assemble.py`](analysis/work/assemble.py) | Assemble cut v2: sections + highlights in running order, hard cuts, per-clip loudness match, one music bed |
| [`analysis/work/engine.py`](analysis/work/engine.py) | Shared engine for video 04 section clips (copied from video 02): canvas, palette, fonts, word timing, frame piping, captions, audio mix. |
| [`analysis/work/fx.py`](analysis/work/fx.py) | Rapid-edit effects for video 04, built from CS2's own interface (kill feed, hitmarkers, money HUD, round history, |
| [`analysis/work/sections4.py`](analysis/work/sections4.py) | Video 04 sections ("Do pistol rounds decide CS2?"). python sections4.py s00 [s01 ...] -> clips/<id>.mp4 |
| [`analysis/work/sections4b.py`](analysis/work/sections4b.py) | Video 04 sections s01–s05 (acts 1–4 + verdict), cut v2: slower, and every analysis ends on a held conclusion. |
| [`analysis/work/sections4b_v1.py`](analysis/work/sections4b_v1.py) | Video 04 sections s01–s05 (acts 1–4 + verdict). python sections4b.py s01 [s02 ...] |
| [`analysis/work/synth_sfx.py`](analysis/work/synth_sfx.py) | Our own sound effects (synthesised, no licence questions) -> work/sfx/*.wav, 48 kHz stereo. |
| [`analysis/work/thumbnail.py`](analysis/work/thumbnail.py) | Thumbnails for video 04 (1280x720), two versions to choose from: |
| [`analysis/work/timeline.py`](analysis/work/timeline.py) | Multi-part section renderer for video 04: narration blocks and footage clips placed one after another. |
| [`analysis/work/tts_narration.py`](analysis/work/tts_narration.py) | Narration for video 02: Brian (Edge TTS), one file per script paragraph, with word timings. |
| [`analysis/work/tts_v2.py`](analysis/work/tts_v2.py) | Brian narration for script_v2.md: one file per [id] block -> narration_v2/<id>.mp3 + narration.json (same format as v1). |
