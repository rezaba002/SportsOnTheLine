# Every CS2 Major So Far: The Must-Watch Recap Before Singapore 2026

Video: https://youtu.be/dr_DOWp8eg8

Scripts as I ran them for the video. Paths are absolute to my machine (D:/Youtube/...), and footage, narration audio, logos and photos are not included. Scripts that go online have an **EDIT ME** proxy block at the top.

## Scripts

| File | What it does |
|---|---|
| [`analysis/research/parse_brackets.py`](analysis/research/parse_brackets.py) | Parse the playoff brackets of the five CS2 Majors (Liquipedia wikitext) into results.json. |
| [`analysis/work/allstars.py`](analysis/work/allstars.py) | Video 02 all-star part (p19–p22): a00 intro, a01 Team 1 (gold), a02 Team 2 (silver), a03 question + Singapore. |
| [`analysis/work/assemble_v2.py`](analysis/work/assemble_v2.py) | Assemble cut v2: sections + highlights in running order, hard cuts, per-clip loudness match, one music bed |
| [`analysis/work/caster_pick.py`](analysis/work/caster_pick.py) | Pick the caster-audio window for each highlight automatically (the user reviews the picks later). |
| [`analysis/work/chapters.py`](analysis/work/chapters.py) | Video 02 Major chapters (p09–p18): c1a/c1b … c5a/c5b. Each Major = a story half (chapter card, underdog path, |
| [`analysis/work/clip_sheet.py`](analysis/work/clip_sheet.py) | Contact sheet of a rendered clip: python clip_sheet.py <path> [n=16] [cols=4] -> <path>_sheet.jpg |
| [`analysis/work/clip_views.py`](analysis/work/clip_views.py) | Twitch metadata (views, duration, date, best height) for every HLTV highlight clip; cached per clip. |
| [`analysis/work/engine.py`](analysis/work/engine.py) | Shared engine for video 02 section clips (copied from video 03): canvas, palette, fonts, word timing, frame piping, captions, audio mix. |
| [`analysis/work/fetch_heatmaps.py`](analysis/work/fetch_heatmaps.py) | Fetch YouTube metadata (title, duration, chapters, "most replayed" heatmap) for every playoff VOD in results.json. |
| [`analysis/work/find_clutches.py`](analysis/work/find_clutches.py) | List every 1-vs-N situation (N >= 2) in a demo, from the kill order of each round. |
| [`analysis/work/find_kills.py`](analysis/work/find_kills.py) | Find kill moments in a broadcast clip by watching the kill feed (top-right) for new entries. |
| [`analysis/work/heat_peaks.py`](analysis/work/heat_peaks.py) | Rank "most replayed" peaks per Major from footage/meta/*.json and tie each to its match and map (via results.json). |
| [`analysis/work/highlight.py`](analysis/work/highlight.py) | Highlight renderer for video 02: one JSON spec -> one finished highlight (1920x1080, 30 fps, H.264 + AAC). |
| [`analysis/work/highlight2.py`](analysis/work/highlight2.py) | Highlight renderer v2 (video 02): rapid kill cuts with HUD-proof graphics. One JSON spec -> one clip. |
| [`analysis/work/multi_sheet.py`](analysis/work/multi_sheet.py) | One row per clip, n frames each: python multi_sheet.py out.jpg n clip1.mp4 clip2.mp4 ... |
| [`analysis/work/name_narration.py`](analysis/work/name_narration.py) | Rebuild a01/a02/a03 narration: Brian's pieces + the casters' own name calls (work/names/<name>.wav). |
| [`analysis/work/outro_ident.py`](analysis/work/outro_ident.py) | Channel signature outro: "This is... Sports On The Line." (Christopher) with sound design, three styles. |
| [`analysis/work/preview.py`](analysis/work/preview.py) | Rough preview cut: every section and highlight in running order, plain cuts, no music bed -> drafts/preview_v0.mp4 |
| [`analysis/work/rank_clips.py`](analysis/work/rank_clips.py) | Rank HLTV highlight clips per Major by Twitch views; Part 1 (observer) + Part 2 (replay) of one play count as one. |
| [`analysis/work/render_all.sh`](analysis/work/render_all.sh) |  |
| [`analysis/work/render_replay.py`](analysis/work/render_replay.py) | 2D tactical replay of one round, drawn from the demo (no broadcast footage). |
| [`analysis/work/sections.py`](analysis/work/sections.py) | Video 02 sections: one function per narration beat, rendered to clips/<sid>.mp4 with the Brian voice and captions. |
| [`analysis/work/sheet.py`](analysis/work/sheet.py) | Contact sheets for picking cut points. python sheet.py <clip> <start> <end> <step> [cols] [crop: x,y,w,h] |
| [`analysis/work/sheet_rows.py`](analysis/work/sheet_rows.py) | One row of 0.1 s frames per window: python sheet_rows.py <clip> "2.9-3.6,4.0-4.7" [crop x,y,w,h] |
| [`analysis/work/synth_sfx.py`](analysis/work/synth_sfx.py) | Our own sound effects (synthesised, no licence questions) -> work/sfx/*.wav, 48 kHz stereo. |
| [`analysis/work/thumbnail.py`](analysis/work/thumbnail.py) | Thumbnails for video 02 (1280x720), two versions to choose from: |
| [`analysis/work/tts_narration.py`](analysis/work/tts_narration.py) | Narration for video 02: Brian (Edge TTS), one file per script paragraph, with word timings. |
| [`analysis/work/tts_v2.py`](analysis/work/tts_v2.py) | Brian narration for script_v2.md: one file per [id] block -> narration_v2/<id>.mp3 + narration.json (same format as v1). |
| [`analysis/work/v2.py`](analysis/work/v2.py) | Video 02, cut v2 (script_v2.md): shorter, chapter = card+story -> final -> [2 highlights] -> MVP slam. |

## Data

Derived tables behind the numbers on screen.

- [`data/majors.json`](data/majors.json)
- [`data/results.json`](data/results.json)
- [`data/entry_stages.json`](data/entry_stages.json)
- [`data/hltv_players_majors.csv`](data/hltv_players_majors.csv)
