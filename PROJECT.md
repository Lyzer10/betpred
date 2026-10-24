# BetPredz project handbook (read this first)

**Every AI agent (Claude Code, Codex or any other) must read this whole file before doing
anything in this repository, and must update it in the same commit as any change it makes**
(sections 5, 6, 7 and the change log at the end). If this file and the code disagree, stop and
fix the disagreement first.

Last updated: 2026-10-25 (Africa/Dar_es_Salaam), by Codex.

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
halves all stakes) -> `web/public/data/predictions.json`. Every run appends the Betpawa prices of the slip
markets (next two local days) to `engine/data/live/prices/<day>.csv` (`src/prices.py`); price-only
snapshots before kick-offs add the closing price; `clv` in predictions.json = published price / last
price logged within 90 min before kick-off - 1, overall and per league, market and tier.

### App (`web/`, React + Vite + Tailwind PWA)
Tabs: **Bets** (date strip, Safe/Medium/Big slips, "why this bet", Flexi, "I placed this bet",
and expandable past slip results with scores), **Matches** (league groups with flags, badges,
every market with Betpawa odds and verdict), **Money** (balances, staking mode, ledger), and
**Record** (model health, live record, backtest). The old `#history` route opens Bets. Data stays
on the device (localStorage).
Staking (`web/src/lib.ts` `STAKING`): smart = quarter Kelly with tier caps (3/2/1%), or % of balance,
or fixed TSh; never a stake without a 3% edge; **pilot cap: max 3% of balance per slip until 30 of
the user's slips have settled**.

### Deployment
- Repo: GitHub `Lyzer10/betpred` (private), branch `main`.
- GitHub Actions `.github/workflows/daily-predictions.yml`, woken every 30 minutes (06:00-23:30 EAT) by
  an external timer (cron-job.org POSTs the workflow_dispatch API with a fine-grained token limited to
  Actions on this repo), plus GitHub's own schedule at 07:07 / 13:17 / 18:17 EAT as backup (GitHub's
  schedule started 3-4 hours late on 24 Oct 2026, so it cannot time the final run). Each wake-up runs
  `scripts/run_mode.py`, which picks one mode:
  - **final**: from 55 minutes before today's first match (so after line-ups, ~25-55 min before kick-off),
    full run with `--final`: today's slips become final (never replaced or added to, even by later
    runs), then `scripts/notify.py` sends the phone notification (ntfy topic in secret `NTFY_TOPIC`).
  - **full**: 07:00, 13:00, 18:00 EAT runs (tests, `src.predict`, publish); slips are "Preview" until final.
  - **prices**: a match kicks off within 35 minutes: `python -m src.prices` logs Betpawa prices only.
  - **skip**: nothing due (costs ~1 of the 2,000 free private-repo minutes a month).
  Publishing commits predictions, archive and `engine/data/live` (resets rebuilt research files, pulls, pushes).
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
  pilot stake cap, health check ("insufficient data" until ~30 settled matches), glass surfaces,
  and a four destination floating menu with past slip results on Bets.
- Profitability: **not proven**. Backtest ROI used estimated odds (indicative only). Real Betpawa
  prices are archived from 24 Oct 2026 onwards: the live period is the **untouched holdout**;
  never tune any setting on it, only judge.
- Verified out-of-sample: Serie A calibration lifts on away favourites are real (lifted legs:
  bookmaker 57.5%, calibrated 63.7%, actual 66.9%, n=160). La Liga away-win lifts look too high
  (calibrated 72.3% vs actual 62.0%, n=50, not yet significant).
- League x market gates (task 1, run 2026-10-25, `engine/reports/market_gates.md`, rules as amended
  2026-10-25): 49 PASS, 6 FAIL, 5 INSUFFICIENT (over 0.5, too few priced legs). FAIL, removed from
  slips, all over-confident: EPL over 2.5 (C4: legs we rated >3 points above the bookmaker won 2.76 sd
  less than we said); Serie A home 1Up (said 56.8%, won 53.3%); Bundesliga home 1Up (61.0% vs 56.9%)
  and home-or-draw (67.6% vs 64.2%); Ligue 1 away 1Up (51.7% vs 46.4%, low in all three seasons) and
  away-or-draw (56.5% vs 53.1%, low in all three). Serie A and Bundesliga home 1Up failures come mostly
  from one season and 2026/27 so far runs the other way (small n): the monthly re-check (same rules,
  more data) is how a pair comes back, never a manual override.
