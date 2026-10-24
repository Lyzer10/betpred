# Stage 3 report

Test seasons: 2024/25, 2025/26, 2026/27 (830 matches).

## Calibration metrics

| Market | Method | Log loss | Brier score |
|---|---|---:|---:|
| home | raw | 0.5948 | 0.2048 |
| home | Platt | 0.5950 | 0.2050 |
| home | isotonic | 0.5952 | 0.2049 |
| draw | raw | 0.5714 | 0.1921 |
| draw | Platt | 0.5728 | 0.1926 |
| draw | isotonic | 0.5749 | 0.1935 |
| away | raw | 0.5568 | 0.1878 |
| away | Platt | 0.5571 | 0.1879 |
| away | isotonic | 0.5565 | 0.1873 |
| over05 | raw | 0.2776 | 0.0727 |
| over05 | Platt | 0.2755 | 0.0723 |
| over05 | isotonic | 0.3113 | 0.0751 |
| over15 | raw | 0.5942 | 0.2011 |
| over15 | Platt | 0.5851 | 0.1978 |
| over15 | isotonic | 0.5872 | 0.1985 |
| over25 | raw | 0.7002 | 0.2533 |
| over25 | Platt | 0.6917 | 0.2493 |
| over25 | isotonic | 0.6948 | 0.2508 |
| over35 | raw | 0.5561 | 0.1848 |
| over35 | Platt | 0.5528 | 0.1835 |
| over35 | isotonic | 0.5537 | 0.1840 |
| btts | raw | 0.6992 | 0.2528 |
| btts | Platt | 0.6952 | 0.2510 |
| btts | isotonic | 0.7275 | 0.2518 |
| home_clean_sheet | raw | 0.5934 | 0.2031 |
| home_clean_sheet | Platt | 0.5925 | 0.2027 |
| home_clean_sheet | isotonic | 0.5903 | 0.2018 |
| away_clean_sheet | raw | 0.5509 | 0.1847 |
| away_clean_sheet | Platt | 0.5539 | 0.1864 |
| away_clean_sheet | isotonic | 0.5848 | 0.1864 |
| home_first | raw | 0.6539 | 0.2312 |
| home_first | Platt | 0.6557 | 0.2320 |
| home_first | isotonic | 0.6582 | 0.2329 |
| away_first | raw | 0.6434 | 0.2262 |
| away_first | Platt | 0.6435 | 0.2262 |
| away_first | isotonic | 0.6464 | 0.2275 |
| no_goal | raw | 0.3531 | 0.0990 |
| no_goal | Platt | 0.3611 | 0.1004 |
| no_goal | isotonic | 0.3953 | 0.1027 |
| home_1up | raw | 0.6315 | 0.2205 |
| home_1up | Platt | 0.6353 | 0.2221 |
| home_1up | isotonic | 0.6389 | 0.2236 |
| away_1up | raw | 0.6434 | 0.2261 |
| away_1up | Platt | 0.6436 | 0.2262 |
| away_1up | isotonic | 0.6482 | 0.2279 |

## Calibration tables

### Home win, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.081 | 0.000 | 8 |
| 0.1 to 0.2 | 0.160 | 0.153 | 118 |
| 0.2 to 0.3 | 0.250 | 0.217 | 138 |
| 0.3 to 0.4 | 0.356 | 0.333 | 180 |
| 0.4 to 0.5 | 0.451 | 0.531 | 145 |
| 0.5 to 0.6 | 0.548 | 0.522 | 115 |
| 0.6 to 0.7 | 0.648 | 0.678 | 87 |
| 0.7 to 0.8 | 0.745 | 0.714 | 35 |
| 0.8 to 0.9 | 0.827 | 0.750 | 4 |
| 0.9 to 1.0 | NA | NA | 0 |

### Home win, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.082 | 0.000 | 10 |
| 0.1 to 0.2 | 0.156 | 0.163 | 129 |
| 0.2 to 0.3 | 0.249 | 0.225 | 142 |
| 0.3 to 0.4 | 0.352 | 0.349 | 175 |
| 0.4 to 0.5 | 0.447 | 0.529 | 140 |
| 0.5 to 0.6 | 0.544 | 0.536 | 112 |
| 0.6 to 0.7 | 0.645 | 0.686 | 86 |
| 0.7 to 0.8 | 0.745 | 0.688 | 32 |
| 0.8 to 0.9 | 0.826 | 0.750 | 4 |
| 0.9 to 1.0 | NA | NA | 0 |

