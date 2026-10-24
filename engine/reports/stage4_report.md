# Stage 4 report: accumulator tiers

Test seasons: 2024/25, 2025/26, 2026/27; 830 matches, 94 betting rounds (weekend Fri-Mon / midweek Tue-Thu).

Leg odds are ESTIMATED from bookmaker opening 1X2 and O/U 2.5 prices with a 7% retail margin (see module docstring). Hit rates do not depend on odds; ROI does, so treat ROI as indicative only.

Leg probability = logit blend of calibrated model and bookmaker-implied probability. Model weight per season, learned on earlier seasons only: 2024/25: 0.50, 2025/26: 0.35, 2026/27: 0.20.

Modes: `accuracy` picks the most likely slip in the odds range using blended probabilities; `market_only` and `model_only` do the same with one source alone (baselines); `value` only uses legs where blended probability x estimated odds >= 1.03. Predicted win uses each mode's own probabilities.

## Slip results

| Mode | Tier | Slips | Avg legs | Avg odds | Predicted win | Actual win | 95% CI | Bookmaker-implied win | ROI |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| accuracy | safe | 166 | 2.0 | 2.55 | 38.0% | 37.3% | 30%-45% | 34.3% | -5.0% |
| accuracy | medium | 135 | 3.0 | 3.54 | 26.8% | 23.7% | 17%-32% | 23.1% | -16.0% |
| accuracy | big | 119 | 4.0 | 8.08 | 11.9% | 13.4% | 8%-21% | 9.4% | +8.7% |
| market_only | safe | 166 | 2.0 | 2.51 | 34.8% | 33.1% | 26%-41% | 34.8% | -16.6% |
| market_only | medium | 135 | 3.0 | 3.51 | 23.3% | 21.5% | 15%-29% | 23.3% | -24.6% |
| market_only | big | 119 | 4.0 | 8.02 | 9.5% | 8.4% | 5%-15% | 9.5% | -32.6% |
| model_only | safe | 166 | 2.0 | 2.60 | 44.2% | 34.9% | 28%-42% | 33.6% | -9.5% |
| model_only | medium | 135 | 3.0 | 3.62 | 33.0% | 24.4% | 18%-32% | 22.7% | -12.3% |
| model_only | big | 119 | 4.0 | 8.18 | 16.5% | 12.6% | 8%-20% | 9.3% | +3.4% |
| value | safe | 6 | 2.0 | 3.13 | 36.0% | 0.0% | 0%-39% | 28.2% | -100.0% |
| value | medium | 2 | 3.0 | 6.52 | 17.8% | 0.0% | 0%-66% | 12.6% | -100.0% |

## By season (accuracy mode)

| Tier | Season | Slips | Predicted win | Actual win |
|---|---|---:|---:|---:|
| safe | 2024/25 | 78 | 38.6% | 46.2% |
| medium | 2024/25 | 61 | 27.4% | 21.3% |
| big | 2024/25 | 53 | 12.4% | 13.2% |
| safe | 2025/26 | 74 | 37.6% | 29.7% |
| medium | 2025/26 | 62 | 26.4% | 25.8% |
| big | 2025/26 | 56 | 11.6% | 14.3% |
| safe | 2026/27 | 14 | 37.0% | 28.6% |
| medium | 2026/27 | 12 | 25.5% | 25.0% |
| big | 2026/27 | 10 | 11.1% | 10.0% |

## Markets used in slips (accuracy mode)

| Tier | Market | Legs | Leg hit rate |
|---|---|---:|---:|
| safe | home_1up | 63 | 60.3% |
| safe | double_x2 | 48 | 62.5% |
| safe | over_2.5 | 46 | 45.7% |
| safe | double_1x | 44 | 56.8% |
| safe | over_1.5 | 36 | 80.6% |
| safe | away_1up | 29 | 62.1% |
| safe | under_3.5 | 18 | 72.2% |
| safe | home_win | 15 | 66.7% |
| safe | double_12 | 14 | 85.7% |
| safe | away_win | 11 | 72.7% |
| safe | under_2.5 | 8 | 50.0% |
| medium | home_1up | 75 | 57.3% |
| medium | over_1.5 | 75 | 80.0% |
| medium | double_1x | 59 | 67.8% |
| medium | double_x2 | 53 | 67.9% |
| medium | over_2.5 | 45 | 40.0% |
| medium | under_3.5 | 34 | 70.6% |
| medium | away_1up | 27 | 63.0% |
| medium | double_12 | 11 | 36.4% |
| medium | home_win | 11 | 36.4% |
| medium | away_win | 8 | 62.5% |
| medium | under_2.5 | 7 | 85.7% |
| big | home_1up | 104 | 55.8% |
| big | double_1x | 67 | 71.6% |
| big | over_1.5 | 63 | 88.9% |
| big | away_1up | 59 | 52.5% |
| big | double_x2 | 55 | 49.1% |
| big | over_2.5 | 41 | 46.3% |
| big | away_win | 23 | 47.8% |
| big | double_12 | 17 | 58.8% |
| big | home_win | 17 | 47.1% |
| big | under_3.5 | 16 | 93.8% |
| big | under_2.5 | 14 | 50.0% |

## Estimated odds sanity check

Bookmaker-implied probability vs actual rate across all test matches, per market. Large gaps would mean the estimated odds are unrealistic.

| Market | Bookmaker-implied | Model (calibrated) | Actual | Median est. odds |
|---|---:|---:|---:|---:|
| home_win | 44.2% | 43.9% | 41.6% | 2.19 |
| draw | 23.8% | 24.1% | 26.1% | 3.77 |
| away_win | 32.0% | 31.9% | 32.3% | 3.14 |
| over_1.5 | 79.7% | 80.0% | 79.5% | 1.17 |
| over_2.5 | 56.6% | 57.1% | 55.7% | 1.67 |
| over_3.5 | 34.6% | 35.3% | 31.7% | 2.76 |
| under_2.5 | 43.4% | 42.9% | 44.3% | 2.13 |
| under_3.5 | 65.4% | 64.7% | 68.3% | 1.41 |
| btts_yes | 55.8% | 56.2% | 56.4% | 1.67 |
| btts_no | 44.2% | 43.8% | 43.6% | 2.12 |
| home_1up | 59.4% | 60.3% | 60.5% | 1.58 |
| away_1up | 49.0% | 50.0% | 50.8% | 1.93 |
| home_first | 51.6% | 51.6% | 51.1% | 1.83 |
| away_first | 42.2% | 42.6% | 43.1% | 2.25 |
| double_1x | 66.2% | 66.3% | 65.8% | 1.37 |
| double_x2 | 55.4% | 55.7% | 58.0% | 1.64 |
| double_12 | 76.1% | 75.8% | 73.6% | 1.24 |
| over_0.5 | 88.4% | 89.2% | 100.0% | 1.06 |
