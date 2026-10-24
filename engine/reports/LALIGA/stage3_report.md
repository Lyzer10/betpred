# Stage 3 report

Test seasons: 2024/25, 2025/26, 2026/27 (849 matches).

## Calibration metrics

| Market | Method | Log loss | Brier score |
|---|---|---:|---:|
| home | raw | 0.6134 | 0.2120 |
| home | Platt | 0.6096 | 0.2105 |
| home | isotonic | 0.6673 | 0.2107 |
| draw | raw | 0.5504 | 0.1837 |
| draw | Platt | 0.5467 | 0.1827 |
| draw | isotonic | 0.5446 | 0.1825 |
| away | raw | 0.5392 | 0.1798 |
| away | Platt | 0.5376 | 0.1792 |
| away | isotonic | 0.5963 | 0.1796 |
| over05 | raw | 0.2055 | 0.0498 |
| over05 | Platt | 0.2043 | 0.0495 |
| over05 | isotonic | 0.2303 | 0.0494 |
| over15 | raw | 0.5421 | 0.1798 |
| over15 | Platt | 0.5459 | 0.1810 |
| over15 | isotonic | 0.5722 | 0.1803 |
| over25 | raw | 0.6731 | 0.2404 |
| over25 | Platt | 0.6731 | 0.2403 |
| over25 | isotonic | 0.7039 | 0.2411 |
| over35 | raw | 0.5523 | 0.1843 |
| over35 | Platt | 0.5534 | 0.1848 |
| over35 | isotonic | 0.6487 | 0.1874 |
| btts | raw | 0.6932 | 0.2496 |
| btts | Platt | 0.6866 | 0.2465 |
| btts | isotonic | 0.6871 | 0.2469 |
| home_clean_sheet | raw | 0.5937 | 0.2035 |
| home_clean_sheet | Platt | 0.5925 | 0.2031 |
| home_clean_sheet | isotonic | 0.7497 | 0.2071 |
| away_clean_sheet | raw | 0.4766 | 0.1521 |
| away_clean_sheet | Platt | 0.4708 | 0.1501 |
| away_clean_sheet | isotonic | 0.5043 | 0.1518 |
| home_first | raw | 0.6563 | 0.2319 |
| home_first | Platt | 0.6566 | 0.2320 |
| home_first | isotonic | 0.7481 | 0.2335 |
| away_first | raw | 0.6349 | 0.2218 |
| away_first | Platt | 0.6354 | 0.2220 |
| away_first | isotonic | 0.8185 | 0.2249 |
| no_goal | raw | 0.3319 | 0.0915 |
| no_goal | Platt | 0.3347 | 0.0917 |
| no_goal | isotonic | 0.3949 | 0.0923 |
| home_1up | raw | 0.6235 | 0.2173 |
| home_1up | Platt | 0.6233 | 0.2173 |
| home_1up | isotonic | 0.6854 | 0.2191 |
| away_1up | raw | 0.6516 | 0.2295 |
| away_1up | Platt | 0.6532 | 0.2300 |
| away_1up | isotonic | 0.8416 | 0.2350 |

## Calibration tables

### Home win, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.079 | 0.000 | 3 |
| 0.1 to 0.2 | 0.169 | 0.250 | 32 |
| 0.2 to 0.3 | 0.250 | 0.205 | 117 |
| 0.3 to 0.4 | 0.352 | 0.329 | 167 |
| 0.4 to 0.5 | 0.444 | 0.456 | 228 |
| 0.5 to 0.6 | 0.547 | 0.510 | 157 |
| 0.6 to 0.7 | 0.649 | 0.829 | 76 |
| 0.7 to 0.8 | 0.736 | 0.875 | 56 |
| 0.8 to 0.9 | 0.821 | 0.846 | 13 |
| 0.9 to 1.0 | NA | NA | 0 |

### Home win, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.072 | 0.143 | 7 |
| 0.1 to 0.2 | 0.169 | 0.222 | 63 |
| 0.2 to 0.3 | 0.252 | 0.245 | 98 |
| 0.3 to 0.4 | 0.356 | 0.311 | 161 |
| 0.4 to 0.5 | 0.442 | 0.466 | 176 |
| 0.5 to 0.6 | 0.546 | 0.483 | 145 |
| 0.6 to 0.7 | 0.643 | 0.622 | 74 |
| 0.7 to 0.8 | 0.755 | 0.843 | 89 |
| 0.8 to 0.9 | 0.848 | 0.917 | 24 |
| 0.9 to 1.0 | 0.956 | 0.833 | 12 |

