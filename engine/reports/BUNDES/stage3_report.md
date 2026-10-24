# Stage 3 report

Test seasons: 2024/25, 2025/26, 2026/27 (666 matches).

## Calibration metrics

| Market | Method | Log loss | Brier score |
|---|---|---:|---:|
| home | raw | 0.5978 | 0.2053 |
| home | Platt | 0.6003 | 0.2066 |
| home | isotonic | 0.6029 | 0.2066 |
| draw | raw | 0.5621 | 0.1858 |
| draw | Platt | 0.5589 | 0.1854 |
| draw | isotonic | 0.5981 | 0.1862 |
| away | raw | 0.5860 | 0.1991 |
| away | Platt | 0.5857 | 0.1995 |
| away | isotonic | 0.6567 | 0.1994 |
| over05 | raw | 0.2213 | 0.0537 |
| over05 | Platt | 0.2223 | 0.0537 |
| over05 | isotonic | 0.2897 | 0.0540 |
| over15 | raw | 0.4747 | 0.1473 |
| over15 | Platt | 0.4699 | 0.1466 |
| over15 | isotonic | 0.5423 | 0.1467 |
| over25 | raw | 0.6582 | 0.2314 |
| over25 | Platt | 0.6539 | 0.2301 |
| over25 | isotonic | 0.7278 | 0.2302 |
| over35 | raw | 0.6770 | 0.2411 |
| over35 | Platt | 0.6739 | 0.2403 |
| over35 | isotonic | 0.7927 | 0.2429 |
| btts | raw | 0.6739 | 0.2405 |
| btts | Platt | 0.6736 | 0.2403 |
| btts | isotonic | 0.7514 | 0.2417 |
| home_clean_sheet | raw | 0.5495 | 0.1822 |
| home_clean_sheet | Platt | 0.5496 | 0.1822 |
| home_clean_sheet | isotonic | 0.6692 | 0.1870 |
| away_clean_sheet | raw | 0.4736 | 0.1536 |
| away_clean_sheet | Platt | 0.4799 | 0.1554 |
| away_clean_sheet | isotonic | 0.4793 | 0.1560 |
| home_first | raw | 0.6546 | 0.2311 |
| home_first | Platt | 0.6571 | 0.2321 |
| home_first | isotonic | 0.6621 | 0.2343 |
| away_first | raw | 0.6485 | 0.2283 |
| away_first | Platt | 0.6510 | 0.2293 |
| away_first | isotonic | 0.6978 | 0.2332 |
| no_goal | raw | 0.3338 | 0.0883 |
| no_goal | Platt | 0.3366 | 0.0895 |
| no_goal | isotonic | 0.4071 | 0.0901 |
| home_1up | raw | 0.6247 | 0.2178 |
| home_1up | Platt | 0.6270 | 0.2187 |
| home_1up | isotonic | 0.6656 | 0.2195 |
| away_1up | raw | 0.6591 | 0.2318 |
| away_1up | Platt | 0.6609 | 0.2325 |
| away_1up | isotonic | 0.7109 | 0.2396 |

## Calibration tables

### Home win, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.066 | 0.000 | 18 |
| 0.1 to 0.2 | 0.158 | 0.149 | 47 |
| 0.2 to 0.3 | 0.261 | 0.206 | 102 |
| 0.3 to 0.4 | 0.350 | 0.336 | 143 |
| 0.4 to 0.5 | 0.448 | 0.435 | 131 |
| 0.5 to 0.6 | 0.543 | 0.566 | 99 |
| 0.6 to 0.7 | 0.639 | 0.644 | 73 |
| 0.7 to 0.8 | 0.739 | 0.879 | 33 |
| 0.8 to 0.9 | 0.844 | 0.929 | 14 |
| 0.9 to 1.0 | 0.909 | 0.333 | 6 |

### Home win, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.075 | 0.000 | 15 |
| 0.1 to 0.2 | 0.162 | 0.146 | 41 |
| 0.2 to 0.3 | 0.264 | 0.196 | 102 |
| 0.3 to 0.4 | 0.351 | 0.325 | 154 |
| 0.4 to 0.5 | 0.449 | 0.459 | 146 |
| 0.5 to 0.6 | 0.548 | 0.586 | 111 |
| 0.6 to 0.7 | 0.638 | 0.684 | 57 |
| 0.7 to 0.8 | 0.738 | 0.929 | 28 |
| 0.8 to 0.9 | 0.844 | 0.583 | 12 |
| 0.9 to 1.0 | NA | NA | 0 |

