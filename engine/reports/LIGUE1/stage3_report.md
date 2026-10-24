# Stage 3 report

Test seasons: 2024/25, 2025/26, 2026/27 (675 matches).

## Calibration metrics

| Market | Method | Log loss | Brier score |
|---|---|---:|---:|
| home | raw | 0.6356 | 0.2224 |
| home | Platt | 0.6364 | 0.2226 |
| home | isotonic | 0.7064 | 0.2224 |
| draw | raw | 0.5312 | 0.1739 |
| draw | Platt | 0.5319 | 0.1741 |
| draw | isotonic | 0.5727 | 0.1757 |
| away | raw | 0.5649 | 0.1915 |
| away | Platt | 0.5643 | 0.1912 |
| away | isotonic | 0.6383 | 0.1927 |
| over05 | raw | 0.2340 | 0.0587 |
| over05 | Platt | 0.2331 | 0.0584 |
| over05 | isotonic | 0.2689 | 0.0586 |
| over15 | raw | 0.5338 | 0.1745 |
| over15 | Platt | 0.5320 | 0.1738 |
| over15 | isotonic | 0.5716 | 0.1746 |
| over25 | raw | 0.6854 | 0.2455 |
| over25 | Platt | 0.6824 | 0.2446 |
| over25 | isotonic | 0.6814 | 0.2444 |
| over35 | raw | 0.6429 | 0.2250 |
| over35 | Platt | 0.6396 | 0.2238 |
| over35 | isotonic | 0.6827 | 0.2264 |
| btts | raw | 0.6929 | 0.2493 |
| btts | Platt | 0.6889 | 0.2479 |
| btts | isotonic | 0.7325 | 0.2502 |
| home_clean_sheet | raw | 0.5993 | 0.2054 |
| home_clean_sheet | Platt | 0.5974 | 0.2047 |
| home_clean_sheet | isotonic | 0.7465 | 0.2055 |
| away_clean_sheet | raw | 0.4966 | 0.1618 |
| away_clean_sheet | Platt | 0.4967 | 0.1618 |
| away_clean_sheet | isotonic | 0.6056 | 0.1622 |
| home_first | raw | 0.6520 | 0.2300 |
| home_first | Platt | 0.6510 | 0.2295 |
| home_first | isotonic | 0.7652 | 0.2311 |
| away_first | raw | 0.6426 | 0.2255 |
| away_first | Platt | 0.6449 | 0.2265 |
| away_first | isotonic | 0.7579 | 0.2287 |
| no_goal | raw | 0.3892 | 0.1067 |
| no_goal | Platt | 0.3880 | 0.1068 |
| no_goal | isotonic | 0.5025 | 0.1077 |
| home_1up | raw | 0.6365 | 0.2231 |
| home_1up | Platt | 0.6399 | 0.2245 |
| home_1up | isotonic | 0.7553 | 0.2262 |
| away_1up | raw | 0.6587 | 0.2331 |
| away_1up | Platt | 0.6618 | 0.2345 |
| away_1up | isotonic | 0.7762 | 0.2373 |

## Calibration tables

### Home win, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.081 | 0.125 | 8 |
| 0.1 to 0.2 | 0.166 | 0.271 | 48 |
| 0.2 to 0.3 | 0.254 | 0.263 | 118 |
| 0.3 to 0.4 | 0.354 | 0.385 | 135 |
| 0.4 to 0.5 | 0.454 | 0.530 | 117 |
| 0.5 to 0.6 | 0.544 | 0.520 | 123 |
| 0.6 to 0.7 | 0.645 | 0.682 | 85 |
| 0.7 to 0.8 | 0.748 | 0.697 | 33 |
| 0.8 to 0.9 | 0.845 | 1.000 | 7 |
| 0.9 to 1.0 | 0.902 | 1.000 | 1 |

### Home win, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.076 | 0.111 | 9 |
| 0.1 to 0.2 | 0.165 | 0.240 | 50 |
| 0.2 to 0.3 | 0.256 | 0.264 | 110 |
| 0.3 to 0.4 | 0.354 | 0.395 | 124 |
| 0.4 to 0.5 | 0.449 | 0.521 | 119 |
| 0.5 to 0.6 | 0.544 | 0.519 | 135 |
| 0.6 to 0.7 | 0.646 | 0.678 | 90 |
| 0.7 to 0.8 | 0.745 | 0.677 | 31 |
| 0.8 to 0.9 | 0.839 | 1.000 | 7 |
| 0.9 to 1.0 | NA | NA | 0 |

