# Daily Trial slip design, margin check, and dry run (PROJECT.md task 27)

Generated: **2026-11-23 13:02 EAT** | Cached `predictions.json` generated: **2026-11-23 07:02 EAT**.

> **Research & dry run only**: nothing here is live. `web/public/data`, `engine/data/live`, `predict.py`, `accumulators.py`, `market_gates.json`, and `web/` are untouched.
> **Scope & honesty**: the Trial slip does **not** collect more data than research price logging already does, and it does **not** prove profitability or an edge. Stake cap is fixed by the owner at **1% of balance (`0.01`)** per Trial slip.

## Step 2 — Betpawa margin check (read-only, last snapshot before kick-off)

Overround = `sum(1 / odds) - 1` computed strictly on complete mutually exclusive outcome sets logged before kick-off (`snapshot_utc < kickoff_utc`, `odds > 1.0`).

### Complete outcome sets (measurable overround)

| League group | Outcome set | Logged markets | Matches (n) | Mean overround | 10th pct | 90th pct |
|---|---|---|---:|---:|---:|---:|
| Main nine | `over_under_2.5` | `over_2.5`, `under_2.5` | 278 | +4.01% | +3.87% | +4.18% |
| Main nine | `dnb` | `dnb_home`, `dnb_away` | 246 | +5.01% | +4.83% | +5.25% |
| Main nine | `interval_10_1x2` | `interval_10_home`, `interval_10_draw`, `interval_10_away` | 41 | +7.01% | +6.78% | +7.26% |
| Research leagues | `1x2` | `home_win`, `draw`, `away_win` | 45 | +3.82% | +1.96% | +5.75% |
| Research leagues | `over_under_2.5` | `over_2.5`, `under_2.5` | 45 | +4.74% | +3.93% | +6.00% |
| Research leagues | `dnb` | `dnb_home`, `dnb_away` | 45 | +5.18% | +4.85% | +5.75% |

Notes on complete sets:
- `main nine` (`engine/data/live/prices`) logs `SLIP_MARKETS` + `RESEARCH_MARKETS`; `draw` is not in `SLIP_MARKETS`, so full `1x2` overround is not measurable from `engine/data/live/prices` (while `engine/data/live/research/prices` logs `home_win`, `draw`, `away_win`, `over_2.5`, `under_2.5` + `RESEARCH_MARKETS`, making `1x2` measurable there).
- `double_1x`, `double_x2`, `double_12` overlap pairwise (each 1X2 outcome appears in two selections, so probabilities sum to 2, not 1) and are therefore not included in the `sum(1/odds) - 1` table.
- `first_goal_home` / `first_goal_away` omit the third outcome (`None`, 0-0), and `home_2up` / `away_2up` omit draw, so their overrounds are not measurable.

### Markets without a complete complementary set logged (`margin not measurable`)

| Market | Main nine logged matches | Research leagues logged matches | Margin status |
|---|---:|---:|---|
| `away_1up` | 278 | 0 | margin not measurable |
| `away_2up` | 146 | 44 | margin not measurable |
| `away_fh_over_0.5` | 115 | 20 | margin not measurable |
| `away_over_0.5` | 243 | 44 | margin not measurable |
| `away_over_1.5` | 245 | 45 | margin not measurable |
| `away_score_both_halves` | 115 | 45 | margin not measurable |
| `away_sh_over_0.5` | 115 | 20 | margin not measurable |
| `away_win` | 278 | 0 | margin not measurable |
| `away_win_both_halves` | 105 | 32 | margin not measurable |
| `away_win_either_half` | 146 | 38 | margin not measurable |
| `dc1up_12` | 109 | 35 | margin not measurable |
| `dc1up_1x` | 142 | 44 | margin not measurable |
| `dc1up_x2` | 146 | 44 | margin not measurable |
| `double_12` | 278 | 0 | margin not measurable |
| `double_1x` | 278 | 0 | margin not measurable |
| `double_x2` | 278 | 0 | margin not measurable |
| `fh_over_0.5` | 146 | 45 | margin not measurable |
| `fh_over_1.5` | 146 | 45 | margin not measurable |
| `first_goal_away` | 115 | 45 | margin not measurable |
| `first_goal_home` | 115 | 45 | margin not measurable |
| `home_1up` | 278 | 0 | margin not measurable |
| `home_2up` | 146 | 44 | margin not measurable |
| `home_fh_over_0.5` | 115 | 20 | margin not measurable |
| `home_over_0.5` | 232 | 41 | margin not measurable |
| `home_over_1.5` | 245 | 45 | margin not measurable |
| `home_score_both_halves` | 115 | 45 | margin not measurable |
| `home_sh_over_0.5` | 114 | 20 | margin not measurable |
| `home_win` | 278 | 0 | margin not measurable |
| `home_win_both_halves` | 114 | 43 | margin not measurable |
| `home_win_either_half` | 146 | 38 | margin not measurable |
| `over_0.5` | 276 | 0 | margin not measurable |
| `over_1.5` | 278 | 0 | margin not measurable |
| `sh_over_0.5` | 146 | 45 | margin not measurable |
| `sh_over_1.5` | 146 | 45 | margin not measurable |
| `under_3.5` | 278 | 0 | margin not measurable |

## Step 3 — TRIAL-ELIGIBLE list (Strong candidates only)

Total TRIAL-ELIGIBLE pairs: **150** across 24 distinct markets (`task16_half`: 44, `task17_up`: 24, `task20_timing`: 24, `task20_team_half`: 58).

