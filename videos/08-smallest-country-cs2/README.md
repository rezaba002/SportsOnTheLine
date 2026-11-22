# The Smallest Country Dominating CS2

Video: https://youtu.be/lCIl8yoWiUg

Pro players per person: which country produces the most CS2 pros for its population.

Scripts as I ran them for the video. Paths are absolute to my machine (D:/Youtube/...), and footage, narration audio, logos, photos, music and sound effects are not included. Lines marked **EDIT ME** point at tools or files you need to supply yourself.

## Scripts

| File | What it does |
|---|---|
| [`analysis/research/build.py`](analysis/research/build.py) | Builds the comparison tables (data/*.csv) from the raw downloads and prints the headline rankings. |
| [`analysis/research/build_pros.py`](analysis/research/build_pros.py) | Which country produces the most CS pros per person: three tiers, each divided by World Bank 2024 population. |
| [`analysis/research/quotes/vtt2txt.py`](analysis/research/quotes/vtt2txt.py) | Turns interview subtitle files (VTT) into plain text for quote lookup. |
| [`analysis/work/build_map.py`](analysis/work/build_map.py) | Projects Natural Earth 1:50m countries (Europe to Mongolia) into SVG paths for the video08 map scene. |
| [`analysis/work/check_numbers.py`](analysis/work/check_numbers.py) | Checks every number Brian says (script_v1.md) against the research tables. Prints one line per claim: OK / FAIL. |
| [`analysis/edit/settings.py`](analysis/edit/settings.py) | Shared paths and the ffmpeg location for the edit scripts (EDIT ME). |
| [`analysis/edit/build_edit.py`](analysis/edit/build_edit.py) | Editorial cut from approved Andrew takes, real interviews and verified evidence. |
| [`analysis/edit/camera.py`](analysis/edit/camera.py) | Continuous camera points, subpixel resampling and explicit transition handles. |
| [`analysis/edit/make_captions.py`](analysis/edit/make_captions.py) | Exact Andrew word cues in Claude's Bahnschrift/yellow-active-word style. |
| [`analysis/edit/check_timing.py`](analysis/edit/check_timing.py) | Check speech handoffs and actual caption font widths without another encode. |

## Data

Derived tables behind the numbers on screen.

- [`data/ewc2026_hours_watched_by_language.csv`](data/ewc2026_hours_watched_by_language.csv)
- [`data/leetify_global_elites_per_million_2021.csv`](data/leetify_global_elites_per_million_2021.csv)
- [`data/leetify_playerbase_share.csv`](data/leetify_playerbase_share.csv)
- [`data/pros_1_any_prize_money.csv`](data/pros_1_any_prize_money.csv)
- [`data/pros_2_s_a_tier_2026.csv`](data/pros_2_s_a_tier_2026.csv)
- [`data/pros_3_hltv_top20_unique_2013_2025.csv`](data/pros_3_hltv_top20_unique_2013_2025.csv)
- [`data/pros_3b_hltv_top20_appearances_2013_2025.csv`](data/pros_3b_hltv_top20_appearances_2013_2025.csv)
- [`data/pros_by_country_esportsearnings.csv`](data/pros_by_country_esportsearnings.csv)
- [`data/s_a_tier_players_2026.csv`](data/s_a_tier_players_2026.csv)
- [`data/s_a_tier_pros_by_country_bettrails.csv`](data/s_a_tier_pros_by_country_bettrails.csv)
- [`data/steam_survey_language_oct2026.csv`](data/steam_survey_language_oct2026.csv)
- [`data/steam_traffic_by_country.csv`](data/steam_traffic_by_country.csv)

## Production

Remotion source for the edit (code only; it expects assets that are not in this repo).

- [`production/src/video08-codex-v2/Film.tsx`](production/src/video08-codex-v2/Film.tsx)
- [`production/src/video08-codex-v2/duration.ts`](production/src/video08-codex-v2/duration.ts)
- [`production/src/video08-codex-v2/edit.ts`](production/src/video08-codex-v2/edit.ts)
- [`production/src/video08-codex-v2/evidence.ts`](production/src/video08-codex-v2/evidence.ts)
- [`production/src/video08-codex-v2/index.tsx`](production/src/video08-codex-v2/index.tsx)
- [`production/src/video08-codex-v2/map.ts`](production/src/video08-codex-v2/map.ts)
- [`production/src/video08-codex-v2/visuals.tsx`](production/src/video08-codex-v2/visuals.tsx)
