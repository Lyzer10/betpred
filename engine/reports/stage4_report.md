# Stage 4 report: accumulator tiers

Test seasons: 2024/25, 2025/26, 2026/27; 830 matches, 94 betting rounds (weekend Fri-Mon / midweek Tue-Thu).

Leg odds are ESTIMATED from bookmaker opening 1X2 and O/U 2.5 prices with a 7% retail margin (see module docstring). Hit rates do not depend on odds; ROI does, so treat ROI as indicative only.

Leg probability = logit blend of calibrated model and bookmaker-implied probability. Model weight per season, learned on earlier seasons only: 2024/25: 0.50, 2025/26: 0.30, 2026/27: 0.15.

Modes: `accuracy` picks the most likely slip in the odds range using blended probabilities; `market_only` and `model_only` do the same with one source alone (baselines); `value` only uses legs where blended probability x estimated odds >= 1.03. Predicted win uses each mode's own probabilities.

## Slip results

| Mode | Tier | Slips | Avg legs | Avg odds | Predicted win | Actual win | 95% CI | Bookmaker-implied win | ROI |
|---|---|---:|---:|---:|---:|---:|---|---:|---:|
| accuracy | safe | 87 | 2.0 | 2.54 | 38.6% | 35.6% | 26%-46% | 34.4% | -9.5% |
| accuracy | medium | 84 | 3.0 | 5.07 | 19.8% | 19.0% | 12%-29% | 16.1% | -3.4% |
| accuracy | big | 83 | 4.0 | 10.09 | 10.0% | 8.4% | 4%-16% | 7.6% | -14.8% |
| market_only | safe | 87 | 2.0 | 2.51 | 34.8% | 29.9% | 21%-40% | 34.8% | -24.9% |
| market_only | medium | 84 | 3.0 | 5.02 | 16.3% | 11.9% | 7%-21% | 16.3% | -40.2% |
| market_only | big | 83 | 4.0 | 10.03 | 7.6% | 13.3% | 8%-22% | 7.6% | +33.0% |
| model_only | safe | 87 | 2.0 | 2.59 | 46.1% | 35.6% | 26%-46% | 33.6% | -7.2% |
| model_only | medium | 84 | 3.0 | 5.12 | 27.1% | 19.0% | 12%-29% | 15.9% | -2.1% |
| model_only | big | 83 | 4.0 | 10.23 | 15.5% | 12.0% | 7%-21% | 7.4% | +23.0% |
| value | big | 4 | 4.0 | 18.12 | 7.8% | 0.0% | 0%-49% | 4.7% | -100.0% |
| value | safe | 6 | 2.0 | 3.24 | 33.8% | 33.3% | 10%-70% | 27.1% | +12.2% |
| value | medium | 6 | 3.0 | 7.01 | 17.2% | 0.0% | 0%-39% | 11.9% | -100.0% |

## By season (accuracy mode)

| Tier | Season | Slips | Predicted win | Actual win |
|---|---|---:|---:|---:|
| safe | 2024/25 | 40 | 39.8% | 42.5% |
| medium | 2024/25 | 38 | 21.0% | 21.1% |
| big | 2024/25 | 38 | 10.8% | 5.3% |
| safe | 2025/26 | 40 | 37.7% | 30.0% |
| medium | 2025/26 | 39 | 19.0% | 15.4% |
| big | 2025/26 | 38 | 9.5% | 10.5% |
| safe | 2026/27 | 7 | 36.7% | 28.6% |
| medium | 2026/27 | 7 | 18.0% | 28.6% |
| big | 2026/27 | 7 | 8.8% | 14.3% |

## Markets used in slips (accuracy mode)

| Tier | Market | Legs | Leg hit rate |
|---|---|---:|---:|
| safe | home_1up | 42 | 64.3% |
| safe | over_1.5 | 39 | 74.4% |
| safe | over_2.5 | 24 | 41.7% |
| safe | away_1up | 22 | 40.9% |
| safe | under_3.5 | 14 | 71.4% |
| safe | away_win | 10 | 70.0% |
| safe | home_win | 8 | 25.0% |
| safe | under_2.5 | 7 | 57.1% |
| safe | btts_yes | 6 | 83.3% |
| safe | over_3.5 | 1 | 100.0% |
| safe | home_first | 1 | 0.0% |
| medium | home_1up | 83 | 56.6% |
| medium | over_1.5 | 43 | 79.1% |
| medium | away_1up | 39 | 53.8% |
| medium | over_2.5 | 21 | 38.1% |
| medium | under_3.5 | 20 | 80.0% |
| medium | away_win | 13 | 53.8% |
| medium | over_3.5 | 9 | 33.3% |
| medium | home_win | 8 | 62.5% |
| medium | btts_yes | 7 | 71.4% |
| medium | under_2.5 | 6 | 50.0% |
| medium | btts_no | 1 | 0.0% |
| medium | home_first | 1 | 0.0% |
| medium | away_first | 1 | 0.0% |
| big | home_1up | 95 | 54.7% |
| big | over_1.5 | 63 | 79.4% |
| big | away_1up | 58 | 55.2% |
| big | away_win | 25 | 56.0% |
| big | under_3.5 | 22 | 86.4% |
| big | over_2.5 | 21 | 28.6% |
| big | home_win | 13 | 53.8% |
| big | over_3.5 | 12 | 25.0% |
| big | under_2.5 | 11 | 54.5% |
| big | btts_yes | 7 | 71.4% |
| big | home_first | 3 | 0.0% |
| big | btts_no | 1 | 0.0% |
| big | away_first | 1 | 0.0% |

## Estimated odds sanity check

Bookmaker-implied probability vs actual rate across all test matches, per market. Large gaps would mean the estimated odds are unrealistic.

| Market | Bookmaker-implied | Model (calibrated) | Actual | Median est. odds |
|---|---:|---:|---:|---:|
| home_win | 44.2% | 43.9% | 41.5% | 2.19 |
| draw | 23.8% | 24.0% | 26.1% | 3.77 |
| away_win | 32.0% | 31.9% | 32.3% | 3.15 |
| over_1.5 | 79.7% | 80.0% | 79.5% | 1.17 |
| over_2.5 | 56.6% | 57.1% | 55.7% | 1.66 |
| over_3.5 | 34.6% | 35.3% | 31.7% | 2.76 |
| under_2.5 | 43.4% | 42.9% | 44.3% | 2.13 |
| under_3.5 | 65.4% | 64.7% | 68.3% | 1.41 |
| btts_yes | 55.7% | 56.1% | 56.4% | 1.67 |
| btts_no | 44.3% | 43.9% | 43.6% | 2.12 |
| home_1up | 59.4% | 60.2% | 60.5% | 1.58 |
| away_1up | 48.9% | 49.9% | 50.8% | 1.94 |
| home_first | 51.6% | 51.6% | 51.1% | 1.82 |
| away_first | 42.2% | 42.5% | 43.1% | 2.26 |
| over_0.5 | 88.5% | 89.2% | 100.0% | 1.06 |