### Over 1.5, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | NA | NA | 0 |
| 0.3 to 0.4 | NA | NA | 0 |
| 0.4 to 0.5 | NA | NA | 0 |
| 0.5 to 0.6 | 0.566 | 0.743 | 35 |
| 0.6 to 0.7 | 0.658 | 0.712 | 306 |
| 0.7 to 0.8 | 0.744 | 0.746 | 370 |
| 0.8 to 0.9 | 0.836 | 0.724 | 116 |
| 0.9 to 1.0 | 0.908 | 0.667 | 3 |

### Over 1.5, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | NA | NA | 0 |
| 0.3 to 0.4 | NA | NA | 0 |
| 0.4 to 0.5 | NA | NA | 0 |
| 0.5 to 0.6 | NA | NA | 0 |
| 0.6 to 0.7 | 0.698 | 0.333 | 3 |
| 0.7 to 0.8 | 0.748 | 0.734 | 816 |
| 0.8 to 0.9 | 0.807 | 0.545 | 11 |
| 0.9 to 1.0 | NA | NA | 0 |

### Over 2.5, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | 0.278 | 0.348 | 23 |
| 0.3 to 0.4 | 0.362 | 0.456 | 206 |
| 0.4 to 0.5 | 0.449 | 0.477 | 350 |
| 0.5 to 0.6 | 0.542 | 0.506 | 176 |
| 0.6 to 0.7 | 0.639 | 0.554 | 65 |
| 0.7 to 0.8 | 0.719 | 0.500 | 10 |
| 0.8 to 0.9 | NA | NA | 0 |
| 0.9 to 1.0 | NA | NA | 0 |

### Over 2.5, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | NA | NA | 0 |
| 0.3 to 0.4 | 0.383 | 0.489 | 47 |
| 0.4 to 0.5 | 0.455 | 0.470 | 558 |
| 0.5 to 0.6 | 0.535 | 0.505 | 212 |
| 0.6 to 0.7 | 0.618 | 0.538 | 13 |
| 0.7 to 0.8 | NA | NA | 0 |
| 0.8 to 0.9 | NA | NA | 0 |
| 0.9 to 1.0 | NA | NA | 0 |

### BTTS, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.159 | 1.000 | 1 |
| 0.2 to 0.3 | 0.247 | 1.000 | 1 |
| 0.3 to 0.4 | 0.373 | 0.485 | 97 |
| 0.4 to 0.5 | 0.453 | 0.471 | 435 |
| 0.5 to 0.6 | 0.539 | 0.502 | 259 |
| 0.6 to 0.7 | 0.628 | 0.639 | 36 |
| 0.7 to 0.8 | 0.728 | 1.000 | 1 |
| 0.8 to 0.9 | NA | NA | 0 |
| 0.9 to 1.0 | NA | NA | 0 |

### BTTS, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | NA | NA | 0 |
| 0.3 to 0.4 | 0.341 | 1.000 | 1 |
| 0.4 to 0.5 | 0.485 | 0.479 | 213 |
| 0.5 to 0.6 | 0.530 | 0.493 | 609 |
| 0.6 to 0.7 | 0.615 | 0.714 | 7 |
| 0.7 to 0.8 | NA | NA | 0 |
| 0.8 to 0.9 | NA | NA | 0 |
| 0.9 to 1.0 | NA | NA | 0 |

### Home first scorer, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.185 | 0.000 | 4 |
| 0.2 to 0.3 | 0.266 | 0.230 | 87 |
| 0.3 to 0.4 | 0.348 | 0.356 | 163 |
| 0.4 to 0.5 | 0.452 | 0.442 | 208 |
| 0.5 to 0.6 | 0.548 | 0.537 | 190 |
| 0.6 to 0.7 | 0.647 | 0.613 | 124 |
| 0.7 to 0.8 | 0.734 | 0.731 | 52 |
| 0.8 to 0.9 | 0.815 | 0.500 | 2 |
| 0.9 to 1.0 | NA | NA | 0 |

### Home first scorer, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.184 | 0.000 | 2 |
| 0.2 to 0.3 | 0.267 | 0.222 | 72 |
| 0.3 to 0.4 | 0.349 | 0.348 | 161 |
| 0.4 to 0.5 | 0.456 | 0.430 | 207 |
| 0.5 to 0.6 | 0.548 | 0.525 | 183 |
| 0.6 to 0.7 | 0.644 | 0.594 | 138 |
| 0.7 to 0.8 | 0.733 | 0.714 | 63 |
| 0.8 to 0.9 | 0.813 | 0.750 | 4 |
| 0.9 to 1.0 | NA | NA | 0 |

