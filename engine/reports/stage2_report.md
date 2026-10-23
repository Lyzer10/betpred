# Stage 2 report

Test seasons: 2024/25, 2025/26, 2026/27 (830 matches).
2014/15 is used only as model history and is excluded from evaluation.

## Chosen validation settings

| Variant | Xi | Blend weight | Validation 1X2 log loss |
|---|---:|---:|---:|
| goals | 0.0019 | NA | 0.9630 |
| xg | 0.0050 | NA | 0.9551 |
| blend | 0.0050 | 0.3 | 0.9551 |

## 1X2

| Method | Accuracy | Log loss | Brier score |
|---|---:|---:|---:|
| Bookmaker opening | 51.45% | 0.9940 | 0.5950 |
| Bookmaker closing | 51.81% | 0.9914 | 0.5929 |
| Elo | 51.08% | 1.0248 | 0.6125 |
| DC goals | 50.60% | 1.0150 | 0.6033 |
| DC xG | 51.57% | 0.9990 | 0.5976 |
| DC best blend | 51.57% | 0.9978 | 0.5966 |

## Goal markets

| Method | Market | Log loss | Brier score |
|---|---|---:|---:|
| DC goals | over 0.5 | 0.2209 | 0.0548 |
| DC goals | over 1.5 | 0.5081 | 0.1635 |
| DC goals | over 2.5 | 0.6920 | 0.2485 |
| DC goals | over 3.5 | 0.6386 | 0.2212 |
| DC goals | BTTS | 0.6908 | 0.2476 |
| DC xg | over 0.5 | 0.2243 | 0.0549 |
| DC xg | over 1.5 | 0.5090 | 0.1629 |
| DC xg | over 2.5 | 0.6917 | 0.2490 |
| DC xg | over 3.5 | 0.6351 | 0.2220 |
| DC xg | BTTS | 0.6915 | 0.2487 |
| DC blend | over 0.5 | 0.2232 | 0.0548 |
| DC blend | over 1.5 | 0.5076 | 0.1626 |
| DC blend | over 2.5 | 0.6914 | 0.2488 |
| DC blend | over 3.5 | 0.6350 | 0.2217 |
| DC blend | BTTS | 0.6896 | 0.2478 |
| Bookmaker opening | over 2.5 | 0.6817 | 0.2443 |
| Bookmaker closing | over 2.5 | 0.6793 | 0.2431 |

## Calibration, best variant: xg

### Home win

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.079 | 0.000 | 9 |
| 0.1 to 0.2 | 0.160 | 0.093 | 54 |
| 0.2 to 0.3 | 0.254 | 0.213 | 127 |
| 0.3 to 0.4 | 0.354 | 0.348 | 164 |
| 0.4 to 0.5 | 0.450 | 0.439 | 171 |
| 0.5 to 0.6 | 0.544 | 0.543 | 140 |
| 0.6 to 0.7 | 0.648 | 0.557 | 97 |
| 0.7 to 0.8 | 0.738 | 0.725 | 51 |
| 0.8 to 0.9 | 0.843 | 0.769 | 13 |
| 0.9 to 1.0 | 0.931 | 1.000 | 4 |

### Away win

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.064 | 0.056 | 36 |
| 0.1 to 0.2 | 0.149 | 0.163 | 160 |
| 0.2 to 0.3 | 0.251 | 0.250 | 200 |
| 0.3 to 0.4 | 0.349 | 0.330 | 182 |
| 0.4 to 0.5 | 0.446 | 0.398 | 128 |
| 0.5 to 0.6 | 0.540 | 0.539 | 76 |
| 0.6 to 0.7 | 0.638 | 0.750 | 32 |
| 0.7 to 0.8 | 0.742 | 0.857 | 14 |
| 0.8 to 0.9 | 0.812 | 1.000 | 2 |
| 0.9 to 1.0 | NA | NA | 0 |