### Over 1.5, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | 0.280 | 1.000 | 1 |
| 0.3 to 0.4 | NA | NA | 0 |
| 0.4 to 0.5 | NA | NA | 0 |
| 0.5 to 0.6 | 0.586 | 0.750 | 4 |
| 0.6 to 0.7 | 0.672 | 0.750 | 76 |
| 0.7 to 0.8 | 0.757 | 0.749 | 350 |
| 0.8 to 0.9 | 0.837 | 0.827 | 231 |
| 0.9 to 1.0 | 0.922 | 0.769 | 13 |

### Over 1.5, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | NA | NA | 0 |
| 0.3 to 0.4 | NA | NA | 0 |
| 0.4 to 0.5 | 0.473 | 1.000 | 1 |
| 0.5 to 0.6 | NA | NA | 0 |
| 0.6 to 0.7 | 0.680 | 0.842 | 19 |
| 0.7 to 0.8 | 0.762 | 0.751 | 397 |
| 0.8 to 0.9 | 0.830 | 0.810 | 253 |
| 0.9 to 1.0 | 0.914 | 0.800 | 5 |

### Over 2.5, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.087 | 1.000 | 1 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | NA | NA | 0 |
| 0.3 to 0.4 | 0.366 | 0.452 | 31 |
| 0.4 to 0.5 | 0.459 | 0.474 | 190 |
| 0.5 to 0.6 | 0.548 | 0.559 | 279 |
| 0.6 to 0.7 | 0.640 | 0.640 | 139 |
| 0.7 to 0.8 | 0.736 | 0.562 | 32 |
| 0.8 to 0.9 | 0.830 | 1.000 | 3 |
| 0.9 to 1.0 | NA | NA | 0 |

### Over 2.5, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | NA | NA | 0 |
| 0.3 to 0.4 | NA | NA | 0 |
| 0.4 to 0.5 | 0.466 | 0.468 | 218 |
| 0.5 to 0.6 | 0.567 | 0.575 | 322 |
| 0.6 to 0.7 | 0.656 | 0.614 | 127 |
| 0.7 to 0.8 | 0.757 | 0.500 | 2 |
| 0.8 to 0.9 | 0.883 | 0.500 | 2 |
| 0.9 to 1.0 | 0.917 | 1.000 | 4 |

### BTTS, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.089 | 1.000 | 1 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | 0.214 | 1.000 | 1 |
| 0.3 to 0.4 | 0.388 | 0.556 | 9 |
| 0.4 to 0.5 | 0.466 | 0.497 | 171 |
| 0.5 to 0.6 | 0.550 | 0.543 | 368 |
| 0.6 to 0.7 | 0.629 | 0.620 | 121 |
| 0.7 to 0.8 | 0.728 | 0.500 | 4 |
| 0.8 to 0.9 | NA | NA | 0 |
| 0.9 to 1.0 | NA | NA | 0 |

### BTTS, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | NA | NA | 0 |
| 0.3 to 0.4 | 0.382 | 1.000 | 1 |
| 0.4 to 0.5 | 0.468 | 1.000 | 1 |
| 0.5 to 0.6 | 0.562 | 0.546 | 667 |
| 0.6 to 0.7 | 0.609 | 0.500 | 6 |
| 0.7 to 0.8 | NA | NA | 0 |
| 0.8 to 0.9 | NA | NA | 0 |
| 0.9 to 1.0 | NA | NA | 0 |

### Home first scorer, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.177 | 1.000 | 2 |
| 0.2 to 0.3 | 0.265 | 0.172 | 29 |
| 0.3 to 0.4 | 0.358 | 0.290 | 124 |
| 0.4 to 0.5 | 0.453 | 0.404 | 171 |
| 0.5 to 0.6 | 0.554 | 0.520 | 179 |
| 0.6 to 0.7 | 0.648 | 0.654 | 130 |
| 0.7 to 0.8 | 0.743 | 0.667 | 36 |
| 0.8 to 0.9 | 0.826 | 1.000 | 4 |
| 0.9 to 1.0 | NA | NA | 0 |

### Home first scorer, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.179 | 0.400 | 5 |
| 0.2 to 0.3 | 0.261 | 0.216 | 37 |
| 0.3 to 0.4 | 0.353 | 0.309 | 149 |
| 0.4 to 0.5 | 0.452 | 0.418 | 153 |
| 0.5 to 0.6 | 0.551 | 0.545 | 167 |
| 0.6 to 0.7 | 0.646 | 0.628 | 121 |
| 0.7 to 0.8 | 0.738 | 0.694 | 36 |
| 0.8 to 0.9 | 0.820 | 0.857 | 7 |
| 0.9 to 1.0 | NA | NA | 0 |