### Over 1.5, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.121 | 1.000 | 1 |
| 0.2 to 0.3 | NA | NA | 0 |
| 0.3 to 0.4 | NA | NA | 0 |
| 0.4 to 0.5 | 0.491 | 0.333 | 3 |
| 0.5 to 0.6 | 0.578 | 0.558 | 52 |
| 0.6 to 0.7 | 0.660 | 0.705 | 302 |
| 0.7 to 0.8 | 0.748 | 0.764 | 322 |
| 0.8 to 0.9 | 0.835 | 0.885 | 165 |
| 0.9 to 1.0 | 0.914 | 1.000 | 4 |

### Over 1.5, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.177 | 1.000 | 1 |
| 0.2 to 0.3 | NA | NA | 0 |
| 0.3 to 0.4 | NA | NA | 0 |
| 0.4 to 0.5 | NA | NA | 0 |
| 0.5 to 0.6 | 0.571 | 0.143 | 7 |
| 0.6 to 0.7 | 0.664 | 0.685 | 362 |
| 0.7 to 0.8 | 0.744 | 0.797 | 408 |
| 0.8 to 0.9 | 0.829 | 0.915 | 71 |
| 0.9 to 1.0 | NA | NA | 0 |

### Over 2.5, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.023 | 0.000 | 1 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | 0.277 | 0.158 | 19 |
| 0.3 to 0.4 | 0.360 | 0.423 | 196 |
| 0.4 to 0.5 | 0.446 | 0.487 | 302 |
| 0.5 to 0.6 | 0.546 | 0.526 | 213 |
| 0.6 to 0.7 | 0.641 | 0.650 | 100 |
| 0.7 to 0.8 | 0.730 | 0.833 | 18 |
| 0.8 to 0.9 | NA | NA | 0 |
| 0.9 to 1.0 | NA | NA | 0 |

### Over 2.5, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.033 | 0.000 | 1 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | 0.277 | 0.000 | 11 |
| 0.3 to 0.4 | 0.362 | 0.416 | 178 |
| 0.4 to 0.5 | 0.447 | 0.483 | 321 |
| 0.5 to 0.6 | 0.546 | 0.540 | 224 |
| 0.6 to 0.7 | 0.639 | 0.636 | 99 |
| 0.7 to 0.8 | 0.731 | 0.800 | 15 |
| 0.8 to 0.9 | NA | NA | 0 |
| 0.9 to 1.0 | NA | NA | 0 |

### BTTS, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.064 | 1.000 | 1 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | 0.264 | 0.167 | 6 |
| 0.3 to 0.4 | 0.377 | 0.452 | 84 |
| 0.4 to 0.5 | 0.454 | 0.560 | 416 |
| 0.5 to 0.6 | 0.542 | 0.578 | 277 |
| 0.6 to 0.7 | 0.631 | 0.635 | 63 |
| 0.7 to 0.8 | 0.703 | 0.500 | 2 |
| 0.8 to 0.9 | NA | NA | 0 |
| 0.9 to 1.0 | NA | NA | 0 |

### BTTS, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.122 | 1.000 | 1 |
| 0.2 to 0.3 | NA | NA | 0 |
| 0.3 to 0.4 | 0.367 | 0.353 | 17 |
| 0.4 to 0.5 | 0.464 | 0.510 | 388 |
| 0.5 to 0.6 | 0.542 | 0.601 | 386 |
| 0.6 to 0.7 | 0.628 | 0.649 | 57 |
| 0.7 to 0.8 | NA | NA | 0 |
| 0.8 to 0.9 | NA | NA | 0 |
| 0.9 to 1.0 | NA | NA | 0 |

### Home first scorer, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.177 | 0.500 | 2 |
| 0.2 to 0.3 | 0.258 | 0.353 | 17 |
| 0.3 to 0.4 | 0.355 | 0.333 | 132 |
| 0.4 to 0.5 | 0.459 | 0.442 | 233 |
| 0.5 to 0.6 | 0.547 | 0.550 | 249 |
| 0.6 to 0.7 | 0.643 | 0.706 | 143 |
| 0.7 to 0.8 | 0.737 | 0.746 | 67 |
| 0.8 to 0.9 | 0.811 | 0.667 | 6 |
| 0.9 to 1.0 | NA | NA | 0 |

