# BetPredz project handbook (read this first)

**Every AI agent (Claude Code, Codex or any other) must read this whole file before doing
anything in this repository, and must update it in the same commit as any change it makes**
(sections 5, 6, 7 and the change log at the end). If this file and the code disagree, stop and
fix the disagreement first.

Last updated: 2026-11-07 (Africa/Dar_es_Salaam), by Gemini.

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
- **Live slip markets, in priority order: over goals, double chance, 1Up** (team goes 1 goal ahead
  at any point), then **team to win**. Under goals and BTTS remain in the model and match-page
  probability lists but are not live slip legs or headline best picks; first scorer and draw also
  remain model outputs rather than slip legs.
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
| ESPN public scoreboards | fallback settlement of completed published matches | exact league, UTC day and canonical teams; goal sequence must reconcile before timing markets settle; never training data |
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
Tabs: **Bets** (shared 15-day date strip, Safe/Medium/Big slips, "why this bet", Flexi, "I placed this bet",
and expandable past slip results with scores), **Matches** (league groups, one best-pick panel per match,
league pages with fixtures/table/news, and tabbed Insights/Line-ups/H2H/Stats/Form match pages), **Money** (balances, staking mode, ledger), and
**Record** (model health, live record, backtest). The old `#history` route opens Bets. Data stays
on the device (localStorage).
Staking (`web/src/lib.ts` `STAKING`): smart = quarter Kelly with tier caps (3/2/1%), or % of balance,
or fixed TSh; never a stake without a 3% edge; **pilot cap: max 3% of balance per slip until 30 of
the user's slips have settled**.

### Deployment
- Repo: GitHub `Lyzer10/betpred` (public; the owner changes visibility manually), branch `main`.
  Standard GitHub-hosted runners have unlimited Actions minutes for public repositories. Repository
  visibility does not expose Actions secrets: notification and external-timer credentials remain in
  GitHub Secrets and are passed only to the steps that need them.
- GitHub Actions `.github/workflows/daily-predictions.yml`, woken every 15 minutes (06:00-23:45 EAT; every 30 minutes until 2026-10-29) by
  an external timer (cron-job.org POSTs the workflow_dispatch API with a fine-grained token limited to
  Actions on this repo), plus GitHub's own schedule at 07:07 / 13:17 / 18:17 EAT as backup (GitHub's
  schedule started 3-4 hours late on 24 Oct 2026, so it cannot time the final run). Each wake-up runs
  `scripts/run_mode.py`, which picks one mode:
  - **final**: from 55 minutes before today's first match (with the 15-minute timer the run starts ~40-55 min before kick-off, around line-up time),
    full run with `--final`: today's slips become final (never replaced or added to, even by later
    runs), then `scripts/notify.py` sends the phone notification (ntfy topic in secret `NTFY_TOPIC`).
  - **full**: 07:00, 13:00, 18:00 EAT runs (tests, `src.predict`, publish); slips are "Preview" until final.
    Also when fixtures.csv shows new upcoming matches with odds not yet published (max ~hourly).
  - **prices**: a match kicks off within 35 minutes: `python -m src.prices` logs Betpawa prices only.
  - **skip**: nothing due (costs ~1 of the 2,000 free private-repo minutes a month).
  Publishing commits predictions, archive and `engine/data/live` (resets rebuilt research files, pulls, pushes).
  Full, final and price runs also execute `python -m src.settle_results`: fill missing archive scores,
  slip outcomes and the app's saved-bet results from ESPN, independently of Understat. Verified
  outcomes survive later source outages. This step never fits models or selects/reprices slips.
- Vercel serves `web/` at **https://betpredz.vercel.app**; every push redeploys.
- Backup: `scripts/daily.sh` + `scripts/install_schedule.ps1` (Windows Task Scheduler). The task
  "PL Predictor daily update" WAS installed and ran in parallel with GitHub; on 25 Oct 2026 its 18:00 run
  collided with GitHub's data (stuck merge in the working folder). It is now DISABLED (not deleted;
  `schtasks /change /tn "PL Predictor daily update" /enable` restores it). GitHub + the external timer
  replace it; never run both.

### How to run locally
```
cd engine; .venv\Scripts\python.exe -m pytest -q          # 79+ tests
.venv\Scripts\python.exe -m src.predict --no-refresh       # full pipeline on cached data
.venv\Scripts\python.exe -m src.settle_results             # results only, no prediction rebuild
cd ..\web; npm ci; npm run dev                             # install exactly from the lockfile; http://localhost:5173
npm run build; npx vite preview --port 4173; npm run check:e2e   # browser checks, phone width
```

## 5. Current status (2026-11-07)
- Tasks 18-22 reviewed and merged (Claude, 2026-11-07): 30 research markets logged from Betpawa;
  timing markets (first goal, 1-10 minutes) and team-half markets mostly calibrated in both test
  periods; simulated Betpawa prices show no market with reliable profit. Next: collect >= 300 settled
  real-priced legs per market, then judge with real prices.
- Task 18 Betpawa market catalogue and research price logging (`src/betpawa_catalogue.py`,
  `reports/betpawa_market_catalogue.md`): catalogued all 128 `marketType` IDs across 27 real upcoming
  events (3 per league across all 9 live leagues). Only one time-interval market exists (`28000173`
  00:01-09:59; no 15-minute market exists). Added 10 new keys to `RESEARCH_MARKETS` (`first_goal_home`,
  `first_goal_away`, `interval_10_home`, `interval_10_away`, `home_score_both_halves`,
  `away_score_both_halves`, `home_win_both_halves`, `away_win_both_halves`, `home_fh_over_0.5`,
  `away_fh_over_0.5`, `home_sh_over_0.5`, `away_sh_over_0.5`) with real trimmed fixture and isolation
  tests. No live change.
- Tasks 15-17 reviewed by Claude (reproduced exactly; task 17 calibration aligned to the
  pre-registration, decisions unchanged). Next step for all candidate markets: collect >= 300 settled
  Betpawa-priced legs per market (logging is live since 21e66d1), then judge them with real prices.
  Watch: Betpawa 2UP looks priced near zero margin vs ~4% on 1X2 (29 matches, 2026-11-07).
- Task 17 Double Chance 1UP and 1X2 2UP backtest (`reports/up_markets_study.md`, five main leagues):
  **24 PASS / 1 FAIL** across 25 league x market pairs on 2024/25+ (`EPL` 4/5, `LALIGA` 5/5, `SERIEA`
  5/5, `BUNDES` 5/5, `LIGUE1` 5/5). Only `EPL home_2up` failed (C2 level -0.0343, CI [-0.0657, -0.0041])
  and stays out; the 24 PASS pairs are **eligible pending real Betpawa prices** (>= 300 settled priced
  legs and one-sided level check passing). No live change.
- Task 16 goals by half and win either half backtest (`reports/half_markets_study.md`, all nine live
  leagues): **49 PASS / 5 FAIL** across 54 league x market pairs on 2024/25+ (`EPL` 4/6, `LALIGA` 6/6,
  `SERIEA` 6/6, `BUNDES` 6/6, `LIGUE1` 6/6, `EREDIV` 5/6, `JUPILER` 5/6, `PRIMEIRA` 5/6, `SUPERLIG`
  6/6). The 49 PASS pairs are **eligible pending real Betpawa prices** (>= 300 settled priced legs and
  one-sided level check passing); the 5 FAIL pairs (`EPL fh_over_1.5`, `EPL sh_over_0.5`, `EREDIV sh_over_1.5`,
  `JUPILER sh_over_0.5`, `PRIMEIRA fh_over_0.5`) stay out. No live change.
- Task 15 first look at team goals and Draw No Bet with real Betpawa prices (`reports/team_goals_dnb_live_study.md`):
  97 settled archived matches (550 scored legs; 13 drawn matches refunded on DNB) have logged
  pre-kickoff Betpawa prices. All 6 markets are **INSUFFICIENT** (84-97 legs each, still needing
  203-216 settled priced legs to reach 300). No live change.
- Candidate market price logging expanded (research only, no live model or slip changes): verified
  from real Betpawa responses across all nine leagues (`4958` first-half O/U -> `fh_over_0.5`,
  `fh_over_1.5`; `4976` second-half O/U -> `sh_over_0.5`, `sh_over_1.5`; `80000` Double Chance 1UP ->
  `dc1up_1x`, `dc1up_x2`, `dc1up_12`; `28000850` 1X2 2UP -> `home_2up`, `away_2up`; `1096806`/`1096809`
  Win Either Half -> `home_win_either_half`, `away_win_either_half`; `28000173` 10-minute interval
  1X2 -> `interval_10_draw` for `"X"`). Added to `RESEARCH_MARKETS` with real-fixture isolation tests.
- Results repair: the Understat results endpoint returned HTML instead of JSON. The independent
  ESPN settlement step repaired 20 missing original-five results from 1 and 2 November, with all
  timing outcomes verified against complete goal sequences. All 21 scores checked independently
  against football-data agree. Predictions, chosen slips and stake settings are unchanged.
  The owner explicitly authorized merging and publishing this repair, an exception for this task
  only. Tests: 162 passed, 4 skipped. Build and Chrome browser assertions passed in both themes.
- Date strips now open with the selected day positioned so the following two days are visible; on
  the default route this keeps Today plus the next two days in view instead of starting at 24 October.
  This is UI-only. Sunday/Monday settlement, previously blocked by Understat, is now repaired by
  the independent results fallback described above.
- Daily Action reliability fix is ready on `codex/fix-daily-action-reliability`: a full/final run
  retries the unchanged live refresh three times after transient source failures, then publishes from
  the latest cached data if all retries fail. This addresses repeated Understat connection timeouts
  without changing models, calibration, data transformation, market gates or slip selection.
