# New league integration verification

Status: implementation present but acceptance INCOMPLETE. STOPPED as required; not ready to merge.

Branch: codex/new-leagues, base origin/main dea160d. No push or merge.

Live source checks on 2026-10-29:

| Code | Betpawa ID | Confirmed competition | ESPN slug | Current football-data distinct teams | ESPN logos returning HTTP 200 |
|---|---:|---|---|---:|---:|
| EREDIV | 12125 | Eredivisie | ned.1 | 18 | 18 |
| JUPILER | 12128 | Pro League | bel.1 | 18 | 18 |
| PRIMEIRA | 12124 | Liga Portugal | por.1 | 18 | 18 |
| SUPERLIG | 12182 | Super Lig | tur.1 | 18 | 18 |

Competition identities were verified by the identified Betpawa categories endpoint. Team names
were fetched from current football-data season CSVs, the identified Betpawa upcoming event-list
endpoint (50 events per competition), and ESPN teams endpoints. Requests to Betpawa were paced
at one second. Each ESPN first-logo URL was fetched and returned HTTP 200.

Historical distinct-team counts from the real study CSVs:

- N1 and P1: 18 in each season 2014/15 through 2026/27.
- B1: 16 in 2014/15 through 2019/20; 18 in 2020/21 through 2022/23; 16 in 2023/24 through
  2025/26; 18 in 2026/27.
- T1: 18 in 2014/15 through 2019/20; 21 in 2020/21; 20 in 2021/22; 19 in 2022/23;
  20 in 2023/24; 19 in 2024/25; 18 in 2025/26 and 2026/27.

## Verification outcomes

- `git fetch origin` succeeded; isolated branch starts from dea160d. No push or merge.
- Unmodified `python -m src.predict --no-refresh`: exit 0, 9 fixtures from all five original leagues,
  2,105 Betpawa prices, health ok. A separate scratch harness froze the clock, recorded real HTTP
  responses and replayed the same raw inputs after changes with only the original five leagues
  enabled. Exact equality passed for complete fixture records (including every probability) and days
  (including slips). This proves the original pool, not the enlarged nine-league pooled slip outcome.
  Scratch harness is in the task visualization folder as new_leagues_regression.py, with replay files
  in its adjacent directory. It is not used by production.
- `python -m src.new_league_setup`: exit 0. Completed-season matches: EREDIV 3598, JUPILER 3285,
  PRIMEIRA 3671, SUPERLIG 3977. Each has 8 usable calibrators. Training excludes 2026/27 and uses
  C=1.0, with fixed rho -0.054288 stored separately per league.
- `python -m src.new_league_sources`: exit 0. Real Betpawa event-list, ESPN teams and completed
  25 October responses captured. Full source aliases: new_league_team_names.md.
- `python -m pytest -q tests/test_new_league_integration.py --disable-warnings`: 17 passed.
  Real completed scores settle in temporary archives for all four leagues; reversed teams and dates
  four days later do not match. Goal timing is unknown, never invented from final scores.
- Full `python -m pytest -q --disable-warnings`: 149 passed, 4 skipped, 6237 warnings, 72.24 s.
  Four skips are the new leagues' intentionally absent Dixon-Coles backtest files.
- `python -m src.market_gates`: exit 0, retained task-13 statuses without missing-backtest crashes.
  The rerun also recalculated the original five's gates with newer live outcomes. Those changes and
  the verification-generated report were restored; only the new entries are retained. An explicit
  comparison confirms all original gates AND detail records equal the base commit.
- `npm run build`: exit 0, 47 modules transformed, production assets and PWA generated.
  Installed dependencies reused through a local junction; no package changes.
- `npx vite preview --port 4173 --host 127.0.0.1 --strictPort`: served production build.
- `BASE_URL=http://127.0.0.1:4173/ npm run check:e2e`: ALL PASSED, light/dark at 375px;
  existing conditional skips for already-started placement and unavailable archived best-pick states.

## Required refreshed run and blocker

`python -m src.predict` completed with refresh, exit 0, health ok, generated_at
2026-10-29T13:40:52.100923Z. Output counts:

| League | Upcoming predictions | Table teams |
|---|---:|---:|
| EPL | 1 | existing |
| LALIGA | 2 | existing |
| SERIEA | 2 | existing |
| BUNDES | 1 | existing |
| LIGUE1 | 3 | existing |
| EREDIV | 0 | 18 |
| JUPILER | 1 | 18 |
| PRIMEIRA | 1 | 18 |
| SUPERLIG | 3 | 18 |

2,760 Betpawa prices across 8 leagues. Explicit check found ZERO new-league blocked best picks or
slip legs. Football-data's live fixtures.csv had ZERO N1 rows; Betpawa's earliest real Eredivisie
event was 38232732, Feyenoord Rotterdam v Fortuna Sittard, 2026-10-31T15:30:00Z. This is outside
the unchanged 48-hour fallback horizon at the run time. No dates, odds or fixtures were invented.

Verification step 3 therefore cannot pass for ALL four leagues on this run. Per the prompt's STOP
rule, implementation stopped. `node e2e/new-leagues.check.mjs` exited 1 with
`No real upcoming EREDIV prediction`, before screenshots; the requested new-league screenshot
acceptance is NOT complete. No new-league match/table screenshots are claimed. Repeat on real
data when a priced N1 fixture is published or is inside the existing fallback window. Do not widen
the horizon based on this failure. Tracked publication/live files are restored after verification.

## Files and purpose

- new_league_config.py: verified identifiers, fixed rho and validated-market restrictions.
- leagues.py: four no-Understat registry entries and observed size changes.
- football_only.py: cached football-data history, strict names, completed ESPN results and known
  score-derived outcomes; goal timing remains null.
- new_league_setup.py: offline completed-season-only calibration/rho/metadata and gate installation.
- new_league_sources.py and tests/fixtures/new_leagues: real source evidence, no edited fixture values.
- market_live.py: market mode and saved rho for new leagues; existing paths unchanged.
- build_dataset.py/fetch_understat.py: route new leagues without Understat and reject unsupported calls.
- predict.py: new-league results/fixtures, nearby dated settlement, blocked NOT_VALIDATED markets.
- betpawa.py: unknown new-league names skip only that event; strict legacy behavior retained.
- health.py: ignore unknown outcome values rather than counting them as losses.
- market_gates.py: retain task-13 gate entries without requiring new-league backtest leg files.
- lineups.py: four verified ESPN slugs, reused by schedule.py; no schedule algorithm changes.
- scripts/run_mode.py: four divisions only; no timing changes.
- web/src/matchData.ts/badgeUrls.json: league names/slugs and 72 verified ESPN logos.
- test_leagues.py/test_new_league_integration.py: registry, real names, calibration cutoff, restricted
  picks, exact dates and real-score temporary archive checks.
- web/e2e/new-leagues.check.mjs: real-output acceptance and screenshot check; honestly fails if missing.
- data/processed/<new code>/{market_calibrators,rho,setup}.json: required offline setup outputs.
- data/raw/football_data/{N1,B1,P1,T1}_*.csv: required source history cache.
- PROJECT.md and these reports: verified evidence, known limitation, incomplete acceptance status.
