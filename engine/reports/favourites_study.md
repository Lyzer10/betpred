# Big favourites calibration study (PROJECT.md task 29)

Generated: **2026-11-23 18:02 EAT** | Pre-registered: `2026-11-23` | Research only (no live changes).

## Summary & locked decisions

| Market | Primary `F >= 0.70` gap (95% CI) | Replication `F >= 0.70` gap (95% CI) | Step 1 | Step 2 | Step 3 | Decision |
|---|---|---|---|---|---|---|
| `win` (Favourite to win) | +1.47% [-2.53%, +5.22%] (n=501) | -0.41% [-2.29%, +1.49%] (n=2096) | **FAIL** | Not run (failed Step 1) | Not run (failed Step 1) | **KEEP current method (failed Step 1)** |
| `1up` (Favourite 1Up) | -2.30% [-6.15%, +1.70%] (n=448) | +0.02% [-2.01%, +2.08%] (n=1033) | **FAIL** | Not run (failed Step 1) | Not run (failed Step 1) | **KEEP current method (failed Step 1)** |
| `win_or_draw` (Favourite win or draw) | +0.85% [-4.30%, +5.58%] (n=152) | -0.09% [-1.25%, +1.06%] (n=1997) | **FAIL** | Not run (failed Step 1) | Not run (failed Step 1) | **KEEP current method (failed Step 1)** |

## Data scope & NOT AVAILABLE audit

- **Primary (`2024/25+`, 5 main leagues)**: `diversity_study.load_legs()` pool WITHOUT removing gate-FAIL pairs (3,850 matches, 42,036 legs; 3 matches lacked one `*_win` side because Stage 4 dropped `odds < 1.05` legs and were excluded from favourite assignment; 0 unknown-outcome legs excluded).
- **Replication (`2019/20–2023/24`, 9 live leagues)**: walk-forward probabilities using each league's exact live method (14,060 matches, 75,504 legs; 3 matches missing one win side; 0 unknown-outcome legs excluded). Note: unlike `accumulator_legs.parquet`, tasks 13/20/21/27 walk-forward market tables do not drop `odds < 1.05` legs, so `win_or_draw` covers every complete-odds match in the 8 market-mode leagues.
- **Bootstrap**: 2,000 whole-day resamples, seed `20261124`.

### Explicitly NOT AVAILABLE (never substituted)
- **NOT AVAILABLE**: EPL `2019/20`, `2020/21` (all 3 markets): `predictions_goal_timing_validation.parquet` starts at `2021/22` (`predictions_dc_history.parquet` has raw DC outputs only, no calibrated/goal-timing/blended legs).
- **NOT AVAILABLE**: EPL `2021/22` (all 3 markets): first validation season has no earlier blended-leg season to fit `model_weight` walk-forward (same rule as `method_retest_study.py`).
- **NOT AVAILABLE**: EREDIV `1up` (`home_1up`/`away_1up`, `2019/20–2023/24`): football-data-only league has no Understat goal-minute / led-at-any-point outcomes (`football_only.score_actuals` sets 1Up to `None`).
- **NOT AVAILABLE**: JUPILER `1up` (`home_1up`/`away_1up`, `2019/20–2023/24`): football-data-only league has no Understat goal-minute / led-at-any-point outcomes (`football_only.score_actuals` sets 1Up to `None`).
- **NOT AVAILABLE**: PRIMEIRA `1up` (`home_1up`/`away_1up`, `2019/20–2023/24`): football-data-only league has no Understat goal-minute / led-at-any-point outcomes (`football_only.score_actuals` sets 1Up to `None`).
- **NOT AVAILABLE**: SUPERLIG `1up` (`home_1up`/`away_1up`, `2019/20–2023/24`): football-data-only league has no Understat goal-minute / led-at-any-point outcomes (`football_only.score_actuals` sets 1Up to `None`).

## Step 1A — Primary data (5 main leagues, 2024/25+)

### Favourite to win (`win`)

