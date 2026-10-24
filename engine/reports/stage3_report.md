# Stage 3 report

Test seasons: 2024/25, 2025/26, 2026/27 (830 matches).

## Calibration metrics

| Market | Method | Log loss | Brier score |
|---|---|---:|---:|
| home | raw | 0.6117 | 0.2129 |
| home | Platt | 0.6127 | 0.2132 |
| home | isotonic | 0.6145 | 0.2143 |
| draw | raw | 0.5720 | 0.1924 |
| draw | Platt | 0.5718 | 0.1923 |
| draw | isotonic | 0.5732 | 0.1928 |
| away | raw | 0.5639 | 0.1908 |
| away | Platt | 0.5637 | 0.1907 |
| away | isotonic | 0.5673 | 0.1919 |
| over05 | raw | 0.2237 | 0.0550 |
| over05 | Platt | 0.2219 | 0.0546 |
| over05 | isotonic | 0.2218 | 0.0547 |
| over15 | raw | 0.5069 | 0.1627 |
| over15 | Platt | 0.5027 | 0.1611 |
| over15 | isotonic | 0.5636 | 0.1619 |
| over25 | raw | 0.6910 | 0.2489 |
| over25 | Platt | 0.6891 | 0.2479 |
| over25 | isotonic | 0.7253 | 0.2508 |
| over35 | raw | 0.6315 | 0.2196 |
| over35 | Platt | 0.6306 | 0.2195 |
| over35 | isotonic | 0.6656 | 0.2220 |
| btts | raw | 0.6888 | 0.2475 |
| btts | Platt | 0.6855 | 0.2461 |
| btts | isotonic | 0.7201 | 0.2479 |
| home_clean_sheet | raw | 0.5503 | 0.1838 |
| home_clean_sheet | Platt | 0.5497 | 0.1834 |
| home_clean_sheet | isotonic | 0.6135 | 0.1849 |
| away_clean_sheet | raw | 0.5156 | 0.1699 |
| away_clean_sheet | Platt | 0.5183 | 0.1709 |
| away_clean_sheet | isotonic | 0.5194 | 0.1717 |
| home_first | raw | 0.6541 | 0.2303 |
| home_first | Platt | 0.6561 | 0.2313 |
| home_first | isotonic | 0.6602 | 0.2329 |
| away_first | raw | 0.6467 | 0.2267 |
| away_first | Platt | 0.6486 | 0.2277 |
| away_first | isotonic | 0.6494 | 0.2279 |
| no_goal | raw | 0.2230 | 0.0548 |
| no_goal | Platt | 0.2224 | 0.0546 |
| no_goal | isotonic | 0.2781 | 0.0548 |
| home_1up | raw | 0.6081 | 0.2101 |
| home_1up | Platt | 0.6070 | 0.2098 |
| home_1up | isotonic | 0.6168 | 0.2129 |
| away_1up | raw | 0.6460 | 0.2270 |
| away_1up | Platt | 0.6475 | 0.2277 |
| away_1up | isotonic | 0.6551 | 0.2291 |

## Calibration tables

### Home win, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.081 | 0.067 | 15 |
| 0.1 to 0.2 | 0.164 | 0.078 | 64 |
| 0.2 to 0.3 | 0.252 | 0.263 | 133 |
| 0.3 to 0.4 | 0.352 | 0.374 | 174 |
| 0.4 to 0.5 | 0.444 | 0.436 | 179 |
| 0.5 to 0.6 | 0.542 | 0.586 | 128 |
| 0.6 to 0.7 | 0.648 | 0.548 | 93 |
| 0.7 to 0.8 | 0.745 | 0.758 | 33 |
| 0.8 to 0.9 | 0.848 | 0.889 | 9 |
| 0.9 to 1.0 | 0.944 | 1.000 | 2 |

### Home win, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.080 | 0.071 | 14 |
| 0.1 to 0.2 | 0.165 | 0.068 | 59 |
| 0.2 to 0.3 | 0.253 | 0.254 | 122 |
| 0.3 to 0.4 | 0.352 | 0.329 | 161 |
| 0.4 to 0.5 | 0.447 | 0.451 | 182 |
| 0.5 to 0.6 | 0.544 | 0.550 | 140 |
| 0.6 to 0.7 | 0.650 | 0.586 | 99 |
| 0.7 to 0.8 | 0.742 | 0.683 | 41 |
| 0.8 to 0.9 | 0.842 | 0.900 | 10 |
| 0.9 to 1.0 | 0.937 | 1.000 | 2 |