### Home 1Up, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.193 | 1.000 | 1 |
| 0.2 to 0.3 | 0.271 | 0.143 | 14 |
| 0.3 to 0.4 | 0.365 | 0.356 | 59 |
| 0.4 to 0.5 | 0.449 | 0.359 | 131 |
| 0.5 to 0.6 | 0.551 | 0.543 | 151 |
| 0.6 to 0.7 | 0.652 | 0.629 | 159 |
| 0.7 to 0.8 | 0.747 | 0.720 | 118 |
| 0.8 to 0.9 | 0.843 | 0.816 | 38 |
| 0.9 to 1.0 | 0.929 | 1.000 | 4 |

### Home 1Up, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.190 | 1.000 | 2 |
| 0.2 to 0.3 | 0.267 | 0.067 | 15 |
| 0.3 to 0.4 | 0.365 | 0.391 | 64 |
| 0.4 to 0.5 | 0.451 | 0.367 | 120 |
| 0.5 to 0.6 | 0.552 | 0.500 | 140 |
| 0.6 to 0.7 | 0.655 | 0.625 | 144 |
| 0.7 to 0.8 | 0.748 | 0.706 | 126 |
| 0.8 to 0.9 | 0.840 | 0.804 | 56 |
| 0.9 to 1.0 | 0.928 | 0.875 | 8 |

### Away 1Up, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.097 | 1.000 | 1 |
| 0.1 to 0.2 | 0.179 | 0.000 | 8 |
| 0.2 to 0.3 | 0.263 | 0.245 | 49 |
| 0.3 to 0.4 | 0.354 | 0.360 | 136 |
| 0.4 to 0.5 | 0.447 | 0.423 | 168 |
| 0.5 to 0.6 | 0.547 | 0.511 | 139 |
| 0.6 to 0.7 | 0.642 | 0.602 | 118 |
| 0.7 to 0.8 | 0.744 | 0.707 | 41 |
| 0.8 to 0.9 | 0.831 | 0.643 | 14 |
| 0.9 to 1.0 | 0.926 | 1.000 | 1 |

### Away 1Up, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.165 | 0.250 | 4 |
| 0.2 to 0.3 | 0.265 | 0.258 | 31 |
| 0.3 to 0.4 | 0.356 | 0.296 | 108 |
| 0.4 to 0.5 | 0.450 | 0.412 | 182 |
| 0.5 to 0.6 | 0.550 | 0.510 | 157 |
| 0.6 to 0.7 | 0.647 | 0.556 | 126 |
| 0.7 to 0.8 | 0.741 | 0.731 | 52 |
| 0.8 to 0.9 | 0.837 | 0.643 | 14 |
| 0.9 to 1.0 | 0.926 | 1.000 | 1 |

## Confidence buckets