- Live integration is implemented only on unmerged codex/new-leagues, acceptance INCOMPLETE.
  Existing-five replay equals baseline exactly; 149 tests pass, 4 skip; existing browser checks pass.
  Refreshed run produces Belgium/Portugal/Turkey but no N1 fixture (none published in fixtures.csv,
  next Betpawa game beyond the unchanged 48-hour horizon). STOP rule applied; new-league screenshots
  and all-four-output acceptance remain incomplete. See reports/new_leagues_integration.md.
- Next-round research (2026-10-29): all four candidate leagues meet the registered READY rule
  (Eredivisie 7/8, Belgium 8/8, Portugal 7/8, Turkey 8/8 markets PASS), with Betpawa and ESPN
  coverage verified. None is live. Task 14 retains independent slips. Candidate market prices are
  collected for research only. Browser checks now replay real captured data without service-worker
  interference and pass in both themes at 375px.
- Public-repo readiness (2026-10-29): the complete reachable history (145 commits, all branches) has
  no committed secret value, private key, webhook URL, push subscription, ntfy topic, cron-job.org key,
  or personal contact detail outside commit-author metadata. Both workflows avoid
  `pull_request_target`, do not print secrets, and request only `contents: write`, which their publish
  steps require. The owner still controls the actual GitHub visibility change.
- Live slips and match-page headline picks are overs-only for goal totals (2026-10-29): under 2.5
  and under 3.5 stay available as probability information but cannot be selected. BTTS remains out
  of slips. Tie priority is over goals, double chance, 1Up, then team win.
- Final-slip churn study (task 12, 2026-10-29): **KEEP F**, the current final selection. K's return
  improvement was +1.14 points per unit, but its whole-day 95% CI was -1.86 to +4.03 points, so the
  lower bound failed the pre-registered -1.00-point requirement. No live preview/final behavior changed.
- Live: five leagues, Betpawa odds for all, slips across leagues, badges for all clubs,
  pilot stake cap, health check ("insufficient data" until ~30 settled matches), glass surfaces,
  a four destination floating menu with past slip results on Bets, and announced line-ups drawn on
  a full pitch by formation, with a safe numbered-list fallback when placement is uncertain. Bets and
  Matches share their URL date; Matches also includes schedule-only days, league tables/news and tabbed details.
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
6. Champions League (needs a free results source). Monthly automatic re-check: DONE 2026-10-25
   (`.github/workflows/monthly-gates.yml`, 1st of each month): the gates re-run with the same rules on
   the backtest legs plus every settled live published prediction (`market_gates.live_legs`), so a
   removed pair returns automatically once the evidence says so. The full backtest is not rebuilt
   monthly: one league takes ~32 min (goal timing 26.5 min) and the raw Understat history (128 MB)
   is not in the repository; live predictions are the better new data anyway (truly out of sample).
7. **Betpawa's own 1Up price** (PRE-REGISTERED 2026-10-25, `python -m src.betpawa_1up_study`; data
   collecting since 24 Oct, needs >= 300 evaluation legs, about two months). Settled archived home/away
   1Up predictions with a Betpawa price; first 60% of match days fit won ~ logit(ours) + logit(1/odds),
   the last 40% compare it with won ~ logit(ours) fitted the same way (so a gain is Betpawa's
   information, not a recalibration of ours). Paired log loss difference, 95% CI by whole days (2,000,
   seed 20261025). Use it only if the CI is entirely above 0.
8. **Team tendencies the prices miss** (PRE-REGISTERED 2026-10-29, before any result,
   `python -m src.team_tendency_study`; full rules in the module docstring). Owner's ideas: teams that
   tend to lead first (1Up), and teams the market keeps over- or underrating ("Juventus"). Two families,
   lead (home/away 1Up) and win (home/away win). Features from each team's previous 38 league matches:
   its own mean (outcome - bookmaker probability) and its opponents' against it. Primary: five leagues
   pooled, seasons 2017/18+, fitted on earlier seasons only, baseline that also recalibrates the price
   (`won ~ logit(p) + away`) vs baseline + team features; paired log loss, 95% CI by whole days (2,000,
   seed 20261029). Secondary: the live probabilities on 2024/25+ legs, first 60% of days fit, last 40%
   scored. USE only if the primary CI is entirely above 0 AND the secondary gain is above 0. Checked on
   synthetic data first (`tests/test_team_tendency_study.py`: finds a planted effect, rejects none).
   - Result (DONE 2026-10-29, `reports/team_tendency_study.md`): DO NOT USE, both families. Lead: 32,910
     legs, gain -0.00009 (95% CI -0.00018 to -0.00000), live -0.00044; win: -0.00004 (-0.00013 to
     +0.00005), live -0.00336. A team's season residual does not carry into the next season (r = 0.016
     lead, 0.021 win, 886 team pairs): the prices already hold what is lasting about a team.
9. **Blended vs market re-test with more data** (PRE-REGISTERED 2026-10-29, `python -m src.method_retest_study`):
   La Liga, Serie A, Bundesliga, Ligue 1; validation + test seasons, all 12 slip markets (the original
   choice used 1X2 on 2024/25+ only). Blend weight fitted walk-forward on earlier seasons; scored
   2022/23 onwards; paired log loss market - blended, 95% CI by whole days (2,000, seed 20261029).
   Switch a league to blended only if the CI is entirely above 0.
   - Result (DONE 2026-10-29, `reports/method_retest_study.md`): KEEP MARKET in all four. Gain (market -
     blended log loss): La Liga -0.00183 (95% CI -0.00391 to +0.00013, 17,761 legs), Serie A -0.00166
     (-0.00278 to -0.00055), Bundesliga -0.00286 (-0.00447 to -0.00117), Ligue 1 -0.00301 (-0.00495 to
     -0.00114). The fitted model weight falls every season (e.g. Ligue 1 0.75 -> 0.20).