### Over 1.5, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | NA | NA | 0 |
| 0.3 to 0.4 | NA | NA | 0 |
| 0.4 to 0.5 | 0.489 | 1.000 | 1 |
| 0.5 to 0.6 | 0.568 | 0.875 | 8 |
| 0.6 to 0.7 | 0.667 | 0.703 | 64 |
| 0.7 to 0.8 | 0.761 | 0.806 | 377 |
| 0.8 to 0.9 | 0.839 | 0.802 | 369 |
| 0.9 to 1.0 | 0.919 | 0.818 | 11 |

### Over 1.5, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | NA | NA | 0 |
| 0.3 to 0.4 | NA | NA | 0 |
| 0.4 to 0.5 | NA | NA | 0 |
| 0.5 to 0.6 | NA | NA | 0 |
| 0.6 to 0.7 | 0.688 | 0.857 | 7 |
| 0.7 to 0.8 | 0.775 | 0.788 | 340 |
| 0.8 to 0.9 | 0.827 | 0.802 | 481 |
| 0.9 to 1.0 | 0.906 | 1.000 | 2 |

### Over 2.5, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | 0.273 | 0.167 | 6 |
| 0.3 to 0.4 | 0.367 | 0.500 | 38 |
| 0.4 to 0.5 | 0.457 | 0.538 | 171 |
| 0.5 to 0.6 | 0.550 | 0.551 | 361 |
| 0.6 to 0.7 | 0.641 | 0.572 | 215 |
| 0.7 to 0.8 | 0.728 | 0.703 | 37 |
| 0.8 to 0.9 | 0.820 | 1.000 | 2 |
| 0.9 to 1.0 | NA | NA | 0 |

### Over 2.5, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | 0.293 | 0.000 | 1 |
| 0.3 to 0.4 | 0.369 | 0.462 | 13 |
| 0.4 to 0.5 | 0.466 | 0.512 | 123 |
| 0.5 to 0.6 | 0.555 | 0.559 | 390 |
| 0.6 to 0.7 | 0.642 | 0.564 | 257 |
| 0.7 to 0.8 | 0.728 | 0.636 | 44 |
| 0.8 to 0.9 | 0.817 | 1.000 | 2 |
| 0.9 to 1.0 | NA | NA | 0 |

### BTTS, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.136 | 1.000 | 1 |
| 0.2 to 0.3 | 0.206 | 0.000 | 1 |
| 0.3 to 0.4 | 0.375 | 0.429 | 21 |
| 0.4 to 0.5 | 0.465 | 0.500 | 152 |
| 0.5 to 0.6 | 0.552 | 0.590 | 422 |
| 0.6 to 0.7 | 0.632 | 0.569 | 225 |
| 0.7 to 0.8 | 0.716 | 0.625 | 8 |
| 0.8 to 0.9 | NA | NA | 0 |
| 0.9 to 1.0 | NA | NA | 0 |

### BTTS, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | 0.223 | 1.000 | 1 |
| 0.3 to 0.4 | 0.341 | 0.000 | 1 |
| 0.4 to 0.5 | 0.474 | 0.468 | 62 |
| 0.5 to 0.6 | 0.557 | 0.570 | 574 |
| 0.6 to 0.7 | 0.626 | 0.578 | 192 |
| 0.7 to 0.8 | NA | NA | 0 |
| 0.8 to 0.9 | NA | NA | 0 |
| 0.9 to 1.0 | NA | NA | 0 |

### Home first scorer, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.185 | 0.167 | 6 |
| 0.2 to 0.3 | 0.263 | 0.294 | 34 |
| 0.3 to 0.4 | 0.355 | 0.260 | 131 |
| 0.4 to 0.5 | 0.454 | 0.478 | 232 |
| 0.5 to 0.6 | 0.547 | 0.576 | 236 |
| 0.6 to 0.7 | 0.647 | 0.697 | 142 |
| 0.7 to 0.8 | 0.731 | 0.700 | 40 |
| 0.8 to 0.9 | 0.819 | 0.625 | 8 |
| 0.9 to 1.0 | 0.945 | 0.000 | 1 |

### Home first scorer, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.199 | 1.000 | 1 |
| 0.2 to 0.3 | 0.261 | 0.158 | 19 |
| 0.3 to 0.4 | 0.359 | 0.259 | 108 |
| 0.4 to 0.5 | 0.456 | 0.429 | 231 |
| 0.5 to 0.6 | 0.548 | 0.571 | 268 |
| 0.6 to 0.7 | 0.646 | 0.697 | 155 |
| 0.7 to 0.8 | 0.731 | 0.707 | 41 |
| 0.8 to 0.9 | 0.814 | 0.500 | 6 |
| 0.9 to 1.0 | 0.936 | 0.000 | 1 |