- Tier diversity study (task 5, `engine/reports/slip_diversity.md`): independent tiers (A) KEPT.
  No-shared-matches (B) passed the pre-registered rule, but the rule's metric was biased (see task 5):
  per TSh staked B lost more (-11.6% vs -8.4%), and all-loss days fell by one day in 402.

## 6. Open tasks (in priority order)
Claude (hard, affects predictions):
1. **Per league x market gates** (DONE 2026-10-25, `python -m src.market_gates`; rerun monthly). PRE-REGISTERED RULES, committed 2026-10-24 before
   any result was computed; do not change them after seeing results:
   - Data: test seasons (2024/25 onwards), each league's legs table, the exact probability the slips
     use (EPL: blended `probability`; market leagues: walk-forward `market_probability`), the 12 slip
     markets. Fewer than 300 legs = INSUFFICIENT (kept in slips, flagged).
   - C1 slope: logistic regression of outcome on logit(p); 95% CI upper bound must be >= 0.8.
   - C2 level: mean(outcome) - mean(p); 95% bootstrap CI (1,000 resamples by matchday) upper bound >= 0.
   - C3 bins: 10 equal-count bins, every z >= -3.
   - AMENDMENT 2026-10-25 (after the first run; direction only, thresholds unchanged): C1-C3 were
     two-sided, so La Liga over 1.5 (said 71.4%, won 74.9%) and EPL under 3.5 (said 64.7%, won 68.3%)
     were removed for being too CAUTIOUS. A market that wins more than stated makes slips safer than
     shown, so every check now guards against over-confidence only, like C4 already did. This can only
     restore pairs, never remove more; it was a flaw in the rule's design, not tuning to results.
   - C4 winner's curse: legs with p - bookmaker p > 0.03 (if >= 50 such legs): actual rate must not be
     significantly below mean p (one-sided z >= -2).
   - Reported, not gating: log loss vs bookmaker with bootstrap CI (non-inferiority vs superiority).
   - A league x market failing any of C1-C4 is removed from slip legs (still shown on match pages);
     the league stays live. Re-checked monthly.
