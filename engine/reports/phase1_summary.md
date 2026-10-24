# Phase 1 league summary

Test seasons are 2024/25, 2025/26, and the played part of 2026/27. Hyperparameters were selected only on 2021/22 through 2023/24. Bookmaker probabilities have their margin removed. Double chance means home or draw (1X). Calibration deviation is the maximum absolute difference between mean prediction and actual rate across 10 equal-width bins containing at least 50 matches.

## Data coverage

| League | Match rows, 2014/15 onward | Test matches | Missing xG | Understat merge |
|---|---:|---:|---:|---:|
| Premier League | 4,630 | 830 | 0.00% | 100.00% |
| La Liga | 4,649 | 849 | 0.02% | 99.98% |
| Serie A | 4,630 | 830 | 0.00% | 100.00% |
| Bundesliga | 3,726 | 666 | 0.00% | 100.00% |
| Ligue 1 | 4,300 | 675 | 0.02% | 99.98% |

Ligue 1 has 279 played matches in the abandoned 2019/20 season and 306 matches in each completed 18-team season from 2023/24. Current 2026/27 totals reflect matches played by 24 October 2026.

## 1X2 test results

| League | Model accuracy | Model log loss | Opening accuracy | Opening log loss | Closing accuracy | Closing log loss |
|---|---:|---:|---:|---:|---:|---:|
| Premier League | 51.81% | 0.9970 | 51.45% | 0.9940 | 51.81% | 0.9914 |
| La Liga | 53.59% | 0.9718 | 54.77% | 0.9551 | 55.48% | 0.9516 |
| Serie A | 53.49% | 0.9802 | 53.98% | 0.9617 | 54.70% | 0.9612 |
| Bundesliga | 52.25% | 0.9950 | 53.60% | 0.9720 | 54.65% | 0.9705 |
| Ligue 1 | 53.33% | 0.9877 | 54.22% | 0.9673 | 54.37% | 0.9671 |

The model column is the validation-selected Dixon-Coles blend variant. Opening and closing columns use normalized inverse odds.

## Calibration maximum deviation

| League | Home 1Up | Over 1.5 | Double chance 1X | Home win | Criterion C |
|---|---:|---:|---:|---:|---|
| Premier League | 0.073 | 0.025 | 0.042 | 0.097 | FAIL |
| La Liga | 0.046 | 0.086 | 0.068 | 0.087 | FAIL |
| Serie A | 0.057 | 0.014 | 0.120 | 0.082 | FAIL |
| Bundesliga | 0.052 | 0.018 | 0.043 | 0.068 | FAIL |
| Ligue 1 | 0.084 | 0.019 | 0.050 | 0.075 | FAIL |

## Accumulator slips

### Premier League

| Tier | Count | Average odds | Predicted | Actual | Actual 95% CI |
|---|---:|---:|---:|---:|---:|
| Safe | 166 | 2.55 | 38.0% | 37.3% | 30.4% to 44.9% |
| Medium | 135 | 3.54 | 26.8% | 23.7% | 17.3% to 31.5% |
| Big | 119 | 8.08 | 11.9% | 13.4% | 8.4% to 20.7% |

### La Liga

| Tier | Count | Average odds | Predicted | Actual | Actual 95% CI |
|---|---:|---:|---:|---:|---:|
| Safe | 188 | 2.54 | 36.9% | 30.3% | 24.2% to 37.2% |
| Medium | 161 | 3.54 | 25.5% | 19.3% | 13.9% to 26.0% |
| Big | 137 | 8.07 | 11.0% | 6.6% | 3.5% to 12.0% |

### Serie A

| Tier | Count | Average odds | Predicted | Actual | Actual 95% CI |
|---|---:|---:|---:|---:|---:|
| Safe | 210 | 2.54 | 36.3% | 32.4% | 26.4% to 39.0% |
| Medium | 164 | 3.54 | 25.0% | 25.0% | 19.0% to 32.1% |
| Big | 108 | 8.09 | 10.8% | 6.5% | 3.2% to 12.8% |

### Bundesliga

| Tier | Count | Average odds | Predicted | Actual | Actual 95% CI |
|---|---:|---:|---:|---:|---:|
| Safe | 147 | 2.54 | 36.1% | 27.9% | 21.3% to 35.6% |
| Medium | 103 | 3.53 | 24.8% | 23.3% | 16.2% to 32.3% |
| Big | 75 | 8.05 | 10.8% | 8.0% | 3.7% to 16.4% |

### Ligue 1

| Tier | Count | Average odds | Predicted | Actual | Actual 95% CI |
|---|---:|---:|---:|---:|---:|
| Safe | 156 | 2.53 | 36.5% | 34.6% | 27.6% to 42.4% |
| Medium | 141 | 3.53 | 25.0% | 19.1% | 13.5% to 26.4% |
| Big | 73 | 8.05 | 10.7% | 11.0% | 5.7% to 20.2% |

## GO or NO-GO

Criterion A requires model 1X2 log loss no more than opening log loss plus 0.010. Criterion B requires the predicted rate for every tier to lie inside the 95% confidence interval of the actual rate. Criterion C requires all four calibration deviations to be no more than 0.05.

| League | A: 1X2 | B: all tiers | C: calibration | Decision |
|---|---|---|---|---|
| Premier League | PASS | PASS | FAIL | NO-GO |
| La Liga | FAIL | PASS | FAIL | NO-GO |
| Serie A | FAIL | PASS | FAIL | NO-GO |
| Bundesliga | FAIL | FAIL | FAIL | NO-GO |
| Ligue 1 | FAIL | PASS | FAIL | NO-GO |

No test-season result was used to alter tuning, calibration selection, market blend weights, or thresholds.
