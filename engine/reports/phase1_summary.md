# Phase 1b league summary

All metrics use the final probabilities supplied to accumulator selection. The blended mode uses a model weight learned from 2021/22 through 2023/24 for the first test season, then updates from earlier seasons only. The market mode uses Platt calibrated bookmaker consensus with margin removed. No test season is used to tune its own probabilities.

Criterion A requires final 1X2 log loss to be no more than bookmaker opening log loss plus 0.010. Criterion B requires every tier's predicted win rate to fall inside the Wilson 95% interval for its actual rate. Criterion C uses 10 equal count bins and requires every absolute calibration z score to be at most 3, plus an overall logistic calibration slope from 0.8 through 1.2.

## Final recommendation

| League | Blended A | Blended B | Blended C | Market A | Market B | Market C | Recommendation |
|---|---|---|---|---|---|---|---|
| Premier League | PASS | PASS | FAIL | PASS | PASS | PASS | GO-MARKET |
| La Liga | PASS | PASS | FAIL | PASS | PASS | FAIL | NO-GO |
| Serie A | PASS | FAIL | PASS | PASS | PASS | PASS | GO-MARKET |
| Bundesliga | PASS | PASS | FAIL | PASS | PASS | FAIL | NO-GO |
| Ligue 1 | PASS | PASS | FAIL | PASS | PASS | FAIL | NO-GO |

## Learned model weights

| League | 2024/25 | 2025/26 | 2026/27 |
|---|---:|---:|---:|
| Premier League | 0.35 | 0.40 | 0.35 |
| La Liga | 0.45 | 0.35 | 0.30 |
| Serie A | 0.40 | 0.25 | 0.15 |
| Bundesliga | 0.35 | 0.30 | 0.20 |
| Ligue 1 | 0.40 | 0.35 | 0.25 |

## Premier League

### 1X2

| Mode | Accuracy | Log loss | Criterion A |
|---|---:|---:|---|
| Bookmaker opening | 51.57% | 0.9939 | Reference |
| Blended | 51.33% | 0.9927 | PASS |
| Market | 51.33% | 0.9956 | PASS |

### Calibration

| Mode | Market | Maximum absolute z | Slope | Pass |
|---|---|---:|---:|---|
| Blended | Home 1Up | 1.73 | 1.239 | FAIL |
| Blended | Over 1.5 | 1.78 | 0.880 | PASS |
| Blended | Double chance 1X | 1.74 | 0.975 | PASS |
| Blended | Home win | 1.77 | 1.044 | PASS |
| Market | Home 1Up | 1.24 | 1.173 | PASS |
| Market | Over 1.5 | 1.78 | 1.001 | PASS |
| Market | Double chance 1X | 1.97 | 0.885 | PASS |
| Market | Home win | 1.63 | 0.982 | PASS |

### Accumulator slips

| Mode | Tier | Count | Average odds | Predicted | Actual | Actual 95% CI | Pass |
|---|---|---:|---:|---:|---:|---|---|
| Blended | Safe | 166 | 2.56 | 39.0% | 34.9% | 28.1% to 42.5% | PASS |
| Blended | Medium | 135 | 3.56 | 28.0% | 25.9% | 19.3% to 33.9% | PASS |
| Blended | Big | 119 | 8.12 | 12.7% | 13.4% | 8.4% to 20.7% | PASS |
| Market | Safe | 166 | 2.54 | 37.5% | 33.1% | 26.4% to 40.6% | PASS |
| Market | Medium | 135 | 3.54 | 26.5% | 23.7% | 17.3% to 31.5% | PASS |
| Market | Big | 119 | 8.08 | 11.5% | 7.6% | 4.0% to 13.8% | PASS |

## La Liga

### 1X2

| Mode | Accuracy | Log loss | Criterion A |
|---|---:|---:|---|
| Bookmaker opening | 54.72% | 0.9565 | Reference |
| Blended | 54.36% | 0.9540 | PASS |
| Market | 54.01% | 0.9534 | PASS |

### Calibration

| Mode | Market | Maximum absolute z | Slope | Pass |
|---|---|---:|---:|---|
| Blended | Home 1Up | 1.75 | 1.049 | PASS |
| Blended | Over 1.5 | 2.28 | 1.750 | FAIL |
| Blended | Double chance 1X | 1.98 | 0.968 | PASS |
| Blended | Home win | 2.51 | 1.058 | PASS |
| Market | Home 1Up | 1.27 | 1.022 | PASS |
| Market | Over 1.5 | 1.66 | 1.582 | FAIL |
| Market | Double chance 1X | 1.68 | 0.930 | PASS |
| Market | Home win | 2.06 | 1.041 | PASS |

### Accumulator slips

| Mode | Tier | Count | Average odds | Predicted | Actual | Actual 95% CI | Pass |
|---|---|---:|---:|---:|---:|---|---|
| Blended | Safe | 188 | 2.55 | 39.0% | 33.5% | 27.2% to 40.5% | PASS |
| Blended | Medium | 161 | 3.56 | 27.6% | 22.4% | 16.6% to 29.4% | PASS |
| Blended | Big | 137 | 8.12 | 11.9% | 8.0% | 4.5% to 13.8% | PASS |
| Market | Safe | 188 | 2.54 | 37.6% | 40.4% | 33.7% to 47.6% | PASS |
| Market | Medium | 161 | 3.55 | 26.6% | 20.5% | 15.0% to 27.4% | PASS |
| Market | Big | 137 | 8.11 | 11.0% | 8.8% | 5.1% to 14.7% | PASS |

## Serie A

### 1X2