| Market | Threshold | Hit rate | Count |
|---|---:|---:|---:|
| Home win | 0.60 | 69.53% | 128 |
| Home win | 0.65 | 77.50% | 80 |
| Home win | 0.70 | 73.68% | 38 |
| Home win | 0.75 | 81.82% | 22 |
| Home win | 0.80 | 100.00% | 7 |
| Home win | 0.85 | 100.00% | 2 |
| Home win | 0.90 | NA | 0 |
| Away win | 0.60 | 61.11% | 36 |
| Away win | 0.65 | 61.90% | 21 |
| Away win | 0.70 | 70.00% | 10 |
| Away win | 0.75 | 100.00% | 3 |
| Away win | 0.80 | 100.00% | 1 |
| Away win | 0.85 | NA | 0 |
| Away win | 0.90 | NA | 0 |
| Over 0.5 | 0.60 | 93.78% | 675 |
| Over 0.5 | 0.65 | 93.78% | 675 |
| Over 0.5 | 0.70 | 93.78% | 675 |
| Over 0.5 | 0.75 | 93.78% | 675 |
| Over 0.5 | 0.80 | 93.78% | 675 |
| Over 0.5 | 0.85 | 93.77% | 674 |
| Over 0.5 | 0.90 | 93.75% | 672 |
| Over 1.5 | 0.60 | 77.60% | 674 |
| Over 1.5 | 0.65 | 77.60% | 674 |
| Over 1.5 | 0.70 | 77.40% | 655 |
| Over 1.5 | 0.75 | 78.15% | 531 |
| Over 1.5 | 0.80 | 81.01% | 258 |
| Over 1.5 | 0.85 | 81.82% | 55 |
| Over 1.5 | 0.90 | 80.00% | 5 |
| Over 2.5 | 0.60 | 62.22% | 135 |
| Over 2.5 | 0.65 | 58.11% | 74 |
| Over 2.5 | 0.70 | 75.00% | 8 |
| Over 2.5 | 0.75 | 71.43% | 7 |
| Over 2.5 | 0.80 | 83.33% | 6 |
| Over 2.5 | 0.85 | 83.33% | 6 |
| Over 2.5 | 0.90 | 100.00% | 4 |
| BTTS yes | 0.60 | 50.00% | 6 |
| BTTS yes | 0.65 | NA | 0 |
| BTTS yes | 0.70 | NA | 0 |
| BTTS yes | 0.75 | NA | 0 |
| BTTS yes | 0.80 | NA | 0 |
| BTTS yes | 0.85 | NA | 0 |
| BTTS yes | 0.90 | NA | 0 |
| Home first scorer | 0.60 | 65.24% | 164 |
| Home first scorer | 0.65 | 72.00% | 100 |
| Home first scorer | 0.70 | 72.09% | 43 |
| Home first scorer | 0.75 | 84.21% | 19 |
| Home first scorer | 0.80 | 85.71% | 7 |
| Home first scorer | 0.85 | 100.00% | 1 |
| Home first scorer | 0.90 | NA | 0 |
| Home 1Up | 0.60 | 69.16% | 334 |
| Home 1Up | 0.65 | 70.97% | 279 |
| Home 1Up | 0.70 | 74.21% | 190 |
| Home 1Up | 0.75 | 77.78% | 126 |
| Home 1Up | 0.80 | 81.25% | 64 |
| Home 1Up | 0.85 | 86.67% | 30 |
| Home 1Up | 0.90 | 87.50% | 8 |
| Away 1Up | 0.60 | 61.14% | 193 |
| Away 1Up | 0.65 | 64.80% | 125 |
| Away 1Up | 0.70 | 71.64% | 67 |
| Away 1Up | 0.75 | 69.44% | 36 |
| Away 1Up | 0.80 | 66.67% | 15 |
| Away 1Up | 0.85 | 100.00% | 6 |
| Away 1Up | 0.90 | 100.00% | 1 |

## Simulation checks

Timing markets are P(event) = sum over final scores of P_DC(score) x P_sim(event | score), so final-score markets come from the DC matrix exactly. The raw (unweighted) simulation is shown below as a diagnostic of how well the minute-level process reproduces DC on its own.

| Raw simulation check | Mean absolute difference |
|---|---:|
| Home win versus DC matrix | 0.0070 |
| Draw versus DC matrix | 0.0105 |
| Over 2.5 versus DC matrix | 0.0018 |
| Mean goals versus DC lambda (relative) | 0.0009 |

| Outcome | Simulated rate | Actual rate |
|---|---:|---:|
| Home first scorer | 50.87% | 47.11% |
| Away first scorer | 42.69% | 41.19% |
| No goal | 6.44% | 11.70% |
| Home 1Up | 58.56% | 55.26% |
| Away 1Up | 49.28% | 46.52% |

## Final fold time profile

| Bucket | Goal share |
|---|---:|
| 1 to 15 | 0.136 |
| 16 to 30 | 0.148 |
| 31 to 45 plus | 0.151 |
| 46 to 60 | 0.181 |
| 61 to 75 | 0.165 |
| 76 to 90 plus | 0.219 |

## Final fold state multipliers

| State | Multiplier |
|---|---:|
| level | 0.962 |
| leading_1 | 0.978 |
| leading_2plus | 0.991 |
| trailing_1 | 1.023 |
| trailing_2plus | 1.076 |

## Calibrated value test

| Bet | Bets | Hit rate | ROI | Positive closing line value | Sample |
|---|---:|---:|---:|---:|---|
| 1X2 home | 188 | 32.98% | -3.62% | 40.96% | insufficient sample |
| 1X2 draw | 111 | 11.71% | -37.86% | 57.66% | insufficient sample |
| 1X2 away | 246 | 21.54% | -10.71% | 48.78% | adequate sample |
| Goals over 2.5 | 122 | 45.90% | -14.49% | 39.34% | insufficient sample |
| Goals under 2.5 | 107 | 31.78% | -23.10% | 42.99% | insufficient sample |