| Band | n legs | n matches | Predicted | Actual | Wilson 95% CI | Gap (actual − pred) | Gap 95% CI (whole-day) |
|---|---:|---:|---:|---:|---|---:|---|
| <0.60 | 2,757 | 2,757 | 45.91% | 46.64% | [44.79%, 48.51%] | +0.73% | [-1.11%, +2.73%] |
| 0.60-0.70 | 589 | 589 | 64.71% | 64.52% | [60.57%, 68.27%] | -0.19% | [-3.89%, +3.51%] |
| 0.70-0.80 | 362 | 362 | 74.62% | 74.59% | [69.86%, 78.80%] | -0.03% | [-4.64%, +4.26%] |
| >=0.80 | 139 | 139 | 84.55% | 89.93% | [83.80%, 93.91%] | +5.37% | [-0.41%, +10.21%] |
| >=0.70 (big fav) | 501 | 501 | 77.37% | 78.84% | [75.05%, 82.19%] | +1.47% | [-2.53%, +5.22%] |

### Favourite 1Up (`1up`)

| Band | n legs | n matches | Predicted | Actual | Wilson 95% CI | Gap (actual − pred) | Gap 95% CI (whole-day) |
|---|---:|---:|---:|---:|---|---:|---|
| <0.60 | 2,757 | 2,757 | 62.39% | 61.99% | [60.16%, 63.78%] | -0.40% | [-2.62%, +1.83%] |
| 0.60-0.70 | 589 | 589 | 76.98% | 75.89% | [72.28%, 79.17%] | -1.09% | [-4.79%, +2.67%] |
| 0.70-0.80 | 361 | 361 | 83.88% | 80.61% | [76.22%, 84.36%] | -3.27% | [-7.39%, +0.83%] |
| >=0.80 | 87 | 87 | 89.08% | 90.80% | [82.89%, 95.27%] | +1.72% | [-5.57%, +7.64%] |
| >=0.70 (big fav) | 448 | 448 | 84.89% | 82.59% | [78.80%, 85.82%] | -2.30% | [-6.15%, +1.70%] |

### Favourite win or draw (`win_or_draw`)

| Band | n legs | n matches | Predicted | Actual | Wilson 95% CI | Gap (actual − pred) | Gap 95% CI (whole-day) |
|---|---:|---:|---:|---:|---|---:|---|
| <0.60 | 2,757 | 2,757 | 74.45% | 74.57% | [72.91%, 76.16%] | +0.13% | [-1.36%, +1.64%] |
| 0.60-0.70 | 577 | 577 | 86.46% | 85.27% | [82.14%, 87.93%] | -1.19% | [-3.91%, +1.49%] |
| 0.70-0.80 | 152 | 152 | 89.94% | 90.79% | [85.13%, 94.43%] | +0.85% | [-4.30%, +5.58%] |
| >=0.80 | 0 | 0 | n/a | n/a | n/a | n/a | n/a |
| >=0.70 (big fav) | 152 | 152 | 89.94% | 90.79% | [85.13%, 94.43%] | +0.85% | [-4.30%, +5.58%] |


## Step 1B — Replication data (9 live leagues, 2019/20–2023/24)

### Favourite to win (`win`)

| Band | n legs | n matches | Predicted | Actual | Wilson 95% CI | Gap (actual − pred) | Gap 95% CI (whole-day) |
|---|---:|---:|---:|---:|---|---:|---|
| <0.60 | 9,874 | 9,874 | 46.18% | 46.23% | [45.25%, 47.22%] | +0.05% | [-0.91%, +0.99%] |
| 0.60-0.70 | 2,087 | 2,087 | 64.81% | 65.88% | [63.82%, 67.89%] | +1.08% | [-1.09%, +3.13%] |
| 0.70-0.80 | 1,399 | 1,399 | 74.48% | 74.12% | [71.77%, 76.35%] | -0.35% | [-2.70%, +1.86%] |
| >=0.80 | 697 | 697 | 84.74% | 84.22% | [81.32%, 86.74%] | -0.52% | [-3.26%, +2.13%] |
| >=0.70 (big fav) | 2,096 | 2,096 | 77.89% | 77.48% | [75.64%, 79.22%] | -0.41% | [-2.29%, +1.49%] |

### Favourite 1Up (`1up`)

