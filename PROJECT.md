# BetPredz project handbook (read this first)

**Every AI agent (Claude Code, Codex or any other) must read this whole file before doing
anything in this repository, and must update it in the same commit as any change it makes**
(sections 5, 6, 7 and the change log at the end). If this file and the code disagree, stop and
fix the disagreement first.

Last updated: 2026-10-24 (Africa/Dar_es_Salaam), by Claude Code.

---

## 1. The owner's rules (non-negotiable)

1. **Accuracy first.** The goal is the most accurate probabilities and slips possible.
2. **Consistency.** Same method, same checks, every league, every day.
3. **Decisions are supported by data, never by feelings.** A change (new factor, new model, new
   setting) goes live only if it beats the current method on data it was never tuned on
   (champion vs challenger). Report the evidence with uncertainty (CIs, z-scores, sample sizes).
4. **No mistakes.** Verify before claiming. Run the tests, look at real outputs, check
   screenshots, reproduce CI failures. Never fake a passing check (e.g. averaging a failing value
   until it passes). If a check fails, say so and fix the cause.
5. **Be honest about uncertainty.** Profitability is NOT yet proven (see section 6). Never promise
   wins. A Safe slip at odds 2.5 wins roughly 40% of the time; that is maths, not a model flaw.
6. **Don't change the live strategy for an idea that isn't proven.** Test it, report it, and leave
   it out if it doesn't beat the current method (the owner explicitly asked this).
7. **Respect data sources.** Only use sources whose robots.txt/terms allow it. Never bypass bot
   protection (SportyBet, Sofascore, PredictZ and scores24 feeds are off-limits; Betpawa's
   public API is allowed by its robots.txt).
8. **Keep this file current** (top of this file).

## 2. Who does what

- **Owner** (Tanzania, bets in TSh on Betpawa and SportyBet): decides goals and priorities.
- **Claude Code**: lead data analyst and engineer. Does the hard work: modelling, statistics,
  evaluation, anything that can change predictions. Reviews and merges Codex's work.
- **Codex**: simple, well-specified tasks from prompts written by Claude (e.g. badges, docs).
  Works on a separate branch, never pushes to `main`; Claude reviews before merging.

## 3. What the owner wants (product requirements)

- **Accumulators only** (no singles). Tiers by total odds: **Safe 2.5-3.5 (2-4 legs)**,
  **Medium 3.5-8 (3-6 legs)**, **Big 8-12 (4-8 legs)**. One leg per match.
- **Markets, in priority order: 1Up** (team goes 1 goal ahead at any point), **over/under goals**,
  **team to win, double chance**. (BTTS, first scorer, draw exist in the model but are not slip legs.)
- Each day (Tanzania time, EAT) has its own slips, built from **all live leagues together**,
  choosing the most likely combination in each tier's odds range.
- **Betpawa** for Safe/Medium, **SportyBet** (Flexi: win if at least k of n legs win) for Big.
- **Money management in TSh**: balances per bookmaker, "I placed this bet", deposits/withdrawals
  separate from profit, automatic settlement, stake recommendation.
- Calendar strip of days (from 24 Oct 2026 onwards) to look back at any day.
- "Why this bet" explanation when tapping a pick. Real club badges. Light/dark switch.
  BETPREDZ branding with the owner's logo. **No app lock / PIN** (owner removed it).
- Future: Champions League (needs a free results source), more leagues.

## 4. How the system works

### Data (all free)
| Source | What | Notes |
|---|---|---|
| football-data.co.uk | results, shots, corners, odds (opening/closing/average), upcoming `fixtures.csv` | per league: E0, SP1, I1, D1, F1 |
| Understat (understatapi) | xG, goal minutes (first scorer / led-at-any-point for 1Up), rosters | polite 1-2 s between requests |
| Betpawa Tanzania public API | live odds for all modelled markets incl. 1Up | `engine/src/betpawa.py`, identified requests, 1 s apart |

Raw downloads are cached in `engine/data/raw/` (completed EPL seasons committed; current season
refreshed each run).

### Two prediction methods, chosen per league by out-of-sample accuracy
1. **Blended (Premier League)**: Dixon-Coles goal model fitted on goals+xG (blend w=0.3, time decay
   xi=0.005, goal level rescaled to actual goals), Platt calibration per market, minute-by-minute
   goal-timing simulation for 1Up / first scorer (reweighted onto the DC score matrix), then a
   logit blend with the bookmaker's de-margined probability (model weight learned on earlier legs;
   currently 0.25 live).
