# Stage 4 report: accumulator tiers

Test seasons: 2024/25, 2025/26, 2026/27; 830 matches, 94 betting rounds (weekend Fri-Mon / midweek Tue-Thu).

Leg odds are ESTIMATED from bookmaker opening 1X2 and O/U 2.5 prices with a 7% retail margin (see module docstring). Hit rates do not depend on odds; ROI does, so treat ROI as indicative only.

Leg probability = logit blend of calibrated model and bookmaker-implied probability. Model weight per season, learned on earlier seasons only: 2024/25: 0.50, 2025/26: 0.30, 2026/27: 0.15.

Modes: `accuracy` picks the most likely slip in the odds range using blended probabilities; `market_only` and `model_only` do the same with one source alone (baselines); `value` only uses legs where blended probability x estimated odds >= 1.03. Predicted win uses each mode's own probabilities.

## Slip results

| Mode | Tier | Slips | Avg legs | Avg odds | Predicted win | Actual win | 95% CI | Bookmaker-implied win | ROI |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| accuracy | safe | 87 | 2.0 | 2.53 | 38.7% | 36.8% | 27%-47% | 34.5% | -6.8% |
| accuracy | medium | 84 | 3.0 | 5.06 | 19.8% | 16.7% | 10%-26% | 16.1% | -15.6% |
| accuracy | big | 83 | 4.0 | 10.09 | 10.0% | 9.6% | 5%-18% | 7.6% | -2.3% |
| market_only | safe | 87 | 2.0 | 2.51 | 34.8% | 26.4% | 18%-37% | 34.8% | -33.6% |
| market_only | medium | 84 | 3.0 | 5.02 | 16.3% | 11.9% | 7%-21% | 16.3% | -40.2% |
| market_only | big | 83 | 4.0 | 10.04 | 7.6% | 13.3% | 8%-22% | 7.6% | +33.0% |
| model_only | safe | 87 | 2.0 | 2.59 | 46.2% | 33.3% | 24%-44% | 33.7% | -13.5% |
| model_only | medium | 84 | 3.0 | 5.12 | 27.1% | 16.7% | 10%-26% | 15.9% | -14.4% |
| model_only | big | 83 | 4.0 | 10.25 | 15.4% | 12.0% | 7%-21% | 7.4% | +24.3% |
| value | big | 5 | 4.0 | 18.50 | 7.7% | 20.0% | 4%-62% | 4.7% | +359.2% |
| value | safe | 7 | 2.0 | 2.99 | 37.0% | 14.3% | 3%-51% | 29.5% | -53.4% |
| value | medium | 4 | 3.0 | 6.18 | 19.8% | 0.0% | 0%-49% | 13.5% | -100.0% |

## By season (accuracy mode)

| Tier | Season | Slips | Predicted win | Actual win |
|---|---|---:|---:|---:|
| safe | 2024/25 | 40 | 40.0% | 37.5% |
| medium | 2024/25 | 38 | 21.0% | 18.4% |
| big | 2024/25 | 38 | 10.8% | 10.5% |
| safe | 2025/26 | 40 | 37.7% | 37.5% |
| medium | 2025/26 | 39 | 19.0% | 12.8% |
| big | 2025/26 | 38 | 9.5% | 7.9% |
| safe | 2026/27 | 7 | 36.7% | 28.6% |
| medium | 2026/27 | 7 | 18.0% | 28.6% |
| big | 2026/27 | 7 | 8.8% | 14.3% |

## Markets used in slips (accuracy mode)

| Tier | Market | Legs | Leg hit rate |
|---|---|---:|---:|
| safe | home_1up | 54 | 66.7% |
| safe | over_1.5 | 30 | 66.7% |
| safe | over_2.5 | 25 | 48.0% |
| safe | away_1up | 22 | 45.5% |
| safe | under_3.5 | 16 | 68.8% |
| safe | home_win | 7 | 28.6% |
| safe | away_win | 7 | 71.4% |
| safe | under_2.5 | 5 | 60.0% |
| safe | btts_yes | 4 | 50.0% |
| safe | over_3.5 | 2 | 50.0% |
| safe | btts_no | 1 | 0.0% |
| safe | away_first | 1 | 0.0% |
| medium | home_1up | 77 | 58.4% |
| medium | over_1.5 | 41 | 82.9% |
| medium | away_1up | 36 | 47.2% |
| medium | under_3.5 | 23 | 78.3% |
| medium | over_2.5 | 20 | 45.0% |
| medium | away_win | 17 | 52.9% |
| medium | home_win | 15 | 66.7% |
| medium | over_3.5 | 9 | 0.0% |
| medium | under_2.5 | 6 | 50.0% |
| medium | btts_yes | 3 | 66.7% |
| medium | home_first | 2 | 0.0% |
| medium | away_first | 2 | 50.0% |
| medium | btts_no | 1 | 0.0% |
| big | home_1up | 112 | 59.8% |
| big | away_1up | 57 | 57.9% |
| big | over_1.5 | 49 | 75.5% |
| big | away_win | 26 | 57.7% |
| big | under_3.5 | 24 | 87.5% |
| big | over_2.5 | 23 | 39.1% |
| big | home_win | 13 | 53.8% |
| big | over_3.5 | 11 | 27.3% |
| big | under_2.5 | 9 | 55.6% |
| big | home_first | 3 | 0.0% |
| big | btts_yes | 3 | 33.3% |
| big | btts_no | 1 | 0.0% |
| big | away_first | 1 | 0.0% |

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
| btts_yes | 55.8% | 56.1% | 56.4% | 1.67 |
| btts_no | 44.2% | 43.9% | 43.6% | 2.12 |
| home_1up | 59.4% | 60.2% | 60.5% | 1.58 |
| away_1up | 49.0% | 50.0% | 50.8% | 1.93 |
| home_first | 51.6% | 51.6% | 51.1% | 1.83 |
| away_first | 42.2% | 42.6% | 43.1% | 2.25 |
| over_0.5 | 88.4% | 89.1% | 100.0% | 1.06 |