| Band | n legs | n matches | Predicted | Actual | Wilson 95% CI | Gap (actual − pred) | Gap 95% CI (whole-day) |
|---|---:|---:|---:|---:|---|---:|---|
| <0.60 | 5,549 | 5,549 | 62.39% | 63.42% | [62.14%, 64.67%] | +1.03% | [-0.26%, +2.18%] |
| 0.60-0.70 | 1,210 | 1,210 | 77.12% | 78.26% | [75.85%, 80.50%] | +1.14% | [-1.17%, +3.48%] |
| 0.70-0.80 | 765 | 765 | 83.89% | 84.44% | [81.70%, 86.84%] | +0.55% | [-1.83%, +2.84%] |
| >=0.80 | 268 | 268 | 90.31% | 88.81% | [84.47%, 92.05%] | -1.50% | [-5.31%, +2.20%] |
| >=0.70 (big fav) | 1,033 | 1,033 | 85.56% | 85.58% | [83.30%, 87.59%] | +0.02% | [-2.01%, +2.08%] |

### Favourite win or draw (`win_or_draw`)

| Band | n legs | n matches | Predicted | Actual | Wilson 95% CI | Gap (actual − pred) | Gap 95% CI (whole-day) |
|---|---:|---:|---:|---:|---|---:|---|
| <0.60 | 9,874 | 9,874 | 73.37% | 74.51% | [73.64%, 75.36%] | +1.14% | [+0.32%, +1.94%] |
| 0.60-0.70 | 2,082 | 2,082 | 85.87% | 85.64% | [84.07%, 87.08%] | -0.24% | [-1.80%, +1.17%] |
| 0.70-0.80 | 1,340 | 1,340 | 90.87% | 91.27% | [89.64%, 92.66%] | +0.40% | [-1.11%, +1.85%] |
| >=0.80 | 657 | 657 | 95.14% | 94.06% | [91.99%, 95.63%] | -1.08% | [-2.99%, +0.63%] |
| >=0.70 (big fav) | 1,997 | 1,997 | 92.27% | 92.19% | [90.93%, 93.29%] | -0.09% | [-1.25%, +1.06%] |

## Primary gate-FAIL vs gate-PASS breakdown

| Market | Scope | Group | n legs | n matches | Predicted | Actual | Wilson 95% CI | Gap | Gap 95% CI |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| `win` | all | `gate_FAIL` | 0 | 0 | n/a | n/a | n/a | n/a | n/a |
| `win` | all | `gate_PASS` | 3,847 | 3,847 | 52.89% | 53.57% | [52.00%, 55.15%] | +0.69% | [-0.77%, +2.23%] |
| `win` | >=0.70 (big fav) | `gate_FAIL` | 0 | 0 | n/a | n/a | n/a | n/a | n/a |
| `win` | >=0.70 (big fav) | `gate_PASS` | 501 | 501 | 77.37% | 78.84% | [75.05%, 82.19%] | +1.47% | [-2.53%, +5.22%] |
| `1up` | all | `gate_FAIL` | 704 | 704 | 68.04% | 63.49% | [59.87%, 66.97%] | -4.54% | [-8.43%, -0.54%] |
| `1up` | all | `gate_PASS` | 3,090 | 3,090 | 67.14% | 67.28% | [65.61%, 68.91%] | +0.14% | [-2.04%, +2.21%] |
| `1up` | >=0.70 (big fav) | `gate_FAIL` | 61 | 61 | 86.63% | 80.33% | [68.69%, 88.37%] | -6.31% | [-17.13%, +3.01%] |
| `1up` | >=0.70 (big fav) | `gate_PASS` | 387 | 387 | 84.62% | 82.95% | [78.88%, 86.36%] | -1.67% | [-6.09%, +2.33%] |
| `win_or_draw` | all | `gate_FAIL` | 407 | 407 | 76.53% | 73.71% | [69.23%, 77.75%] | -2.82% | [-7.18%, +1.56%] |
| `win_or_draw` | all | `gate_PASS` | 3,079 | 3,079 | 77.19% | 77.49% | [75.98%, 78.93%] | +0.30% | [-1.06%, +1.75%] |
| `win_or_draw` | >=0.70 (big fav) | `gate_FAIL` | 13 | 13 | 90.02% | 100.00% | [77.19%, 100.00%] | +9.98% | [+9.66%, +10.33%] |
| `win_or_draw` | >=0.70 (big fav) | `gate_PASS` | 139 | 139 | 89.94% | 89.93% | [83.80%, 93.91%] | -0.01% | [-5.71%, +4.88%] |