### Home first scorer, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.174 | 0.500 | 4 |
| 0.2 to 0.3 | 0.268 | 0.393 | 28 |
| 0.3 to 0.4 | 0.352 | 0.315 | 124 |
| 0.4 to 0.5 | 0.457 | 0.453 | 212 |
| 0.5 to 0.6 | 0.546 | 0.544 | 241 |
| 0.6 to 0.7 | 0.641 | 0.660 | 144 |
| 0.7 to 0.8 | 0.740 | 0.771 | 83 |
| 0.8 to 0.9 | 0.821 | 0.615 | 13 |
| 0.9 to 1.0 | NA | NA | 0 |

### Home 1Up, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.180 | 1.000 | 1 |
| 0.2 to 0.3 | 0.260 | 0.200 | 10 |
| 0.3 to 0.4 | 0.368 | 0.373 | 67 |
| 0.4 to 0.5 | 0.453 | 0.404 | 136 |
| 0.5 to 0.6 | 0.552 | 0.587 | 252 |
| 0.6 to 0.7 | 0.647 | 0.621 | 203 |
| 0.7 to 0.8 | 0.744 | 0.833 | 108 |
| 0.8 to 0.9 | 0.838 | 0.845 | 71 |
| 0.9 to 1.0 | 0.913 | 1.000 | 1 |

### Home 1Up, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.169 | 0.500 | 4 |
| 0.2 to 0.3 | 0.253 | 0.250 | 12 |
| 0.3 to 0.4 | 0.357 | 0.375 | 80 |
| 0.4 to 0.5 | 0.451 | 0.407 | 118 |
| 0.5 to 0.6 | 0.554 | 0.562 | 217 |
| 0.6 to 0.7 | 0.652 | 0.642 | 190 |
| 0.7 to 0.8 | 0.743 | 0.712 | 118 |
| 0.8 to 0.9 | 0.844 | 0.890 | 91 |
| 0.9 to 1.0 | 0.917 | 0.842 | 19 |

### Away 1Up, raw

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.176 | 0.583 | 12 |
| 0.2 to 0.3 | 0.262 | 0.220 | 100 |
| 0.3 to 0.4 | 0.357 | 0.325 | 191 |
| 0.4 to 0.5 | 0.446 | 0.439 | 253 |
| 0.5 to 0.6 | 0.543 | 0.530 | 164 |
| 0.6 to 0.7 | 0.647 | 0.719 | 89 |
| 0.7 to 0.8 | 0.730 | 0.647 | 34 |
| 0.8 to 0.9 | 0.825 | 0.667 | 6 |
| 0.9 to 1.0 | NA | NA | 0 |

### Away 1Up, calibrated

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.167 | 0.368 | 19 |
| 0.2 to 0.3 | 0.258 | 0.246 | 114 |
| 0.3 to 0.4 | 0.358 | 0.331 | 169 |
| 0.4 to 0.5 | 0.448 | 0.436 | 234 |
| 0.5 to 0.6 | 0.547 | 0.519 | 160 |
| 0.6 to 0.7 | 0.648 | 0.663 | 89 |
| 0.7 to 0.8 | 0.739 | 0.685 | 54 |
| 0.8 to 0.9 | 0.836 | 0.667 | 9 |
| 0.9 to 1.0 | 0.902 | 1.000 | 1 |

## Confidence buckets