| Mode | Accuracy | Log loss | Criterion A |
|---|---:|---:|---|
| Bookmaker opening | 53.86% | 0.9622 | Reference |
| Blended | 54.46% | 0.9637 | PASS |
| Market | 54.70% | 0.9596 | PASS |

### Calibration

| Mode | Market | Maximum absolute z | Slope | Pass |
|---|---|---:|---:|---|
| Blended | Home 1Up | 2.64 | 1.101 | PASS |
| Blended | Over 1.5 | 2.52 | 1.083 | PASS |
| Blended | Double chance 1X | 2.61 | 1.013 | PASS |
| Blended | Home win | 1.70 | 1.082 | PASS |
| Market | Home 1Up | 1.83 | 1.062 | PASS |
| Market | Over 1.5 | 1.95 | 1.113 | PASS |
| Market | Double chance 1X | 2.61 | 0.962 | PASS |
| Market | Home win | 1.67 | 1.045 | PASS |

### Accumulator slips

| Mode | Tier | Count | Average odds | Predicted | Actual | Actual 95% CI | Pass |
|---|---|---:|---:|---:|---:|---|---|
| Blended | Safe | 210 | 2.56 | 38.8% | 36.2% | 30.0% to 42.9% | PASS |
| Blended | Medium | 164 | 3.57 | 27.7% | 25.6% | 19.5% to 32.8% | PASS |
| Blended | Big | 108 | 8.13 | 12.2% | 4.6% | 2.0% to 10.4% | FAIL |
| Market | Safe | 210 | 2.56 | 38.4% | 37.6% | 31.3% to 44.3% | PASS |
| Market | Medium | 164 | 3.57 | 27.4% | 26.8% | 20.6% to 34.1% | PASS |
| Market | Big | 108 | 8.12 | 11.8% | 11.1% | 6.5% to 18.4% | PASS |

## Bundesliga

### 1X2

| Mode | Accuracy | Log loss | Criterion A |
|---|---:|---:|---|
| Bookmaker opening | 53.61% | 0.9749 | Reference |
| Blended | 52.71% | 0.9812 | PASS |
| Market | 53.01% | 0.9776 | PASS |

### Calibration

| Mode | Market | Maximum absolute z | Slope | Pass |
|---|---|---:|---:|---|
| Blended | Home 1Up | 2.86 | 1.024 | PASS |
| Blended | Over 1.5 | 2.50 | 0.944 | PASS |
| Blended | Double chance 1X | 1.59 | 0.989 | PASS |
| Blended | Home win | 2.15 | 1.304 | FAIL |
| Market | Home 1Up | 2.49 | 0.999 | PASS |
| Market | Over 1.5 | 1.75 | 0.949 | PASS |
| Market | Double chance 1X | 2.58 | 0.975 | PASS |
| Market | Home win | 1.99 | 1.283 | FAIL |

### Accumulator slips

| Mode | Tier | Count | Average odds | Predicted | Actual | Actual 95% CI | Pass |
|---|---|---:|---:|---:|---:|---|---|
| Blended | Safe | 147 | 2.55 | 37.3% | 32.7% | 25.6% to 40.6% | PASS |
| Blended | Medium | 103 | 3.54 | 26.4% | 21.4% | 14.5% to 30.2% | PASS |
| Blended | Big | 75 | 8.07 | 11.7% | 5.3% | 2.1% to 12.9% | PASS |
| Market | Safe | 147 | 2.54 | 36.5% | 35.4% | 28.1% to 43.4% | PASS |
| Market | Medium | 103 | 3.54 | 25.5% | 22.3% | 15.4% to 31.3% | PASS |
| Market | Big | 75 | 8.07 | 10.8% | 12.0% | 6.4% to 21.3% | PASS |

## Ligue 1

### 1X2

| Mode | Accuracy | Log loss | Criterion A |
|---|---:|---:|---|
| Bookmaker opening | 54.22% | 0.9673 | Reference |
| Blended | 54.22% | 0.9737 | PASS |
| Market | 54.37% | 0.9700 | PASS |

### Calibration

| Mode | Market | Maximum absolute z | Slope | Pass |
|---|---|---:|---:|---|
| Blended | Home 1Up | 1.57 | 1.027 | PASS |
| Blended | Over 1.5 | 1.37 | 0.753 | FAIL |
| Blended | Double chance 1X | 1.05 | 1.083 | PASS |
| Blended | Home win | 1.88 | 0.954 | PASS |
| Market | Home 1Up | 1.69 | 0.991 | PASS |
| Market | Over 1.5 | 1.31 | 0.746 | FAIL |
| Market | Double chance 1X | 1.74 | 1.057 | PASS |
| Market | Home win | 1.62 | 0.923 | PASS |

### Accumulator slips

| Mode | Tier | Count | Average odds | Predicted | Actual | Actual 95% CI | Pass |
|---|---|---:|---:|---:|---:|---|---|
| Blended | Safe | 156 | 2.55 | 38.2% | 34.0% | 27.0% to 41.7% | PASS |
| Blended | Medium | 141 | 3.55 | 26.8% | 22.0% | 15.9% to 29.5% | PASS |
| Blended | Big | 73 | 8.10 | 12.1% | 6.8% | 3.0% to 15.1% | PASS |
| Market | Safe | 156 | 2.54 | 37.2% | 35.3% | 28.2% to 43.0% | PASS |
| Market | Medium | 141 | 3.55 | 25.9% | 24.8% | 18.4% to 32.6% | PASS |
| Market | Big | 73 | 8.07 | 11.5% | 9.6% | 4.7% to 18.5% | PASS |

Double chance means home or draw (1X).