### Home 1Up, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.181 | 0.500 | 2 |
| 0.2 to 0.3 | 0.259 | 0.235 | 17 |
| 0.3 to 0.4 | 0.362 | 0.303 | 76 |
| 0.4 to 0.5 | 0.455 | 0.449 | 127 |
| 0.5 to 0.6 | 0.551 | 0.564 | 211 |
| 0.6 to 0.7 | 0.649 | 0.697 | 211 |
| 0.7 to 0.8 | 0.750 | 0.832 | 131 |
| 0.8 to 0.9 | 0.836 | 0.812 | 48 |
| 0.9 to 1.0 | 0.930 | 1.000 | 7 |

### Home 1Up, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.180 | 1.000 | 1 |
| 0.2 to 0.3 | 0.253 | 0.100 | 10 |
| 0.3 to 0.4 | 0.354 | 0.333 | 42 |
| 0.4 to 0.5 | 0.451 | 0.369 | 111 |
| 0.5 to 0.6 | 0.555 | 0.543 | 184 |
| 0.6 to 0.7 | 0.649 | 0.610 | 210 |
| 0.7 to 0.8 | 0.743 | 0.790 | 167 |
| 0.8 to 0.9 | 0.835 | 0.839 | 93 |
| 0.9 to 1.0 | 0.930 | 0.917 | 12 |

### Away 1Up, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.040 | 1.000 | 1 |
| 0.1 to 0.2 | 0.175 | 0.250 | 8 |
| 0.2 to 0.3 | 0.264 | 0.174 | 46 |
| 0.3 to 0.4 | 0.351 | 0.410 | 134 |
| 0.4 to 0.5 | 0.451 | 0.397 | 209 |
| 0.5 to 0.6 | 0.547 | 0.548 | 199 |
| 0.6 to 0.7 | 0.648 | 0.624 | 157 |
| 0.7 to 0.8 | 0.741 | 0.870 | 54 |
| 0.8 to 0.9 | 0.838 | 0.864 | 22 |
| 0.9 to 1.0 | NA | NA | 0 |

### Away 1Up, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.053 | 1.000 | 1 |
| 0.1 to 0.2 | 0.189 | 0.333 | 3 |
| 0.2 to 0.3 | 0.264 | 0.147 | 34 |
| 0.3 to 0.4 | 0.358 | 0.386 | 127 |
| 0.4 to 0.5 | 0.454 | 0.410 | 210 |
| 0.5 to 0.6 | 0.547 | 0.529 | 221 |
| 0.6 to 0.7 | 0.646 | 0.622 | 164 |
| 0.7 to 0.8 | 0.739 | 0.885 | 52 |
| 0.8 to 0.9 | 0.829 | 0.833 | 18 |
| 0.9 to 1.0 | NA | NA | 0 |

## Confidence buckets

