# Stage 2 report

Test seasons: 2024/25, 2025/26, 2026/27 (830 matches).
2014/15 is used only as model history and is excluded from evaluation.

## Chosen validation settings

| Variant | Xi | Blend weight | Validation 1X2 log loss |
|---|---:|---:|---:|
| goals | 0.0019 | NA | 0.9632 |
| xg | 0.0050 | NA | 0.9573 |
| blend | 0.0050 | 0.3 | 0.9567 |

## 1X2

| Method | Accuracy | Log loss | Brier score |
|---|---:|---:|---:|
| Bookmaker opening | 51.45% | 0.9940 | 0.5950 |
| Bookmaker closing | 51.81% | 0.9914 | 0.5929 |
| Elo | 51.08% | 1.0248 | 0.6125 |
| DC goals | 50.84% | 1.0152 | 0.6035 |
| DC xG | 52.17% | 0.9974 | 0.5967 |
| DC best blend | 51.81% | 0.9970 | 0.5961 |

## Goal markets

| Method | Market | Log loss | Brier score |
|---|---|---:|---:|
| DC goals | over 0.5 | 0.2209 | 0.0548 |
| DC goals | over 1.5 | 0.5083 | 0.1636 |
| DC goals | over 2.5 | 0.6922 | 0.2486 |
| DC goals | over 3.5 | 0.6387 | 0.2213 |
| DC goals | BTTS | 0.6911 | 0.2477 |
| DC xg | over 0.5 | 0.2244 | 0.0551 |
| DC xg | over 1.5 | 0.5068 | 0.1627 |
| DC xg | over 2.5 | 0.6893 | 0.2481 |
| DC xg | over 3.5 | 0.6279 | 0.2182 |
| DC xg | BTTS | 0.6891 | 0.2478 |
| DC blend | over 0.5 | 0.2237 | 0.0550 |
| DC blend | over 1.5 | 0.5069 | 0.1627 |
| DC blend | over 2.5 | 0.6910 | 0.2489 |
| DC blend | over 3.5 | 0.6315 | 0.2196 |
| DC blend | BTTS | 0.6888 | 0.2475 |
| Bookmaker opening | over 2.5 | 0.6817 | 0.2443 |
| Bookmaker closing | over 2.5 | 0.6793 | 0.2431 |

## Calibration, best variant: blend

### Home win

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

### Away win

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.066 | 0.062 | 32 |
| 0.1 to 0.2 | 0.151 | 0.144 | 146 |
| 0.2 to 0.3 | 0.253 | 0.222 | 203 |
| 0.3 to 0.4 | 0.345 | 0.353 | 187 |
| 0.4 to 0.5 | 0.446 | 0.402 | 132 |
| 0.5 to 0.6 | 0.545 | 0.562 | 80 |
| 0.6 to 0.7 | 0.638 | 0.636 | 33 |
| 0.7 to 0.8 | 0.742 | 0.929 | 14 |
| 0.8 to 0.9 | 0.814 | 0.667 | 3 |
| 0.9 to 1.0 | NA | NA | 0 |

### Over 1.5

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

### Over 2.5

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

### BTTS

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

## Confidence buckets

| Market | Threshold | Hit rate | Count |
|---|---:|---:|---:|
| Home win | 0.70 | 79.55% | 44 |
| Home win | 0.75 | 81.48% | 27 |
| Home win | 0.80 | 90.91% | 11 |
| Home win | 0.85 | 100.00% | 7 |
| Home win | 0.90 | 100.00% | 2 |
| Away win | 0.70 | 88.24% | 17 |
| Away win | 0.75 | 88.89% | 9 |
| Away win | 0.80 | 66.67% | 3 |
| Away win | 0.85 | NA | 0 |
| Away win | 0.90 | NA | 0 |
| Over 0.5 | 0.70 | 94.22% | 830 |
| Over 0.5 | 0.75 | 94.22% | 830 |
| Over 0.5 | 0.80 | 94.22% | 830 |
| Over 0.5 | 0.85 | 94.17% | 823 |
| Over 0.5 | 0.90 | 94.25% | 748 |
| Over 1.5 | 0.70 | 80.45% | 757 |
| Over 1.5 | 0.75 | 81.57% | 624 |
| Over 1.5 | 0.80 | 80.26% | 380 |
| Over 1.5 | 0.85 | 86.72% | 128 |
| Over 1.5 | 0.90 | 81.82% | 11 |
| Over 2.5 | 0.70 | 71.79% | 39 |
| Over 2.5 | 0.75 | 66.67% | 9 |
| Over 2.5 | 0.80 | 100.00% | 2 |
| Over 2.5 | 0.85 | NA | 0 |
| Over 2.5 | 0.90 | NA | 0 |
| BTTS yes | 0.70 | 62.50% | 8 |
| BTTS yes | 0.75 | NA | 0 |
| BTTS yes | 0.80 | NA | 0 |
| BTTS yes | 0.85 | NA | 0 |
| BTTS yes | 0.90 | NA | 0 |
| Home clean sheet | 0.70 | 0.00% | 1 |
| Home clean sheet | 0.75 | 0.00% | 1 |
| Home clean sheet | 0.80 | 0.00% | 1 |
| Home clean sheet | 0.85 | 0.00% | 1 |
| Home clean sheet | 0.90 | NA | 0 |
| Away clean sheet | 0.70 | 0.00% | 1 |
| Away clean sheet | 0.75 | NA | 0 |
| Away clean sheet | 0.80 | NA | 0 |
| Away clean sheet | 0.85 | NA | 0 |
| Away clean sheet | 0.90 | NA | 0 |

## Value test

One unit is staked when model probability multiplied by opening odds exceeds 1.05.

| Bet | Bets | Hit rate | ROI | Positive closing line value |
|---|---:|---:|---:|---:|
| 1X2 home | 158 | 31.01% | -8.28% | 44.94% |
| 1X2 draw | 227 | 28.63% | 32.06% | 59.03% |
| 1X2 away | 352 | 30.11% | -0.96% | 46.88% |
| Goals over25 | 88 | 45.45% | -18.44% | 46.59% |
| Goals under25 | 218 | 46.79% | 4.20% | 49.54% |
