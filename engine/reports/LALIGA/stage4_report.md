# Stage 4 report: accumulator tiers

Test seasons: 2024/25, 2025/26, 2026/27; 849 matches, 101 betting rounds (weekend Fri-Mon / midweek Tue-Thu).

Leg odds are ESTIMATED from bookmaker opening 1X2 and O/U 2.5 prices with a 7% retail margin (see module docstring). Hit rates do not depend on odds; ROI does, so treat ROI as indicative only.

Leg probability = logit blend of calibrated model and bookmaker-implied probability. Model weight per season, learned on earlier seasons only: 2024/25: 0.45, 2025/26: 0.35, 2026/27: 0.30.

Modes: `blended` picks the most likely slip using the learned model and market blend; `market` uses the calibrated bookmaker consensus; `model_only` is a diagnostic; `value` only uses legs where blended probability x estimated odds >= 1.03. Predicted win uses each mode's own probabilities.

## Slip results

| Mode | Tier | Slips | Avg legs | Avg odds | Predicted win | Actual win | 95% CI | Bookmaker-implied win | ROI |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| blended | safe | 188 | 2.2 | 2.55 | 39.0% | 33.5% | 27%-41% | 33.8% | -14.4% |
| market | safe | 188 | 2.3 | 2.54 | 37.6% | 40.4% | 34%-48% | 33.6% | +2.9% |
| blended | medium | 161 | 3.1 | 3.56 | 27.6% | 22.4% | 17%-29% | 22.8% | -20.1% |
| blended | big | 137 | 4.0 | 8.12 | 11.9% | 8.0% | 5%-14% | 9.4% | -35.1% |
| market | medium | 161 | 3.1 | 3.55 | 26.6% | 20.5% | 15%-27% | 22.8% | -27.0% |
| market | big | 137 | 4.1 | 8.11 | 11.0% | 8.8% | 5%-15% | 9.4% | -28.8% |

## By season (blended mode)

| Tier | Season | Slips | Predicted win | Actual win |
|---|---|---:|---:|---:|
| safe | 2024/25 | 84 | 39.0% | 27.4% |
| medium | 2024/25 | 71 | 27.7% | 22.5% |
| big | 2024/25 | 64 | 12.1% | 9.4% |
| safe | 2025/26 | 80 | 39.0% | 36.2% |
| medium | 2025/26 | 74 | 27.5% | 23.0% |
| big | 2025/26 | 65 | 11.8% | 7.7% |
| safe | 2026/27 | 24 | 38.5% | 45.8% |
| medium | 2026/27 | 16 | 27.4% | 18.8% |
| big | 2026/27 | 8 | 12.1% | 0.0% |

## Markets used in slips (blended mode)

| Tier | Market | Legs | Leg hit rate |
|---|---|---:|---:|
| safe | home_win | 113 | 64.6% |
| safe | double_1x | 46 | 78.3% |
| safe | under_3.5 | 39 | 59.0% |
| safe | over_1.5 | 35 | 60.0% |
| safe | away_1up | 35 | 60.0% |
| safe | under_2.5 | 31 | 48.4% |
| safe | home_1up | 29 | 62.1% |
| safe | double_x2 | 22 | 59.1% |
| safe | double_12 | 21 | 81.0% |
| safe | away_win | 20 | 60.0% |
| safe | over_2.5 | 17 | 58.8% |
| safe | over_0.5 | 3 | 100.0% |
| medium | home_win | 128 | 61.7% |
| medium | double_1x | 61 | 68.9% |
| medium | under_3.5 | 57 | 47.4% |
| medium | away_1up | 43 | 69.8% |
| medium | under_2.5 | 39 | 48.7% |
| medium | home_1up | 37 | 73.0% |
| medium | double_x2 | 33 | 66.7% |
| medium | over_1.5 | 32 | 56.2% |
| medium | away_win | 23 | 60.9% |
| medium | over_2.5 | 20 | 45.0% |
| medium | double_12 | 16 | 75.0% |
| medium | over_0.5 | 3 | 100.0% |
| big | home_win | 151 | 58.3% |
| big | away_1up | 72 | 48.6% |
| big | under_3.5 | 60 | 63.3% |
| big | under_2.5 | 60 | 48.3% |
| big | away_win | 43 | 51.2% |
| big | double_1x | 43 | 72.1% |
| big | home_1up | 38 | 60.5% |
| big | over_1.5 | 30 | 63.3% |
| big | over_2.5 | 26 | 61.5% |
| big | double_x2 | 14 | 71.4% |
| big | double_12 | 11 | 90.9% |
| big | over_0.5 | 3 | 100.0% |

## Estimated odds sanity check

Bookmaker-implied probability vs actual rate across all test matches, per market. Large gaps would mean the estimated odds are unrealistic.

| Market | Bookmaker-implied | Model (calibrated) | Actual | Median est. odds |
|---|---:|---:|---:|---:|
| home_win | 44.3% | 45.8% | 46.3% | 2.20 |
| draw | 25.9% | 25.5% | 25.3% | 3.41 |
| away_win | 29.8% | 28.4% | 28.3% | 3.41 |
| over_1.5 | 72.3% | 71.4% | 74.9% | 1.30 |
| over_2.5 | 48.8% | 48.4% | 50.1% | 1.98 |
| over_3.5 | 27.4% | 26.4% | 26.3% | 3.72 |
| under_2.5 | 51.2% | 51.6% | 49.9% | 1.77 |
| under_3.5 | 72.6% | 73.6% | 73.7% | 1.25 |
| btts_yes | 48.7% | 51.1% | 55.8% | 1.94 |
| btts_no | 51.3% | 48.9% | 44.2% | 1.81 |
| home_1up | 58.1% | 59.0% | 59.4% | 1.64 |
| away_1up | 45.7% | 45.9% | 44.6% | 2.11 |
| home_first | 51.7% | 51.9% | 52.5% | 1.84 |
| away_first | 40.3% | 40.0% | 37.3% | 2.38 |
| double_1x | 67.9% | 69.2% | 69.3% | 1.32 |
| double_x2 | 55.2% | 53.6% | 53.0% | 1.63 |
| double_12 | 73.9% | 74.2% | 74.4% | 1.29 |
| over_0.5 | 87.2% | 88.3% | 90.0% | 1.07 |
