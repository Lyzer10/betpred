# Stage 2 report

Test seasons: 2024/25, 2025/26, 2026/27 (675 matches).
2014/15 is used only as model history and is excluded from evaluation.

## Chosen validation settings

| Variant | Xi | Blend weight | Validation 1X2 log loss |
|---|---:|---:|---:|
| goals | 0.0019 | NA | 1.0174 |
| xg | 0.0030 | NA | 1.0121 |
| blend | 0.0030 | 0.5 | 1.0095 |

## 1X2

| Method | Accuracy | Log loss | Brier score |
|---|---:|---:|---:|
| Bookmaker opening | 54.22% | 0.9673 | 0.5745 |
| Bookmaker closing | 54.37% | 0.9671 | 0.5743 |
| Elo | 53.63% | 0.9984 | 0.5945 |
| DC goals | 54.07% | 0.9923 | 0.5908 |
| DC xG | 53.19% | 0.9874 | 0.5877 |
| DC best blend | 53.33% | 0.9877 | 0.5878 |

## Goal markets

| Method | Market | Log loss | Brier score |
|---|---|---:|---:|
| DC goals | over 0.5 | 0.2378 | 0.0599 |
| DC goals | over 1.5 | 0.5460 | 0.1776 |
| DC goals | over 2.5 | 0.6985 | 0.2480 |
| DC goals | over 3.5 | 0.6475 | 0.2269 |
| DC goals | BTTS | 0.7028 | 0.2513 |
| DC xg | over 0.5 | 0.2324 | 0.0584 |
| DC xg | over 1.5 | 0.5292 | 0.1727 |
| DC xg | over 2.5 | 0.6828 | 0.2446 |
| DC xg | over 3.5 | 0.6424 | 0.2246 |
| DC xg | BTTS | 0.6906 | 0.2486 |
| DC blend | over 0.5 | 0.2340 | 0.0587 |
| DC blend | over 1.5 | 0.5338 | 0.1745 |
| DC blend | over 2.5 | 0.6854 | 0.2455 |
| DC blend | over 3.5 | 0.6429 | 0.2250 |
| DC blend | BTTS | 0.6929 | 0.2493 |
| Bookmaker opening | over 2.5 | 0.6696 | 0.2384 |
| Bookmaker closing | over 2.5 | 0.6644 | 0.2358 |

## Calibration, best variant: blend

### Home win

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

### Away win

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.074 | 0.091 | 33 |
| 0.1 to 0.2 | 0.156 | 0.123 | 122 |
| 0.2 to 0.3 | 0.250 | 0.256 | 180 |
| 0.3 to 0.4 | 0.353 | 0.310 | 126 |
| 0.4 to 0.5 | 0.451 | 0.407 | 113 |
| 0.5 to 0.6 | 0.545 | 0.629 | 62 |
| 0.6 to 0.7 | 0.637 | 0.520 | 25 |
| 0.7 to 0.8 | 0.731 | 0.667 | 12 |
| 0.8 to 0.9 | 0.837 | 1.000 | 2 |
| 0.9 to 1.0 | NA | NA | 0 |

### Over 1.5

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

### Over 2.5

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

### BTTS

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

## Confidence buckets

| Market | Threshold | Hit rate | Count |
|---|---:|---:|---:|
| Home win | 0.70 | 75.61% | 41 |
| Home win | 0.75 | 79.17% | 24 |
| Home win | 0.80 | 100.00% | 8 |
| Home win | 0.85 | 100.00% | 4 |
| Home win | 0.90 | 100.00% | 1 |
| Away win | 0.70 | 71.43% | 14 |
| Away win | 0.75 | 66.67% | 6 |
| Away win | 0.80 | 100.00% | 2 |
| Away win | 0.85 | 100.00% | 1 |
| Away win | 0.90 | NA | 0 |
| Over 0.5 | 0.70 | 93.77% | 674 |
| Over 0.5 | 0.75 | 93.77% | 674 |
| Over 0.5 | 0.80 | 93.77% | 674 |
| Over 0.5 | 0.85 | 93.77% | 674 |
| Over 0.5 | 0.90 | 94.06% | 623 |
| Over 1.5 | 0.70 | 77.95% | 594 |
| Over 1.5 | 0.75 | 78.82% | 458 |
| Over 1.5 | 0.80 | 82.38% | 244 |
| Over 1.5 | 0.85 | 84.71% | 85 |
| Over 1.5 | 0.90 | 76.92% | 13 |
| Over 2.5 | 0.70 | 60.00% | 35 |
| Over 2.5 | 0.75 | 58.33% | 12 |
| Over 2.5 | 0.80 | 100.00% | 3 |
| Over 2.5 | 0.85 | NA | 0 |
| Over 2.5 | 0.90 | NA | 0 |
| BTTS yes | 0.70 | 50.00% | 4 |
| BTTS yes | 0.75 | 100.00% | 1 |
| BTTS yes | 0.80 | NA | 0 |
| BTTS yes | 0.85 | NA | 0 |
| BTTS yes | 0.90 | NA | 0 |
| Home clean sheet | 0.70 | 0.00% | 2 |
| Home clean sheet | 0.75 | 0.00% | 1 |
| Home clean sheet | 0.80 | 0.00% | 1 |
| Home clean sheet | 0.85 | 0.00% | 1 |
| Home clean sheet | 0.90 | NA | 0 |
| Away clean sheet | 0.70 | NA | 0 |
| Away clean sheet | 0.75 | NA | 0 |
| Away clean sheet | 0.80 | NA | 0 |
| Away clean sheet | 0.85 | NA | 0 |
| Away clean sheet | 0.90 | NA | 0 |

## Value test

One unit is staked when model probability multiplied by opening odds exceeds 1.05.

| Bet | Bets | Hit rate | ROI | Positive closing line value |
|---|---:|---:|---:|---:|
| 1X2 home | 167 | 31.74% | -6.43% | 39.52% |
| 1X2 draw | 107 | 11.21% | -50.32% | 58.88% |
| 1X2 away | 248 | 21.37% | -14.82% | 49.19% |
| Goals over25 | 87 | 45.98% | -16.41% | 42.53% |
| Goals under25 | 143 | 38.46% | -13.36% | 45.45% |