### Home 1Up, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.195 | 0.000 | 1 |
| 0.2 to 0.3 | 0.268 | 0.179 | 39 |
| 0.3 to 0.4 | 0.353 | 0.317 | 139 |
| 0.4 to 0.5 | 0.454 | 0.409 | 149 |
| 0.5 to 0.6 | 0.552 | 0.592 | 201 |
| 0.6 to 0.7 | 0.651 | 0.651 | 149 |
| 0.7 to 0.8 | 0.745 | 0.739 | 111 |
| 0.8 to 0.9 | 0.838 | 0.800 | 40 |
| 0.9 to 1.0 | 0.911 | 1.000 | 1 |

### Home 1Up, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | 0.277 | 0.042 | 24 |
| 0.3 to 0.4 | 0.358 | 0.321 | 106 |
| 0.4 to 0.5 | 0.450 | 0.399 | 148 |
| 0.5 to 0.6 | 0.552 | 0.524 | 187 |
| 0.6 to 0.7 | 0.645 | 0.640 | 178 |
| 0.7 to 0.8 | 0.746 | 0.689 | 135 |
| 0.8 to 0.9 | 0.839 | 0.843 | 51 |
| 0.9 to 1.0 | 0.915 | 1.000 | 1 |

### Away 1Up, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.093 | 0.000 | 1 |
| 0.1 to 0.2 | 0.183 | 0.444 | 9 |
| 0.2 to 0.3 | 0.258 | 0.198 | 91 |
| 0.3 to 0.4 | 0.351 | 0.393 | 163 |
| 0.4 to 0.5 | 0.450 | 0.425 | 193 |
| 0.5 to 0.6 | 0.544 | 0.544 | 160 |
| 0.6 to 0.7 | 0.645 | 0.689 | 122 |
| 0.7 to 0.8 | 0.738 | 0.705 | 78 |
| 0.8 to 0.9 | 0.832 | 0.923 | 13 |
| 0.9 to 1.0 | NA | NA | 0 |

### Away 1Up, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.090 | 0.000 | 1 |
| 0.1 to 0.2 | 0.182 | 0.444 | 9 |
| 0.2 to 0.3 | 0.258 | 0.191 | 89 |
| 0.3 to 0.4 | 0.351 | 0.385 | 156 |
| 0.4 to 0.5 | 0.450 | 0.430 | 186 |
| 0.5 to 0.6 | 0.546 | 0.533 | 165 |
| 0.6 to 0.7 | 0.648 | 0.672 | 122 |
| 0.7 to 0.8 | 0.742 | 0.709 | 86 |
| 0.8 to 0.9 | 0.834 | 0.875 | 16 |
| 0.9 to 1.0 | NA | NA | 0 |

## Confidence buckets

