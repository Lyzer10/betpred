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

Raw downloads are cached under `engine/data/raw`. Completed seasons never change, so they are committed (force-added past the ignore rule) to spare the daily job thousands of downloads; the in-progress season stays ignored and is refreshed by `src.predict`. When a season ends, add its files with `git add -f`. Processed outputs remain versionable.

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
`reports/stage3_report.md`. First scorer and 1Up probabilities combine the DC
final-score matrix with simulated path behaviour per scoreline, so they always
agree with the DC result and goal markets. Run order after any model change:
`src.backtest` -> `src.calibration` -> `src.goal_timing` (the full timing backtest
takes about 25 minutes; a single matchday takes seconds).

## Stage 4: accumulator tiers

`python -m src.accumulators` builds one slip per tier per betting round
(safe 2.5-3.5 odds / 2-3 legs, medium 5-8 / 3-5, big 10-25 / 4-8; one leg per
match) and backtests them on 2024/25 onwards, writing `reports/stage4_report.md`.
Leg probabilities are a logit blend of the calibrated model and the bookmaker's
implied probability, with the model weight learned on earlier seasons only:
used alone, the model over-promises because the slip search selects the legs
where it disagrees most with the market. Odds for markets without price history
(1Up, first scorer, BTTS, other goal lines) are estimated from bookmaker 1X2 and
O/U 2.5 prices plus a 7% retail margin, so the report's ROI is indicative only.

## Stage 5: live predictions and the app

`python -m src.predict` refreshes the in-progress season, predicts the upcoming
fixtures in https://football-data.co.uk/fixtures.csv, builds the next round's
slips and writes `web/public/data/predictions.json`. Published slips are stored
in `engine/data/live/slip_history.json`, frozen at their first kickoff and
settled automatically. Use `--no-refresh` to skip downloads.

The app (React + Vite + Tailwind, installable on a phone as a PWA):

```powershell
cd web
npm install
npm run dev        # http://localhost:5173
npm run build      # production build in web/dist
```

Screens: **Slips** (three tiers; type your bookmaker's odds to get a value
verdict), **Matches** (every market with our probability vs the bookmaker's),
**My picks** (saved on the device, settled from results), **Record** (backtest
and live slip history).

## Deploying for free

1. Push this repository to a **private** GitHub repository. Past seasons' raw
   data is committed; the current season is ignored and re-downloaded.
2. GitHub Actions (`.github/workflows/daily-predictions.yml`) runs the tests and
   `src.predict` every morning (plus Fri-Sun refreshes) and commits the new
   predictions. Trigger it manually from the Actions tab with "Run workflow".
3. On vercel.com, import the repository with **Root Directory = `web`** (Vite is
   detected automatically). Every predictions commit redeploys the app.
4. On the phone, open the Vercel URL and choose **Add to Home Screen**.