## Per-league big favourites (`F >= 0.70`) — Primary (2024/25+)

### `win` (Favourite to win)

| League | Availability | n legs | n matches | Predicted | Actual | Wilson 95% CI | Gap | Gap 95% CI |
|---|---|---:|---:|---:|---:|---|---:|---|
| `EPL` | 2024/25+ | 73 | 73 | 76.45% | 76.71% | [65.83%, 84.92%] | +0.27% | [-9.25%, +9.48%] |
| `LALIGA` | 2024/25+ | 146 | 146 | 79.40% | 82.19% | [75.19%, 87.55%] | +2.80% | [-3.43%, +8.57%] |
| `SERIEA` | 2024/25+ | 115 | 115 | 75.57% | 77.39% | [68.93%, 84.08%] | +1.82% | [-5.58%, +8.95%] |
| `BUNDES` | 2024/25+ | 80 | 80 | 78.17% | 78.75% | [68.58%, 86.29%] | +0.58% | [-8.57%, +9.53%] |
| `LIGUE1` | 2024/25+ | 87 | 87 | 76.41% | 77.01% | [67.14%, 84.60%] | +0.60% | [-9.02%, +9.33%] |

### `1up` (Favourite 1Up)

| League | Availability | n legs | n matches | Predicted | Actual | Wilson 95% CI | Gap | Gap 95% CI |
|---|---|---:|---:|---:|---:|---|---:|---|
| `EPL` | 2024/25+ | 63 | 63 | 84.29% | 85.71% | [75.03%, 92.30%] | +1.43% | [-8.09%, +10.95%] |
| `LALIGA` | 2024/25+ | 133 | 133 | 85.04% | 80.45% | [72.90%, 86.30%] | -4.59% | [-11.40%, +1.64%] |
| `SERIEA` | 2024/25+ | 113 | 113 | 83.77% | 85.84% | [78.23%, 91.09%] | +2.07% | [-3.89%, +7.86%] |
| `BUNDES` | 2024/25+ | 59 | 59 | 87.59% | 81.36% | [69.62%, 89.26%] | -6.23% | [-16.18%, +2.70%] |
| `LIGUE1` | 2024/25+ | 80 | 80 | 84.73% | 80.00% | [69.95%, 87.30%] | -4.73% | [-14.17%, +3.91%] |

### `win_or_draw` (Favourite win or draw)

| League | Availability | n legs | n matches | Predicted | Actual | Wilson 95% CI | Gap | Gap 95% CI |
|---|---|---:|---:|---:|---:|---|---:|---|
| `EPL` | 2024/25+ | 13 | 13 | 89.24% | 92.31% | [66.69%, 98.63%] | +3.07% | [-14.42%, +11.03%] |
| `LALIGA` | 2024/25+ | 52 | 52 | 90.58% | 90.38% | [79.39%, 95.82%] | -0.20% | [-9.28%, +7.10%] |
| `SERIEA` | 2024/25+ | 33 | 33 | 90.69% | 87.88% | [72.67%, 95.18%] | -2.81% | [-13.74%, +6.26%] |
| `BUNDES` | 2024/25+ | 17 | 17 | 89.95% | 100.00% | [81.57%, 100.00%] | +10.05% | [+9.73%, +10.39%] |
| `LIGUE1` | 2024/25+ | 37 | 37 | 88.63% | 89.19% | [75.29%, 95.71%] | +0.56% | [-9.25%, +8.67%] |


## Per-league big favourites (`F >= 0.70`) — Replication (2019/20–2023/24)

### `win` (Favourite to win)