### Over 1.5, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.144 | 1.000 | 1 |
| 0.2 to 0.3 | NA | NA | 0 |
| 0.3 to 0.4 | 0.369 | 0.000 | 1 |
| 0.4 to 0.5 | NA | NA | 0 |
| 0.5 to 0.6 | 0.532 | 1.000 | 3 |
| 0.6 to 0.7 | 0.670 | 0.793 | 29 |
| 0.7 to 0.8 | 0.759 | 0.765 | 170 |
| 0.8 to 0.9 | 0.849 | 0.832 | 404 |
| 0.9 to 1.0 | 0.926 | 0.931 | 58 |

### Over 1.5, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | NA | NA | 0 |
| 0.3 to 0.4 | NA | NA | 0 |
| 0.4 to 0.5 | 0.402 | 1.000 | 1 |
| 0.5 to 0.6 | NA | NA | 0 |
| 0.6 to 0.7 | 0.660 | 0.667 | 3 |
| 0.7 to 0.8 | 0.781 | 0.787 | 89 |
| 0.8 to 0.9 | 0.844 | 0.826 | 552 |
| 0.9 to 1.0 | 0.915 | 0.857 | 21 |

### Over 2.5, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.029 | 0.000 | 1 |
| 0.1 to 0.2 | 0.138 | 0.000 | 1 |
| 0.2 to 0.3 | 0.237 | 1.000 | 2 |
| 0.3 to 0.4 | 0.372 | 0.611 | 18 |
| 0.4 to 0.5 | 0.456 | 0.488 | 82 |
| 0.5 to 0.6 | 0.554 | 0.582 | 194 |
| 0.6 to 0.7 | 0.647 | 0.663 | 273 |
| 0.7 to 0.8 | 0.736 | 0.743 | 74 |
| 0.8 to 0.9 | 0.833 | 0.789 | 19 |
| 0.9 to 1.0 | 0.970 | 0.500 | 2 |

### Over 2.5, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.078 | 0.000 | 1 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | 0.241 | 0.000 | 1 |
| 0.3 to 0.4 | 0.350 | 1.000 | 3 |
| 0.4 to 0.5 | 0.470 | 0.482 | 56 |
| 0.5 to 0.6 | 0.558 | 0.559 | 238 |
| 0.6 to 0.7 | 0.640 | 0.679 | 315 |
| 0.7 to 0.8 | 0.735 | 0.804 | 46 |
| 0.8 to 0.9 | 0.820 | 0.750 | 4 |
| 0.9 to 1.0 | 0.934 | 0.500 | 2 |

### BTTS, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.070 | 0.000 | 1 |
| 0.1 to 0.2 | 0.180 | 0.000 | 1 |
| 0.2 to 0.3 | 0.246 | 0.333 | 3 |
| 0.3 to 0.4 | 0.370 | 0.667 | 6 |
| 0.4 to 0.5 | 0.466 | 0.603 | 68 |
| 0.5 to 0.6 | 0.557 | 0.542 | 253 |
| 0.6 to 0.7 | 0.645 | 0.633 | 308 |
| 0.7 to 0.8 | 0.716 | 0.667 | 24 |
| 0.8 to 0.9 | 0.863 | 0.500 | 2 |
| 0.9 to 1.0 | NA | NA | 0 |

### BTTS, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.092 | 0.000 | 1 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | 0.211 | 0.000 | 1 |
| 0.3 to 0.4 | 0.355 | 0.500 | 6 |
| 0.4 to 0.5 | 0.472 | 0.636 | 44 |
| 0.5 to 0.6 | 0.559 | 0.547 | 243 |
| 0.6 to 0.7 | 0.645 | 0.625 | 336 |
| 0.7 to 0.8 | 0.712 | 0.606 | 33 |
| 0.8 to 0.9 | 0.821 | 0.500 | 2 |
| 0.9 to 1.0 | NA | NA | 0 |

### Home first scorer, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.170 | 0.167 | 6 |
| 0.2 to 0.3 | 0.255 | 0.303 | 33 |
| 0.3 to 0.4 | 0.362 | 0.304 | 92 |
| 0.4 to 0.5 | 0.450 | 0.394 | 193 |
| 0.5 to 0.6 | 0.548 | 0.599 | 187 |
| 0.6 to 0.7 | 0.645 | 0.596 | 109 |
| 0.7 to 0.8 | 0.739 | 0.829 | 35 |
| 0.8 to 0.9 | 0.833 | 0.727 | 11 |
| 0.9 to 1.0 | NA | NA | 0 |