### Explicit exclusions in v1
- **Draw No Bet (`dnb_home`, `dnb_away`)**: excluded in v1 because a draw refunds the leg at odds `1.00`, and `accumulators.best_slip` / slip win-probability maths do not implement push/refund legs (`new_markets_study.md:9-10, 15-16, 21-22, 27-28, 33-34`).
- **Team overs from Task 10 (`home_over_0.5`, `away_over_0.5`, `home_over_1.5`, `away_over_1.5`)**: excluded in v1 because Task 10 (`new_markets_study.md`) was evaluated on `2024/25+` only and has **no `2019/20-2023/24` replication report** in `engine/reports/` (`19` pairs passed `2024/25+`, `SERIEA home_over_0.5` FAILED at `new_markets_study.md:17`). Per the pre-registered rule, only pairs that passed BOTH original and replication periods (`Strong candidates`) enter v1.
- **Other excluded pairs (failed original or replication gate)**: 26 pairs across Tasks 16, 17, and 20.

### Complete TRIAL-ELIGIBLE table (with source file and line)

| # | League | Market | Family | Original source | Replication source |
|---:|---|---|---|---|---|
| 1 | EPL | `fh_over_0.5` | `task16_half` | `half_markets_study.md:10` | `tasks_16_17_replication.md:16` |
| 2 | EPL | `sh_over_1.5` | `task16_half` | `half_markets_study.md:13` | `tasks_16_17_replication.md:19` |
| 3 | EPL | `home_win_either_half` | `task16_half` | `half_markets_study.md:14` | `tasks_16_17_replication.md:20` |
| 4 | EPL | `away_win_either_half` | `task16_half` | `half_markets_study.md:15` | `tasks_16_17_replication.md:21` |
| 5 | LALIGA | `fh_over_0.5` | `task16_half` | `half_markets_study.md:16` | `tasks_16_17_replication.md:22` |
| 6 | LALIGA | `fh_over_1.5` | `task16_half` | `half_markets_study.md:17` | `tasks_16_17_replication.md:23` |
| 7 | LALIGA | `sh_over_0.5` | `task16_half` | `half_markets_study.md:18` | `tasks_16_17_replication.md:24` |
| 8 | LALIGA | `away_win_either_half` | `task16_half` | `half_markets_study.md:21` | `tasks_16_17_replication.md:27` |
| 9 | SERIEA | `fh_over_0.5` | `task16_half` | `half_markets_study.md:22` | `tasks_16_17_replication.md:28` |
| 10 | SERIEA | `fh_over_1.5` | `task16_half` | `half_markets_study.md:23` | `tasks_16_17_replication.md:29` |
| 11 | SERIEA | `sh_over_0.5` | `task16_half` | `half_markets_study.md:24` | `tasks_16_17_replication.md:30` |
| 12 | SERIEA | `sh_over_1.5` | `task16_half` | `half_markets_study.md:25` | `tasks_16_17_replication.md:31` |
| 13 | SERIEA | `home_win_either_half` | `task16_half` | `half_markets_study.md:26` | `tasks_16_17_replication.md:32` |
| 14 | SERIEA | `away_win_either_half` | `task16_half` | `half_markets_study.md:27` | `tasks_16_17_replication.md:33` |
| 15 | BUNDES | `fh_over_0.5` | `task16_half` | `half_markets_study.md:28` | `tasks_16_17_replication.md:34` |
| 16 | BUNDES | `fh_over_1.5` | `task16_half` | `half_markets_study.md:29` | `tasks_16_17_replication.md:35` |
| 17 | BUNDES | `sh_over_0.5` | `task16_half` | `half_markets_study.md:30` | `tasks_16_17_replication.md:36` |
| 18 | BUNDES | `sh_over_1.5` | `task16_half` | `half_markets_study.md:31` | `tasks_16_17_replication.md:37` |
| 19 | BUNDES | `home_win_either_half` | `task16_half` | `half_markets_study.md:32` | `tasks_16_17_replication.md:38` |
| 20 | BUNDES | `away_win_either_half` | `task16_half` | `half_markets_study.md:33` | `tasks_16_17_replication.md:39` |
| 21 | LIGUE1 | `fh_over_0.5` | `task16_half` | `half_markets_study.md:34` | `tasks_16_17_replication.md:40` |
| 22 | LIGUE1 | `fh_over_1.5` | `task16_half` | `half_markets_study.md:35` | `tasks_16_17_replication.md:41` |
| 23 | LIGUE1 | `sh_over_0.5` | `task16_half` | `half_markets_study.md:36` | `tasks_16_17_replication.md:42` |
| 24 | LIGUE1 | `sh_over_1.5` | `task16_half` | `half_markets_study.md:37` | `tasks_16_17_replication.md:43` |
| 25 | LIGUE1 | `home_win_either_half` | `task16_half` | `half_markets_study.md:38` | `tasks_16_17_replication.md:44` |
| 26 | LIGUE1 | `away_win_either_half` | `task16_half` | `half_markets_study.md:39` | `tasks_16_17_replication.md:45` |
| 27 | EREDIV | `fh_over_0.5` | `task16_half` | `half_markets_study.md:40` | `tasks_16_17_replication.md:46` |
| 28 | EREDIV | `fh_over_1.5` | `task16_half` | `half_markets_study.md:41` | `tasks_16_17_replication.md:47` |
| 29 | EREDIV | `sh_over_0.5` | `task16_half` | `half_markets_study.md:42` | `tasks_16_17_replication.md:48` |
| 30 | EREDIV | `home_win_either_half` | `task16_half` | `half_markets_study.md:44` | `tasks_16_17_replication.md:50` |
| 31 | EREDIV | `away_win_either_half` | `task16_half` | `half_markets_study.md:45` | `tasks_16_17_replication.md:51` |
| 32 | JUPILER | `fh_over_0.5` | `task16_half` | `half_markets_study.md:46` | `tasks_16_17_replication.md:52` |
| 33 | JUPILER | `fh_over_1.5` | `task16_half` | `half_markets_study.md:47` | `tasks_16_17_replication.md:53` |
| 34 | JUPILER | `sh_over_1.5` | `task16_half` | `half_markets_study.md:49` | `tasks_16_17_replication.md:55` |
| 35 | JUPILER | `home_win_either_half` | `task16_half` | `half_markets_study.md:50` | `tasks_16_17_replication.md:56` |
| 36 | JUPILER | `away_win_either_half` | `task16_half` | `half_markets_study.md:51` | `tasks_16_17_replication.md:57` |
| 37 | PRIMEIRA | `sh_over_0.5` | `task16_half` | `half_markets_study.md:54` | `tasks_16_17_replication.md:60` |
| 38 | PRIMEIRA | `sh_over_1.5` | `task16_half` | `half_markets_study.md:55` | `tasks_16_17_replication.md:61` |
| 39 | PRIMEIRA | `home_win_either_half` | `task16_half` | `half_markets_study.md:56` | `tasks_16_17_replication.md:62` |
| 40 | PRIMEIRA | `away_win_either_half` | `task16_half` | `half_markets_study.md:57` | `tasks_16_17_replication.md:63` |
| 41 | SUPERLIG | `sh_over_0.5` | `task16_half` | `half_markets_study.md:60` | `tasks_16_17_replication.md:66` |
| 42 | SUPERLIG | `sh_over_1.5` | `task16_half` | `half_markets_study.md:61` | `tasks_16_17_replication.md:67` |
| 43 | SUPERLIG | `home_win_either_half` | `task16_half` | `half_markets_study.md:62` | `tasks_16_17_replication.md:68` |
| 44 | SUPERLIG | `away_win_either_half` | `task16_half` | `half_markets_study.md:63` | `tasks_16_17_replication.md:69` |
| 45 | EPL | `dc1up_1x` | `task17_up` | `up_markets_study.md:40` | `tasks_16_17_replication.md:74` |
| 46 | EPL | `dc1up_x2` | `task17_up` | `up_markets_study.md:41` | `tasks_16_17_replication.md:75` |
| 47 | EPL | `dc1up_12` | `task17_up` | `up_markets_study.md:42` | `tasks_16_17_replication.md:76` |
| 48 | EPL | `away_2up` | `task17_up` | `up_markets_study.md:44` | `tasks_16_17_replication.md:78` |
| 49 | LALIGA | `dc1up_1x` | `task17_up` | `up_markets_study.md:45` | `tasks_16_17_replication.md:79` |
| 50 | LALIGA | `dc1up_x2` | `task17_up` | `up_markets_study.md:46` | `tasks_16_17_replication.md:80` |
| 51 | LALIGA | `dc1up_12` | `task17_up` | `up_markets_study.md:47` | `tasks_16_17_replication.md:81` |
| 52 | LALIGA | `home_2up` | `task17_up` | `up_markets_study.md:48` | `tasks_16_17_replication.md:82` |
| 53 | LALIGA | `away_2up` | `task17_up` | `up_markets_study.md:49` | `tasks_16_17_replication.md:83` |
| 54 | SERIEA | `dc1up_1x` | `task17_up` | `up_markets_study.md:50` | `tasks_16_17_replication.md:84` |
| 55 | SERIEA | `dc1up_x2` | `task17_up` | `up_markets_study.md:51` | `tasks_16_17_replication.md:85` |
| 56 | SERIEA | `dc1up_12` | `task17_up` | `up_markets_study.md:52` | `tasks_16_17_replication.md:86` |
| 57 | SERIEA | `home_2up` | `task17_up` | `up_markets_study.md:53` | `tasks_16_17_replication.md:87` |
| 58 | SERIEA | `away_2up` | `task17_up` | `up_markets_study.md:54` | `tasks_16_17_replication.md:88` |
| 59 | BUNDES | `dc1up_1x` | `task17_up` | `up_markets_study.md:55` | `tasks_16_17_replication.md:89` |
| 60 | BUNDES | `dc1up_x2` | `task17_up` | `up_markets_study.md:56` | `tasks_16_17_replication.md:90` |
| 61 | BUNDES | `dc1up_12` | `task17_up` | `up_markets_study.md:57` | `tasks_16_17_replication.md:91` |
| 62 | BUNDES | `home_2up` | `task17_up` | `up_markets_study.md:58` | `tasks_16_17_replication.md:92` |
| 63 | BUNDES | `away_2up` | `task17_up` | `up_markets_study.md:59` | `tasks_16_17_replication.md:93` |
| 64 | LIGUE1 | `dc1up_1x` | `task17_up` | `up_markets_study.md:60` | `tasks_16_17_replication.md:94` |
| 65 | LIGUE1 | `dc1up_x2` | `task17_up` | `up_markets_study.md:61` | `tasks_16_17_replication.md:95` |
| 66 | LIGUE1 | `dc1up_12` | `task17_up` | `up_markets_study.md:62` | `tasks_16_17_replication.md:96` |
| 67 | LIGUE1 | `home_2up` | `task17_up` | `up_markets_study.md:63` | `tasks_16_17_replication.md:97` |
| 68 | LIGUE1 | `away_2up` | `task17_up` | `up_markets_study.md:64` | `tasks_16_17_replication.md:98` |
| 69 | EPL | `first_goal_home` | `task20_timing` | `timing_half_markets_study.md:19` | `timing_half_markets_study.md:19` |
| 70 | EPL | `first_goal_away` | `task20_timing` | `timing_half_markets_study.md:20` | `timing_half_markets_study.md:20` |
| 71 | EPL | `interval_10_home` | `task20_timing` | `timing_half_markets_study.md:21` | `timing_half_markets_study.md:21` |
| 72 | EPL | `interval_10_draw` | `task20_timing` | `timing_half_markets_study.md:22` | `timing_half_markets_study.md:22` |
| 73 | EPL | `interval_10_away` | `task20_timing` | `timing_half_markets_study.md:23` | `timing_half_markets_study.md:23` |
| 74 | LALIGA | `first_goal_home` | `task20_timing` | `timing_half_markets_study.md:24` | `timing_half_markets_study.md:24` |
| 75 | LALIGA | `first_goal_away` | `task20_timing` | `timing_half_markets_study.md:25` | `timing_half_markets_study.md:25` |
| 76 | LALIGA | `interval_10_home` | `task20_timing` | `timing_half_markets_study.md:26` | `timing_half_markets_study.md:26` |
| 77 | LALIGA | `interval_10_draw` | `task20_timing` | `timing_half_markets_study.md:27` | `timing_half_markets_study.md:27` |
| 78 | LALIGA | `interval_10_away` | `task20_timing` | `timing_half_markets_study.md:28` | `timing_half_markets_study.md:28` |
| 79 | SERIEA | `first_goal_home` | `task20_timing` | `timing_half_markets_study.md:29` | `timing_half_markets_study.md:29` |
| 80 | SERIEA | `first_goal_away` | `task20_timing` | `timing_half_markets_study.md:30` | `timing_half_markets_study.md:30` |
| 81 | SERIEA | `interval_10_home` | `task20_timing` | `timing_half_markets_study.md:31` | `timing_half_markets_study.md:31` |
| 82 | SERIEA | `interval_10_draw` | `task20_timing` | `timing_half_markets_study.md:32` | `timing_half_markets_study.md:32` |
| 83 | SERIEA | `interval_10_away` | `task20_timing` | `timing_half_markets_study.md:33` | `timing_half_markets_study.md:33` |
| 84 | BUNDES | `first_goal_home` | `task20_timing` | `timing_half_markets_study.md:34` | `timing_half_markets_study.md:34` |
| 85 | BUNDES | `first_goal_away` | `task20_timing` | `timing_half_markets_study.md:35` | `timing_half_markets_study.md:35` |
| 86 | BUNDES | `interval_10_home` | `task20_timing` | `timing_half_markets_study.md:36` | `timing_half_markets_study.md:36` |
| 87 | BUNDES | `interval_10_draw` | `task20_timing` | `timing_half_markets_study.md:37` | `timing_half_markets_study.md:37` |
| 88 | BUNDES | `interval_10_away` | `task20_timing` | `timing_half_markets_study.md:38` | `timing_half_markets_study.md:38` |
| 89 | LIGUE1 | `first_goal_away` | `task20_timing` | `timing_half_markets_study.md:40` | `timing_half_markets_study.md:40` |
| 90 | LIGUE1 | `interval_10_home` | `task20_timing` | `timing_half_markets_study.md:41` | `timing_half_markets_study.md:41` |
| 91 | LIGUE1 | `interval_10_draw` | `task20_timing` | `timing_half_markets_study.md:42` | `timing_half_markets_study.md:42` |
| 92 | LIGUE1 | `interval_10_away` | `task20_timing` | `timing_half_markets_study.md:43` | `timing_half_markets_study.md:43` |
| 93 | EPL | `home_score_both_halves` | `task20_team_half` | `timing_half_markets_study.md:48` | `timing_half_markets_study.md:48` |
| 94 | EPL | `away_score_both_halves` | `task20_team_half` | `timing_half_markets_study.md:49` | `timing_half_markets_study.md:49` |
| 95 | EPL | `home_win_both_halves` | `task20_team_half` | `timing_half_markets_study.md:50` | `timing_half_markets_study.md:50` |
| 96 | EPL | `away_win_both_halves` | `task20_team_half` | `timing_half_markets_study.md:51` | `timing_half_markets_study.md:51` |
| 97 | EPL | `home_fh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:52` | `timing_half_markets_study.md:52` |
| 98 | EPL | `away_fh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:53` | `timing_half_markets_study.md:53` |
| 99 | EPL | `away_sh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:55` | `timing_half_markets_study.md:55` |
| 100 | LALIGA | `home_score_both_halves` | `task20_team_half` | `timing_half_markets_study.md:56` | `timing_half_markets_study.md:56` |
| 101 | LALIGA | `away_score_both_halves` | `task20_team_half` | `timing_half_markets_study.md:57` | `timing_half_markets_study.md:57` |
| 102 | LALIGA | `home_win_both_halves` | `task20_team_half` | `timing_half_markets_study.md:58` | `timing_half_markets_study.md:58` |
| 103 | LALIGA | `home_fh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:60` | `timing_half_markets_study.md:60` |
| 104 | LALIGA | `away_fh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:61` | `timing_half_markets_study.md:61` |
| 105 | LALIGA | `home_sh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:62` | `timing_half_markets_study.md:62` |
| 106 | LALIGA | `away_sh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:63` | `timing_half_markets_study.md:63` |
| 107 | SERIEA | `home_score_both_halves` | `task20_team_half` | `timing_half_markets_study.md:64` | `timing_half_markets_study.md:64` |
| 108 | SERIEA | `away_score_both_halves` | `task20_team_half` | `timing_half_markets_study.md:65` | `timing_half_markets_study.md:65` |
| 109 | SERIEA | `home_win_both_halves` | `task20_team_half` | `timing_half_markets_study.md:66` | `timing_half_markets_study.md:66` |
| 110 | SERIEA | `away_win_both_halves` | `task20_team_half` | `timing_half_markets_study.md:67` | `timing_half_markets_study.md:67` |
| 111 | SERIEA | `home_fh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:68` | `timing_half_markets_study.md:68` |
| 112 | SERIEA | `away_fh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:69` | `timing_half_markets_study.md:69` |
| 113 | SERIEA | `away_sh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:71` | `timing_half_markets_study.md:71` |
| 114 | BUNDES | `home_score_both_halves` | `task20_team_half` | `timing_half_markets_study.md:72` | `timing_half_markets_study.md:72` |
| 115 | BUNDES | `away_score_both_halves` | `task20_team_half` | `timing_half_markets_study.md:73` | `timing_half_markets_study.md:73` |
| 116 | BUNDES | `home_win_both_halves` | `task20_team_half` | `timing_half_markets_study.md:74` | `timing_half_markets_study.md:74` |
| 117 | BUNDES | `away_win_both_halves` | `task20_team_half` | `timing_half_markets_study.md:75` | `timing_half_markets_study.md:75` |
| 118 | BUNDES | `home_fh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:76` | `timing_half_markets_study.md:76` |
| 119 | BUNDES | `away_fh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:77` | `timing_half_markets_study.md:77` |
| 120 | BUNDES | `home_sh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:78` | `timing_half_markets_study.md:78` |
| 121 | BUNDES | `away_sh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:79` | `timing_half_markets_study.md:79` |
| 122 | LIGUE1 | `away_score_both_halves` | `task20_team_half` | `timing_half_markets_study.md:81` | `timing_half_markets_study.md:81` |
| 123 | LIGUE1 | `home_win_both_halves` | `task20_team_half` | `timing_half_markets_study.md:82` | `timing_half_markets_study.md:82` |
| 124 | LIGUE1 | `away_win_both_halves` | `task20_team_half` | `timing_half_markets_study.md:83` | `timing_half_markets_study.md:83` |
| 125 | LIGUE1 | `home_fh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:84` | `timing_half_markets_study.md:84` |
| 126 | LIGUE1 | `away_fh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:85` | `timing_half_markets_study.md:85` |
| 127 | LIGUE1 | `away_sh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:87` | `timing_half_markets_study.md:87` |
| 128 | EREDIV | `home_score_both_halves` | `task20_team_half` | `timing_half_markets_study.md:88` | `timing_half_markets_study.md:88` |
| 129 | EREDIV | `away_score_both_halves` | `task20_team_half` | `timing_half_markets_study.md:89` | `timing_half_markets_study.md:89` |
| 130 | EREDIV | `home_win_both_halves` | `task20_team_half` | `timing_half_markets_study.md:90` | `timing_half_markets_study.md:90` |
| 131 | EREDIV | `away_win_both_halves` | `task20_team_half` | `timing_half_markets_study.md:91` | `timing_half_markets_study.md:91` |
| 132 | EREDIV | `home_fh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:92` | `timing_half_markets_study.md:92` |
| 133 | EREDIV | `away_fh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:93` | `timing_half_markets_study.md:93` |
| 134 | EREDIV | `home_sh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:94` | `timing_half_markets_study.md:94` |
| 135 | EREDIV | `away_sh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:95` | `timing_half_markets_study.md:95` |
| 136 | JUPILER | `home_score_both_halves` | `task20_team_half` | `timing_half_markets_study.md:96` | `timing_half_markets_study.md:96` |
| 137 | JUPILER | `away_score_both_halves` | `task20_team_half` | `timing_half_markets_study.md:97` | `timing_half_markets_study.md:97` |
| 138 | JUPILER | `home_win_both_halves` | `task20_team_half` | `timing_half_markets_study.md:98` | `timing_half_markets_study.md:98` |
| 139 | JUPILER | `home_fh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:100` | `timing_half_markets_study.md:100` |
| 140 | PRIMEIRA | `away_score_both_halves` | `task20_team_half` | `timing_half_markets_study.md:105` | `timing_half_markets_study.md:105` |
| 141 | PRIMEIRA | `away_fh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:109` | `timing_half_markets_study.md:109` |
| 142 | PRIMEIRA | `home_sh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:110` | `timing_half_markets_study.md:110` |
| 143 | PRIMEIRA | `away_sh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:111` | `timing_half_markets_study.md:111` |
| 144 | SUPERLIG | `home_score_both_halves` | `task20_team_half` | `timing_half_markets_study.md:112` | `timing_half_markets_study.md:112` |
| 145 | SUPERLIG | `away_score_both_halves` | `task20_team_half` | `timing_half_markets_study.md:113` | `timing_half_markets_study.md:113` |
| 146 | SUPERLIG | `home_win_both_halves` | `task20_team_half` | `timing_half_markets_study.md:114` | `timing_half_markets_study.md:114` |
| 147 | SUPERLIG | `away_win_both_halves` | `task20_team_half` | `timing_half_markets_study.md:115` | `timing_half_markets_study.md:115` |
| 148 | SUPERLIG | `home_fh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:116` | `timing_half_markets_study.md:116` |
| 149 | SUPERLIG | `home_sh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:118` | `timing_half_markets_study.md:118` |
| 150 | SUPERLIG | `away_sh_over_0.5` | `task20_team_half` | `timing_half_markets_study.md:119` | `timing_half_markets_study.md:119` |