### Over 1.5

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | NA | NA | 0 |
| 0.3 to 0.4 | 0.344 | 1.000 | 1 |
| 0.4 to 0.5 | NA | NA | 0 |
| 0.5 to 0.6 | 0.575 | 0.667 | 3 |
| 0.6 to 0.7 | 0.671 | 0.778 | 27 |
| 0.7 to 0.8 | 0.765 | 0.765 | 234 |
| 0.8 to 0.9 | 0.846 | 0.808 | 511 |
| 0.9 to 1.0 | 0.917 | 0.852 | 54 |

### Over 2.5

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.122 | 0.000 | 1 |
| 0.2 to 0.3 | 0.289 | 0.500 | 2 |
| 0.3 to 0.4 | 0.366 | 0.364 | 11 |
| 0.4 to 0.5 | 0.461 | 0.495 | 91 |
| 0.5 to 0.6 | 0.556 | 0.560 | 282 |
| 0.6 to 0.7 | 0.647 | 0.558 | 337 |
| 0.7 to 0.8 | 0.737 | 0.606 | 99 |
| 0.8 to 0.9 | 0.847 | 0.857 | 7 |
| 0.9 to 1.0 | NA | NA | 0 |

### BTTS

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.186 | 1.000 | 1 |
| 0.2 to 0.3 | 0.207 | 0.000 | 1 |
| 0.3 to 0.4 | 0.375 | 0.429 | 7 |
| 0.4 to 0.5 | 0.464 | 0.456 | 79 |
| 0.5 to 0.6 | 0.558 | 0.582 | 354 |
| 0.6 to 0.7 | 0.644 | 0.580 | 350 |
| 0.7 to 0.8 | 0.719 | 0.500 | 38 |
| 0.8 to 0.9 | NA | NA | 0 |
| 0.9 to 1.0 | NA | NA | 0 |

## Confidence buckets

| Market | Threshold | Hit rate | Count |
|---|---:|---:|---:|
| Home win | 0.70 | 75.00% | 68 |
| Home win | 0.75 | 78.12% | 32 |
| Home win | 0.80 | 82.35% | 17 |
| Home win | 0.85 | 90.00% | 10 |
| Home win | 0.90 | 100.00% | 4 |
| Away win | 0.70 | 87.50% | 16 |
| Away win | 0.75 | 85.71% | 7 |
| Away win | 0.80 | 100.00% | 2 |
| Away win | 0.85 | NA | 0 |
| Away win | 0.90 | NA | 0 |
| Over 0.5 | 0.70 | 94.21% | 829 |
| Over 0.5 | 0.75 | 94.21% | 829 |
| Over 0.5 | 0.80 | 94.21% | 829 |
| Over 0.5 | 0.85 | 94.20% | 827 |
| Over 0.5 | 0.90 | 94.26% | 802 |
| Over 1.5 | 0.70 | 79.85% | 799 |
| Over 1.5 | 0.75 | 80.95% | 735 |
| Over 1.5 | 0.80 | 81.24% | 565 |
| Over 1.5 | 0.85 | 82.01% | 289 |
| Over 1.5 | 0.90 | 85.19% | 54 |
| Over 2.5 | 0.70 | 62.26% | 106 |
| Over 2.5 | 0.75 | 70.27% | 37 |
| Over 2.5 | 0.80 | 85.71% | 7 |
| Over 2.5 | 0.85 | 100.00% | 4 |
| Over 2.5 | 0.90 | NA | 0 |
| BTTS yes | 0.70 | 50.00% | 38 |
| BTTS yes | 0.75 | 100.00% | 1 |
| BTTS yes | 0.80 | NA | 0 |
| BTTS yes | 0.85 | NA | 0 |
| BTTS yes | 0.90 | NA | 0 |
| Home clean sheet | 0.70 | 0.00% | 1 |
| Home clean sheet | 0.75 | 0.00% | 1 |
| Home clean sheet | 0.80 | 0.00% | 1 |
| Home clean sheet | 0.85 | NA | 0 |
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
| 1X2 home | 262 | 34.73% | -5.00% | 43.89% |
| 1X2 draw | 120 | 25.00% | 21.82% | 62.50% |
| 1X2 away | 312 | 30.77% | 5.00% | 48.40% |
| Goals over25 | 310 | 54.19% | -6.93% | 42.90% |
| Goals under25 | 68 | 48.53% | 9.99% | 50.00% |