2. **Market mode (La Liga, Serie A, Bundesliga, Ligue 1)**: bookmaker consensus (average odds,
   margin removed, scoreline matrix implied) calibrated per market with logistic (Platt)
   calibration chosen on 2021/22-2023/24 and fitted on validation+test seasons
   (`engine/src/market_live.py`, saved in `data/processed/<LEAGUE>/market_calibrators.json`).
   A calibrator is used only with >=300 legs, >=30 of each outcome and a positive slope.

Evidence for the choice (test seasons 2024/25-2026/27, lower log loss = better):
| League | Blended 1X2 log loss / Safe won | Market 1X2 log loss / Safe won | Live |
|---|---|---|---|
| Premier League | **0.9927 / 34.9%** | 0.9956 / 33.1% | Blended |
| La Liga | 0.9540 / 33.5% | **0.9534 / 40.4%** | Market |
| Serie A | 0.9637 / 36.2% | **0.9596 / 37.6%** | Market |
| Bundesliga | 0.9812 / 32.7% | **0.9776 / 35.4%** | Market |
| Ligue 1 | 0.9737 / 34.0% | **0.9700 / 35.3%** | Market |

### Daily pipeline (`engine/src/predict.py`)
Refresh data -> EPL blended predictions -> each market-mode league (current season only, a failing
league is skipped, not fatal) -> Betpawa odds for every league -> legs per market with value edge and
stale-price warning (Betpawa > market average by 8%: halve stake) -> drop league x market pairs that
FAILED the gates (`data/processed/market_gates.json`, `predict.failed_gates`) -> per-day Safe/Medium/Big slips
(exact DP search, `accumulators.best_slip`) with Flexi chances -> slip history frozen at first
kickoff -> per-day archive `web/public/data/archive/<day>.json` settled from results -> live record
and **health check** (`engine/src/health.py`: accuracy vs bookmaker, calibration, slips; "warning"
halves all stakes) -> `web/public/data/predictions.json`.

