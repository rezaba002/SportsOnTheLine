# Video 10 — Singapore 2026 Major contender analysis

Code and derived data behind the MOUZ, FURIA and Vitality championship
comparison. The published baseline used 100,000 simulations: **23.1%** for
MOUZ, **16.7%** for FURIA and **13.5%** for Vitality.

Run the verification with Python 3.11 or later. No packages are required:

```sh
python analysis/check_forecast.py
```

The checker reproduces headline and playoff-conditional probabilities,
cross-checks the scenario table against the episode's claim table, and
verifies the three contender roster summaries. It reads frozen outputs; it
does not refit ratings or regenerate the simulations.

| File | Contents |
|---|---|
| [`major_probabilities.csv`](data/major_probabilities.csv) | Per-team baseline results and the 60-day recency comparator. `advance_s3` is the chance to make playoffs. |
| [`pressure_sensitivity.csv`](data/pressure_sensitivity.csv) | Baseline, roster-only, and moderate and strong experience sensitivity scenarios. |
| [`forecast_metadata.json`](data/forecast_metadata.json) | Cutoff dates, draw counts and scenario parameters. |
| [`claim_table.json`](data/claim_table.json) | Sourced claims and qualifiers from the final episode. |
| [`contender_experience.csv`](data/contender_experience.csv) | Dated career LAN map and individual Major title counts for the three featured teams. |
| [`production/`](production) | Code-only Remotion production reference. |

The forecast was frozen November 16, 2026, using Valve's November 2
standings and results through November 15. An experience scenario is
an assumption, not a validated pressure effect: the published forecast
retained the results-only baseline. The conditional playoff figures average
over simulated paths, rather than predicting any specific head-to-head.

No video, footage, photos, audio, fonts, caption files or other production
assets are distributed. Repository [code](../../LICENSE) and
[derived-data](../../LICENSE-data) licenses apply.
