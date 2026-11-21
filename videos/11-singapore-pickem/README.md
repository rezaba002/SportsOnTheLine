# Video 11 — Singapore 2026 Major Stage 1 Pick’Em

The baseline searched ticket cleared the five-pick threshold in **31.9%**
of held-out simulations. The eye-test ticket cleared it in **28.8%**.
These are conditional forecasts, not real-world success rates.

## Reproduce the numbers

From this folder, with Python 3.11 or newer:

```sh
python -m pip install -r requirements.txt
python analysis/check_pickem.py
python analysis/check_pickem.py --search
```

The first command after dependency installation checks the four ticket
comparisons, all six sensitivity settings, and the baseline finish table.
`--search` also repeats the original six-start local swap search on the
30,000 search draws. It does not claim a global optimum.

- [`data/stage1_draws.npz`](data/stage1_draws.npz): simulation outputs only;
  no source match records. One array per recency half-life. Arrays contain
  16 columns in the team order in `data/forecast_summary.json`. A cell
  encodes the terminal record: `0=0–3`, `1=1–3`, `2=2–3`, `3=3–2`, `4=3–1`,
  `5=3–0`. The baseline (21 days) contains 100,000 Stage 1 simulations.
- [`data/stage1_probabilities.csv`](data/stage1_probabilities.csv): derived
  outcome probabilities from that baseline, plus advance sensitivity.
- [`data/forecast_summary.json`](data/forecast_summary.json): cutoffs, ticket
  definitions and expected evaluation results. The first 30,000 draws in
  each array are excluded from evaluation. The baseline held-out set has
  70,000 draws; alternate settings have either 20,000 or 70,000.

The snapshot used Valve standings from November 2, 2026 and results through
November 15. The forecast was frozen November 16. The included arrays let
you reproduce the analysis **from frozen simulation outputs**; this package
does not rebuild the upstream ratings or regenerate the Swiss draws from
raw historical matches. The reported 95% Monte Carlo intervals reflect
simulation noise only. The sensitivity range compares the same ticket under
different model settings; it is not a confidence interval.

[`production/`](production) contains a code-only reference for the edit.
Footage, images, fonts, audio, thumbnails, rendered exports and raw source
material are not included. Repository [code](../../LICENSE) and
[derived-data](../../LICENSE-data) licenses apply.
