# Stage 2 report

Test seasons: 2024/25, 2025/26, 2026/27 (666 matches).
2014/15 is used only as model history and is excluded from evaluation.

## Chosen validation settings

| Variant | Xi | Blend weight | Validation 1X2 log loss |
|---|---:|---:|---:|
| goals | 0.0010 | NA | 0.9999 |
| xg | 0.0050 | NA | 0.9897 |
| blend | 0.0050 | 0.3 | 0.9884 |

## 1X2

| Method | Accuracy | Log loss | Brier score |
|---|---:|---:|---:|
| Bookmaker opening | 53.60% | 0.9720 | 0.5778 |
| Bookmaker closing | 54.65% | 0.9705 | 0.5770 |
| Elo | 51.65% | 1.0109 | 0.6028 |
| DC goals | 52.25% | 1.0291 | 0.6033 |
| DC xG | 53.75% | 0.9880 | 0.5861 |
| DC best blend | 52.25% | 0.9950 | 0.5902 |

## Goal markets

| Method | Market | Log loss | Brier score |
|---|---|---:|---:|
| DC goals | over 0.5 | 0.2243 | 0.0554 |
| DC goals | over 1.5 | 0.4705 | 0.1478 |
| DC goals | over 2.5 | 0.6625 | 0.2336 |
| DC goals | over 3.5 | 0.6830 | 0.2420 |
| DC goals | BTTS | 0.6842 | 0.2425 |
| DC xg | over 0.5 | 0.2217 | 0.0533 |
| DC xg | over 1.5 | 0.4747 | 0.1465 |
| DC xg | over 2.5 | 0.6599 | 0.2316 |
| DC xg | over 3.5 | 0.6809 | 0.2426 |
| DC xg | BTTS | 0.6764 | 0.2414 |
| DC blend | over 0.5 | 0.2213 | 0.0537 |
| DC blend | over 1.5 | 0.4747 | 0.1473 |
| DC blend | over 2.5 | 0.6582 | 0.2314 |
| DC blend | over 3.5 | 0.6770 | 0.2411 |
| DC blend | BTTS | 0.6739 | 0.2405 |
| Bookmaker opening | over 2.5 | 0.6372 | 0.2232 |
| Bookmaker closing | over 2.5 | 0.6330 | 0.2213 |

## Calibration, best variant: blend

### Home win

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

### Away win

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.063 | 0.073 | 41 |
| 0.1 to 0.2 | 0.158 | 0.162 | 117 |
| 0.2 to 0.3 | 0.249 | 0.242 | 149 |
| 0.3 to 0.4 | 0.348 | 0.375 | 144 |
| 0.4 to 0.5 | 0.446 | 0.462 | 119 |
| 0.5 to 0.6 | 0.547 | 0.500 | 52 |
| 0.6 to 0.7 | 0.659 | 0.667 | 24 |
| 0.7 to 0.8 | 0.763 | 0.692 | 13 |
| 0.8 to 0.9 | 0.828 | 0.833 | 6 |
| 0.9 to 1.0 | 0.979 | 0.000 | 1 |

### Over 1.5

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

### Over 2.5

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

### BTTS

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

## Confidence buckets

| Market | Threshold | Hit rate | Count |
|---|---:|---:|---:|
| Home win | 0.70 | 83.02% | 53 |
| Home win | 0.75 | 83.33% | 30 |
| Home win | 0.80 | 75.00% | 20 |
| Home win | 0.85 | 58.33% | 12 |
| Home win | 0.90 | 33.33% | 6 |
| Away win | 0.70 | 70.00% | 20 |
| Away win | 0.75 | 70.59% | 17 |
| Away win | 0.80 | 71.43% | 7 |
| Away win | 0.85 | 50.00% | 2 |
| Away win | 0.90 | 0.00% | 1 |
| Over 0.5 | 0.70 | 94.29% | 665 |
| Over 0.5 | 0.75 | 94.28% | 664 |
| Over 0.5 | 0.80 | 94.28% | 664 |
| Over 0.5 | 0.85 | 94.24% | 660 |
| Over 0.5 | 0.90 | 94.66% | 618 |
| Over 1.5 | 0.70 | 82.28% | 632 |
| Over 1.5 | 0.75 | 83.42% | 573 |
| Over 1.5 | 0.80 | 84.42% | 462 |
| Over 1.5 | 0.85 | 85.50% | 262 |
| Over 1.5 | 0.90 | 93.10% | 58 |
| Over 2.5 | 0.70 | 74.74% | 95 |
| Over 2.5 | 0.75 | 79.55% | 44 |
| Over 2.5 | 0.80 | 76.19% | 21 |
| Over 2.5 | 0.85 | 66.67% | 6 |
| Over 2.5 | 0.90 | 50.00% | 2 |
| BTTS yes | 0.70 | 65.38% | 26 |
| BTTS yes | 0.75 | 33.33% | 3 |
| BTTS yes | 0.80 | 50.00% | 2 |
| BTTS yes | 0.85 | 100.00% | 1 |
| BTTS yes | 0.90 | NA | 0 |
| Home clean sheet | 0.70 | 100.00% | 2 |
| Home clean sheet | 0.75 | 100.00% | 1 |
| Home clean sheet | 0.80 | 100.00% | 1 |
| Home clean sheet | 0.85 | NA | 0 |
| Home clean sheet | 0.90 | NA | 0 |
| Away clean sheet | 0.70 | 100.00% | 1 |
| Away clean sheet | 0.75 | 100.00% | 1 |
| Away clean sheet | 0.80 | 100.00% | 1 |
| Away clean sheet | 0.85 | NA | 0 |
| Away clean sheet | 0.90 | NA | 0 |

## Value test

One unit is staked when model probability multiplied by opening odds exceeds 1.05.

| Bet | Bets | Hit rate | ROI | Positive closing line value |
|---|---:|---:|---:|---:|
| 1X2 home | 75 | 25.33% | -29.23% | 48.00% |
| 1X2 draw | 141 | 20.57% | 0.79% | 58.87% |
| 1X2 away | 236 | 24.58% | -23.65% | 41.10% |
| Goals over25 | 98 | 57.14% | -6.14% | 39.80% |
| Goals under25 | 130 | 31.54% | -24.29% | 47.69% |