### Home first scorer, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.162 | 0.273 | 11 |
| 0.2 to 0.3 | 0.257 | 0.303 | 33 |
| 0.3 to 0.4 | 0.358 | 0.311 | 90 |
| 0.4 to 0.5 | 0.449 | 0.392 | 181 |
| 0.5 to 0.6 | 0.550 | 0.574 | 176 |
| 0.6 to 0.7 | 0.649 | 0.624 | 117 |
| 0.7 to 0.8 | 0.742 | 0.721 | 43 |
| 0.8 to 0.9 | 0.840 | 0.857 | 14 |
| 0.9 to 1.0 | 0.912 | 0.000 | 1 |

### Home 1Up, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.175 | 0.000 | 4 |
| 0.2 to 0.3 | 0.255 | 0.316 | 19 |
| 0.3 to 0.4 | 0.360 | 0.326 | 43 |
| 0.4 to 0.5 | 0.461 | 0.425 | 106 |
| 0.5 to 0.6 | 0.549 | 0.497 | 169 |
| 0.6 to 0.7 | 0.647 | 0.686 | 153 |
| 0.7 to 0.8 | 0.745 | 0.702 | 114 |
| 0.8 to 0.9 | 0.839 | 0.902 | 41 |
| 0.9 to 1.0 | 0.924 | 0.882 | 17 |

### Home 1Up, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.173 | 0.286 | 7 |
| 0.2 to 0.3 | 0.258 | 0.222 | 18 |
| 0.3 to 0.4 | 0.350 | 0.341 | 41 |
| 0.4 to 0.5 | 0.457 | 0.443 | 106 |
| 0.5 to 0.6 | 0.546 | 0.494 | 158 |
| 0.6 to 0.7 | 0.647 | 0.654 | 159 |
| 0.7 to 0.8 | 0.749 | 0.712 | 111 |
| 0.8 to 0.9 | 0.839 | 0.872 | 47 |
| 0.9 to 1.0 | 0.930 | 0.895 | 19 |

### Away 1Up, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.068 | 0.000 | 1 |
| 0.1 to 0.2 | 0.173 | 0.364 | 11 |
| 0.2 to 0.3 | 0.259 | 0.211 | 38 |
| 0.3 to 0.4 | 0.363 | 0.441 | 118 |
| 0.4 to 0.5 | 0.452 | 0.377 | 151 |
| 0.5 to 0.6 | 0.549 | 0.497 | 157 |
| 0.6 to 0.7 | 0.642 | 0.653 | 121 |
| 0.7 to 0.8 | 0.738 | 0.725 | 40 |
| 0.8 to 0.9 | 0.843 | 0.840 | 25 |
| 0.9 to 1.0 | 0.931 | 0.750 | 4 |

### Away 1Up, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.058 | 0.000 | 1 |
| 0.1 to 0.2 | 0.166 | 0.385 | 13 |
| 0.2 to 0.3 | 0.254 | 0.179 | 39 |
| 0.3 to 0.4 | 0.358 | 0.449 | 118 |
| 0.4 to 0.5 | 0.449 | 0.375 | 144 |
| 0.5 to 0.6 | 0.548 | 0.507 | 152 |
| 0.6 to 0.7 | 0.642 | 0.647 | 119 |
| 0.7 to 0.8 | 0.739 | 0.680 | 50 |
| 0.8 to 0.9 | 0.848 | 0.792 | 24 |
| 0.9 to 1.0 | 0.928 | 0.833 | 6 |

## Confidence buckets