| League | Availability | n legs | n matches | Predicted | Actual | Wilson 95% CI | Gap | Gap 95% CI |
|---|---|---:|---:|---:|---:|---|---:|---|
| `EPL` | 2022/23–2023/24 only (blended) | 133 | 133 | 77.56% | 75.19% | [67.21%, 81.75%] | -2.37% | [-9.95%, +4.83%] |
| `LALIGA` | 2019/20–2023/24 | 192 | 192 | 76.56% | 74.48% | [67.87%, 80.12%] | -2.08% | [-8.28%, +4.13%] |
| `SERIEA` | 2019/20–2023/24 | 321 | 321 | 76.69% | 75.08% | [70.07%, 79.49%] | -1.62% | [-6.29%, +3.06%] |
| `BUNDES` | 2019/20–2023/24 | 191 | 191 | 76.99% | 75.39% | [68.82%, 80.96%] | -1.60% | [-8.28%, +4.57%] |
| `LIGUE1` | 2019/20–2023/24 | 214 | 214 | 77.03% | 75.70% | [69.53%, 80.96%] | -1.33% | [-7.34%, +4.56%] |
| `EREDIV` | 2019/20–2023/24 | 348 | 348 | 79.73% | 79.89% | [75.36%, 83.76%] | +0.16% | [-4.13%, +4.20%] |
| `JUPILER` | 2019/20–2023/24 | 143 | 143 | 75.28% | 76.22% | [68.62%, 82.46%] | +0.94% | [-6.31%, +8.03%] |
| `PRIMEIRA` | 2019/20–2023/24 | 408 | 408 | 80.31% | 80.39% | [76.26%, 83.95%] | +0.08% | [-4.05%, +4.00%] |
| `SUPERLIG` | 2019/20–2023/24 | 146 | 146 | 76.41% | 81.51% | [74.43%, 86.97%] | +5.10% | [-1.64%, +11.28%] |

### `1up` (Favourite 1Up)

| League | Availability | n legs | n matches | Predicted | Actual | Wilson 95% CI | Gap | Gap 95% CI |
|---|---|---:|---:|---:|---:|---|---:|---|
| `EPL` | 2022/23–2023/24 only (blended) | 115 | 115 | 85.02% | 81.74% | [73.69%, 87.73%] | -3.28% | [-10.49%, +3.27%] |
| `LALIGA` | 2019/20–2023/24 | 192 | 192 | 84.98% | 85.42% | [79.73%, 89.71%] | +0.44% | [-4.79%, +5.19%] |
| `SERIEA` | 2019/20–2023/24 | 321 | 321 | 84.76% | 86.29% | [82.10%, 89.63%] | +1.53% | [-2.30%, +5.25%] |
| `BUNDES` | 2019/20–2023/24 | 191 | 191 | 87.13% | 84.82% | [79.04%, 89.22%] | -2.31% | [-7.61%, +2.50%] |
| `LIGUE1` | 2019/20–2023/24 | 214 | 214 | 86.15% | 87.38% | [82.27%, 91.18%] | +1.23% | [-2.74%, +5.56%] |
| `EREDIV` | **NOT AVAILABLE** (football-data only) | 0 | 0 | n/a | n/a | n/a | n/a | n/a |
| `JUPILER` | **NOT AVAILABLE** (football-data only) | 0 | 0 | n/a | n/a | n/a | n/a | n/a |
| `PRIMEIRA` | **NOT AVAILABLE** (football-data only) | 0 | 0 | n/a | n/a | n/a | n/a | n/a |
| `SUPERLIG` | **NOT AVAILABLE** (football-data only) | 0 | 0 | n/a | n/a | n/a | n/a | n/a |

### `win_or_draw` (Favourite win or draw)

| League | Availability | n legs | n matches | Predicted | Actual | Wilson 95% CI | Gap | Gap 95% CI |
|---|---|---:|---:|---:|---:|---|---:|---|
| `EPL` | 2022/23–2023/24 only (blended) | 34 | 34 | 89.44% | 88.24% | [73.38%, 95.33%] | -1.20% | [-14.26%, +8.15%] |
| `LALIGA` | 2019/20–2023/24 | 192 | 192 | 92.13% | 90.62% | [85.67%, 93.99%] | -1.51% | [-5.59%, +2.27%] |
| `SERIEA` | 2019/20–2023/24 | 321 | 321 | 92.13% | 92.52% | [89.12%, 94.92%] | +0.40% | [-2.45%, +3.03%] |
| `BUNDES` | 2019/20–2023/24 | 191 | 191 | 91.91% | 91.10% | [86.21%, 94.37%] | -0.81% | [-5.02%, +2.91%] |
| `LIGUE1` | 2019/20–2023/24 | 214 | 214 | 91.60% | 90.65% | [86.01%, 93.87%] | -0.94% | [-5.02%, +2.96%] |
| `EREDIV` | 2019/20–2023/24 | 348 | 348 | 92.75% | 94.25% | [91.29%, 96.25%] | +1.50% | [-1.06%, +3.87%] |
| `JUPILER` | 2019/20–2023/24 | 143 | 143 | 91.10% | 90.91% | [85.07%, 94.61%] | -0.19% | [-5.30%, +4.13%] |
| `PRIMEIRA` | 2019/20–2023/24 | 408 | 408 | 93.34% | 92.40% | [89.42%, 94.60%] | -0.93% | [-3.61%, +1.49%] |
| `SUPERLIG` | 2019/20–2023/24 | 146 | 146 | 91.97% | 93.84% | [88.70%, 96.72%] | +1.87% | [-2.26%, +5.36%] |