| Market | Threshold | Hit rate | Count |
|---|---:|---:|---:|
| Home win | 0.60 | 68.85% | 122 |
| Home win | 0.65 | 75.34% | 73 |
| Home win | 0.70 | 69.44% | 36 |
| Home win | 0.75 | 80.00% | 20 |
| Home win | 0.80 | 75.00% | 4 |
| Home win | 0.85 | 100.00% | 1 |
| Home win | 0.90 | NA | 0 |
| Away win | 0.60 | 65.45% | 55 |
| Away win | 0.65 | 81.48% | 27 |
| Away win | 0.70 | 80.00% | 10 |
| Away win | 0.75 | 100.00% | 3 |
| Away win | 0.80 | NA | 0 |
| Away win | 0.85 | NA | 0 |
| Away win | 0.90 | NA | 0 |
| Over 0.5 | 0.60 | 92.17% | 830 |
| Over 0.5 | 0.65 | 92.17% | 830 |
| Over 0.5 | 0.70 | 92.17% | 830 |
| Over 0.5 | 0.75 | 92.17% | 830 |
| Over 0.5 | 0.80 | 92.17% | 830 |
| Over 0.5 | 0.85 | 92.17% | 830 |
| Over 0.5 | 0.90 | 92.16% | 829 |
| Over 1.5 | 0.60 | 73.01% | 830 |
| Over 1.5 | 0.65 | 73.01% | 830 |
| Over 1.5 | 0.70 | 73.16% | 827 |
| Over 1.5 | 0.75 | 73.08% | 338 |
| Over 1.5 | 0.80 | 54.55% | 11 |
| Over 1.5 | 0.85 | NA | 0 |
| Over 1.5 | 0.90 | NA | 0 |
| Over 2.5 | 0.60 | 53.85% | 13 |
| Over 2.5 | 0.65 | 100.00% | 1 |
| Over 2.5 | 0.70 | NA | 0 |
| Over 2.5 | 0.75 | NA | 0 |
| Over 2.5 | 0.80 | NA | 0 |
| Over 2.5 | 0.85 | NA | 0 |
| Over 2.5 | 0.90 | NA | 0 |
| BTTS yes | 0.60 | 71.43% | 7 |
| BTTS yes | 0.65 | NA | 0 |
| BTTS yes | 0.70 | NA | 0 |
| BTTS yes | 0.75 | NA | 0 |
| BTTS yes | 0.80 | NA | 0 |
| BTTS yes | 0.85 | NA | 0 |
| BTTS yes | 0.90 | NA | 0 |
| Home first scorer | 0.60 | 63.41% | 205 |
| Home first scorer | 0.65 | 66.14% | 127 |
| Home first scorer | 0.70 | 71.64% | 67 |
| Home first scorer | 0.75 | 70.83% | 24 |
| Home first scorer | 0.80 | 75.00% | 4 |
| Home first scorer | 0.85 | NA | 0 |
| Home first scorer | 0.90 | NA | 0 |
| Home 1Up | 0.60 | 68.77% | 365 |
| Home 1Up | 0.65 | 72.39% | 268 |
| Home 1Up | 0.70 | 73.26% | 187 |
| Home 1Up | 0.75 | 76.79% | 112 |
| Home 1Up | 0.80 | 84.62% | 52 |
| Home 1Up | 0.85 | 75.00% | 20 |
| Home 1Up | 0.90 | 100.00% | 1 |
| Away 1Up | 0.60 | 70.09% | 224 |
| Away 1Up | 0.65 | 70.97% | 155 |
| Away 1Up | 0.70 | 73.53% | 102 |
| Away 1Up | 0.75 | 77.55% | 49 |
| Away 1Up | 0.80 | 87.50% | 16 |
| Away 1Up | 0.85 | 100.00% | 4 |
| Away 1Up | 0.90 | NA | 0 |

## Simulation checks

Timing markets are P(event) = sum over final scores of P_DC(score) x P_sim(event | score), so final-score markets come from the DC matrix exactly. The raw (unweighted) simulation is shown below as a diagnostic of how well the minute-level process reproduces DC on its own.

| Raw simulation check | Mean absolute difference |
|---|---:|
| Home win versus DC matrix | 0.0131 |
| Draw versus DC matrix | 0.0151 |
| Over 2.5 versus DC matrix | 0.0021 |
| Mean goals versus DC lambda (relative) | 0.0014 |

| Outcome | Simulated rate | Actual rate |
|---|---:|---:|
| Home first scorer | 48.05% | 46.63% |
| Away first scorer | 42.72% | 42.29% |
| No goal | 9.23% | 11.08% |
| Home 1Up | 54.52% | 53.37% |
| Away 1Up | 48.61% | 48.92% |

## Final fold time profile

| Bucket | Goal share |
|---|---:|
| 1 to 15 | 0.135 |
| 16 to 30 | 0.144 |
| 31 to 45 plus | 0.152 |
| 46 to 60 | 0.188 |
| 61 to 75 | 0.173 |
| 76 to 90 plus | 0.208 |

## Final fold state multipliers

| State | Multiplier |
|---|---:|
| level | 0.971 |
| leading_1 | 0.864 |
| leading_2plus | 0.891 |
| trailing_1 | 1.100 |
| trailing_2plus | 1.052 |

## Calibrated value test

| Bet | Bets | Hit rate | ROI | Positive closing line value | Sample |
|---|---:|---:|---:|---:|---|
| 1X2 home | 74 | 24.32% | -28.05% | 40.54% | insufficient sample |
| 1X2 draw | 427 | 25.29% | -3.07% | 65.11% | adequate sample |
| 1X2 away | 265 | 24.53% | -16.29% | 48.30% | adequate sample |
| Goals over 2.5 | 144 | 38.89% | -7.66% | 45.14% | insufficient sample |
| Goals under 2.5 | 119 | 47.06% | 3.76% | 46.22% | insufficient sample |
