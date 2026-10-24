# Stage 4 report: accumulator tiers

Test seasons: 2024/25, 2025/26, 2026/27; 830 matches, 92 betting rounds (weekend Fri-Mon / midweek Tue-Thu).

Leg odds are ESTIMATED from bookmaker opening 1X2 and O/U 2.5 prices with a 7% retail margin (see module docstring). Hit rates do not depend on odds; ROI does, so treat ROI as indicative only.

Leg probability = logit blend of calibrated model and bookmaker-implied probability. Model weight per season, learned on earlier seasons only: 2024/25: 0.50, 2025/26: 0.00, 2026/27: 0.00.

Modes: `accuracy` picks the most likely slip in the odds range using blended probabilities; `market_only` and `model_only` do the same with one source alone (baselines); `value` only uses legs where blended probability x estimated odds >= 1.03. Predicted win uses each mode's own probabilities.

## Slip results

| Mode | Tier | Slips | Avg legs | Avg odds | Predicted win | Actual win | 95% CI | Bookmaker-implied win | ROI |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| accuracy | safe | 210 | 2.0 | 2.54 | 36.3% | 32.4% | 26%-39% | 34.4% | -17.9% |
| accuracy | medium | 164 | 3.0 | 3.54 | 25.0% | 25.0% | 19%-32% | 23.1% | -11.4% |
| accuracy | big | 108 | 4.0 | 8.09 | 10.8% | 6.5% | 3%-13% | 9.4% | -47.5% |
| market_only | safe | 210 | 2.0 | 2.51 | 34.7% | 35.7% | 30%-42% | 34.7% | -10.2% |
| market_only | medium | 164 | 3.0 | 3.51 | 23.2% | 25.0% | 19%-32% | 23.2% | -12.2% |
| market_only | big | 108 | 4.0 | 8.02 | 9.5% | 9.3% | 5%-16% | 9.5% | -25.6% |
| model_only | safe | 210 | 2.2 | 2.62 | 43.0% | 30.5% | 25%-37% | 33.1% | -20.4% |
| model_only | medium | 164 | 3.0 | 3.61 | 31.7% | 25.6% | 20%-33% | 22.6% | -7.7% |
| model_only | big | 108 | 4.0 | 8.21 | 15.7% | 10.2% | 6%-17% | 9.3% | -16.3% |
| value | safe | 6 | 2.0 | 2.99 | 38.2% | 0.0% | 0%-39% | 29.5% | -100.0% |

## By season (accuracy mode)

| Tier | Season | Slips | Predicted win | Actual win |
|---|---|---:|---:|---:|
| safe | 2024/25 | 94 | 38.4% | 28.7% |
| medium | 2024/25 | 76 | 27.1% | 28.9% |
| big | 2024/25 | 50 | 12.2% | 12.0% |
| safe | 2025/26 | 96 | 34.7% | 34.4% |
| medium | 2025/26 | 73 | 23.3% | 21.9% |
| big | 2025/26 | 50 | 9.5% | 2.0% |
| safe | 2026/27 | 20 | 34.7% | 40.0% |
| medium | 2026/27 | 15 | 23.3% | 20.0% |
| big | 2026/27 | 8 | 9.5% | 0.0% |

## Markets used in slips (accuracy mode)

| Tier | Market | Legs | Leg hit rate |
|---|---|---:|---:|
| safe | double_x2 | 59 | 49.2% |
| safe | over_2.5 | 47 | 53.2% |
| safe | under_3.5 | 46 | 52.2% |
| safe | under_2.5 | 44 | 52.3% |
| safe | home_1up | 43 | 65.1% |
| safe | over_1.5 | 41 | 65.9% |
| safe | away_1up | 35 | 57.1% |
| safe | double_1x | 33 | 57.6% |
| safe | double_12 | 27 | 74.1% |
| safe | home_win | 26 | 46.2% |
| safe | away_win | 16 | 87.5% |
| safe | over_0.5 | 5 | 80.0% |
| medium | double_x2 | 86 | 62.8% |
| medium | under_3.5 | 68 | 73.5% |
| medium | home_1up | 53 | 50.9% |
| medium | over_1.5 | 51 | 72.5% |
| medium | double_1x | 49 | 65.3% |
| medium | away_1up | 41 | 51.2% |
| medium | under_2.5 | 39 | 64.1% |
| medium | double_12 | 28 | 75.0% |
| medium | over_2.5 | 25 | 52.0% |
| medium | home_win | 23 | 43.5% |
| medium | away_win | 20 | 65.0% |
| medium | over_0.5 | 9 | 88.9% |
| big | double_x2 | 81 | 55.6% |
| big | home_1up | 55 | 54.5% |
| big | away_1up | 53 | 54.7% |
| big | over_1.5 | 45 | 68.9% |
| big | under_3.5 | 44 | 61.4% |
| big | double_1x | 29 | 62.1% |
| big | over_2.5 | 27 | 37.0% |
| big | under_2.5 | 26 | 38.5% |
| big | home_win | 23 | 30.4% |
| big | double_12 | 22 | 77.3% |
| big | away_win | 18 | 38.9% |
| big | over_0.5 | 9 | 88.9% |

## Estimated odds sanity check

Bookmaker-implied probability vs actual rate across all test matches, per market. Large gaps would mean the estimated odds are unrealistic.

| Market | Bookmaker-implied | Model (calibrated) | Actual | Median est. odds |
|---|---:|---:|---:|---:|
| home_win | 42.4% | 41.6% | 40.0% | 2.27 |
| draw | 26.1% | 26.9% | 26.4% | 3.44 |
| away_win | 31.5% | 31.4% | 33.6% | 3.24 |
| over_1.5 | 73.1% | 73.3% | 73.0% | 1.28 |
| over_2.5 | 47.5% | 47.5% | 48.1% | 1.99 |
| over_3.5 | 26.0% | 25.8% | 24.6% | 3.71 |
| under_2.5 | 52.5% | 52.5% | 51.9% | 1.76 |
| under_3.5 | 74.0% | 74.2% | 75.4% | 1.25 |
| btts_yes | 48.4% | 49.1% | 49.2% | 1.94 |
| btts_no | 51.6% | 50.9% | 50.8% | 1.80 |
| home_1up | 56.5% | 56.7% | 53.3% | 1.66 |
| away_1up | 46.8% | 47.3% | 48.9% | 2.05 |
| home_first | 50.1% | 49.9% | 46.6% | 1.88 |
| away_first | 41.3% | 41.6% | 42.3% | 2.32 |
| double_1x | 66.1% | 66.2% | 63.3% | 1.35 |
| double_x2 | 57.3% | 58.2% | 59.7% | 1.59 |
| double_12 | 73.9% | 73.0% | 73.6% | 1.28 |
| over_0.5 | 88.0% | 88.9% | 87.6% | 1.06 |
