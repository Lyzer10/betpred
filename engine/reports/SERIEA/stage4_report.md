# Stage 4 report: accumulator tiers

Test seasons: 2024/25, 2025/26, 2026/27; 830 matches, 92 betting rounds (weekend Fri-Mon / midweek Tue-Thu).

Leg odds are ESTIMATED from bookmaker opening 1X2 and O/U 2.5 prices with a 7% retail margin (see module docstring). Hit rates do not depend on odds; ROI does, so treat ROI as indicative only.

Leg probability = logit blend of calibrated model and bookmaker-implied probability. Model weight per season, learned on earlier seasons only: 2024/25: 0.40, 2025/26: 0.25, 2026/27: 0.15.

Modes: `blended` picks the most likely slip using the learned model and market blend; `market` uses the calibrated bookmaker consensus; `model_only` is a diagnostic; `value` only uses legs where blended probability x estimated odds >= 1.03. Predicted win uses each mode's own probabilities.

## Slip results

| Mode | Tier | Slips | Avg legs | Avg odds | Predicted win | Actual win | 95% CI | Bookmaker-implied win | ROI |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| blended | safe | 210 | 2.1 | 2.56 | 38.8% | 36.2% | 30%-43% | 33.8% | -7.6% |
| blended | medium | 164 | 3.0 | 3.57 | 27.7% | 25.6% | 20%-33% | 22.9% | -8.4% |
| blended | big | 108 | 4.0 | 8.13 | 12.2% | 4.6% | 2%-10% | 9.4% | -62.3% |
| market | safe | 210 | 2.2 | 2.56 | 38.4% | 37.6% | 31%-44% | 33.7% | -4.4% |
| market | medium | 164 | 3.1 | 3.57 | 27.4% | 26.8% | 21%-34% | 22.8% | -3.9% |
| market | big | 108 | 4.1 | 8.12 | 11.8% | 11.1% | 6%-18% | 9.4% | -9.2% |

## By season (blended mode)

| Tier | Season | Slips | Predicted win | Actual win |
|---|---|---:|---:|---:|
| safe | 2024/25 | 94 | 39.0% | 35.1% |
| medium | 2024/25 | 76 | 28.0% | 27.6% |
| big | 2024/25 | 50 | 12.4% | 8.0% |
| safe | 2025/26 | 96 | 38.6% | 37.5% |
| medium | 2025/26 | 73 | 27.4% | 23.3% |
| big | 2025/26 | 50 | 12.0% | 0.0% |
| safe | 2026/27 | 20 | 38.8% | 35.0% |
| medium | 2026/27 | 15 | 27.8% | 26.7% |
| big | 2026/27 | 8 | 12.1% | 12.5% |

## Markets used in slips (blended mode)

| Tier | Market | Legs | Leg hit rate |
|---|---|---:|---:|
| safe | double_x2 | 96 | 54.2% |
| safe | away_1up | 75 | 60.0% |
| safe | away_win | 63 | 68.3% |
| safe | over_1.5 | 57 | 78.9% |
| safe | under_3.5 | 45 | 64.4% |
| safe | under_2.5 | 38 | 44.7% |
| safe | home_1up | 34 | 70.6% |
| safe | double_1x | 26 | 73.1% |
| safe | home_win | 5 | 60.0% |
| safe | over_2.5 | 5 | 80.0% |
| safe | over_0.5 | 4 | 75.0% |
| medium | double_x2 | 136 | 64.7% |
| medium | away_win | 68 | 66.2% |
| medium | over_1.5 | 63 | 73.0% |
| medium | under_3.5 | 62 | 66.1% |
| medium | away_1up | 60 | 60.0% |
| medium | under_2.5 | 35 | 54.3% |
| medium | home_1up | 35 | 60.0% |
| medium | double_1x | 30 | 80.0% |
| medium | over_2.5 | 2 | 100.0% |
| medium | over_0.5 | 1 | 100.0% |
| medium | home_win | 1 | 100.0% |
| big | double_x2 | 115 | 53.9% |
| big | away_1up | 65 | 52.3% |
| big | away_win | 64 | 54.7% |
| big | under_2.5 | 42 | 54.8% |
| big | under_3.5 | 40 | 67.5% |
| big | over_1.5 | 40 | 77.5% |
| big | home_1up | 30 | 36.7% |
| big | double_1x | 24 | 70.8% |
| big | over_2.5 | 12 | 33.3% |
| big | over_0.5 | 3 | 100.0% |
| big | home_win | 2 | 50.0% |

## Estimated odds sanity check

Bookmaker-implied probability vs actual rate across all test matches, per market. Large gaps would mean the estimated odds are unrealistic.

| Market | Bookmaker-implied | Model (calibrated) | Actual | Median est. odds |
|---|---:|---:|---:|---:|
| home_win | 42.4% | 39.6% | 40.0% | 2.27 |
| draw | 26.1% | 28.4% | 26.4% | 3.44 |
| away_win | 31.5% | 31.7% | 33.6% | 3.24 |
| over_1.5 | 73.1% | 74.1% | 73.0% | 1.28 |
| over_2.5 | 47.5% | 47.1% | 48.1% | 1.99 |
| over_3.5 | 26.0% | 24.9% | 24.6% | 3.71 |
| under_2.5 | 52.5% | 52.9% | 51.9% | 1.76 |
| under_3.5 | 74.0% | 75.1% | 75.4% | 1.25 |
| btts_yes | 48.4% | 51.2% | 49.2% | 1.94 |
| btts_no | 51.6% | 48.8% | 50.8% | 1.80 |
| home_1up | 56.5% | 56.9% | 53.3% | 1.66 |
| away_1up | 46.8% | 48.6% | 48.9% | 2.05 |
| home_first | 50.1% | 49.3% | 46.6% | 1.88 |
| away_first | 41.3% | 42.2% | 42.3% | 2.32 |
| double_1x | 66.1% | 65.8% | 63.3% | 1.35 |
| double_x2 | 57.3% | 60.0% | 59.7% | 1.59 |
| double_12 | 73.9% | 71.5% | 73.6% | 1.28 |
| over_0.5 | 88.0% | 88.7% | 87.6% | 1.06 |