| Market | Threshold | Hit rate | Count |
|---|---:|---:|---:|
| Home win | 0.60 | 63.82% | 152 |
| Home win | 0.65 | 71.00% | 100 |
| Home win | 0.70 | 73.58% | 53 |
| Home win | 0.75 | 80.65% | 31 |
| Home win | 0.80 | 91.67% | 12 |
| Home win | 0.85 | 100.00% | 7 |
| Home win | 0.90 | 100.00% | 2 |
| Away win | 0.60 | 77.27% | 44 |
| Away win | 0.65 | 84.62% | 26 |
| Away win | 0.70 | 86.67% | 15 |
| Away win | 0.75 | 85.71% | 7 |
| Away win | 0.80 | 100.00% | 2 |
| Away win | 0.85 | NA | 0 |
| Away win | 0.90 | NA | 0 |
| Over 0.5 | 0.60 | 94.22% | 830 |
| Over 0.5 | 0.65 | 94.22% | 830 |
| Over 0.5 | 0.70 | 94.22% | 830 |
| Over 0.5 | 0.75 | 94.22% | 830 |
| Over 0.5 | 0.80 | 94.22% | 830 |
| Over 0.5 | 0.85 | 94.22% | 830 |
| Over 0.5 | 0.90 | 94.21% | 829 |
| Over 1.5 | 0.60 | 79.76% | 830 |
| Over 1.5 | 0.65 | 79.76% | 830 |
| Over 1.5 | 0.70 | 79.71% | 823 |
| Over 1.5 | 0.75 | 79.92% | 777 |
| Over 1.5 | 0.80 | 80.33% | 483 |
| Over 1.5 | 0.85 | 81.43% | 70 |
| Over 1.5 | 0.90 | 100.00% | 2 |
| Over 2.5 | 0.60 | 57.76% | 303 |
| Over 2.5 | 0.65 | 61.70% | 141 |
| Over 2.5 | 0.70 | 65.22% | 46 |
| Over 2.5 | 0.75 | 77.78% | 9 |
| Over 2.5 | 0.80 | 100.00% | 2 |
| Over 2.5 | 0.85 | NA | 0 |
| Over 2.5 | 0.90 | NA | 0 |
| BTTS yes | 0.60 | 57.81% | 192 |
| BTTS yes | 0.65 | 55.17% | 29 |
| BTTS yes | 0.70 | NA | 0 |
| BTTS yes | 0.75 | NA | 0 |
| BTTS yes | 0.80 | NA | 0 |
| BTTS yes | 0.85 | NA | 0 |
| BTTS yes | 0.90 | NA | 0 |
| Home first scorer | 0.60 | 68.97% | 203 |
| Home first scorer | 0.65 | 65.83% | 120 |
| Home first scorer | 0.70 | 66.67% | 48 |
| Home first scorer | 0.75 | 68.75% | 16 |
| Home first scorer | 0.80 | 42.86% | 7 |
| Home first scorer | 0.85 | 0.00% | 1 |
| Home first scorer | 0.90 | 0.00% | 1 |
| Home 1Up | 0.60 | 72.41% | 482 |
| Home 1Up | 0.65 | 75.27% | 376 |
| Home 1Up | 0.70 | 81.25% | 272 |
| Home 1Up | 0.75 | 83.24% | 173 |
| Home 1Up | 0.80 | 84.76% | 105 |
| Home 1Up | 0.85 | 91.18% | 34 |
| Home 1Up | 0.90 | 91.67% | 12 |
| Away 1Up | 0.60 | 69.66% | 234 |
| Away 1Up | 0.65 | 76.03% | 146 |
| Away 1Up | 0.70 | 87.14% | 70 |
| Away 1Up | 0.75 | 90.91% | 33 |
| Away 1Up | 0.80 | 83.33% | 18 |
| Away 1Up | 0.85 | 75.00% | 4 |
| Away 1Up | 0.90 | NA | 0 |

## Simulation checks

Terminal consistency probabilities use a halfway anchor to the DC matrix so its low score correction remains authoritative. Unanchored simulation values remain in the prediction file.

| Check | Mean absolute difference |
|---|---:|
| Home win versus DC matrix | 0.0037 |
| Draw versus DC matrix | 0.0062 |
| Over 2.5 versus DC matrix | 0.0022 |

| Outcome | Simulated rate | Actual rate |
|---|---:|---:|
| Home first scorer | 50.53% | 51.08% |
| Away first scorer | 43.79% | 43.13% |
| No goal | 5.67% | 5.78% |
| Home 1Up | 58.80% | 60.96% |
| Away 1Up | 51.08% | 50.84% |

## Final fold time profile

| Bucket | Goal share |
|---|---:|
| 1 to 15 | 0.134 |
| 16 to 30 | 0.145 |
| 31 to 45 plus | 0.154 |
| 46 to 60 | 0.184 |
| 61 to 75 | 0.166 |
| 76 to 90 plus | 0.216 |

## Final fold state multipliers

| State | Multiplier |
|---|---:|
| level | 1.028 |
| leading_1 | 0.935 |
| leading_2plus | 0.992 |
| trailing_1 | 1.086 |
| trailing_2plus | 0.950 |

## Calibrated value test

| Bet | Bets | Hit rate | ROI | Positive closing line value | Sample |
|---|---:|---:|---:|---:|---|
| 1X2 home | 209 | 33.97% | -4.38% | 44.50% | adequate sample |
| 1X2 draw | 255 | 26.67% | 23.64% | 58.82% | adequate sample |
| 1X2 away | 248 | 33.06% | 11.74% | 48.79% | adequate sample |
| Goals over 2.5 | 160 | 51.88% | -5.52% | 45.62% | insufficient sample |
| Goals under 2.5 | 101 | 40.59% | -4.13% | 54.46% | insufficient sample |
