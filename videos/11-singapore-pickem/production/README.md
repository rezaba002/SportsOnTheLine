# Code-only production reference

These are the director’s cut source files for the opening, method, probability
scenes, and ticket comparison, plus the local render and sound-mix entry points.
They document how the edit was made; this folder is not a turnkey render.

- `director_art.py`, `director_open.py`, `director_close.py`: Skia artwork and
  frame-based motion, synchronized to narration word cues.
- `director_render.py`: independent 1920×1080, 30 fps scenes via PyAV/x264.
- `director_sound.py`: word-timed sound cues, ducked score, and FFmpeg mastering.
- `coin_poster.py`, `coin_thumbnail.py`: thumbnail composition and supporting
  artwork functions. Valve's CS2 agent and official coin images are not bundled.

The source expects the original production workspace layout, including the
prepared director timeline and analysis dataset, separately supplied audio
and archive imagery, team marks, system fonts, a local CC0 sound library,
and Skia/PyAV/FFmpeg. No such production assets or compiled binaries are
distributed here. `director_inputs.py` supplies the workspace paths and
records how the original narration timing was prepared. The standalone
analysis checker does not depend on any of the production code or assets.