| Market | Threshold | Hit rate | Count |
|---|---:|---:|---:|
| Home win | 0.60 | 76.88% | 199 |
| Home win | 0.65 | 82.91% | 158 |
| Home win | 0.70 | 85.60% | 125 |
| Home win | 0.75 | 86.05% | 86 |
| Home win | 0.80 | 88.89% | 36 |
| Home win | 0.85 | 88.00% | 25 |
| Home win | 0.90 | 83.33% | 12 |
| Away win | 0.60 | 61.90% | 42 |
| Away win | 0.65 | 77.27% | 22 |
| Away win | 0.70 | 92.86% | 14 |
| Away win | 0.75 | 100.00% | 6 |
| Away win | 0.80 | 100.00% | 4 |
| Away win | 0.85 | 100.00% | 1 |
| Away win | 0.90 | NA | 0 |
| Over 0.5 | 0.60 | 94.81% | 848 |
| Over 0.5 | 0.65 | 94.81% | 848 |
| Over 0.5 | 0.70 | 94.81% | 848 |
| Over 0.5 | 0.75 | 94.81% | 848 |
| Over 0.5 | 0.80 | 94.81% | 848 |
| Over 0.5 | 0.85 | 94.79% | 845 |
| Over 0.5 | 0.90 | 95.80% | 691 |
| Over 1.5 | 0.60 | 75.86% | 841 |
| Over 1.5 | 0.65 | 77.46% | 741 |
| Over 1.5 | 0.70 | 81.42% | 479 |
| Over 1.5 | 0.75 | 87.29% | 236 |
| Over 1.5 | 0.80 | 91.55% | 71 |
| Over 1.5 | 0.85 | 83.33% | 12 |
| Over 1.5 | 0.90 | NA | 0 |
| Over 2.5 | 0.60 | 65.79% | 114 |
| Over 2.5 | 0.65 | 69.23% | 52 |
| Over 2.5 | 0.70 | 80.00% | 15 |
| Over 2.5 | 0.75 | 75.00% | 4 |
| Over 2.5 | 0.80 | NA | 0 |
| Over 2.5 | 0.85 | NA | 0 |
| Over 2.5 | 0.90 | NA | 0 |
| BTTS yes | 0.60 | 64.91% | 57 |
| BTTS yes | 0.65 | 66.67% | 9 |
| BTTS yes | 0.70 | NA | 0 |
| BTTS yes | 0.75 | NA | 0 |
| BTTS yes | 0.80 | NA | 0 |
| BTTS yes | 0.85 | NA | 0 |
| BTTS yes | 0.90 | NA | 0 |
| Home first scorer | 0.60 | 69.58% | 240 |
| Home first scorer | 0.65 | 76.87% | 147 |
| Home first scorer | 0.70 | 75.00% | 96 |
| Home first scorer | 0.75 | 77.78% | 45 |
| Home first scorer | 0.80 | 61.54% | 13 |
| Home first scorer | 0.85 | NA | 0 |
| Home first scorer | 0.90 | NA | 0 |
| Home 1Up | 0.60 | 72.49% | 418 |
| Home 1Up | 0.65 | 74.62% | 327 |
| Home 1Up | 0.70 | 79.39% | 228 |
| Home 1Up | 0.75 | 84.66% | 163 |
| Home 1Up | 0.80 | 88.18% | 110 |
| Home 1Up | 0.85 | 87.93% | 58 |
| Home 1Up | 0.90 | 84.21% | 19 |
| Away 1Up | 0.60 | 67.32% | 153 |
| Away 1Up | 0.65 | 68.57% | 105 |
| Away 1Up | 0.70 | 68.75% | 64 |
| Away 1Up | 0.75 | 65.38% | 26 |
| Away 1Up | 0.80 | 70.00% | 10 |
| Away 1Up | 0.85 | 50.00% | 2 |
| Away 1Up | 0.90 | 100.00% | 1 |

## Simulation checks

Timing markets are P(event) = sum over final scores of P_DC(score) x P_sim(event | score), so final-score markets come from the DC matrix exactly. The raw (unweighted) simulation is shown below as a diagnostic of how well the minute-level process reproduces DC on its own.

| Raw simulation check | Mean absolute difference |
|---|---:|
| Home win versus DC matrix | 0.0104 |
| Draw versus DC matrix | 0.0227 |
| Over 2.5 versus DC matrix | 0.0019 |
| Mean goals versus DC lambda (relative) | 0.0014 |

| Outcome | Simulated rate | Actual rate |
|---|---:|---:|
| Home first scorer | 51.94% | 52.53% |
| Away first scorer | 39.85% | 37.34% |
| No goal | 8.20% | 10.13% |
| Home 1Up | 58.93% | 59.84% |
| Away 1Up | 45.43% | 44.64% |

## Final fold time profile

| Bucket | Goal share |
|---|---:|
| 1 to 15 | 0.134 |
| 16 to 30 | 0.139 |
| 31 to 45 plus | 0.157 |
| 46 to 60 | 0.177 |
| 61 to 75 | 0.165 |
| 76 to 90 plus | 0.227 |

## Final fold state multipliers

| State | Multiplier |
|---|---:|
| level | 0.968 |
| leading_1 | 0.902 |
| leading_2plus | 0.953 |
| trailing_1 | 1.142 |
| trailing_2plus | 1.172 |

## Calibrated value test

| Bet | Bets | Hit rate | ROI | Positive closing line value | Sample |
|---|---:|---:|---:|---:|---|
| 1X2 home | 295 | 40.68% | -9.33% | 52.20% | adequate sample |
| 1X2 draw | 94 | 24.47% | -8.69% | 62.77% | insufficient sample |
| 1X2 away | 156 | 28.21% | -19.16% | 41.03% | insufficient sample |
| Goals over 2.5 | 151 | 42.38% | -3.19% | 38.41% | insufficient sample |
| Goals under 2.5 | 199 | 37.69% | -12.93% | 46.23% | insufficient sample |
