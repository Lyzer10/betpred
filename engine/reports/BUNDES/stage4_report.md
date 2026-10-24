# Stage 4 report: accumulator tiers

Test seasons: 2024/25, 2025/26, 2026/27; 666 matches, 76 betting rounds (weekend Fri-Mon / midweek Tue-Thu).

Leg odds are ESTIMATED from bookmaker opening 1X2 and O/U 2.5 prices with a 7% retail margin (see module docstring). Hit rates do not depend on odds; ROI does, so treat ROI as indicative only.

Leg probability = logit blend of calibrated model and bookmaker-implied probability. Model weight per season, learned on earlier seasons only: 2024/25: 0.50, 2025/26: 0.00, 2026/27: 0.00.

Modes: `accuracy` picks the most likely slip in the odds range using blended probabilities; `market_only` and `model_only` do the same with one source alone (baselines); `value` only uses legs where blended probability x estimated odds >= 1.03. Predicted win uses each mode's own probabilities.

## Slip results

| Mode | Tier | Slips | Avg legs | Avg odds | Predicted win | Actual win | 95% CI | Bookmaker-implied win | ROI |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| accuracy | safe | 147 | 2.0 | 2.54 | 36.1% | 27.9% | 21%-36% | 34.5% | -29.2% |
| accuracy | medium | 103 | 3.0 | 3.53 | 24.8% | 23.3% | 16%-32% | 23.1% | -17.7% |
| accuracy | big | 75 | 4.0 | 8.05 | 10.8% | 8.0% | 4%-16% | 9.5% | -35.3% |
| market_only | safe | 147 | 2.0 | 2.51 | 34.7% | 27.9% | 21%-36% | 34.7% | -29.8% |
| market_only | medium | 103 | 3.0 | 3.51 | 23.3% | 25.2% | 18%-34% | 23.3% | -11.4% |
| market_only | big | 75 | 4.0 | 8.03 | 9.5% | 13.3% | 7%-23% | 9.5% | +7.0% |
| model_only | safe | 147 | 2.1 | 2.60 | 42.2% | 27.9% | 21%-36% | 33.5% | -27.6% |
| model_only | medium | 103 | 3.0 | 3.61 | 31.6% | 13.6% | 8%-22% | 22.6% | -51.4% |
| model_only | big | 75 | 4.0 | 8.18 | 15.8% | 2.7% | 1%-9% | 9.3% | -78.4% |
| value | safe | 1 | 2.0 | 2.64 | 41.2% | 100.0% | 21%-100% | 33.1% | +163.7% |
| value | medium | 1 | 3.0 | 4.72 | 24.8% | 100.0% | 21%-100% | 17.3% | +371.9% |
| value | big | 1 | 4.0 | 9.27 | 13.1% | 100.0% | 21%-100% | 8.2% | +826.5% |

## By season (accuracy mode)

| Tier | Season | Slips | Predicted win | Actual win |
|---|---|---:|---:|---:|
| safe | 2024/25 | 67 | 37.7% | 31.3% |
| medium | 2024/25 | 46 | 26.7% | 21.7% |
| big | 2024/25 | 35 | 12.2% | 8.6% |
| safe | 2025/26 | 68 | 34.7% | 23.5% |
| medium | 2025/26 | 50 | 23.3% | 26.0% |
| big | 2025/26 | 34 | 9.5% | 8.8% |
| safe | 2026/27 | 12 | 34.5% | 33.3% |
| medium | 2026/27 | 7 | 23.2% | 14.3% |
| big | 2026/27 | 6 | 9.5% | 0.0% |

## Markets used in slips (accuracy mode)

| Tier | Market | Legs | Leg hit rate |
|---|---|---:|---:|
| safe | home_1up | 42 | 52.4% |
| safe | over_2.5 | 42 | 64.3% |
| safe | under_3.5 | 36 | 55.6% |
| safe | double_x2 | 33 | 54.5% |
| safe | double_1x | 32 | 59.4% |
| safe | away_1up | 29 | 41.4% |
| safe | over_1.5 | 28 | 78.6% |
| safe | under_2.5 | 16 | 18.8% |
| safe | double_12 | 16 | 62.5% |
| safe | home_win | 13 | 53.8% |
| safe | away_win | 7 | 57.1% |
| medium | over_1.5 | 54 | 77.8% |
| medium | double_x2 | 38 | 60.5% |
| medium | over_2.5 | 35 | 62.9% |
| medium | double_1x | 34 | 61.8% |
| medium | home_1up | 33 | 69.7% |
| medium | under_3.5 | 33 | 51.5% |
| medium | away_1up | 29 | 58.6% |
| medium | double_12 | 19 | 68.4% |
| medium | under_2.5 | 15 | 40.0% |
| medium | away_win | 10 | 50.0% |
| medium | home_win | 9 | 55.6% |
| big | over_1.5 | 52 | 69.2% |
| big | double_x2 | 48 | 45.8% |
| big | home_1up | 36 | 52.8% |
| big | double_1x | 31 | 64.5% |
| big | away_1up | 25 | 52.0% |
| big | under_3.5 | 22 | 45.5% |
| big | over_2.5 | 22 | 81.8% |
| big | under_2.5 | 21 | 28.6% |
| big | double_12 | 16 | 75.0% |
| big | home_win | 16 | 43.8% |
| big | away_win | 11 | 27.3% |

## Estimated odds sanity check

Bookmaker-implied probability vs actual rate across all test matches, per market. Large gaps would mean the estimated odds are unrealistic.

| Market | Bookmaker-implied | Model (calibrated) | Actual | Median est. odds |
|---|---:|---:|---:|---:|
| home_win | 44.8% | 44.4% | 41.9% | 2.16 |
| draw | 23.3% | 23.7% | 24.5% | 3.80 |
| away_win | 31.8% | 31.7% | 33.5% | 3.10 |
| over_1.5 | 81.5% | 82.1% | 81.1% | 1.14 |
| over_2.5 | 60.1% | 60.3% | 62.8% | 1.56 |
| over_3.5 | 38.4% | 38.7% | 43.8% | 2.47 |
| under_2.5 | 39.9% | 39.7% | 37.2% | 2.34 |
| under_3.5 | 61.6% | 61.3% | 56.2% | 1.50 |
| btts_yes | 59.0% | 59.6% | 59.3% | 1.57 |
| btts_no | 41.0% | 40.4% | 40.7% | 2.31 |
| home_1up | 60.1% | 60.2% | 56.9% | 1.55 |
| away_1up | 49.3% | 49.6% | 49.5% | 1.90 |
| home_first | 52.1% | 52.2% | 49.4% | 1.81 |
| away_first | 42.2% | 42.4% | 40.8% | 2.22 |
| double_1x | 66.2% | 66.3% | 64.2% | 1.37 |
| double_x2 | 54.2% | 54.7% | 57.0% | 1.66 |
| double_12 | 76.3% | 75.8% | 75.0% | 1.24 |
| over_0.5 | 87.9% | 89.4% | 25.0% | 1.06 |
