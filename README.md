# Premier League prediction app

Stage 1 builds a free, reproducible Premier League data foundation. It downloads match results and odds from football data.co.uk, downloads xG and goal events from Understat, joins both sources, computes leakage safe Elo ratings, and writes a baseline report.

## Setup on Windows

```powershell
cd engine
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

From `engine`:

```powershell
python -m src.fetch_results
python -m src.fetch_understat
python -m src.build_dataset
python -m src.baselines
python -m src.backtest
pytest
```

`python -m src.build_dataset` is also the complete from scratch command. It fetches any missing raw files, builds `data/processed/matches.parquet` and `data/processed/goals.parquet`, adds pre match Elo ratings, prints merge and missing data diagnostics, then creates `reports/baseline_report.md`.

Raw downloads are cached under `engine/data/raw` and ignored by Git. Delete a cached season file if you deliberately want to fetch it again. Processed outputs remain versionable.

The current season is inferred from the date. A season starts in its first calendar year, so `2026` means the 2026/27 season.

## Data notes

Team names are canonicalized through one strict mapping in `src/team_names.py`. A new or unknown name raises an error instead of silently breaking a merge. Odds prefer Pinnacle, then market average, then Bet365. Understat goal events identify the team credited with the goal, so an own goal is assigned to the team that benefits.

No paid service or API key is required.

## Stage 2

`python -m src.backtest` tunes Dixon Coles goals, xG, and blended variants on
2021/22 through 2023/24 only. It then evaluates the selected settings on 2024/25
through the completed part of 2026/27. Predictions are written to
`data/processed/predictions_dc.parquet` and the evaluation is written to
`reports/stage2_report.md`. Opening and closing odds are evaluation fields only
and are never passed into the model.

## Stage 3

`python -m src.calibration` compares seasonal walk forward Platt and isotonic
calibration and writes `data/processed/predictions_calibrated.parquet`.
`python -m src.goal_timing` fits the historical goal time profile and score state
effects, runs 20,000 vectorized simulations per match, and writes
`data/processed/predictions_goal_timing.parquet` plus
`reports/stage3_report.md`.
