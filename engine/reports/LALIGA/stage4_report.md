# Stage 4 report: accumulator tiers

Test seasons: 2024/25, 2025/26, 2026/27; 849 matches, 101 betting rounds (weekend Fri-Mon / midweek Tue-Thu).

Leg odds are ESTIMATED from bookmaker opening 1X2 and O/U 2.5 prices with a 7% retail margin (see module docstring). Hit rates do not depend on odds; ROI does, so treat ROI as indicative only.

Leg probability = logit blend of calibrated model and bookmaker-implied probability. Model weight per season, learned on earlier seasons only: 2024/25: 0.50, 2025/26: 0.10, 2026/27: 0.10.

Modes: `accuracy` picks the most likely slip in the odds range using blended probabilities; `market_only` and `model_only` do the same with one source alone (baselines); `value` only uses legs where blended probability x estimated odds >= 1.03. Predicted win uses each mode's own probabilities.

## Slip results

| Mode | Tier | Slips | Avg legs | Avg odds | Predicted win | Actual win | 95% CI | Bookmaker-implied win | ROI |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| accuracy | safe | 188 | 2.0 | 2.54 | 36.9% | 30.3% | 24%-37% | 34.3% | -22.8% |
| market_only | safe | 188 | 2.0 | 2.51 | 34.8% | 34.6% | 28%-42% | 34.8% | -13.1% |
| model_only | safe | 188 | 2.1 | 2.60 | 44.8% | 34.0% | 28%-41% | 33.3% | -11.7% |
| accuracy | medium | 161 | 3.0 | 3.54 | 25.5% | 19.3% | 14%-26% | 23.1% | -31.9% |
| accuracy | big | 137 | 4.0 | 8.07 | 11.0% | 6.6% | 3%-12% | 9.5% | -46.9% |
| market_only | medium | 161 | 3.0 | 3.51 | 23.2% | 23.0% | 17%-30% | 23.2% | -19.2% |
| market_only | big | 137 | 4.0 | 8.03 | 9.5% | 11.7% | 7%-18% | 9.5% | -6.3% |
| model_only | medium | 161 | 3.0 | 3.62 | 32.9% | 22.4% | 17%-29% | 22.6% | -19.4% |
| model_only | big | 137 | 4.0 | 8.20 | 15.7% | 7.3% | 4%-13% | 9.3% | -40.5% |
| value | safe | 5 | 2.0 | 2.70 | 41.7% | 40.0% | 12%-77% | 32.5% | +2.9% |
| value | medium | 2 | 3.0 | 4.04 | 29.0% | 50.0% | 9%-91% | 20.3% | +117.3% |
| value | big | 2 | 4.0 | 8.25 | 15.7% | 0.0% | 0%-66% | 9.2% | -100.0% |

## By season (accuracy mode)

| Tier | Season | Slips | Predicted win | Actual win |
|---|---|---:|---:|---:|
| safe | 2024/25 | 84 | 38.7% | 29.8% |
| medium | 2024/25 | 71 | 27.3% | 15.5% |
| big | 2024/25 | 64 | 12.1% | 6.2% |
| safe | 2025/26 | 80 | 35.5% | 30.0% |
| medium | 2025/26 | 74 | 24.1% | 23.0% |
| big | 2025/26 | 65 | 10.0% | 7.7% |
| safe | 2026/27 | 24 | 35.5% | 33.3% |
| medium | 2026/27 | 16 | 24.1% | 18.8% |
| big | 2026/27 | 8 | 10.1% | 0.0% |

## Markets used in slips (accuracy mode)

| Tier | Market | Legs | Leg hit rate |
|---|---|---:|---:|
| safe | under_3.5 | 71 | 57.7% |
| safe | double_12 | 44 | 79.5% |
| safe | home_win | 43 | 60.5% |
| safe | home_1up | 38 | 47.4% |
| safe | double_1x | 36 | 69.4% |
| safe | under_2.5 | 35 | 51.4% |
| safe | over_2.5 | 31 | 45.2% |
| safe | away_1up | 24 | 41.7% |
| safe | over_1.5 | 23 | 69.6% |
| safe | double_x2 | 22 | 54.5% |
| safe | away_win | 6 | 16.7% |
| safe | over_0.5 | 5 | 100.0% |
| medium | under_3.5 | 81 | 56.8% |
| medium | home_win | 68 | 58.8% |
| medium | double_1x | 66 | 60.6% |
| medium | double_12 | 59 | 81.4% |
| medium | home_1up | 41 | 56.1% |
| medium | away_1up | 35 | 57.1% |
| medium | double_x2 | 32 | 62.5% |
| medium | under_2.5 | 32 | 43.8% |
| medium | over_1.5 | 28 | 53.6% |
| medium | over_2.5 | 19 | 42.1% |
| medium | over_0.5 | 13 | 100.0% |
| medium | away_win | 9 | 44.4% |
| big | home_win | 85 | 51.8% |
| big | under_3.5 | 74 | 67.6% |
| big | under_2.5 | 70 | 32.9% |
| big | double_1x | 53 | 71.7% |
| big | away_1up | 44 | 45.5% |
| big | double_12 | 42 | 81.0% |
| big | home_1up | 42 | 50.0% |
| big | over_2.5 | 32 | 43.8% |
| big | away_win | 31 | 41.9% |
| big | over_1.5 | 29 | 58.6% |
| big | double_x2 | 28 | 60.7% |
| big | over_0.5 | 18 | 88.9% |

## Estimated odds sanity check

Bookmaker-implied probability vs actual rate across all test matches, per market. Large gaps would mean the estimated odds are unrealistic.

| Market | Bookmaker-implied | Model (calibrated) | Actual | Median est. odds |
|---|---:|---:|---:|---:|
| home_win | 44.3% | 44.9% | 46.3% | 2.20 |
| draw | 25.9% | 25.5% | 25.3% | 3.41 |
| away_win | 29.8% | 29.4% | 28.3% | 3.41 |
| over_1.5 | 72.3% | 72.0% | 74.9% | 1.30 |
| over_2.5 | 48.8% | 48.6% | 50.1% | 1.98 |
| over_3.5 | 27.4% | 27.2% | 26.3% | 3.72 |
| under_2.5 | 51.2% | 51.4% | 49.9% | 1.77 |
| under_3.5 | 72.6% | 72.8% | 73.7% | 1.25 |
| btts_yes | 48.7% | 49.3% | 55.8% | 1.94 |
| btts_no | 51.3% | 50.7% | 44.2% | 1.81 |
| home_1up | 58.1% | 58.5% | 59.4% | 1.64 |
| away_1up | 45.7% | 45.8% | 44.6% | 2.11 |
| home_first | 51.7% | 51.8% | 52.5% | 1.84 |
| away_first | 40.3% | 40.3% | 37.3% | 2.38 |
| double_1x | 67.9% | 68.3% | 69.3% | 1.32 |
| double_x2 | 55.2% | 54.5% | 53.0% | 1.63 |
| double_12 | 73.9% | 74.3% | 74.4% | 1.29 |
| over_0.5 | 87.2% | 87.9% | 90.0% | 1.07 |
