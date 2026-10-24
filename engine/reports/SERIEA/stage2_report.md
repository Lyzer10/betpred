# Stage 2 report

Test seasons: 2024/25, 2025/26, 2026/27 (830 matches).
2014/15 is used only as model history and is excluded from evaluation.

## Chosen validation settings

| Variant | Xi | Blend weight | Validation 1X2 log loss |
|---|---:|---:|---:|
| goals | 0.0050 | NA | 1.0006 |
| xg | 0.0050 | NA | 0.9896 |
| blend | 0.0050 | 0.5 | 0.9868 |

## 1X2

| Method | Accuracy | Log loss | Brier score |
|---|---:|---:|---:|
| Bookmaker opening | 53.98% | 0.9617 | 0.5719 |
| Bookmaker closing | 54.70% | 0.9612 | 0.5721 |
| Elo | 52.05% | 1.0124 | 0.6031 |
| DC goals | 52.77% | 0.9835 | 0.5864 |
| DC xG | 53.37% | 0.9831 | 0.5866 |
| DC best blend | 53.49% | 0.9802 | 0.5847 |

## Goal markets

| Method | Market | Log loss | Brier score |
|---|---|---:|---:|
| DC goals | over 0.5 | 0.2784 | 0.0729 |
| DC goals | over 1.5 | 0.5967 | 0.2022 |
| DC goals | over 2.5 | 0.7177 | 0.2612 |
| DC goals | over 3.5 | 0.5706 | 0.1899 |
| DC goals | BTTS | 0.7059 | 0.2557 |
| DC xg | over 0.5 | 0.2780 | 0.0728 |
| DC xg | over 1.5 | 0.5935 | 0.2011 |
| DC xg | over 2.5 | 0.6963 | 0.2514 |
| DC xg | over 3.5 | 0.5528 | 0.1833 |
| DC xg | BTTS | 0.6987 | 0.2526 |
| DC blend | over 0.5 | 0.2776 | 0.0727 |
| DC blend | over 1.5 | 0.5942 | 0.2011 |
| DC blend | over 2.5 | 0.7002 | 0.2533 |
| DC blend | over 3.5 | 0.5561 | 0.1848 |
| DC blend | BTTS | 0.6992 | 0.2528 |
| Bookmaker opening | over 2.5 | 0.6881 | 0.2474 |
| Bookmaker closing | over 2.5 | 0.6872 | 0.2470 |

## Calibration, best variant: blend

### Home win

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

### Away win

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.080 | 0.073 | 41 |
| 0.1 to 0.2 | 0.151 | 0.147 | 156 |
| 0.2 to 0.3 | 0.250 | 0.209 | 187 |
| 0.3 to 0.4 | 0.345 | 0.301 | 173 |
| 0.4 to 0.5 | 0.449 | 0.530 | 115 |
| 0.5 to 0.6 | 0.549 | 0.646 | 96 |
| 0.6 to 0.7 | 0.639 | 0.608 | 51 |
| 0.7 to 0.8 | 0.742 | 0.727 | 11 |
| 0.8 to 0.9 | NA | NA | 0 |
| 0.9 to 1.0 | NA | NA | 0 |

### Over 1.5

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

### Over 2.5

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

### BTTS

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

## Confidence buckets

| Market | Threshold | Hit rate | Count |
|---|---:|---:|---:|
| Home win | 0.70 | 71.79% | 39 |
| Home win | 0.75 | 78.95% | 19 |
| Home win | 0.80 | 75.00% | 4 |
| Home win | 0.85 | 100.00% | 1 |
| Home win | 0.90 | NA | 0 |
| Away win | 0.70 | 72.73% | 11 |
| Away win | 0.75 | 100.00% | 4 |
| Away win | 0.80 | NA | 0 |
| Away win | 0.85 | NA | 0 |
| Away win | 0.90 | NA | 0 |
| Over 0.5 | 0.70 | 92.17% | 830 |
| Over 0.5 | 0.75 | 92.17% | 830 |
| Over 0.5 | 0.80 | 92.17% | 830 |
| Over 0.5 | 0.85 | 92.36% | 798 |
| Over 0.5 | 0.90 | 93.05% | 518 |
| Over 1.5 | 0.70 | 74.03% | 489 |
| Over 1.5 | 0.75 | 75.38% | 264 |
| Over 1.5 | 0.80 | 72.27% | 119 |
| Over 1.5 | 0.85 | 75.00% | 36 |
| Over 1.5 | 0.90 | 66.67% | 3 |
| Over 2.5 | 0.70 | 50.00% | 10 |
| Over 2.5 | 0.75 | 100.00% | 1 |
| Over 2.5 | 0.80 | NA | 0 |
| Over 2.5 | 0.85 | NA | 0 |
| Over 2.5 | 0.90 | NA | 0 |
| BTTS yes | 0.70 | 100.00% | 1 |
| BTTS yes | 0.75 | NA | 0 |
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
| 1X2 home | 104 | 22.12% | -30.63% | 36.54% |
| 1X2 draw | 209 | 20.57% | -11.98% | 63.16% |
| 1X2 away | 383 | 23.50% | -18.02% | 45.43% |
| Goals over25 | 140 | 44.29% | -12.81% | 46.43% |
| Goals under25 | 215 | 51.16% | -3.39% | 51.63% |