### Excluded pairs audit (Tasks 10, 16, 17, 20)

| League | Market | Family | Reason | Source |
|---|---|---|---|---|
| EPL | `fh_over_1.5` | `task16_half` | gate status original=FAIL, primary=FAIL, replication=PASS | `half_markets_study.md:11; tasks_16_17_replication.md:17` |
| EPL | `sh_over_0.5` | `task16_half` | gate status original=FAIL, primary=FAIL, replication=PASS | `half_markets_study.md:12; tasks_16_17_replication.md:18` |
| LALIGA | `sh_over_1.5` | `task16_half` | gate status original=PASS, primary=PASS, replication=FAIL | `half_markets_study.md:19; tasks_16_17_replication.md:25` |
| LALIGA | `home_win_either_half` | `task16_half` | gate status original=PASS, primary=PASS, replication=FAIL | `half_markets_study.md:20; tasks_16_17_replication.md:26` |
| EREDIV | `sh_over_1.5` | `task16_half` | gate status original=FAIL, primary=FAIL, replication=PASS | `half_markets_study.md:43; tasks_16_17_replication.md:49` |
| JUPILER | `sh_over_0.5` | `task16_half` | gate status original=FAIL, primary=FAIL, replication=PASS | `half_markets_study.md:48; tasks_16_17_replication.md:54` |
| PRIMEIRA | `fh_over_0.5` | `task16_half` | gate status original=FAIL, primary=FAIL, replication=FAIL | `half_markets_study.md:52; tasks_16_17_replication.md:58` |
| PRIMEIRA | `fh_over_1.5` | `task16_half` | gate status original=PASS, primary=PASS, replication=FAIL | `half_markets_study.md:53; tasks_16_17_replication.md:59` |
| SUPERLIG | `fh_over_0.5` | `task16_half` | gate status original=PASS, primary=PASS, replication=FAIL | `half_markets_study.md:58; tasks_16_17_replication.md:64` |
| SUPERLIG | `fh_over_1.5` | `task16_half` | gate status original=PASS, primary=PASS, replication=FAIL | `half_markets_study.md:59; tasks_16_17_replication.md:65` |
| EPL | `home_2up` | `task17_up` | gate status original=FAIL, primary=FAIL, replication=PASS | `up_markets_study.md:43; tasks_16_17_replication.md:77` |
| LIGUE1 | `first_goal_home` | `task20_timing` | gate status primary=PASS, replication=FAIL | `timing_half_markets_study.md:39` |
| EPL | `home_sh_over_0.5` | `task20_team_half` | gate status primary=FAIL, replication=FAIL | `timing_half_markets_study.md:54` |
| LALIGA | `away_win_both_halves` | `task20_team_half` | gate status primary=FAIL, replication=PASS | `timing_half_markets_study.md:59` |
| SERIEA | `home_sh_over_0.5` | `task20_team_half` | gate status primary=PASS, replication=FAIL | `timing_half_markets_study.md:70` |
| LIGUE1 | `home_score_both_halves` | `task20_team_half` | gate status primary=PASS, replication=FAIL | `timing_half_markets_study.md:80` |
| LIGUE1 | `home_sh_over_0.5` | `task20_team_half` | gate status primary=PASS, replication=FAIL | `timing_half_markets_study.md:86` |
| JUPILER | `away_win_both_halves` | `task20_team_half` | gate status primary=FAIL, replication=PASS | `timing_half_markets_study.md:99` |
| JUPILER | `away_fh_over_0.5` | `task20_team_half` | gate status primary=PASS, replication=FAIL | `timing_half_markets_study.md:101` |
| JUPILER | `home_sh_over_0.5` | `task20_team_half` | gate status primary=PASS, replication=FAIL | `timing_half_markets_study.md:102` |
| JUPILER | `away_sh_over_0.5` | `task20_team_half` | gate status primary=FAIL, replication=PASS | `timing_half_markets_study.md:103` |
| PRIMEIRA | `home_score_both_halves` | `task20_team_half` | gate status primary=PASS, replication=FAIL | `timing_half_markets_study.md:104` |
| PRIMEIRA | `home_win_both_halves` | `task20_team_half` | gate status primary=PASS, replication=FAIL | `timing_half_markets_study.md:106` |
| PRIMEIRA | `away_win_both_halves` | `task20_team_half` | gate status primary=PASS, replication=FAIL | `timing_half_markets_study.md:107` |
| PRIMEIRA | `home_fh_over_0.5` | `task20_team_half` | gate status primary=PASS, replication=FAIL | `timing_half_markets_study.md:108` |
| SUPERLIG | `away_fh_over_0.5` | `task20_team_half` | gate status primary=PASS, replication=FAIL | `timing_half_markets_study.md:117` |
| EPL | `home_over_0.5` | `task10_team_goals_dnb` | excluded in v1: passed 2024/25+ in new_markets_study.md, but no 2019/20-2023/24 replication report exists in engine/reports/ | `new_markets_study.md:5` |
| EPL | `away_over_0.5` | `task10_team_goals_dnb` | excluded in v1: passed 2024/25+ in new_markets_study.md, but no 2019/20-2023/24 replication report exists in engine/reports/ | `new_markets_study.md:6` |
| EPL | `home_over_1.5` | `task10_team_goals_dnb` | excluded in v1: passed 2024/25+ in new_markets_study.md, but no 2019/20-2023/24 replication report exists in engine/reports/ | `new_markets_study.md:7` |
| EPL | `away_over_1.5` | `task10_team_goals_dnb` | excluded in v1: passed 2024/25+ in new_markets_study.md, but no 2019/20-2023/24 replication report exists in engine/reports/ | `new_markets_study.md:8` |
| EPL | `dnb_home` | `task10_team_goals_dnb` | excluded in v1: Draw No Bet refunds the leg at odds 1.00 on a draw (slip maths not implemented); task 10 gate=PASS | `new_markets_study.md:9` |
| EPL | `dnb_away` | `task10_team_goals_dnb` | excluded in v1: Draw No Bet refunds the leg at odds 1.00 on a draw (slip maths not implemented); task 10 gate=PASS | `new_markets_study.md:10` |
| LALIGA | `home_over_0.5` | `task10_team_goals_dnb` | excluded in v1: passed 2024/25+ in new_markets_study.md, but no 2019/20-2023/24 replication report exists in engine/reports/ | `new_markets_study.md:11` |
| LALIGA | `away_over_0.5` | `task10_team_goals_dnb` | excluded in v1: passed 2024/25+ in new_markets_study.md, but no 2019/20-2023/24 replication report exists in engine/reports/ | `new_markets_study.md:12` |
| LALIGA | `home_over_1.5` | `task10_team_goals_dnb` | excluded in v1: passed 2024/25+ in new_markets_study.md, but no 2019/20-2023/24 replication report exists in engine/reports/ | `new_markets_study.md:13` |
| LALIGA | `away_over_1.5` | `task10_team_goals_dnb` | excluded in v1: passed 2024/25+ in new_markets_study.md, but no 2019/20-2023/24 replication report exists in engine/reports/ | `new_markets_study.md:14` |
| LALIGA | `dnb_home` | `task10_team_goals_dnb` | excluded in v1: Draw No Bet refunds the leg at odds 1.00 on a draw (slip maths not implemented); task 10 gate=PASS | `new_markets_study.md:15` |
| LALIGA | `dnb_away` | `task10_team_goals_dnb` | excluded in v1: Draw No Bet refunds the leg at odds 1.00 on a draw (slip maths not implemented); task 10 gate=PASS | `new_markets_study.md:16` |
| SERIEA | `home_over_0.5` | `task10_team_goals_dnb` | task 10 gate=FAIL (and no replication-period report in repo) | `new_markets_study.md:17` |
| SERIEA | `away_over_0.5` | `task10_team_goals_dnb` | excluded in v1: passed 2024/25+ in new_markets_study.md, but no 2019/20-2023/24 replication report exists in engine/reports/ | `new_markets_study.md:18` |
| SERIEA | `home_over_1.5` | `task10_team_goals_dnb` | excluded in v1: passed 2024/25+ in new_markets_study.md, but no 2019/20-2023/24 replication report exists in engine/reports/ | `new_markets_study.md:19` |
| SERIEA | `away_over_1.5` | `task10_team_goals_dnb` | excluded in v1: passed 2024/25+ in new_markets_study.md, but no 2019/20-2023/24 replication report exists in engine/reports/ | `new_markets_study.md:20` |
| SERIEA | `dnb_home` | `task10_team_goals_dnb` | excluded in v1: Draw No Bet refunds the leg at odds 1.00 on a draw (slip maths not implemented); task 10 gate=PASS | `new_markets_study.md:21` |
| SERIEA | `dnb_away` | `task10_team_goals_dnb` | excluded in v1: Draw No Bet refunds the leg at odds 1.00 on a draw (slip maths not implemented); task 10 gate=PASS | `new_markets_study.md:22` |
| BUNDES | `home_over_0.5` | `task10_team_goals_dnb` | excluded in v1: passed 2024/25+ in new_markets_study.md, but no 2019/20-2023/24 replication report exists in engine/reports/ | `new_markets_study.md:23` |
| BUNDES | `away_over_0.5` | `task10_team_goals_dnb` | excluded in v1: passed 2024/25+ in new_markets_study.md, but no 2019/20-2023/24 replication report exists in engine/reports/ | `new_markets_study.md:24` |
| BUNDES | `home_over_1.5` | `task10_team_goals_dnb` | excluded in v1: passed 2024/25+ in new_markets_study.md, but no 2019/20-2023/24 replication report exists in engine/reports/ | `new_markets_study.md:25` |
| BUNDES | `away_over_1.5` | `task10_team_goals_dnb` | excluded in v1: passed 2024/25+ in new_markets_study.md, but no 2019/20-2023/24 replication report exists in engine/reports/ | `new_markets_study.md:26` |
| BUNDES | `dnb_home` | `task10_team_goals_dnb` | excluded in v1: Draw No Bet refunds the leg at odds 1.00 on a draw (slip maths not implemented); task 10 gate=FAIL | `new_markets_study.md:27` |
| BUNDES | `dnb_away` | `task10_team_goals_dnb` | excluded in v1: Draw No Bet refunds the leg at odds 1.00 on a draw (slip maths not implemented); task 10 gate=PASS | `new_markets_study.md:28` |
| LIGUE1 | `home_over_0.5` | `task10_team_goals_dnb` | excluded in v1: passed 2024/25+ in new_markets_study.md, but no 2019/20-2023/24 replication report exists in engine/reports/ | `new_markets_study.md:29` |
| LIGUE1 | `away_over_0.5` | `task10_team_goals_dnb` | excluded in v1: passed 2024/25+ in new_markets_study.md, but no 2019/20-2023/24 replication report exists in engine/reports/ | `new_markets_study.md:30` |
| LIGUE1 | `home_over_1.5` | `task10_team_goals_dnb` | excluded in v1: passed 2024/25+ in new_markets_study.md, but no 2019/20-2023/24 replication report exists in engine/reports/ | `new_markets_study.md:31` |
| LIGUE1 | `away_over_1.5` | `task10_team_goals_dnb` | excluded in v1: passed 2024/25+ in new_markets_study.md, but no 2019/20-2023/24 replication report exists in engine/reports/ | `new_markets_study.md:32` |
| LIGUE1 | `dnb_home` | `task10_team_goals_dnb` | excluded in v1: Draw No Bet refunds the leg at odds 1.00 on a draw (slip maths not implemented); task 10 gate=PASS | `new_markets_study.md:33` |
| LIGUE1 | `dnb_away` | `task10_team_goals_dnb` | excluded in v1: Draw No Bet refunds the leg at odds 1.00 on a draw (slip maths not implemented); task 10 gate=PASS | `new_markets_study.md:34` |