2. **Closing-line value tracking** (DONE 2026-10-25: price log, CLV report, Record page "Are we
   beating Betpawa's prices?"; judge after >= 200 final legs). Still to test: whether fresh Betpawa
   prices should feed the probabilities (Bet365 closing beat the early average by 0.0020 log loss;
   Betpawa must show the same on our logged data before any change).
3. **Per-league and per-market monitoring** (DONE 2026-10-25, `health.pair_monitor`): every settled
   published prediction per league x slip market, z = (wins - sum p)/sqrt(sum p(1-p)) from 30
   predictions, one-sided; z < -3 pauses the pair (kept out of slips, `engine/data/live/paused_pairs.json`)
   until z >= -2; -3..-2 = watch. Slip legs reported separately (shown only). Record page lists them.
4. **EPL model weight** (DONE 2026-10-25, `python -m src.weight_study`: KEEP V, the live 0.25). PRE-REGISTERED RULES, committed 2026-10-25 before any result:
   - Procedures: V (current live) fits the weight with `fit_model_weight` on earlier TEST-era legs only
     (2024/25 onwards); A fits it on validation legs (2021/22-2023/24, `build_validation_leg_table`)
     plus earlier test-era legs. Both walk-forward: the weight for season S uses only seasons before S.
   - Evaluation: every EPL leg of the 12 slip markets in 2025/26 and 2026/27 (the seasons where V has
     history), not only legs chosen for slips, so no procedure can win by betting less. Metric: mean
     log loss; paired difference V - A per leg; 95% CI by bootstrap of whole days (2,000, seed 20261025).
   - Decision: switch the live weight to procedure A only if the CI of V - A is entirely above 0
     (A clearly more accurate). Otherwise keep V. Reported, not deciding: the weights each procedure
     picks, and the task-1 gates (C1-C4) for each procedure on the same legs.
   - Result (4,919 legs, 137 days): log loss V 0.61285, A 0.61252; V - A +0.00033 (95% CI -0.00166 to
     +0.00231): no clear difference, so V is kept. Weights V 0.35 (2025/26), 0.20 (2026/27); A 0.05, 0.05.
   - Found while checking: the stored EPL legs `probability` equals V, but rebuilding the legs table now
     fills it with A (`build_leg_table` passes validation legs). `market_gates.gate_column` therefore
     recomputes the live V blend, so a rebuild cannot make the gates judge numbers the app does not use
     (gate results unchanged today).
5. **Tier diversification** (DONE 2026-10-25, `python -m src.diversity_study`; independent tiers KEPT,
   see the review after the result).
   PRE-REGISTERED RULES, committed before any result was computed; do not change them after seeing results:
   - Data: test seasons 2024/25 onwards. Combine all five leagues' `paths(code).accumulator_legs`
     tables because the live app pools all leagues. Use `probability` for EPL and
     `market_probability` for La Liga, Serie A, Bundesliga and Ligue 1. Keep only `SLIP_MARKETS`,
     exclude league x market pairs marked FAIL in `engine/data/processed/market_gates.json`, use the
     legs' `odds` column, identify matches by league plus `match_id`, and group days by the `date`
     column's calendar day exactly as `backtest_slips` does.
   - Variant A (current): choose each tier independently with `best_slip`.
   - Variant B (no shared matches): choose Safe, remove its matches, choose Medium, remove its
     matches, then choose Big.
   - Variant C (at most one shared match): use the same tier order, but a later tier may reuse at
     most one match already used by an earlier tier. Implement this exactly by trying every allowed
     single reuse and keeping the best, not approximately.
   - Primary metric: bankroll growth. Each day stake a fixed fraction of current bankroll on every
     offered tier: Safe 3%, Medium 2%, Big 1%. Daily growth is
     `log(1 + sum(stake_i * (won_i * odds_i - 1)))`. Report mean daily log growth for each variant,
     and B-A and C-A differences with 95% bootstrap CIs from 2,000 whole-day resamples using seed
     20261025.
   - Secondary metrics, reported but not deciding: share of days where every offered slip lost;
     per-tier win rate with predicted versus actual and Wilson CIs; maximum simulated-bankroll
     drawdown; and number of days each tier was offered.
   - Decision: adopt B or C, whichever has the higher mean daily log growth, only if the CI of its
     difference versus A includes zero or is above zero, and its every-slip-lost share is below A's.
     If both pass, take the higher log growth. If neither passes, keep A.
   - Result: A mean daily log growth -0.00599 and 54.0% all-loss days; B -0.00580, difference
     +0.00019 (95% CI -0.00383 to +0.00442), and 53.7% all-loss days; C -0.00506, difference
     +0.00093 (95% CI -0.00240 to +0.00401), and 54.0% all-loss days. B passed both adoption
     conditions. C failed the lower-all-loss condition. Safe / Medium / Big actual win rates were
     A 35.7% / 27.2% / 10.2%, B 35.7% / 25.9% / 8.0%, C 35.7% / 26.2% / 11.2%.
   - REVIEW (Claude, 2026-10-25), why B was NOT adopted although it passed: every backtest slip loses
     on average (estimated odds include the margin), so a variant that offers fewer slips "grows" the
     bankroll just by betting less. B offers 220 fewer Medium/Big slips. Measured without that bias,
     B is worse: ROI per unit staked A -8.4%, B -11.6%, C -8.7%; on the 207 days where A and B offer
     the same tiers, B-A daily log growth -0.0013 (95% CI -0.0075 to +0.0049); the 220 slips B drops
     were well calibrated (won 19.5%, predicted 19.3%); all-loss days A 198, B 197 of 402. The flaw
     was in the rule (Claude's design), not in Codex's work. Shared matches do not cause the all-loss
     days: about half of days lose every slip in all variants because each slip's chance is low.
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
| EPL weight from all seasons (A) vs test-era only (V, live) | log loss difference +0.00033, 95% CI -0.00166 to +0.00231 | V kept (`src/weight_study.py`) |
| No shared matches across Safe/Medium/Big | growth gain only from betting less; ROI per stake worse (-11.6% vs -8.4%); all-loss days 197 vs 198 of 402 | rejected (`src/diversity_study.py`) |

## 8. Lessons and pitfalls (read before changing things)
- When comparing strategies that bet different amounts, compare per unit staked or on matched days:
  with negative-EV backtest odds, the variant that bets least always "grows" most (2026-10-25).
- Settlement must not wait for football-data.co.uk (results lag days); Understat is same-night.
- 24 Oct 2026: one result (Chelsea 0-2 Tottenham) lost all three slips: the same match was in every
  tier. Evidence for open task 5 (tier diversification).
- GitHub's scheduled runs can start hours late: never rely on them for timing (use the external timer).
- Closing odds beat early odds (2019/20-2025/26, 12,457 matches, five leagues: 1X2 log loss 0.9729 ->
  0.9705, O/U 2.5 0.6708 -> 0.6681, both 95% CIs above zero). Our consensus odds (fixtures.csv) are
  early odds; only Betpawa prices are fresh at run time.
- **Winner's curse**: the slip search picks legs where our probability most exceeds the price, so
  any over-confidence gets exploited. Always check calibration of the *selected* legs.
- Safety gates must be one-sided: being too cautious is not a reason to drop a market (2026-10-25
  mistake: La Liga over 1.5 and EPL under 3.5 were wrongly removed for winning more than stated).
- Calibrations need enough data (Ligue 1 over 0.5: 36 legs gave a 100% probability).
- Bookmaker average odds in `fixtures.csv` can be stale vs live Betpawa (team news): price warning.
- CI runs on Linux with the live raw cache: tests must not depend on the in-progress season.
- In Git Bash heredocs and `sed`, backslashes get stripped: edit regexes with the editor.
- Windows working copies use CRLF; `*.sh` is forced to LF by `.gitattributes`.
- The workflow's push trigger only fires when the workflow file changes; otherwise use
  "Run workflow" (or the API).
- Leftover folder `Desktop\FOOTBALL-main` is an old temporary worktree, safe to delete.

## Change log
- 2026-10-25: EPL model weight study (pre-registered): live weighting kept; gates now recompute the live
  EPL blend (`gate_column`) so rebuilt legs tables cannot change what they judge.
- 2026-10-25: notifications from the app itself (Web Push): Money -> Notifications subscribes the
  phone and shows a code; the code goes into secret PUSH_SUBSCRIPTION; the final run signs with secret
  VAPID_PRIVATE_KEY (public key in `web/src/push.ts`, handler `web/public/push-sw.js`). ntfy kept as
  an optional second channel.
- 2026-10-25: announced line-ups from ESPN's public data (`src/lineups.py`, every non-skip run,
  `web/public/data/lineups.json`), shown on match pages; display only, not a model input until a study
  shows a gain over the odds. ESPN team names added to `team_names.py` (all five leagues map).
- 2026-10-25: per league x bet type monitoring with automatic pause (`health.pair_monitor`), slip-leg
  monitor, realised slip results; Record page: price tracking, bet-type checks, real results. Past-day
  slips use #001339 (owner's choice). Tests added.
- 2026-10-25: colours from the logo (navy #000f30, electric blue #0dd9fe, gold #f6c956), real-black
  dark mode without purple; past slips on logo-blue glass; Money placed bets as month summary + day
  strip + compact table, deposits/withdrawals in their own collapsed section.
- 2026-10-25: pre-registered tier diversity study (`src/diversity_study.py`, tests); its rule picked
  no-shared-matches, but review showed the metric rewarded betting less, so live tiers stay independent.
- 2026-10-25: glass surfaces and floating four destination menu; History removed and past slip
  statuses, scores and Flexi results moved to expandable cards on Bets.
- 2026-10-25: locked (in-play) slips are published complete, incl. Flexi, so past days can show
  whether Flexi paid.
- 2026-10-25: slips settle the same night from Understat (`build_dataset.understat_results`, settlement
  only, never training data); football-data rows replace them when they arrive. Check: scores agree on
  21,932 of 21,934 matches 2014/15-2026/27 (2 later disciplinary changes), EPL 2026/27 scores and 1Up
  outcomes 70/70. Football-data lagged days (25 Oct: EPL results only to 19 Oct).
- 2026-10-25: run modes (final / full / prices / skip) with an external 30-minute timer; final slips
  before the first match (locked, phone notification via ntfy); Betpawa price log and CLV report
  (`src/prices.py`); Bets page shows Preview / Final. Tests: test_schedule, test_prices, final history.
- 2026-10-25: accumulator legs now show the selected team's badge, or both badges for match-wide markets.
- 2026-10-25: gates made one-sided (over-confidence only): La Liga over 1.5 and EPL under 3.5 back in
  slips; 6 pairs remain excluded. Tests in `engine/tests/test_market_gates.py`.
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
