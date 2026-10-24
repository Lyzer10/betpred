# Stage 4 report: accumulator tiers

Test seasons: 2024/25, 2025/26, 2026/27; 675 matches, 80 betting rounds (weekend Fri-Mon / midweek Tue-Thu).

Leg odds are ESTIMATED from bookmaker opening 1X2 and O/U 2.5 prices with a 7% retail margin (see module docstring). Hit rates do not depend on odds; ROI does, so treat ROI as indicative only.

Leg probability = logit blend of calibrated model and bookmaker-implied probability. Model weight per season, learned on earlier seasons only: 2024/25: 0.40, 2025/26: 0.35, 2026/27: 0.25.

Modes: `blended` picks the most likely slip using the learned model and market blend; `market` uses the calibrated bookmaker consensus; `model_only` is a diagnostic; `value` only uses legs where blended probability x estimated odds >= 1.03. Predicted win uses each mode's own probabilities.

## Slip results

| Mode | Tier | Slips | Avg legs | Avg odds | Predicted win | Actual win | 95% CI | Bookmaker-implied win | ROI |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| blended | safe | 156 | 2.0 | 2.55 | 38.2% | 34.0% | 27%-42% | 34.2% | -13.5% |
| blended | medium | 141 | 3.0 | 3.55 | 26.8% | 22.0% | 16%-30% | 23.0% | -22.2% |
| market | safe | 156 | 2.0 | 2.54 | 37.2% | 35.3% | 28%-43% | 34.3% | -10.5% |
| market | medium | 141 | 3.0 | 3.55 | 25.9% | 24.8% | 18%-33% | 23.0% | -11.9% |
| blended | big | 73 | 4.0 | 8.10 | 12.1% | 6.8% | 3%-15% | 9.4% | -44.4% |
| market | big | 73 | 4.0 | 8.07 | 11.5% | 9.6% | 5%-18% | 9.5% | -22.3% |

## By season (blended mode)

| Tier | Season | Slips | Predicted win | Actual win |
|---|---|---:|---:|---:|
| safe | 2024/25 | 73 | 39.0% | 38.4% |
| medium | 2024/25 | 66 | 27.6% | 25.8% |
| big | 2024/25 | 34 | 12.5% | 5.9% |
| safe | 2025/26 | 68 | 37.7% | 29.4% |
| medium | 2025/26 | 61 | 26.4% | 16.4% |
| big | 2025/26 | 33 | 12.0% | 9.1% |
| safe | 2026/27 | 15 | 36.6% | 33.3% |
| medium | 2026/27 | 14 | 25.1% | 28.6% |
| big | 2026/27 | 6 | 10.8% | 0.0% |

## Markets used in slips (blended mode)

| Tier | Market | Legs | Leg hit rate |
|---|---|---:|---:|
| safe | away_1up | 99 | 51.5% |
| safe | under_3.5 | 34 | 67.6% |
| safe | over_2.5 | 33 | 45.5% |
| safe | double_x2 | 24 | 58.3% |
| safe | over_1.5 | 23 | 82.6% |
| safe | double_12 | 23 | 87.0% |
| safe | home_1up | 22 | 77.3% |
| safe | home_win | 18 | 72.2% |
| safe | away_win | 17 | 35.3% |
| safe | double_1x | 15 | 73.3% |
| safe | under_2.5 | 7 | 28.6% |
| medium | away_1up | 131 | 44.3% |
| medium | over_1.5 | 47 | 87.2% |
| medium | double_x2 | 45 | 66.7% |
| medium | double_12 | 37 | 67.6% |
| medium | home_1up | 36 | 75.0% |
| medium | over_2.5 | 34 | 58.8% |
| medium | under_3.5 | 34 | 70.6% |
| medium | double_1x | 23 | 65.2% |
| medium | home_win | 17 | 70.6% |
| medium | away_win | 15 | 73.3% |
| medium | under_2.5 | 4 | 50.0% |
| big | away_1up | 106 | 42.5% |
| big | over_2.5 | 30 | 30.0% |
| big | home_1up | 25 | 84.0% |
| big | over_1.5 | 21 | 61.9% |
| big | double_12 | 20 | 85.0% |
| big | double_x2 | 18 | 72.2% |
| big | home_win | 17 | 52.9% |
| big | double_1x | 17 | 64.7% |
| big | away_win | 15 | 46.7% |
| big | under_3.5 | 15 | 80.0% |
| big | under_2.5 | 7 | 28.6% |
| big | over_0.5 | 1 | 100.0% |

## Estimated odds sanity check

Bookmaker-implied probability vs actual rate across all test matches, per market. Large gaps would mean the estimated odds are unrealistic.

| Market | Bookmaker-implied | Model (calibrated) | Actual | Median est. odds |
|---|---:|---:|---:|---:|
| home_win | 43.6% | 43.1% | 46.2% | 2.18 |
| draw | 24.4% | 24.1% | 22.5% | 3.66 |
| away_win | 32.0% | 32.8% | 31.3% | 3.12 |
| over_1.5 | 77.7% | 78.2% | 77.5% | 1.20 |
| over_2.5 | 54.8% | 55.3% | 55.0% | 1.73 |
| over_3.5 | 32.6% | 32.6% | 34.4% | 2.98 |
| under_2.5 | 45.2% | 44.7% | 45.0% | 2.03 |
| under_3.5 | 67.4% | 67.4% | 65.6% | 1.36 |
| btts_yes | 54.1% | 56.1% | 54.7% | 1.73 |
| btts_no | 45.9% | 43.9% | 45.3% | 2.03 |
| home_1up | 58.9% | 58.1% | 55.0% | 1.58 |
| away_1up | 48.9% | 51.7% | 46.4% | 1.94 |
| home_first | 51.3% | 48.6% | 47.1% | 1.82 |
| away_first | 42.4% | 44.8% | 41.2% | 2.24 |
| double_1x | 66.5% | 65.7% | 67.4% | 1.36 |
| double_x2 | 55.9% | 56.4% | 53.1% | 1.65 |
| double_12 | 75.4% | 75.7% | 77.2% | 1.26 |
| over_0.5 | 88.6% | 93.0% | 100.0% | 1.06 |