## Step 4 — Live probability verification

- Every eligible family (`task16_half`, `task17_up`, `task20_timing`, `task20_team_half`) is scored by reusing its exact study raw-probability function (`half_markets_study.half_market_raw_probabilities`, `up_markets_study.raw_up_probabilities_from_matrix`, `timing_half_markets_study.timing_market_raw_probabilities`, `timing_half_markets_study.half_team_raw_probabilities`) on `accumulators.bookmaker_implied` lambdas/score matrix reconstructed from the cached fixture's fair 1X2 + O/U 2.5 `market_probability` and `league_rho(league)`.
- Historical shares (`s`, `w`) and Platt calibrators (`LogisticRegression(C=1.0)` on `logit(raw)`) are fitted strictly on seasons `< target_season` (`< 2026/27`). No new model is created.
- **0 eligible markets dropped** for live probability reproducibility on the cached fixtures' leagues.

## Step 5 — Dry run on cached `web/public/data/predictions.json`

Tier: `Tier('trial', min_odds=3.0, max_odds=5.0, min_legs=2, max_legs=4)`, `stake_cap = 0.01` (1%), `trial = true`, real Betpawa prices only (`odds >= 1.05`), one leg per match, excluding any `match + market` on Safe/Medium/Big.

### Day `2026-11-23`