## Step 2 — Walk-forward logit shift (`F >= 0.70`)

- `win`: **Not run** (did not pass Step 1).
- `1up`: **Not run** (did not pass Step 1).
- `win_or_draw`: **Not run** (did not pass Step 1).

## Step 3 — Slip-level check (live task-24 no-identical-leg rule)

- `win`: **Not run** (failed Step 1).
- `1up`: **Not run** (failed Step 1).
- `win_or_draw`: **Not run** (failed Step 1).

## Live archive descriptive check (untouched holdout — NEVER fitted on)

Settled archived fixtures: **277** (2026-10-24 to 2026-11-22; unknown outcomes excluded: 61). Reported descriptively only.

| Market | Band | n legs | n matches | Predicted | Actual | Wilson 95% CI | Gap | Gap 95% CI |
|---|---|---:|---:|---:|---:|---|---:|---|
| `win` | <0.60 | 182 | 182 | 46.87% | 48.90% | [41.74%, 56.11%] | +2.04% | [-6.04%, +9.90%] |
| `win` | 0.60-0.70 | 47 | 47 | 64.65% | 74.47% | [60.49%, 84.75%] | +9.82% | [-1.99%, +20.55%] |
| `win` | 0.70-0.80 | 29 | 29 | 74.04% | 89.66% | [73.61%, 96.42%] | +15.62% | [-0.67%, +26.53%] |
| `win` | >=0.80 | 19 | 19 | 85.10% | 84.21% | [62.43%, 94.48%] | -0.89% | [-15.83%, +10.84%] |
| `win` | >=0.70 (big fav) | 48 | 48 | 78.42% | 87.50% | [75.30%, 94.14%] | +9.08% | [-5.72%, +19.73%] |
| `1up` | <0.60 | 142 | 142 | 63.64% | 64.79% | [56.64%, 72.16%] | +1.15% | [-8.44%, +9.46%] |
| `1up` | 0.60-0.70 | 39 | 39 | 76.44% | 82.05% | [67.33%, 91.02%] | +5.61% | [-7.80%, +15.91%] |
| `1up` | 0.70-0.80 | 23 | 23 | 83.24% | 95.65% | [79.01%, 99.23%] | +12.41% | [+0.71%, +17.79%] |
| `1up` | >=0.80 | 12 | 12 | 90.04% | 91.67% | [64.61%, 98.51%] | +1.63% | [-24.13%, +11.46%] |
| `1up` | >=0.70 (big fav) | 35 | 35 | 85.57% | 94.29% | [81.39%, 98.42%] | +8.72% | [-3.87%, +14.96%] |
| `win_or_draw` | <0.60 | 182 | 182 | 73.39% | 71.98% | [65.05%, 78.00%] | -1.41% | [-7.48%, +4.29%] |
| `win_or_draw` | 0.60-0.70 | 47 | 47 | 85.24% | 87.23% | [74.83%, 94.02%] | +2.00% | [-11.61%, +10.89%] |
| `win_or_draw` | 0.70-0.80 | 29 | 29 | 90.71% | 93.10% | [78.04%, 98.09%] | +2.40% | [-7.14%, +9.37%] |
| `win_or_draw` | >=0.80 | 19 | 19 | 95.04% | 94.74% | [75.36%, 99.06%] | -0.31% | [-8.90%, +5.12%] |
| `win_or_draw` | >=0.70 (big fav) | 48 | 48 | 92.42% | 93.75% | [83.16%, 97.85%] | +1.33% | [-4.27%, +7.37%] |