10. **New candidate markets: team over 0.5 / 1.5 goals, Draw No Bet** (PRE-REGISTERED 2026-10-29,
   `python -m src.new_markets_study`; owner's request, full rules in the module docstring). Probability =
   score matrix implied by the bookmaker average, Platt-calibrated per league x market on earlier seasons
   only; judged by the unchanged task-1 gates (one-sided C1-C4, >= 300 legs) on 2024/25 onwards. DNB is
   scored on non-drawn matches (draw = refund). A PASS pair may enter slips only after implementation
   and Betpawa price logging; FAIL/INSUFFICIENT stays out.
   - Result (DONE 2026-10-29, `reports/new_markets_study.md`): 28 PASS, 2 FAIL (Serie A home over 0.5:
     said 74.7%, won 71.7%; Bundesliga DNB home: said 60.9%, won 55.7%). The raw matrix (no Platt) passed
     all 30; using raw instead would need its own pre-registered test, not a switch after seeing this.
     NOT LIVE: Betpawa parsing and research price logging added 2026-10-29; still needs slip
     maths for DNB refunds (a draw turns the leg into odds 1.00).
11. **Owner's market preference (DONE/LIVE 2026-10-29): no under goals, no BTTS in slips.** Backtest (not
   pre-registered; owner's product rule, checked for cost): 367 days, 2024/25+, five leagues, gate FAILs
   excluded. Without under 2.5/3.5: Safe won 37.6% vs 35.7% (predicted 38.4% vs 38.6%), Medium 28.8% vs
   27.2%, Big 9.8% vs 10.2%; matched-day differences all within chance (Safe +0.019, 95% CI -0.011 to
   +0.049). No measurable cost. The owner approved it: live slip construction and match-page best
   picks now exclude under 2.5/3.5, while research `SLIP_MARKETS`, model outputs and gates are unchanged.
12. **Final-run preview churn** (PRE-REGISTERED 2026-10-29, before any result; research only,
   `python -m src.final_churn_study`):
   - Module `engine/src/final_churn_study.py`, report `engine/reports/final_churn_study.md`, tests in
     `engine/tests/test_final_churn_study.py`.
   - Data: five leagues (EPL, LALIGA, SERIEA, BUNDES, LIGUE1), seasons 2019/20 onwards, matches with
     both the average odds (`avg_odds_*`) and closing odds (`close_odds_*`) for 1X2 and over/under 2.5.
   - Probabilities: `accumulators.bookmaker_implied(odds..., league_rho(league))` with the league's rho
     from `market_live.league_rho`. "Preview" uses the average (early) odds; "final" uses the closing
     odds. Use the same probabilities for every variant (no calibration) so only the selection rule differs.
   - Legs: the live slip markets after task 11 (`SLIP_MARKETS` minus under 2.5 and under 3.5), excluding
     league x market pairs that FAIL in `engine/data/processed/market_gates.json`. Leg odds are what the
     bettor gets at final time: `1 / (p_final * (1 + accumulators.RETAIL_MARGIN))`; legs with odds below
     1.05 are excluded. Days are grouped by calendar date of kick-off and all leagues pooled per day,
     as the live app does.
   - Variants, with each Safe, Medium and Big tier selected by `accumulators.best_slip`:
     F (current) builds from final probabilities and odds. P (never change) builds from preview
     probabilities, then bets those legs at final odds. K (keep unless clearly better) takes P unless
     (i) P's total final odds fall outside the tier's range, or (ii) F's product of final probabilities
     exceeds P's product of final probabilities by more than 3% relative (`F > 1.03 * P`). If either
     condition holds, K takes F.
   - Primary metric: return per unit staked, `won * total_odds - 1`, per day and tier, on days and tiers
     where F offers a slip, so all variants are matched on the same days and tiers. Report K - F and
     P - F with 95% confidence intervals from 2,000 bootstrap resamples of whole days, seed 20261029.
   - Secondary metrics, reported but not deciding: win rate per tier with Wilson confidence intervals,
     predicted versus actual, share of days where K kept the preview, and number of slips.
   - Decision: adopt K only if the K - F point estimate is at least zero AND its confidence-interval
     lower bound is at least -0.01. Otherwise keep F (current). P is reported only.
   - Before real data: synthetic known-answer tests must show (1) identical preview and final gives
     identical K, P and F; (2) K takes F when F is more than 3% better; and (3) K takes F when P's
     final odds fall outside the tier range. Report the result exactly, including if it says keep F.
   - Result (DONE 2026-10-29, `reports/final_churn_study.md`): **KEEP F**. Across 3,106 matched slips
     on 1,182 days, mean estimated return per unit was F -17.35%, P -13.74%, K -16.21%. P - F was
     +3.61 points (95% whole-day bootstrap CI -5.39 to +12.81); K - F was +1.14 points (-1.86 to
     +4.03). K kept 510 previews (16.4%) on 430 days. Its point estimate passed, but the CI lower
     bound was below -1.00 point, so the registered adoption rule failed. These margin-based estimated
     returns compare selection rules; they do not prove profitability. No live churn behavior changed.
Codex (simple): README upkeep, UI polish tasks given as prompts. Daily Action timeout resilience is
implemented on `codex/fix-daily-action-reliability`, pending review/merge and a successful live run.
Results availability repair (4 November): completed with regression tests and verified archive
backfill. ESPN is a settlement fallback only; no prediction strategy change or new study.

13. **Four new leagues** (PRE-REGISTERED 2026-10-29, before results; research only).
   Module `src/new_leagues_study.py`, report `reports/new_leagues_study.md`, tests
   `tests/test_new_leagues_study.py`. Eredivisie N1, Belgian Pro League B1, Primeira Liga P1,
   Super Lig T1: football-data season CSVs 2014/15 through 2026/27. Use AvgH/D/A and
   Avg>2.5/<2.5, otherwise older BbAvH/D/A and BbAv>2.5/<2.5. Verify real column names;
   report matches and complete-odds counts per season. Drop incomplete rows without filling.
   Raw probabilities: `accumulators.bookmaker_implied`, rho fixed to the median of
   `market_live.league_rho` over the five live leagues; report rho. Markets: home_win,
   away_win, double_1x, double_x2, double_12, over_0.5, over_1.5, over_2.5. No 1Up or unders.
   Platt calibration per league/market, LogisticRegression(C=1.0) on logit(raw), fitted
   on earlier seasons only; first season unscored. Judge 2024/25 onwards with unchanged
   `market_gates.evaluate` (one-sided C1-C4, >=300 legs), bookmaker_probability = raw.
   Verify Betpawa competition IDs from its public API and ESPN league slugs with actual
   scores/fixtures responses; report evidence. READY only if >=6 of 8 markets PASS and
   both Betpawa and ESPN cover it; otherwise NOT READY with reason. No live league additions.
   Result (DONE 2026-10-29, `reports/new_leagues_study.md`): all four READY. Eredivisie 7/8
   (double_12 FAIL), Belgium 8/8, Portugal 7/8 (home_win FAIL), Turkey 8/8. Fixed rho -0.054288.
   Betpawa IDs respectively 12125, 12128, 12124, 12182; ESPN ned.1, bel.1, por.1, tur.1 has both
   scheduled fixtures and verified completed scores. Full per-season coverage and unchanged gate
   details are in the report. Downloads and real responses are cached. No live integration.
   Integration follow-up: implemented on codex/new-leagues only; STOPPED with incomplete acceptance
   because the refreshed real output has no EREDIV fixture within the existing source/horizon rules.
   Not merged or deployed; details in reports/new_leagues_integration.md.
14. **At most two slips per match** (PRE-REGISTERED 2026-10-29, before results; research only).
   Module `src/overlap_study.py`, report `reports/overlap_study.md`, tests
   `tests/test_overlap_study.py`. Pool exactly `diversity_study.load_legs` (five leagues,
   2024/25+, gate FAILs excluded), additionally excluding under_2.5/under_3.5.
   A independently selects Safe/Medium/Big with best_slip. M keeps A's Safe/Medium;
   Big uses best_slip after excluding every match appearing in BOTH Safe and Medium.
   If no valid Big remains, M offers none. Primary: return per unit staked,
   won * total_odds - 1, on matched day/tier pairs offered by both. M-A 95% CI from
   2,000 whole-day bootstrap resamples, seed 20261029. Secondary: all-offered-slips-lost
   day share, days with a match on all three under A, per-tier predicted/actual win
   rates and Wilson CIs, Big slip counts. Adopt M only if M-A >=0, CI lower >=-0.01,
   and M all-loss share <= A; otherwise keep A. Known-answer tests before real run:
   no shared matches => M=A; Safe/Medium intersection never enters M Big; no valid
   Big after removal => M offers none. No live change in this task.
   Result: KEEP A. Matched return M-A -0.045543 (95% CI -0.144478 to +0.045067),
   884 matched slips. All-loss day share A 48.01%, M 46.27%; Big offers A 265, M 194.
   A had a match on all three tiers on 241 days. Return and CI criteria fail; live unchanged.
15. **Team goals and Draw No Bet with real Betpawa prices** (PRE-REGISTERED 2026-11-07, before results;
   report only, `python -m src.team_goals_dnb_live_study`):
   - Module `engine/src/team_goals_dnb_live_study.py`, report `engine/reports/team_goals_dnb_live_study.md`,
     tests in `engine/tests/test_team_goals_dnb_live_study.py`.
   - Data: every settled archived match (`web/public/data/archive`, `predict.settled_predictions`) with
     logged Betpawa prices (`engine/data/live/prices`, last price logged before kick-off) for
     `home_over_0.5`, `away_over_0.5`, `home_over_1.5`, `away_over_1.5`, `dnb_home`, `dnb_away`.
   - Probability: rebuild the score matrix from the archived fair `home_win`, `draw`, `away_win`,
     `over_2.5` and `under_2.5` probabilities (`market_probability` in the archived fixture) with
     `accumulators.bookmaker_implied` and the league's rho (`market_live.league_rho`), then apply the
     task-10 method (`new_markets_study.py`) with Platt (`LogisticRegression(C=1.0)` on logit(raw))
     fitted per league x market on seasons before 2026/27 only. DNB is scored on non-drawn matches
     (draw = refund).
   - Report per market: legs, our mean probability vs actual win rate (Wilson 95% CI), Betpawa's mean
     implied probability (`1 / odds`) and margin, and the return per unit staked (`won * odds - 1`) if
     every leg with `probability * betpawa_odds - 1 >= 0.03` had been backed.
   - Decision rule: none yet; a market may enter slips only when it has >= 300 settled priced legs and
     its one-sided level check (actual - predicted, 95% CI upper bound >= 0) passes. State plainly how
     many legs are still needed. No live change.
   - Result (DONE 2026-11-07, `reports/team_goals_dnb_live_study.md`): **INSUFFICIENT** across all 6
     markets (97 settled priced matches, 550 scored legs; 13 draws refunded on DNB). Per market:
     `home_over_0.5` n=92 (208 needed), our mean p 0.7908 vs actual 0.7826 (Wilson 95% CI 0.6879-0.8546),
     Betpawa mean implied 0.8038 (+0.0130 over our p), 5 value legs (return -0.2040/unit);
     `away_over_0.5` n=96 (204 needed), p 0.7288 vs actual 0.6667 (0.5676-0.7529), Betpawa implied
     0.7444 (+0.0156), 5 value legs (-0.4740/unit);
     `home_over_1.5` n=97 (203 needed), p 0.4875 vs actual 0.5670 (0.4677-0.6612), Betpawa implied
     0.5099 (+0.0224), 14 value legs (+0.3757/unit);
     `away_over_1.5` n=97 (203 needed), p 0.3857 vs actual 0.3299 (0.2444-0.4284), Betpawa implied
     0.4121 (+0.0264), 7 value legs (-0.7129/unit);
     `dnb_home` n=84 (216 needed), p 0.5781 vs actual 0.6548 (0.5483-0.7477), Betpawa implied 0.5996
     (+0.0215 vs our p; 2-way DNB margin +0.0502), 8 value legs (+0.4175/unit);
     `dnb_away` n=84 (216 needed), p 0.4219 vs actual 0.3452 (0.2523-0.4517), Betpawa implied 0.4506
     (+0.0287 vs our p; 2-way DNB margin +0.0502), 10 value legs (+0.2020/unit).
     One-sided level CI upper bounds are all >= 0, but 203-216 more settled priced legs are needed
     before any pair can be judged for slip eligibility.
16. **Goals by half and win either half** (PRE-REGISTERED 2026-11-07, before results; research backtest
   only, `python -m src.half_markets_study`):
   - Module `engine/src/half_markets_study.py`, report `engine/reports/half_markets_study.md`, tests in
     `engine/tests/test_half_markets_study.py`.
   - Data: all nine live leagues (`EPL`, `LALIGA`, `SERIEA`, `BUNDES`, `LIGUE1`, `EREDIV`, `JUPILER`,
     `PRIMEIRA`, `SUPERLIG`), football-data season files 2014/15 onwards (`FTHG`/`FTAG`/`HTHG`/`HTAG`
     and the average odds as in `new_leagues_study.odds_columns`); five main leagues from their
     `matches.parquet` (`ht_home_goals`, `ht_away_goals` and `avg_odds_*` from the football-data average
     columns), the four new leagues from their cached raw CSVs. Drop matches missing any needed value;
     never fill.
   - Raw probability: `lambda_home` and `lambda_away` from `accumulators.bookmaker_implied` (league rho
     from `market_live.league_rho`); first-half goal share `s` per league = mean first-half goals /
     mean total goals over EARLIER seasons only; each team's goals per half Poisson with mean
     `s * lambda` (first) and `(1 - s) * lambda` (second), independent.
   - Markets: `fh_over_0.5`, `fh_over_1.5`, `sh_over_0.5`, `sh_over_1.5`, `home_win_either_half`,
     `away_win_either_half`.
   - Calibration: Platt (`LogisticRegression(C=1.0)` on logit(raw)) per league x market, walk-forward
     by season (first season unscored).
   - Judgement: `market_gates.evaluate` unchanged (one-sided C1-C4, >= 300 legs, seed 20261029) on
     2024/25 onwards with `bookmaker_probability = raw`.
   - Decision rule: a PASS pair is only "eligible pending real Betpawa prices" (>= 300 settled priced
     legs and one-sided level check passing, as in task 15); FAIL or INSUFFICIENT stays out. Report the
     typical fair odds (`median(1 / probability)`). Synthetic known-answer tests before real data verify
     exact Poisson half-goal and win-either-half formulas for a fixed lambda and share `s`. No live change.
   - Result (DONE 2026-11-07, `reports/half_markets_study.md`): **49 PASS / 5 FAIL** across 54 league x
     market pairs (`EPL` 4/6, `LALIGA` 6/6, `SERIEA` 6/6, `BUNDES` 6/6, `LIGUE1` 6/6, `EREDIV` 5/6,
     `JUPILER` 5/6, `PRIMEIRA` 5/6, `SUPERLIG` 6/6; first-half goal share `s` 0.4329-0.4474 across
     leagues). Typical fair odds (`median(1 / probability)` across leagues): `fh_over_0.5` 1.29-1.51,
     `fh_over_1.5` 2.32-3.31, `sh_over_0.5` 1.19-1.32, `sh_over_1.5` 1.87-2.52,
     `home_win_either_half` 1.64-1.79, `away_win_either_half` 2.12-2.40. The 5 FAIL pairs stay out:
     `EPL fh_over_1.5` (C2 level -0.0349, CI [-0.0694, -0.0000]), `EPL sh_over_0.5` (C1 slope -0.138,
     CI [-0.894, 0.619]; C3 min_z -3.31), `EREDIV sh_over_1.5` (C4 lifted legs z -2.53, n=69),
     `JUPILER sh_over_0.5` (C2 level -0.0467, CI [-0.0789, -0.0159]), and `PRIMEIRA fh_over_0.5`
     (C4 lifted legs z -2.07, n=68). The 49 PASS pairs are **eligible pending real Betpawa prices**
     (same >= 300 settled priced legs and one-sided level rule as task 15).
17. **Double Chance 1UP and 2UP** (PRE-REGISTERED 2026-11-07, before results; research backtest only,
   `python -m src.up_markets_study`):
   - Module `engine/src/up_markets_study.py`, report `engine/reports/up_markets_study.md`, tests in
     `engine/tests/test_up_markets_study.py`.
   - Data: five main leagues only (`EPL`, `LALIGA`, `SERIEA`, `BUNDES`, `LIGUE1`, seasons 2014/15
     onwards: they have Understat goal minutes in `engine/data/processed/<league>/goals.parquet` and
     `matches.parquet`). Drop matches missing average odds (`avg_odds_*`), scores, or goal-minute
     coverage (matches with total goals > 0 must reconcile with `goals.parquet`); never fill.
   - Outcomes from goal minutes in event order (matching the settlement rules confirmed from Betpawa's
     API explainers and real price inequalities in Part A):
     `dc1up_1x` wins if the home team led at any point OR the final result is home win or draw;
     `dc1up_x2` wins if the away team led at any point OR the final result is away win or draw;
     `dc1up_12` wins if either team led at any point OR the final result is not a draw (equivalently,
     any goal is scored);
     CORRECTION 2026-11-07 (settlement definition corrected before any task-17 result was computed):
     real Betpawa prices prove 2UP is an early-payout enhancement of 1X2 that includes normal 1-goal
     full-time wins: across all 9 real events fetched (and the 6 reviewed: e.g. Torino v Lecce 1.77 vs
     1.82; Fulham v Newcastle 2.01 vs 2.09; Espanyol v Deportivo 2.49 vs 2.58; Paderborn v Frankfurt
     2.70 vs 2.87; Auxerre v Paris FC 4.54 vs 4.76; Arsenal v Hull 1.14 vs 1.16), the 2UP `"1"` and
     `"2"` prices are always strictly below the plain 1X2 `"1"` and `"2"` prices. Likewise, across all
     active DC 1UP quotes in the 9 real events, DC 1UP `1X`, `X2`, `12` are strictly below plain
     Double Chance (`4693`) `1X`, `X2`, `12` (e.g. Torino v Lecce 1.16/1.66/1.03 vs 1.21/1.99/1.29;
     Espanyol v Deportivo 1.30/1.38/1.05 vs 1.41/1.53/1.35; Arsenal v Hull DC 1UP `1X` and `12` are
     `0.0` suspended, skipped by the parser's `odds > 1` rule). Therefore:
     `home_2up` wins if the home team was ever two goals ahead OR the home team won (mirror for
     `away_2up`).
   - Raw probability from the bookmaker score matrix (`accumulators.bookmaker_implied`, league rho):
     `dc1up_1x = sum over scores of P(score) * [1 if home >= away else P(home led at some point | score)]`
     (mirror for `dc1up_x2`; `dc1up_12 = 1 - P(0-0)` since any goal produces a leader), using the same
     exchangeable goal-order assumption as `accumulators.PRIORS`; for 2UP:
     `home_2up = sum over scores of P(score) * [1 if home > away else P(home ever 2 ahead | score)]`
     (mirror for `away_2up`), computing `P(lead reached 2 | final score)` exactly by enumerating every
     goal order of that score (equally likely). Verify on small scores (1-0, 2-1, 3-1) that enumeration
     matches hand counts before running real data.
   - Calibration and judgement: Platt (`LogisticRegression(C=1.0)` on logit(raw)) per league x market,
     walk-forward by season; judged with `market_gates.evaluate` unchanged (one-sided C1-C4, >= 300
     legs, seed 20261029) on 2024/25 onwards with `bookmaker_probability = raw`. Same eligibility rule
     and typical fair odds reporting as task 16. No live change.
   - Result (DONE 2026-11-07, `reports/up_markets_study.md`): **24 PASS / 1 FAIL** across 25 league x
     market pairs (`EPL` 4/5, `LALIGA` 5/5, `SERIEA` 5/5, `BUNDES` 5/5, `LIGUE1` 5/5). Exact goal-order
     enumeration verified on small scores (`1-0`: 0/1 reach +2, `home_2up` weight 1.0; `2-1`: 1/3 (`HHA`)
     reaches +2, `home_2up` weight 1.0; `3-1`: 4/4 reach +2, `home_2up` weight 1.0; `2-2`: 1/6 (`HHAA`)
     reaches +2, weight 1/6; `2-3`: 1/10 (`HHAAA`) reaches +2, weight 1/10; `3-3`: 6/20 reach +2,
     weight 0.30). Typical fair odds (`median(1 / probability)` across leagues): `dc1up_1x` 1.29-1.31,
     `dc1up_x2` 1.49-1.57, `dc1up_12` 1.05-1.09, `home_2up` 2.17-2.45, `away_2up` 3.10-3.58. Only
     `EPL home_2up` failed (n=830, said 0.4680, won 0.4337, C2 level -0.0343, CI [-0.0657, -0.0041])
     and stays out; the 24 PASS pairs are **eligible pending real Betpawa prices** (>= 300 settled
     priced legs and one-sided level check passing).

18. **Betpawa market catalogue and additional research price logging** (PRE-REGISTERED 2026-11-07,
   before results; read-only research and price logging only, `python -m src.betpawa_catalogue`):
   - Module `engine/src/betpawa_catalogue.py`, report `engine/reports/betpawa_market_catalogue.md`.
   - For each of the 9 live leagues, fetch the upcoming events list and the full detail of up to 3
     events (>= 1 s apart, `betpawa.HEADERS`, cached under gitignored `engine/data/raw/betpawa/`).
   - For every `marketType` id observed: report `id`, `name`, `displayName`, outcome names, handicap
     values and their meaning (`handicap / 4 = line`, verified on each market), how many fetched
     events offer it, the event ids as evidence, `"can we settle it from our data"` (`goal minutes` /
     `HT-FT score` / `corners HC,AC` / `cards HY,AY,HR,AR` / `no`), and `"historical outcomes
     available"` (which leagues, seasons).
   - Search specifically for every time-interval market (e.g. 1-10, 1-15, 15-30 minutes, `"goal
     before"`, `"first goal time"`). Report what exists and on which events; if a 15-minute market
     does not exist, state so plainly.
   - For corners and bookings markets, check Betpawa's settlement rule in Betpawa's own published
     rules/explainers; if not found in Betpawa's published rules, write `"rule unverified"` and do not
     study it.
   - Add to `RESEARCH_MARKETS` logging (prices only, never slips) after verifying every id, outcome
     name and handicap on real responses first, with a real trimmed event fixture and parser/isolation
     tests: `28000224` (`"Goal 1"`: `"1"`, `"2"`, `"None"`) -> `first_goal_home`, `first_goal_away`;
     `28000173` `"1"` and `"2"` -> `interval_10_home`, `interval_10_away`; `1096807`/`1096814` `"Yes"` ->
     `home_score_both_halves`, `away_score_both_halves`; `1096805`/`1096808` `"Yes"` ->
     `home_win_both_halves`, `away_win_both_halves`; `4964`/`4961`/`4982`/`4979` Over 0.5 ->
     `home_fh_over_0.5`, `away_fh_over_0.5`, `home_sh_over_0.5`, `away_sh_over_0.5`.
   - Result (DONE 2026-11-07, `reports/betpawa_market_catalogue.md`): catalogued 128 `marketType` IDs
     across 27 upcoming events (3 per league across all 9 leagues): 94 settleable from `HT-FT score`
     (all 9 leagues, 2014/15-2026/27), 6 from `goal minutes` (5 main leagues, 2014/15-2026/27), 7 FT
     corner markets from `corners HC,AC` (5 main leagues 2014/15-2026/27; 4 new leagues
     2017/18-2026/27), 3 dismissal markets from `cards HY,AY,HR,AR`, and 18 `no` (8 player props, 9
     1H/sequence corner markets, 5 1H booking markets, plus FT booking totals where Betpawa counts a
     2nd yellow leading to red as 2 bookings rather than 3, which `HY,AY,HR,AR` cannot separate from a
     straight red, and team/3-way booking markets whose card-point formula is unverified in the API
     explainer). Only one time-interval market exists (`28000173`, 00:01-09:59; no 15-minute market
     exists). All 10 new `RESEARCH_MARKETS` keys verified on real responses and added with trimmed
     real fixture `38916500` in `tests/fixtures/betpawa_research.json`.
19. **Goal-minute accuracy check** (PRE-REGISTERED 2026-11-07, before results; must pass before task
   20 uses minutes, `python -m src.goal_minute_check`):
   - Module `engine/src/goal_minute_check.py`, report `engine/reports/goal_minute_check.md`, tests in
     `engine/tests/test_goal_minute_check.py`.
   - Data: >= 300 goals across the 5 main leagues (`EPL`, `LALIGA`, `SERIEA`, `BUNDES`, `LIGUE1`) and
     at least 3 seasons, comparing Understat's `minute` (`engine/data/processed/<league>/goals.parquet`)
     with ESPN summary `keyEvents` (`scoringPlay`; `clock.value` in seconds, `clock.displayValue`,
     `period.number`, fetched >= 1 s apart with `User-Agent: "BetPredz research"`, cached under
     gitignored `engine/data/raw/espn/`).
   - Determine the exact mapping between ESPN clock and Understat `minute` and how first-half stoppage
     goals (`45+x`) are stored.
   - Betpawa's 10-minute window is `"00:01-09:59"`: a goal counts if it is before `10:00` on the match
     clock (`clock.value < 600` in period 1).
   - Rule: Understat may be used for the 10-minute window and timing markets in task 20 only if the
     mapping assigns >= 98% of the compared goals to the same side of `10:00` as ESPN, AND goal ORDER
     agrees in >= 99% of compared matches. Otherwise task 20 uses only the HT/FT-based markets and
     reports the timing ones as `INSUFFICIENT`.
   - Report the agreement tables and every disagreement example (match, ESPN seconds, Understat minute).
   - Result (DONE 2026-11-07, `reports/goal_minute_check.md`): **PASS** across 332 goals in 73 matches
     (all 5 main leagues, seasons `2023/24`, `2024/25`, `2025/26`). Understat stores 0-indexed completed
     minutes (`minute = floor(seconds / 60) = display_minute - 1` for regular time, matching `293/296` =
     `98.99%` exactly and differing by `-1` minute on the remaining `3`), `44 + x` for first-half
     stoppage (`45'+x'`, `16/16` = `100.00%`), and `89 + x` for second-half stoppage (`90'+x'`, `20/20` =
     `100.00%`). Under `minute <= 9`, `< 10:00` (`clock.value < 600.0s` in period 1) agrees in
     **`332/332` (`100.00%` >= `98%`)** goals (naive `minute <= 10` misclassifies two 11th-minute goals at
     `608.0s` and `646.0s`, giving `330/332` = `99.40%`). Sorting `goals.parquet` by `minute` reproduces
     ESPN's full goal-scoring team sequence in **`73/73` (`100.00%` >= `99%`)** matches (unsorted raw
     `goals.parquet` groups `home` before `away`, agreeing in `36/73` = `49.32%`). Task 20 is cleared to
     use Understat minutes with `minute <= 9` and sorted `goals.parquet`.
20. **Goal-timing and half markets backtest** (PRE-REGISTERED 2026-11-07, before results; research
   backtest only, `python -m src.timing_half_markets_study`):
   - Module `engine/src/timing_half_markets_study.py`, report
     `engine/reports/timing_half_markets_study.md`, tests in
     `engine/tests/test_timing_half_markets_study.py`.
   - Markets: `first_goal_home`, `first_goal_away`, `interval_10_home`, `interval_10_draw`,
     `interval_10_away` (5 main leagues, goal minutes from reconciled `goals.parquet` and
     `matches.parquet` 2014/15+, only if task 19 passes; otherwise `INSUFFICIENT`);
     `home_score_both_halves`, `away_score_both_halves`, `home_win_both_halves`,
     `away_win_both_halves`, `home_fh_over_0.5`, `away_fh_over_0.5`, `home_sh_over_0.5`,
     `away_sh_over_0.5` (all 9 live leagues, HT/FT scores 2014/15+).
   - Raw probability from `accumulators.bookmaker_implied` lambdas (league rho), as in task 16:
     first-half share `s` and 10-minute share `w` (fraction of all goals scored before `10:00`) per
     league from EARLIER seasons only; each team's goals in a period ~ `Poisson(share * lambda)`,
     independent; `first_goal_home = lambda_h / (lambda_h + lambda_a) * (1 - P(no goal))` (mirror for
     `first_goal_away`). Outcomes from goal order / HT-FT.
   - Synthetic known-answer tests before real data (fixed lambdas: exact formulas, and a simulated
     league where the answer is known).
   - Calibration and judgement: Platt (`LogisticRegression(C=1.0)` on `logit(raw)`) per league x
     market, walk-forward by season; `market_gates.evaluate` unchanged (one-sided C1-C4, >= 300 legs,
     seed 20261029), `bookmaker_probability = raw`. Judged on `2024/25+` (primary) AND on
     `2019/20-2023/24` (replication, each season scored with a calibrator fitted on earlier seasons
     only). `"Strong candidate"` = `PASS` in both periods; otherwise stays out. No live change.
   - Result (DONE 2026-11-07, `reports/timing_half_markets_study.md`):
     - **Timing markets** (5 main leagues x 5 markets = 25 pairs, Understat `goals.parquet` after Task 19
       PASS, dropping 3 matches with earliest-minute home/away ties out of 20,305): Primary `2024/25+`
       **25 PASS / 0 FAIL**; Replication `2019/20-2023/24` **24 PASS / 1 FAIL** (`LIGUE1 first_goal_home`);
       **24 / 25 Strong candidates** (`PASS` in both periods, pending real Betpawa prices).
     - **Team-half markets** (9 live leagues x 8 markets = 72 pairs, `HTHG`/`HTAG` & `FTHG`/`FTAG`):
       Primary `2024/25+` **68 PASS / 4 FAIL** (`EPL home_sh_over_0.5`, `LALIGA away_win_both_halves`,
       `JUPILER away_win_both_halves`, `JUPILER away_sh_over_0.5`); Replication `2019/20-2023/24`
       **61 PASS / 11 FAIL**; **58 / 72 Strong candidates** (`PASS` in both periods, pending real Betpawa
       prices).
     - **Combined**: **82 / 97 Strong candidates** (`PASS` in both periods), **15 stay out**.
21. **Replication of tasks 16 and 17 on 2019/20-2023/24** (PRE-REGISTERED 2026-11-07, before results;
   research backtest only, `python -m src.replicate_tasks_16_17`):
   - Module `engine/src/replicate_tasks_16_17.py`, report
     `engine/reports/tasks_16_17_replication.md`, tests in
     `engine/tests/test_replicate_tasks_16_17.py`.
   - Re-judge the markets of task 16 (9 leagues x 6 half markets = 54 pairs) and task 17 (5 main
     leagues x 5 UP markets = 25 pairs) on `2019/20-2023/24` with the exact same code and rules (no
     other change; each season calibrated on earlier seasons only with `LogisticRegression(C=1.0)` on
     `logit(raw)`, judged with `market_gates.evaluate` unchanged, seed 20261029).
   - Report `PASS`/`FAIL` per pair across both periods (`2024/25+` and `2019/20-2023/24`); `"Strong
     candidate"` = `PASS` in both periods. Do not change the earlier reports' numbers. No live change.
   - Result (DONE 2026-11-07, `reports/tasks_16_17_replication.md`):
     - **Task 16 replication** (9 leagues x 6 half markets = 54 pairs): Primary `2024/25+` **49 PASS /
       5 FAIL**; Replication `2019/20-2023/24` **48 PASS / 6 FAIL** (`LALIGA sh_over_1.5`,
       `LALIGA home_win_either_half`, `PRIMEIRA fh_over_0.5`, `PRIMEIRA fh_over_1.5`,
       `SUPERLIG fh_over_0.5`, `SUPERLIG fh_over_1.5`); **44 / 54 Strong candidates** (`PASS` in both
       periods, pending real Betpawa prices).
     - **Task 17 replication** (5 main leagues x 5 UP markets = 25 pairs): Primary `2024/25+` **24 PASS /
       1 FAIL** (`EPL home_2up`); Replication `2019/20-2023/24` **25 PASS / 0 FAIL**; **24 / 25 Strong
       candidates** (`PASS` in both periods, pending real Betpawa prices).
     - **Combined**: **68 / 79 Strong candidates** (`PASS` in both periods), **11 stay out**. Earlier
       reports (`reports/half_markets_study.md`, `reports/up_markets_study.md`) unchanged.
22. **Simulated Betpawa-price value check** (PRE-REGISTERED 2026-11-07, before results; clearly
   labelled `SIMULATED`, never `"real prices"`, `python -m src.simulated_value_study`):
   - Module `engine/src/simulated_value_study.py`, report `engine/reports/simulated_value_study.md`,
     tests in `engine/tests/test_simulated_value_study.py`.
   - From `engine/data/live/prices` (last pre-kickoff snapshot per match) and the archived consensus
     fair probabilities (same reconstruction as task 15), compute per research market the ratio
     `r = (1 / Betpawa odds) / raw_consensus_probability`. Report median, 25th and 75th percentile,
     and `n`. Fewer than 50 priced matches for a market = `INSUFFICIENT` for that market.
   - For each market with `r` (`n >= 50`), over the historical matches of tasks 16/17/20 (`2014/15+`):
     simulated return per unit = `mean(won / (raw * r)) - 1`, with 95% CI by bootstrap of whole days
     (2,000 resamples, seed 20261029), pooled and per league, also at the 25th and 75th percentile `r`
     (sensitivity).
   - Decision rule: report only. A market whose CI lower bound is above 0 at the median `r` AND the
     75th percentile `r` becomes `"priority for the real-price test"`; nothing enters slips from this
     task.
   - Result (DONE 2026-11-07, `reports/simulated_value_study.md`, **SIMULATED** only):
     - Checked all 30 `RESEARCH_MARKETS`: **17 markets meet `n >= 50`** priced matches (`11` from Tasks
       16/17 with `n = 52–71` and `6` from Tasks 10/15 with `n = 163–171`), while **13 markets are
       `INSUFFICIENT` (`n < 50`)** (`interval_10_draw` has `n = 41` in the 5 main leagues where 10-minute
       share `w` is defined from Understat `goals.parquet`, and the 12 newly added Task-18 markets have
       `n = 0`).
     - Observed median `r = (1 / Betpawa odds) / raw_consensus_probability`: lowest on 2UP (`away_2up`
       `0.9980`, `home_2up` `1.0059`, `n = 71`), `sh_over_0.5` (`1.0238`), `fh_over_0.5` (`1.0316`),
       `home_over_0.5` (`1.0326`), `away_over_0.5` (`1.0348`), `dc1up_12` (`1.0390`), `sh_over_1.5`
       (`1.0418`), `dnb_home` (`1.0446`), `dnb_away` (`1.0552`), `home_over_1.5` (`1.0628`), `dc1up_1x`
       (`1.0669`), `dc1up_x2` (`1.0733`), `away_over_1.5` (`1.0735`), `fh_over_1.5` (`1.0804`),
       `home_win_either_half` (`1.0806`), `away_win_either_half` (`1.0919`).
     - Over `2014/15+` historical matches (2,000 whole-day bootstrap resamples, `SEED = 20261029`),
       `home_2up` has a positive **SIMULATED** pooled return at `p25 r` (`+0.0243`, 95% CI `+0.0074` to
       `+0.0419`), but at `median r` (`-0.0207`, CI `-0.0368` to `-0.0042`) and `p75 r` (`-0.0401`, CI
       `-0.0562` to `-0.0243`) its CI lower bound is below 0. **0 markets** have a 95% CI lower bound `> 0`
       at both `median r` and `p75 r` (**no market flagged as priority**; report only, no live change).

## 7. Studies already done (do not redo without a new reason)
Operational note (4 November): the results fallback is not a modelling study. It fills verified
outcomes for already published picks without changing any study decision below.

| Idea | Result | Decision |
|---|---|---|
| SIMULATED Betpawa-price value check (task 22) | 17/30 research markets have `n >= 50` (`home_2up` med `r = 1.0059`, `away_2up` `0.9980`); 0 markets have SIMULATED 95% CI lower bound `> 0` at both median and p75 `r` | report only; keep logging real prices toward 300 settled legs |
| Replication of tasks 16 and 17 on 2019/20-2023/24 (task 21) | Task 16: 44/54 PASS both periods; Task 17: 24/25 PASS both periods (`68/79` Strong candidates) | 68 Strong candidates pending >= 300 real Betpawa priced legs |
| Goal-timing and team-half markets backtest (task 20) | Timing (5 leagues): 24/25 PASS both periods; Team-half (9 leagues): 58/72 PASS both periods (`82/97` Strong candidates) | 82 Strong candidates pending >= 300 real Betpawa priced legs |
| Goal-minute accuracy check, Understat vs ESPN (task 19) | 332 goals / 73 matches (5 leagues, 3 seasons): `< 10:00` (`minute <= 9`) `332/332` (`100%`), sorted goal order `73/73` (`100%`) | PASS; cleared Understat minutes for task 20 |
| Betpawa market catalogue, 9 leagues (task 18) | 128 `marketType` IDs across 27 events; only 00:01-09:59 interval exists; 10 new research keys logged | price logging expanded; bookings not studied (`HY,AY,HR,AR` lacks 2nd-yellow split / rule unverified) |
| Double Chance 1UP and 1X2 2UP, 5 main leagues (task 17) | 24/25 PASS, 1 FAIL (`EPL home_2up`) | 24 PASS eligible pending >= 300 real Betpawa priced legs; `EPL home_2up` stays out |
| Goals by half and win either half, 9 leagues (task 16) | 49/54 PASS, 5 FAIL (`EPL fh_over_1.5`, `EPL sh_over_0.5`, `EREDIV sh_over_1.5`, `JUPILER sh_over_0.5`, `PRIMEIRA fh_over_0.5`) | 49 PASS eligible pending >= 300 real Betpawa priced legs; 5 FAIL stay out |
| Team goals and DNB with real Betpawa prices (task 15) | 84-97 settled priced legs per market (need 203-216 more for 300) | INSUFFICIENT; keep collecting prices |
| Four candidate leagues (task 13) | N1 7/8, B1 8/8, P1 7/8, T1 8/8 PASS; Betpawa and ESPN verified | READY for a later integration task; not live |
| Limit a match to two slips (task 14) | matched return -4.55 points, CI -14.45 to +4.51; all-loss days slightly lower | KEEP A |
| League table, derbies, team home strength, rest days | none lowered log loss on unseen seasons | rejected |
| Missing players (Understat lineups; upper bound of injury news) | no improvement; team news already in prices | rejected |
| Shots+corners "pressure" (Wheatcroft 2020, LSE paper owner sent) | no reliable gain for over/under or 1Up; paper loses at average odds | rejected (`src/pressure_study.py`, `src/pressure_1up_study.py`) |
| Per-market model weights (EPL) | worse than one global weight (0.60164 vs 0.60147) | rejected (`src/market_weight_study.py`) |
| Blended model for La Liga/Serie A/Bundesliga/Ligue 1 | less accurate than market mode | market mode used |
| EPL weight from all seasons (A) vs test-era only (V, live) | log loss difference +0.00033, 95% CI -0.00166 to +0.00231 | V kept (`src/weight_study.py`) |
| Team tendencies: first-to-lead (1Up) and "market keeps misjudging a team" (2026-10-29) | no gain; season-to-season persistence r = 0.02 | rejected (`src/team_tendency_study.py`) |
| Blended vs market, 4 leagues, 5 seasons, 12 slip markets (2026-10-29) | market better in all four (3 of 4 significant) | market kept (`src/method_retest_study.py`) |
| No shared matches across Safe/Medium/Big | growth gain only from betting less; ROI per stake worse (-11.6% vs -8.4%); all-loss days 197 vs 198 of 402 | rejected (`src/diversity_study.py`) |
| Remove under 2.5/3.5 from live slips (owner's product rule, 2026-10-29) | no measurable cost on 367 days; Safe and Medium point estimates improved | approved; live slips and best picks are overs-only |
| Keep preview unless final is >3% better (2026-10-29) | K - F +1.14 return points, 95% CI -1.86 to +4.03; lower bound failed the registered -1.00 threshold | rejected; current final selection kept (`src/final_churn_study.py`) |

## 8. Lessons and pitfalls (read before changing things)
- "Nothing to predict" is a normal day, not an error: every step after it (settlement, publishing) must
  still run (2026-10-27).
- Cross-check derived data with an independent source before showing it (league tables vs ESPN standings
  exposed both football-data's lag and an Understat home/away swap, 2026-10-25).
- Test data must be real: Codex's invented line-up hid a left/right ordering bug that the real
  Sunderland v Leeds line-ups exposed at once (2026-10-25).
- Workflow runs must check out `main`, not the triggering commit: a queued run otherwise starts from
  data older than the previous run's publish and its push fails on rebase conflicts.
- When comparing strategies that bet different amounts, compare per unit staked or on matched days:
  with negative-EV backtest odds, the variant that bets least always "grows" most (2026-10-25).
- Settlement must not wait for football-data.co.uk (results lag days); Understat is same-night.
  Understat itself can fail or return HTML: `src.settle_results` independently repairs pending
  published outcomes from ESPN, and a missing source must never reset a known outcome to pending.
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
- 2026-11-07: Claude reviewed tasks 18-22. Tests pass and all five reports reproduced byte for byte
  (sha256 identical). Independent boundary check of the task-19 minute mapping on 49 different goals
  recorded by Understat at minutes 8-11 (2022/23-2025/26, 10 random matches per league, seed
  20261107): 48/49 on the same side of 10:00 as ESPN's clock seconds (one miss: Roma v Lazio,
  Understat minute 9 vs ESPN 601 s). Fixes: task 20 now computes the task-19 gate instead of stating
  it (timing markets are skipped if it fails); task 22 report counts are computed, not typed;
  health.py imports moved to the top. Results unchanged. Plain reading for the owner: no candidate
  market shows a reliable profit at Betpawa's typical prices (simulated); 2UP is the cheapest
  (about -2% at the median price, vs -5% to -10% for most others). Real-price checks still need
  >= 300 settled priced legs per market.
- 2026-11-07: Added non-fatal badge coverage warning in `src/health.py` (`known_badge_teams`,
  `missing_badge_teams`, wired into `health_check` and `src/predict.py` without changing `status` or
  `stake_factor`) listing any team in published fixtures or tables without a badge in
  `web/src/badgeUrls.json` or `PL_BADGE_IDS` in `web/src/badges.tsx`, plus tests in
  `tests/test_health.py` verifying the badge warning and that every league country in `src/leagues.py`
  has a flag `case` in `web/src/badges.tsx`.
- 2026-11-07: Completed task 22 (`src/simulated_value_study.py`, `reports/simulated_value_study.md`,
  `tests/test_simulated_value_study.py`): computed pre-kickoff ratio `r = (1 / Betpawa odds) /
  raw_consensus_probability` across all 30 `RESEARCH_MARKETS` (`17` with `n >= 50`, `13` `INSUFFICIENT`)
  and evaluated **SIMULATED** historical returns (`2014/15+`, 2,000 whole-day bootstrap resamples,
  `SEED = 20261029`) pooled and per league at `p25`, `median`, and `p75` of `r`. Found 0 markets with 95%
  CI lower bound `> 0` at both `median r` and `p75 r`. Report only; no live change.
- 2026-11-07: Completed task 21 (`src/replicate_tasks_16_17.py`,
  `reports/tasks_16_17_replication.md`, `tests/test_replicate_tasks_16_17.py`): replicated Tasks 16
  (54 pairs) and 17 (25 pairs) on `2019/20-2023/24` with identical rules and `market_gates.evaluate`
  (`SEED = 20261029`). Found 44/54 Task-16 and 24/25 Task-17 Strong candidates (68/79 combined `PASS` in
  both `2024/25+` and `2019/20-2023/24`). Earlier reports unchanged. No live change.
- 2026-11-07: Completed task 20 (`src/timing_half_markets_study.py`,
  `reports/timing_half_markets_study.md`, `tests/test_timing_half_markets_study.py`): ran synthetic
  known-answer tests before real data, then evaluated 5 timing markets across 5 main leagues (25 pairs)
  and 8 team-half markets across 9 live leagues (72 pairs) on `2024/25+` (primary) and
  `2019/20-2023/24` (replication). Found 24/25 timing and 58/72 team-half Strong candidates (82/97
  combined `PASS` in both periods, pending real Betpawa prices). No live change.
- 2026-11-07: Completed task 19 (`src/goal_minute_check.py`, `reports/goal_minute_check.md`,
  `tests/fixtures/espn_summary_671408.json`, `tests/test_goal_minute_check.py`): compared 332 goals
  across 73 matches (5 main leagues, `2023/24`–`2025/26`) between Understat `goals.parquet` and ESPN
  `keyEvents`. Verified Understat's 0-indexed minute convention (`floor(seconds / 60)` in regular time,
  `44 + x` in 1H stoppage, `89 + x` in 2H stoppage); `minute <= 9` agrees with ESPN `< 600.0s` on
  `332/332` (`100.00%`) goals and sorting `goals.parquet` by `minute` agrees with ESPN goal order on
  `73/73` (`100.00%`) matches (PASS).
- 2026-11-07: Completed task 18 (`src/betpawa_catalogue.py`, `reports/betpawa_market_catalogue.md`,
  `src/betpawa.py`, `tests/fixtures/betpawa_research.json`, `tests/test_betpawa.py`,
  `tests/test_research_prices.py`): catalogued all 128 `marketType` IDs across 27 upcoming events (3 per
  league across all 9 leagues), verified that only the 00:01-09:59 interval market (`28000173`) exists
  (no 15-minute market), documented corners and bookings rules/limitations, and added 10 new keys to
  `RESEARCH_MARKETS` with real fixture and isolation tests. No live change.
- 2026-11-07: Pre-registered tasks 18 (Betpawa market catalogue and additional research price
  logging), 19 (Understat vs ESPN goal-minute accuracy check), 20 (goal-timing and half markets
  backtest on 2024/25+ and 2019/20-2023/24 replication), 21 (2019/20-2023/24 replication of tasks 16
  and 17), and 22 (simulated Betpawa-price value check) in PROJECT.md before computing any results.
- 2026-11-07: Added league flags for Netherlands, Belgium, Portugal and Turkey (`web/src/badges.tsx`;
  they showed a grey box). Checked all 168 team names in the published data and archive: every one
  has a badge URL, all 173 URLs load a real image and all 148 ESPN images are distinct.
- 2026-11-07: Claude reviewed tasks 15-17. All three reports reproduced byte for byte; 168 tests
  pass. Fixed task 17 to use the pre-registered Platt (`LogisticRegression(C=1.0)`; it had used
  `calibration.fit_calibrator`, C=1e6): probabilities moved by at most 0.0007, all 25 decisions
  unchanged. Task 15 report text no longer hard-codes counts. Independent check of the new market
  definitions on 29 real Betpawa matches (2026-11-07): our model probability built from Betpawa's
  own 1X2 + over/under 2.5 sits just below Betpawa's implied probability in every market (median
  ratio 1.00-1.10, i.e. Betpawa's margin), so no definition is wrong. Observation to test later,
  not a decision: 2UP is priced at about zero margin (ratio 1.00-1.01) while 1X2 carries about 4%.
- 2026-11-07: Completed task 17 (`src/up_markets_study.py`, `reports/up_markets_study.md`,
  `tests/test_up_markets_study.py`): backtested `dc1up_1x`, `dc1up_x2`, `dc1up_12`, `home_2up`,
  `away_2up` across the five main leagues (`EPL`, `LALIGA`, `SERIEA`, `BUNDES`, `LIGUE1`) on 2024/25+
  with exact goal-order enumeration for 2UP and walk-forward Platt calibration. 24 of 25 pairs PASS
  (eligible pending >= 300 settled Betpawa priced legs) and 1 FAIL (`EPL home_2up`). No live change.
- 2026-11-07: Completed task 16 (`src/half_markets_study.py`, `reports/half_markets_study.md`,
  `tests/test_half_markets_study.py`): backtested `fh_over_0.5`, `fh_over_1.5`, `sh_over_0.5`,
  `sh_over_1.5`, `home_win_either_half`, `away_win_either_half` across all nine live leagues on 2024/25+
  with earlier-season first-half goal share `s` and walk-forward Platt calibration. 49 of 54 pairs PASS
  (eligible pending >= 300 settled Betpawa priced legs) and 5 FAIL (`EPL fh_over_1.5`, `EPL sh_over_0.5`,
  `EREDIV sh_over_1.5`, `JUPILER sh_over_0.5`, `PRIMEIRA fh_over_0.5`). No live change.
- 2026-11-07: Completed task 15 (`src/team_goals_dnb_live_study.py`, `reports/team_goals_dnb_live_study.md`,
  `tests/test_team_goals_dnb_live_study.py`): 97 settled archived matches (550 scored legs) have logged
  pre-kickoff Betpawa prices for team over 0.5/1.5 and DNB; all 6 markets have 84-97 legs and still need
  203-216 legs to reach the 300-leg threshold. No live change.
- 2026-11-07: Corrected task 17 2UP settlement definition in PROJECT.md before computing any task-17
  results: real Betpawa prices (2UP `"1"`/`"2"` always below 1X2 `"1"`/`"2"`, and DC 1UP always below
  plain Double Chance) prove `home_2up`/`away_2up` win when the team is ever two goals ahead OR wins at
  full time (`sum over scores of P(score) * [1 if home > away else P(home ever 2 ahead | score)]`).
- 2026-11-07: Pre-registered study tasks 15 (team goals and Draw No Bet with real Betpawa prices),
  16 (goals by half and win either half across all nine leagues) and 17 (Double Chance 1UP and 2UP
  across the five main leagues) in PROJECT.md before computing any results.
- 2026-11-07: Expanded research-only Betpawa market parsing and price logging after verifying all
  seven market families across real events from all nine leagues (`4958` first-half Over 0.5/1.5,
  `4976` second-half Over 0.5/1.5, `80000` Double Chance 1UP `1X`/`X2`/`12`, `28000850` 1X2 2UP `1`/`2`,
  `1096806`/`1096809` Win Either Half `Yes`, and `28000173` 10-minute interval `X` as `interval_10_draw`).
  Trimmed real event 38292840 added to `tests/fixtures/betpawa_research.json`; parser and isolation
  tests pass. No live model, gate or slip behavior changed.
- 2026-11-04: Owner-authorized results repair and merge. Added independent ESPN settlement after
  full/final/price runs, complete-goal verification for 1Up/first scorer, exact competition/team/date
  matching, cached responses and outage-safe history. Backfilled 20 missing November results;
  every original prediction, chosen leg, odds and staking setting checked unchanged. 162 tests
  passed, 4 skipped; build and phone browser checks passed in Chrome (Edge failed to launch).
- 2026-11-03: Date strips initially position the selected day with two later days visible, keeping
  Today near the right side on the default Bets and Matches screens. Added a phone-width browser
  assertion. No prediction, settlement, or data-processing behavior changed.
- 2026-11-03: Daily predictions now retries the normal refreshed prediction three times when an
  external source fails, then uses the existing `--no-refresh` cached-data path so a prolonged
  Understat timeout does not prevent settlement/publication. Prediction and processing methods are
  unchanged. Local frontend setup is documented as `cd web; npm ci`; the repository root is not an
  npm package.
- 2026-10-29: Four-league integration implemented on codex/new-leagues only, not merged. Saved
  completed-season calibrators, fixed rho, strict source names, verified badges, ESPN score settlement,
  task-13 market blocking and resilient monthly gates. Exact original-five regression passed.
  STOPPED incomplete: no real N1 upcoming prediction at the current time; all-four acceptance and
  new-league screenshots cannot pass honestly. Original live artifacts restored; no push or merge.
- 2026-10-29: Began new-league integration preflight on a separate branch. Live Betpawa identities,
  football-data/Betpawa/ESPN team lists and 72 logo URLs verified; integration verification report
  records historical size evidence. No live prediction code changed.
- 2026-10-29: Research team-total parsing logs and skips invalid handicap rows so this optional
  collection cannot disrupt existing market parsing. Final full suite: 132 passed.
- 2026-10-29: Confirmed the browser replay root cause: service workers bypassed routed fixtures
  on reload. Test contexts now block them; ALL PASSED in light/dark at 375px, including 3 real
  schedule-only rows on 27 October. Final light/dark screenshots inspected; app unchanged.
- 2026-10-29: Completed task 13: four leagues READY by the pre-registered rule, real historical
  CSVs and ESPN/Betpawa responses cached; no live leagues changed. Source failures during the cached
  pipeline check were caught and publication finished with health ok and zero new fixtures; generated
  tracked data was restored. Browser replay now passes in both themes with service workers blocked.
- 2026-10-29: Task 14 overlap study keeps independent tiers; limiting a match to two slips failed
  the registered matched-return rule. Report and known-answer optimizer-state tests added.
- 2026-10-29: Candidate market prices (home/away over 0.5/1.5 and DNB) parsed from verified real
  Betpawa event 38781890 and logged as research only in full/price snapshots. Team handicaps are
  line times four; DNB names are 1/2. Real-response parser and selection-isolation tests pass.
  Additional monitor-isolation checks use real archive predictions; full engine suite:
  131 passed, 1 skipped (2026-10-29).
- 2026-10-29: Repository made public (unlimited Actions minutes). External timer (cron-job.org job 8716884)
  changed from every 30 to every 15 minutes, 06:00-23:45 EAT: final run and notification now ~40-55 min before
  the first kick-off (was ~25-55), and twice as many price snapshots before kick-offs. No code logic changed.
- 2026-10-29: Pre-registered research tasks 13 and 14 before any results; implementation pending.
- 2026-10-29: Browser checks select a real fixture's badge and an available league table from the
  committed test data; schedule days use Tanzania time explicitly and replay uses the captured
  publication time. Test contexts block service workers so reloads cannot bypass response routing
  and mix current production data with captured fixtures. The app already supports schedule-only days
  through MatchesRedesign; the earlier diagnosis from the unused Matches component was incorrect.
- 2026-10-29: Final-slip churn study (task 12) kept the current final selection: K improved estimated
  return by +1.14 points, but its 95% CI (-1.86 to +4.03) failed the pre-registered lower-bound rule.
  The report and synthetic known-answer tests were added; no live preview/final behavior changed.
- 2026-10-29: Pre-registered task 12, the final-slip churn study, before computing any result. It
  compares current final selection with never changing and a fixed 3%-relative "keep preview"
  threshold on matched day/tier returns; no live preview/final behavior has changed.
- 2026-10-29: Owner-approved overs-only live rule: under 2.5/3.5 cannot enter live slips or the
  match-page best pick, while their model probabilities and all research/gate markets remain intact.
  BTTS remains outside slips. Best-pick tie priority is over goals, double chance, 1Up, then team win.
- 2026-10-29: Prepared the repository documentation for public visibility after auditing all 145
  reachable commits and every workflow. No real secret was found; GitHub Secret names and the public
  cron job ID are references only. Workflow permissions were already minimal for their push steps, so
  no workflow or schedule change was needed.
- 2026-10-29: Studies only, no live change (tasks 8-11): team tendencies rejected; market mode re-confirmed
  for La Liga, Serie A, Bundesliga, Ligue 1; team over 0.5/1.5 and Draw No Bet pass the gates in 28 of 30
  league pairs (not live yet); dropping under goals costs nothing measurable (awaiting owner approval).
  Betpawa lists 107 markets per match (EPL); SportPesa's robots.txt allows reading (not used yet).
- 2026-10-27: Betpawa fallback (`predict.add_betpawa_fixtures`): a match football-data has not posted yet
  (e.g. the midweek Serie A round) is priced from Betpawa's 1X2 and over/under 2.5 instead of the
  bookmaker average, within 48 hours of kick-off; the method after that is unchanged and the match is
  marked `odds_source: "betpawa"` (label on its Insights tab). Checked first on 28 matches with both
  sources: mean difference +0.04 points, typical 1.9, log loss 0.5577 (Betpawa) vs 0.5621 (average).
  Betpawa prices are fetched once per run and reused.
- 2026-10-27: run_mode also starts a full run when football-data posts upcoming matches with odds that we
  have not published (late midweek rounds), at most about once an hour; it reads only fixtures.csv,
  so no wasted runs and no model change. Tests in test_schedule.
- 2026-10-27: FIX: with no upcoming fixtures in any league (football-data had not yet posted the midweek
  round), `predict` exited with an error, so every run failed from 07:00 and nothing was published (not even
  the night's settlement). It now settles, updates archive/tables/monitoring and publishes without slips.
- 2026-10-25: line-up pitch follows SofaScore (owner's reference): straight lines, players spread evenly
  across the width (back four at ~13/38/62/87, front two at a third / two thirds), lines evenly spaced from
  the goalkeeper; replaces the earlier up/down "shape" offsets.
- 2026-10-25: line-up pitch drawn as a real team shape (full-backs/wing-backs higher and wider, centre-backs
  tucked in, wide midfielders up, holding midfielders deeper, wingers just behind the striker); unknown
  ESPN codes (e.g. RCF for Pulisic in Milan's 4-4-1-1) are read from their letters instead of falling back
  to a list. FIX: moving from one match page to another kept the previous match's line-ups (and stats); each
  match page now starts fresh. Checked on six real line-ups of 25 Oct 2026, no overlapping names.
- 2026-10-25: official line-ups appear as soon as ESPN publishes them: the match page asks ESPN directly from
  90 minutes before kick-off and re-checks every 2 minutes (no waiting for a run). Display only.
- 2026-10-25: "Full table" from a match opens `#league/<CODE>/table/<home>/<away>` and highlights the two
  teams in light blue; from the league header nothing is highlighted.
- 2026-10-25: Bets page shows the health banner only when stakes are halved ("under review"); "on watch"
  is shown on the Record page only (owner request).
- 2026-10-25: merged Codex `codex/matches-redesign` (shared calendar, league pages with table and ESPN
  news, match tabs, expected line-ups) and reworked per the owner: Matches rows keep the 1/X/2
  percentages plus one slim best-pick column (code, odds, %; same height as the boxes; won = bold light
  blue ✓, lost = faint grey ✕; empty when no pick, no "Later" placeholders); scores beside the names;
  short list names for the longest clubs. Match tabs: Insights, Form & table, Stats (H2H + match stats),
  Line-ups, Overview (after kick-off: score, goals and cards with minutes, our pick's result). Played
  matches show the line-ups actually played (stored into the archive by `src/schedule.py`, or ESPN's
  match record). `predict.backfill_archive` completes older archive entries (last 14 days) with form,
  table and head-to-head as they stood BEFORE each match and the best pick from archived Betpawa prices.
- 2026-10-25: redesigned Matches around a single best-pick state, shared Bets/Matches calendar through
  the next 14 days, schedule-only "Later" rows, league fixture/table/ESPN-news pages, and URL-backed
  Insights/Line-ups/H2H/Stats/Form tabs with official or clearly labelled expected line-ups.
- 2026-10-25: FIX (settlement safety): Understat had Rennes v Paris SG (23 Aug 2026, ESPN: Rennes at home)
  as Paris SG v Rennes, which double-counted it in tables and could have settled the real reverse fixture
  later with that score. Now `merge_results` drops a same-night row matching an official match (same teams
  within 2 days, either order) and `result_lookup` settles only results within 3 days of the match date.
- 2026-10-25: data for the Matches redesign: `best_pick` per fixture (most likely slip-eligible market paying
  >= 1.20, gates/monitoring respected, owner's market priority breaks ties; display only), full league
  `tables` (P W D L GF GA GD Pts, form) including tonight's results: cross-checked with ESPN standings,
  96/96 teams identical. `src/schedule.py` (full/final runs, ~1 min): fixtures of the next 14 days and
  expected line-ups (each team's starting XI from its last league match, labelled as such) in
  web/public/data/schedule.json.
- 2026-10-25: FIX: matches already started or finished could not be opened (only upcoming ones had an id).
  The archive now keeps the full published record of each match; matches open by date and teams
  (`#matches/<day>/<home>/<away>`) on any day; Back keeps the chosen day; data files are cached in memory
  for a minute (`lib.cachedJson`), so returning to Matches is instant. Head-to-head distinguishes "not
  computed yet" from "no meetings".
- 2026-10-25: FIX (would have stopped Monday's runs): `load_fixtures` crashed once every match of a league
  had kicked off (an empty list filter made pandas select no columns); now a boolean array, with a test.
- 2026-10-25: match page: head-to-head (last 6 league meetings since 2014/15 from our own results, with a
  summary; display only, `predict.head_to_head`) and ESPN match stats once a match has started. Today's
  Matches list keeps matches already under way (from the archive) with live scores; the live feed follows
  every ESPN event of our five leagues.
- 2026-10-25: live tracking (display only; the official result still settles overnight). `src/lineups.py`
  writes ESPN event ids (`events` in lineups.json, last 18 h to next 36 h); the app (`web/src/live.ts`)
  polls ESPN scoreboards every 45 s while open and shows live minute and score on Matches, and per leg
  ✓ / ✕ / on track plus a slip state (Live x/y, Won, Lost; Flexi aware) on Bets and Money placed bets.
  Leg rules mirror `add_actuals`; own goals count for the benefiting team (as ESPN credits them).
  Verified: 69 real matches, 1,242 legs, 0 disagreements with the official settlement
  (`npm run check:live`, recorded fixture). Browser checks use a normal phone user agent: ESPN refuses
  "Headless" browsers (not real phones).
- 2026-10-25: line-ups on a full pitch by formation (Codex branch `codex/lineup-pitch`, code only; its
  local data files were not merged). Fixes before merging: left-to-right order now has five bands (wide
  left, inner left, centre, inner right, wide right; Codex's three bands put RB Hume inside CB-R
  Mukiele); surnames keep particles ("Le Fée"); the test example is the REAL ESPN line-ups of Sunderland v
  Leeds 25 Oct 2026 (Codex's example was invented). Browser check skips Flexi placement when the Big slip
  is already in play. Recovered 576 Betpawa price rows logged only by the local backup run.
- 2026-10-25: external timer live: cron-job.org job 8716884 "BetPredz" (owner's account), POST to the
  workflow_dispatch API every 30 min 06:00-23:30 Africa/Dar_es_Salaam with a fine-grained token (Actions
  read/write on betpred only). Phone notifications live (secret PUSH_SUBSCRIPTION; test sent OK).
  Workflow mode `test-notify` sends a test notification.
- 2026-10-25: monthly gate re-check workflow; gates include settled live predictions (same rules).
- 2026-10-25: Betpawa 1Up price study pre-registered and scripted (reports "insufficient" until enough
  settled data); its first draft compared against our raw probability, which a useless price could
  beat by recalibration alone. Fixed before any real data: baseline fitted the same way.
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
