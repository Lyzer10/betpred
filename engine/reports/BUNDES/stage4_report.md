# Stage 4 report: accumulator tiers

Test seasons: 2024/25, 2025/26, 2026/27; 666 matches, 76 betting rounds (weekend Fri-Mon / midweek Tue-Thu).

Leg odds are ESTIMATED from bookmaker opening 1X2 and O/U 2.5 prices with a 7% retail margin (see module docstring). Hit rates do not depend on odds; ROI does, so treat ROI as indicative only.

Leg probability = logit blend of calibrated model and bookmaker-implied probability. Model weight per season, learned on earlier seasons only: 2024/25: 0.35, 2025/26: 0.30, 2026/27: 0.20.

Modes: `blended` picks the most likely slip using the learned model and market blend; `market` uses the calibrated bookmaker consensus; `model_only` is a diagnostic; `value` only uses legs where blended probability x estimated odds >= 1.03. Predicted win uses each mode's own probabilities.

## Slip results

| Mode | Tier | Slips | Avg legs | Avg odds | Predicted win | Actual win | 95% CI | Bookmaker-implied win | ROI |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| blended | safe | 147 | 2.0 | 2.55 | 37.3% | 32.7% | 26%-41% | 34.2% | -17.0% |
| blended | medium | 103 | 3.0 | 3.54 | 26.4% | 21.4% | 15%-30% | 23.1% | -24.4% |
| blended | big | 75 | 4.0 | 8.07 | 11.7% | 5.3% | 2%-13% | 9.4% | -57.1% |
| market | safe | 147 | 2.1 | 2.54 | 36.5% | 35.4% | 28%-43% | 34.3% | -10.2% |
| market | medium | 103 | 3.0 | 3.54 | 25.5% | 22.3% | 15%-31% | 23.0% | -21.2% |
| market | big | 75 | 4.1 | 8.07 | 10.8% | 12.0% | 6%-21% | 9.4% | -3.2% |

## By season (blended mode)

| Tier | Season | Slips | Predicted win | Actual win |
|---|---|---:|---:|---:|
| safe | 2024/25 | 67 | 37.7% | 31.3% |
| medium | 2024/25 | 46 | 26.7% | 23.9% |
| big | 2024/25 | 35 | 12.0% | 8.6% |
| safe | 2025/26 | 68 | 37.1% | 33.8% |
| medium | 2025/26 | 50 | 26.1% | 20.0% |
| big | 2025/26 | 34 | 11.4% | 2.9% |
| safe | 2026/27 | 12 | 36.1% | 33.3% |
| medium | 2026/27 | 7 | 26.3% | 14.3% |
| big | 2026/27 | 6 | 11.2% | 0.0% |

## Markets used in slips (blended mode)

| Tier | Market | Legs | Leg hit rate |
|---|---|---:|---:|
| safe | over_2.5 | 80 | 51.2% |
| safe | double_x2 | 47 | 55.3% |
| safe | home_1up | 45 | 60.0% |
| safe | double_1x | 35 | 60.0% |
| safe | away_1up | 32 | 62.5% |
| safe | over_1.5 | 30 | 80.0% |
| safe | home_win | 10 | 70.0% |
| safe | under_3.5 | 9 | 44.4% |
| safe | double_12 | 6 | 66.7% |
| safe | under_2.5 | 3 | 33.3% |
| safe | away_win | 2 | 100.0% |
| medium | over_2.5 | 59 | 59.3% |
| medium | double_x2 | 53 | 52.8% |
| medium | away_1up | 51 | 64.7% |
| medium | double_1x | 47 | 59.6% |
| medium | over_1.5 | 41 | 78.0% |
| medium | home_1up | 38 | 68.4% |
| medium | under_3.5 | 7 | 14.3% |
| medium | under_2.5 | 6 | 50.0% |
| medium | home_win | 4 | 25.0% |
| medium | double_12 | 2 | 50.0% |
| medium | away_win | 1 | 0.0% |
| big | double_x2 | 63 | 46.0% |
| big | over_2.5 | 53 | 56.6% |
| big | double_1x | 42 | 40.5% |
| big | over_1.5 | 41 | 68.3% |
| big | away_1up | 37 | 62.2% |
| big | home_1up | 34 | 61.8% |
| big | under_2.5 | 13 | 46.2% |
| big | home_win | 10 | 10.0% |
| big | away_win | 6 | 33.3% |
| big | under_3.5 | 3 | 33.3% |

## Estimated odds sanity check

Bookmaker-implied probability vs actual rate across all test matches, per market. Large gaps would mean the estimated odds are unrealistic.

| Market | Bookmaker-implied | Model (calibrated) | Actual | Median est. odds |
|---|---:|---:|---:|---:|
| home_win | 44.8% | 43.9% | 41.9% | 2.16 |
| draw | 23.3% | 24.8% | 24.5% | 3.80 |
| away_win | 31.8% | 31.0% | 33.5% | 3.10 |
| over_1.5 | 81.5% | 83.2% | 81.1% | 1.14 |
| over_2.5 | 60.1% | 61.2% | 62.8% | 1.56 |
| over_3.5 | 38.4% | 40.7% | 43.8% | 2.47 |
| under_2.5 | 39.9% | 38.8% | 37.2% | 2.34 |
| under_3.5 | 61.6% | 59.3% | 56.2% | 1.50 |
| btts_yes | 59.0% | 60.7% | 59.3% | 1.57 |
| btts_no | 41.0% | 39.3% | 40.7% | 2.31 |
| home_1up | 60.1% | 60.3% | 56.9% | 1.55 |
| away_1up | 49.3% | 49.4% | 49.5% | 1.90 |
| home_first | 52.1% | 52.3% | 49.4% | 1.81 |
| away_first | 42.2% | 42.2% | 40.8% | 2.22 |
| double_1x | 66.2% | 66.9% | 64.2% | 1.37 |
| double_x2 | 54.2% | 55.2% | 57.0% | 1.66 |
| double_12 | 76.3% | 74.7% | 75.0% | 1.24 |
| over_0.5 | 87.9% | 92.0% | 25.0% | 1.06 |
