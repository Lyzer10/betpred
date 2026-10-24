# BetPredz

Football accumulator predictions for the Premier League, La Liga, Serie A, Bundesliga and Ligue 1,
with live Betpawa odds, Safe / Medium / Big slips per day, and money management in TSh.

**Live app:** https://betpredz.vercel.app

> **Working on this project (human or AI)? Read [PROJECT.md](PROJECT.md) first.** It holds the
> owner's rules, how everything works, the current status, open tasks, studies already done and
> lessons learned. Update it with every change.

## Layout
| Path | What |
|---|---|
| `engine/` | Python: data pipeline, models, backtests, daily predictions (`src/predict.py`) |
| `engine/reports/` | Backtest and study reports (Premier League at the top level, other leagues in subfolders) |
| `web/` | React + Vite + Tailwind app (PWA), deployed by Vercel |
| `web/public/data/` | Published predictions and the per-day archive (written by the daily run) |
| `.github/workflows/` | Daily run at 07:00, 13:00, 18:00 Tanzania time |
| `scripts/` | Optional local backup of the daily run |

## Quick start (Windows)
```powershell
cd engine
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q                      # all tests
python -m src.predict --no-refresh       # full daily pipeline on cached data

cd ..\web
npm install
npm run dev                              # http://localhost:5173
npm run build; npx vite preview --port 4173; npm run check:e2e   # browser checks
```

## Research pipeline (per league: `--league EPL|LALIGA|SERIEA|BUNDES|LIGUE1`)
`src.build_dataset` -> `src.backtest` -> `src.calibration` -> `src.goal_timing` -> `src.accumulators`,
then `src.phase1_evaluation` for the league go/no-go report and `src.market_live` to refit the
market-mode calibrators. Raw downloads are cached under `engine/data/raw` (completed EPL seasons
committed; the current season is refreshed by the daily run).

Data sources are free: football-data.co.uk, Understat and Betpawa's public API. See PROJECT.md for
which sources may and may not be used.