| Market | Threshold | Hit rate | Count |
|---|---:|---:|---:|
| Home win | 0.60 | 74.23% | 97 |
| Home win | 0.65 | 80.70% | 57 |
| Home win | 0.70 | 82.50% | 40 |
| Home win | 0.75 | 76.19% | 21 |
| Home win | 0.80 | 58.33% | 12 |
| Home win | 0.85 | 50.00% | 4 |
| Home win | 0.90 | NA | 0 |
| Away win | 0.60 | 71.79% | 39 |
| Away win | 0.65 | 76.92% | 26 |
| Away win | 0.70 | 70.59% | 17 |
| Away win | 0.75 | 71.43% | 7 |
| Away win | 0.80 | 50.00% | 2 |
| Away win | 0.85 | 0.00% | 1 |
| Away win | 0.90 | 0.00% | 1 |
| Over 0.5 | 0.60 | 94.29% | 666 |
| Over 0.5 | 0.65 | 94.29% | 666 |
| Over 0.5 | 0.70 | 94.29% | 666 |
| Over 0.5 | 0.75 | 94.29% | 665 |
| Over 0.5 | 0.80 | 94.29% | 665 |
| Over 0.5 | 0.85 | 94.28% | 664 |
| Over 0.5 | 0.90 | 94.25% | 661 |
| Over 1.5 | 0.60 | 82.11% | 665 |
| Over 1.5 | 0.65 | 82.23% | 664 |
| Over 1.5 | 0.70 | 82.18% | 662 |
| Over 1.5 | 0.75 | 82.14% | 655 |
| Over 1.5 | 0.80 | 82.72% | 573 |
| Over 1.5 | 0.85 | 86.29% | 248 |
| Over 1.5 | 0.90 | 85.71% | 21 |
| Over 2.5 | 0.60 | 69.48% | 367 |
| Over 2.5 | 0.65 | 68.29% | 164 |
| Over 2.5 | 0.70 | 78.85% | 52 |
| Over 2.5 | 0.75 | 77.27% | 22 |
| Over 2.5 | 0.80 | 66.67% | 6 |
| Over 2.5 | 0.85 | 50.00% | 2 |
| Over 2.5 | 0.90 | 50.00% | 2 |
| BTTS yes | 0.60 | 62.26% | 371 |
| BTTS yes | 0.65 | 65.71% | 175 |
| BTTS yes | 0.70 | 60.00% | 35 |
| BTTS yes | 0.75 | 33.33% | 3 |
| BTTS yes | 0.80 | 50.00% | 2 |
| BTTS yes | 0.85 | NA | 0 |
| BTTS yes | 0.90 | NA | 0 |
| Home first scorer | 0.60 | 66.29% | 175 |
| Home first scorer | 0.65 | 65.52% | 116 |
| Home first scorer | 0.70 | 74.14% | 58 |
| Home first scorer | 0.75 | 78.79% | 33 |
| Home first scorer | 0.80 | 80.00% | 15 |
| Home first scorer | 0.85 | 66.67% | 6 |
| Home first scorer | 0.90 | 0.00% | 1 |
| Home 1Up | 0.60 | 71.73% | 336 |
| Home 1Up | 0.65 | 76.10% | 251 |
| Home 1Up | 0.70 | 77.40% | 177 |
| Home 1Up | 0.75 | 79.51% | 122 |
| Home 1Up | 0.80 | 87.88% | 66 |
| Home 1Up | 0.85 | 86.49% | 37 |
| Home 1Up | 0.90 | 89.47% | 19 |
| Away 1Up | 0.60 | 67.84% | 199 |
| Away 1Up | 0.65 | 72.44% | 127 |
| Away 1Up | 0.70 | 72.50% | 80 |
| Away 1Up | 0.75 | 78.26% | 46 |
| Away 1Up | 0.80 | 80.00% | 30 |
| Away 1Up | 0.85 | 82.35% | 17 |
| Away 1Up | 0.90 | 83.33% | 6 |

## Simulation checks

Timing markets are P(event) = sum over final scores of P_DC(score) x P_sim(event | score), so final-score markets come from the DC matrix exactly. The raw (unweighted) simulation is shown below as a diagnostic of how well the minute-level process reproduces DC on its own.

| Raw simulation check | Mean absolute difference |
|---|---:|
| Home win versus DC matrix | 0.0074 |
| Draw versus DC matrix | 0.0149 |
| Over 2.5 versus DC matrix | 0.0021 |
| Mean goals versus DC lambda (relative) | 0.0007 |

| Outcome | Simulated rate | Actual rate |
|---|---:|---:|
| Home first scorer | 50.67% | 49.40% |
| Away first scorer | 43.48% | 40.84% |
| No goal | 5.85% | 9.76% |
| Home 1Up | 59.57% | 57.96% |
| Away 1Up | 51.23% | 49.70% |

## Final fold time profile

| Bucket | Goal share |
|---|---:|
| 1 to 15 | 0.136 |
| 16 to 30 | 0.146 |
| 31 to 45 plus | 0.155 |
| 46 to 60 | 0.184 |
| 61 to 75 | 0.163 |
| 76 to 90 plus | 0.215 |

## Final fold state multipliers

| State | Multiplier |
|---|---:|
| level | 0.946 |
| leading_1 | 0.990 |
| leading_2plus | 1.017 |
| trailing_1 | 1.040 |
| trailing_2plus | 0.978 |

## Calibrated value test

| Bet | Bets | Hit rate | ROI | Positive closing line value | Sample |
|---|---:|---:|---:|---:|---|
| 1X2 home | 83 | 18.07% | -37.34% | 49.40% | insufficient sample |
| 1X2 draw | 231 | 20.35% | 5.36% | 54.11% | adequate sample |
| 1X2 away | 225 | 22.67% | -26.17% | 42.22% | adequate sample |
| Goals over 2.5 | 84 | 45.24% | -17.32% | 45.24% | insufficient sample |
| Goals under 2.5 | 117 | 29.06% | -20.40% | 46.15% | insufficient sample |