### App (`web/`, React + Vite + Tailwind PWA)
Tabs: **Bets** (date strip, Safe/Medium/Big slips, "why this bet", Flexi, "I placed this bet"),
**Matches** (league groups with flags, badges, every market with Betpawa odds and verdict),
**History** (each day's predictions vs results), **Money** (balances, staking mode, ledger),
**Record** (model health, live record, backtest). Data stays on the device (localStorage).
Staking (`web/src/lib.ts` `STAKING`): smart = quarter Kelly with tier caps (3/2/1%), or % of balance,
or fixed TSh; never a stake without a 3% edge; **pilot cap: max 3% of balance per slip until 30 of
the user's slips have settled**.

### Deployment
- Repo: GitHub `Lyzer10/betpred` (private), branch `main`.
- GitHub Actions `.github/workflows/daily-predictions.yml`: 07:00, 13:00, 18:00 EAT (04/10/15 UTC),
  runs tests then `src.predict`, commits predictions (resets rebuilt research files, pulls, pushes).
  Also runs on workflow-file changes and via "Run workflow".
- Vercel serves `web/` at **https://betpredz.vercel.app**; every push redeploys.
- Backup: `scripts/daily.sh` + `scripts/install_schedule.ps1` (Windows Task Scheduler), not installed.

### How to run locally
```
cd engine; .venv\Scripts\python.exe -m pytest -q          # 79+ tests
.venv\Scripts\python.exe -m src.predict --no-refresh       # full pipeline on cached data
cd ..\web; npm run dev                                     # http://localhost:5173
npm run build; npx vite preview --port 4173; npm run check:e2e   # browser checks, phone width
```

## 5. Current status (2026-10-25)
- Live: five leagues, Betpawa odds for all, slips across leagues, badges for all clubs,
  pilot stake cap, health check ("insufficient data" until ~30 settled matches).
- Profitability: **not proven**. Backtest ROI used estimated odds (indicative only). Real Betpawa
  prices are archived from 24 Oct 2026 onwards: the live period is the **untouched holdout**;
  never tune any setting on it, only judge.
- Verified out-of-sample: Serie A calibration lifts on away favourites are real (lifted legs:
  bookmaker 57.5%, calibrated 63.7%, actual 66.9%, n=160). La Liga away-win lifts look too high
  (calibrated 72.3% vs actual 62.0%, n=50, not yet significant).
- League x market gates (task 1, run 2026-10-25, `engine/reports/market_gates.md`): 47 PASS,
  8 FAIL, 5 INSUFFICIENT (over 0.5, too few priced legs). FAIL, removed from slips: EPL over 2.5
  (C4 winner's curse) and under 3.5 (C2, C3); La Liga over 1.5 (C2, under-confident); Serie A home
  1Up; Bundesliga home 1Up and home-or-draw; Ligue 1 away 1Up and away-or-draw (all C2: won 3.4 to
  5.2 points less often than predicted). Note: 55 pairs x 4 checks means a few FAILs can be chance;
  the monthly re-check (same rules, more data) is how a pair comes back, never a manual override.

## 6. Open tasks (in priority order)
Claude (hard, affects predictions):
1. **Per league x market gates** (DONE 2026-10-25, `python -m src.market_gates`; rerun monthly). PRE-REGISTERED RULES, committed 2026-10-24 before
   any result was computed; do not change them after seeing results:
   - Data: test seasons (2024/25 onwards), each league's legs table, the exact probability the slips
     use (EPL: blended `probability`; market leagues: walk-forward `market_probability`), the 12 slip
     markets. Fewer than 300 legs = INSUFFICIENT (kept in slips, flagged).
   - C1 slope: logistic regression of outcome on logit(p); its 95% CI must overlap [0.8, 1.2].
   - C2 level: mean(outcome) - mean(p); 95% bootstrap CI (1,000 resamples by matchday) must include 0.
   - C3 bins: 10 equal-count bins, every |z| <= 3.
   - C4 winner's curse: legs with p - bookmaker p > 0.03 (if >= 50 such legs): actual rate must not be
     significantly below mean p (one-sided z >= -2).
   - Reported, not gating: log loss vs bookmaker with bootstrap CI (non-inferiority vs superiority).
   - A league x market failing any of C1-C4 is removed from slip legs (still shown on match pages);
     the league stays live. Re-checked monthly.
2. **Closing-line value tracking**: compare each published leg's Betpawa odds with the last
   pre-kickoff snapshot; report CLV and realised ROI per league/market/tier.
3. **Per-league and per-market monitoring** in the health check and Record page (1Up first).
4. **EPL model weight**: live 0.25 was learned on test legs only; learned on all 5 seasons it is
   ~0.05. Test 0.05 vs 0.25 on slip outcomes under the task-1 rules; change only if it wins.
5. **Tier diversification** (same leg in several slips correlates them): quantify the trade-off.
6. Champions League (needs a free results source), monthly automatic re-check job.
Codex (simple): README upkeep, UI polish tasks given as prompts.

## 7. Studies already done (do not redo without a new reason)
| Idea | Result | Decision |
|---|---|---|
| League table, derbies, team home strength, rest days | none lowered log loss on unseen seasons | rejected |
| Missing players (Understat lineups; upper bound of injury news) | no improvement; team news already in prices | rejected |
| Shots+corners "pressure" (Wheatcroft 2020, LSE paper owner sent) | no reliable gain for over/under or 1Up; paper loses at average odds | rejected (`src/pressure_study.py`, `src/pressure_1up_study.py`) |
| Per-market model weights (EPL) | worse than one global weight (0.60164 vs 0.60147) | rejected (`src/market_weight_study.py`) |
| Blended model for La Liga/Serie A/Bundesliga/Ligue 1 | less accurate than market mode | market mode used |

## 8. Lessons and pitfalls (read before changing things)
- **Winner's curse**: the slip search picks legs where our probability most exceeds the price, so
  any over-confidence gets exploited. Always check calibration of the *selected* legs.
- Calibrations need enough data (Ligue 1 over 0.5: 36 legs gave a 100% probability).
- Bookmaker average odds in `fixtures.csv` can be stale vs live Betpawa (team news): price warning.
- CI runs on Linux with the live raw cache: tests must not depend on the in-progress season.
- In Git Bash heredocs and `sed`, backslashes get stripped: edit regexes with the editor.
- Windows working copies use CRLF; `*.sh` is forced to LF by `.gitattributes`.
- The workflow's push trigger only fires when the workflow file changes; otherwise use
  "Run workflow" (or the API).
- Leftover folder `Desktop\FOOTBALL-main` is an old temporary worktree, safe to delete.

## Change log
- 2026-10-25: pre-registered league x market gates run (`engine/src/market_gates.py`); the 8 FAIL
  pairs are excluded from slip legs (`predict.failed_gates`, `build_slips(blocked=...)`), still shown
  on match pages. Tests added.
- 2026-10-25: match lists and details now show current table position and last-five form for display only.
- 2026-10-25: GitHub Actions now use the latest Node 24 action majors for checkout, Python setup and caching.
- 2026-10-24: fixtures now carry `context` (current-season table position, played, points, goal
  difference, last-5 form per team) for display only; the table is not a model input (rejected study).
- 2026-10-23..24: data pipeline, Dixon-Coles + backtest, calibration + goal timing, accumulators,
  live pipeline, React app, GitHub Actions + Vercel, Betpawa odds, per-day bets, money ledger,
  health check, factor/injury studies, five leagues (EPL blended, others market mode), badges,
  BetPredz logo, staking modes, "why this bet", pilot stake cap, this handbook.