- Cached fixtures: **4** (EPL: Brentford v Everton, LALIGA: Levante v Elche, SERIEA: Monza v Fiorentina, SUPERLIG: Buyuksehyr v Corum).
- Main slip tiers present: big, medium, safe.
- Priced TRIAL-ELIGIBLE candidate legs (from `engine/data/live/prices`, pre-kickoff, `odds >= 1.05`): **63 legs** across **4 matches**.

**Trial slip selected** (`trial: true`, `stake_cap: 0.01`, total odds **3.05**, predicted win **34.12%**, EV `+0.0405`, odds source `betpawa`, slip margin: not measurable):

| League | Match | Market | Raw p | Calibrated p | Betpawa odds | Fair odds | Margin (Step 2) | trial | stake_cap |
|---|---|---|---:|---:|---:|---:|---|---|---:|
| LALIGA | Levante v Elche | `home_sh_over_0.5` | 0.5943 | 0.6133 | 1.58 | 1.63 | not measurable | `true` | 0.01 |
| SERIEA | Monza v Fiorentina | `away_2up` | 0.5111 | 0.5564 | 1.93 | 1.80 | not measurable | `true` | 0.01 |

## Step 6 — Pre-registered judgement rules (locked before any live Trial slip)

- **PROMOTION** of a league x market to main slips: unchanged existing rule (`>= 300` settled Betpawa-priced legs, one-sided level check passes, and `pair_monitor` not paused).
- **PAUSE** of the whole Trial: after `>= 30` settled Trial slips, if actual win rate is below predicted with one-sided `z < -2.5` (`z = (wins - sum p) / sqrt(sum p(1 - p))`), pause the Trial.
- **Reporting cadence (every 30 settled Trial slips)**: report predicted vs actual win rate with Wilson 95% CI, return per unit staked, per-market leg results, and the share of days every slip (main + Trial) lost.

## What was NOT checked

- **No historical Trial slip backtest at real Betpawa prices**: real Betpawa prices for most Trial markets only started logging on 2026-11-07 (and were paused during the Understat outage until 2026-11-21), so historical slip-level winner's curse cannot yet be measured at real prices.
- **No Task 10 replication**: team overs (`home_over_0.5/1.5`, `away_over_0.5/1.5`) were excluded from v1 because `new_markets_study.md` has no `2019/20-2023/24` replication report; replicating Task 10 is a separate pre-registered task if desired.
- **No Draw No Bet refund slip maths**: `dnb_home`/`dnb_away` are excluded from v1 because `best_slip` and slip win-probability products do not model odds-`1.00` pushes on draws.
- **No live publishing, booking-code generation, or web UI rendering**: this task is strictly offline research and dry run.
- **No margin measurement for single-sided logged markets**: Betpawa complementary prices (e.g. Under 0.5/1.5 halves, No on win/score halves, `None` on first goal, Draw on 2UP) are not logged in `prices/*.csv`, so overround is unknown for 21 of the 24 eligible Trial markets (only `interval_10_*` has a complete 3-way set logged).
