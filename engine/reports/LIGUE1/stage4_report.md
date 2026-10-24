# Stage 4 report: accumulator tiers

Test seasons: 2024/25, 2025/26, 2026/27; 675 matches, 80 betting rounds (weekend Fri-Mon / midweek Tue-Thu).

Leg odds are ESTIMATED from bookmaker opening 1X2 and O/U 2.5 prices with a 7% retail margin (see module docstring). Hit rates do not depend on odds; ROI does, so treat ROI as indicative only.

Leg probability = logit blend of calibrated model and bookmaker-implied probability. Model weight per season, learned on earlier seasons only: 2024/25: 0.50, 2025/26: 0.00, 2026/27: 0.00.

Modes: `accuracy` picks the most likely slip in the odds range using blended probabilities; `market_only` and `model_only` do the same with one source alone (baselines); `value` only uses legs where blended probability x estimated odds >= 1.03. Predicted win uses each mode's own probabilities.

## Slip results

| Mode | Tier | Slips | Avg legs | Avg odds | Predicted win | Actual win | 95% CI | Bookmaker-implied win | ROI |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| accuracy | safe | 156 | 2.0 | 2.53 | 36.5% | 34.6% | 28%-42% | 34.5% | -12.2% |
| accuracy | medium | 141 | 3.0 | 3.53 | 25.0% | 19.1% | 14%-26% | 23.1% | -32.4% |
| market_only | safe | 156 | 2.0 | 2.51 | 34.8% | 36.5% | 29%-44% | 34.8% | -8.2% |
| market_only | medium | 141 | 3.0 | 3.51 | 23.3% | 16.3% | 11%-23% | 23.3% | -42.8% |
| model_only | safe | 156 | 2.1 | 2.58 | 42.7% | 34.0% | 27%-42% | 33.6% | -12.1% |
| model_only | medium | 141 | 3.0 | 3.59 | 31.2% | 21.3% | 15%-29% | 22.7% | -23.6% |
| accuracy | big | 73 | 4.0 | 8.05 | 10.7% | 11.0% | 6%-20% | 9.5% | -12.0% |
| market_only | big | 73 | 4.0 | 8.02 | 9.5% | 15.1% | 9%-25% | 9.5% | +21.0% |
| model_only | big | 73 | 4.0 | 8.14 | 15.4% | 6.8% | 3%-15% | 9.4% | -44.6% |
| value | safe | 4 | 2.0 | 3.16 | 35.7% | 25.0% | 5%-70% | 27.8% | -23.6% |
| value | medium | 2 | 3.0 | 6.28 | 20.7% | 0.0% | 0%-66% | 13.5% | -100.0% |

## By season (accuracy mode)

| Tier | Season | Slips | Predicted win | Actual win |
|---|---|---:|---:|---:|
| safe | 2024/25 | 73 | 38.4% | 32.9% |
| medium | 2024/25 | 66 | 27.0% | 24.2% |
| big | 2024/25 | 34 | 12.1% | 2.9% |
| safe | 2025/26 | 68 | 34.8% | 33.8% |
| medium | 2025/26 | 61 | 23.3% | 14.8% |
| big | 2025/26 | 33 | 9.5% | 15.2% |
| safe | 2026/27 | 15 | 34.8% | 46.7% |
| medium | 2026/27 | 14 | 23.3% | 14.3% |
| big | 2026/27 | 6 | 9.5% | 33.3% |

## Markets used in slips (accuracy mode)

| Tier | Market | Legs | Leg hit rate |
|---|---|---:|---:|
| safe | double_x2 | 45 | 62.2% |
| safe | under_3.5 | 41 | 68.3% |
| safe | away_1up | 37 | 51.4% |
| safe | over_2.5 | 30 | 53.3% |
| safe | under_2.5 | 28 | 42.9% |
| safe | double_1x | 28 | 75.0% |
| safe | home_1up | 24 | 70.8% |
| safe | over_1.5 | 21 | 76.2% |
| safe | away_win | 20 | 30.0% |
| safe | double_12 | 20 | 85.0% |
| safe | home_win | 19 | 52.6% |
| medium | under_3.5 | 59 | 74.6% |
| medium | double_x2 | 56 | 66.1% |
| medium | away_1up | 53 | 47.2% |
| medium | over_1.5 | 50 | 74.0% |
| medium | double_1x | 47 | 63.8% |
| medium | double_12 | 35 | 62.9% |
| medium | over_2.5 | 35 | 60.0% |
| medium | home_1up | 34 | 61.8% |
| medium | under_2.5 | 28 | 39.3% |
| medium | away_win | 16 | 62.5% |
| medium | home_win | 10 | 40.0% |
| big | away_1up | 40 | 35.0% |
| big | double_x2 | 38 | 65.8% |
| big | under_3.5 | 33 | 66.7% |
| big | under_2.5 | 32 | 56.2% |
| big | over_2.5 | 30 | 53.3% |
| big | double_1x | 26 | 65.4% |
| big | home_1up | 21 | 47.6% |
| big | over_1.5 | 21 | 71.4% |
| big | double_12 | 21 | 81.0% |
| big | home_win | 16 | 50.0% |
| big | away_win | 14 | 42.9% |

## Estimated odds sanity check

Bookmaker-implied probability vs actual rate across all test matches, per market. Large gaps would mean the estimated odds are unrealistic.

| Market | Bookmaker-implied | Model (calibrated) | Actual | Median est. odds |
|---|---:|---:|---:|---:|
| home_win | 43.6% | 43.0% | 46.2% | 2.18 |
| draw | 24.4% | 24.6% | 22.5% | 3.66 |
| away_win | 32.0% | 32.3% | 31.3% | 3.12 |
| over_1.5 | 77.7% | 77.7% | 77.5% | 1.20 |
| over_2.5 | 54.8% | 54.8% | 55.0% | 1.73 |
| over_3.5 | 32.6% | 32.3% | 34.4% | 2.98 |
| under_2.5 | 45.2% | 45.2% | 45.0% | 2.03 |
| under_3.5 | 67.4% | 67.7% | 65.6% | 1.36 |
| btts_yes | 54.1% | 54.4% | 54.7% | 1.73 |
| btts_no | 45.9% | 45.6% | 45.3% | 2.03 |
| home_1up | 58.9% | 58.6% | 55.0% | 1.58 |
| away_1up | 48.9% | 49.8% | 46.4% | 1.94 |
| home_first | 51.3% | 50.6% | 47.1% | 1.82 |
| away_first | 42.4% | 43.2% | 41.2% | 2.24 |
| double_1x | 66.5% | 66.2% | 67.4% | 1.36 |
| double_x2 | 55.9% | 56.4% | 53.1% | 1.65 |
| double_12 | 75.4% | 75.3% | 77.2% | 1.26 |
| over_0.5 | 88.6% | 90.6% | 100.0% | 1.06 |
