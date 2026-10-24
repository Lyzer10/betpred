# Stage 2 report

Test seasons: 2024/25, 2025/26, 2026/27 (849 matches).
2014/15 is used only as model history and is excluded from evaluation.

## Chosen validation settings

| Variant | Xi | Blend weight | Validation 1X2 log loss |
|---|---:|---:|---:|
| goals | 0.0019 | NA | 0.9971 |
| xg | 0.0010 | NA | 0.9822 |
| blend | 0.0010 | 0.3 | 0.9828 |

## 1X2

| Method | Accuracy | Log loss | Brier score |
|---|---:|---:|---:|
| Bookmaker opening | 54.77% | 0.9551 | 0.5654 |
| Bookmaker closing | 55.48% | 0.9516 | 0.5628 |
| Elo | 53.00% | 0.9940 | 0.5903 |
| DC goals | 52.53% | 0.9817 | 0.5825 |
| DC xG | 54.42% | 0.9741 | 0.5769 |
| DC best blend | 53.59% | 0.9718 | 0.5756 |

## Goal markets

| Method | Market | Log loss | Brier score |
|---|---|---:|---:|
| DC goals | over 0.5 | 0.2092 | 0.0506 |
| DC goals | over 1.5 | 0.5501 | 0.1834 |
| DC goals | over 2.5 | 0.6843 | 0.2456 |
| DC goals | over 3.5 | 0.5648 | 0.1882 |
| DC goals | BTTS | 0.7032 | 0.2539 |
| DC xg | over 0.5 | 0.2054 | 0.0498 |
| DC xg | over 1.5 | 0.5410 | 0.1793 |
| DC xg | over 2.5 | 0.6727 | 0.2402 |
| DC xg | over 3.5 | 0.5534 | 0.1849 |
| DC xg | BTTS | 0.6933 | 0.2495 |
| DC blend | over 0.5 | 0.2055 | 0.0498 |
| DC blend | over 1.5 | 0.5421 | 0.1798 |
| DC blend | over 2.5 | 0.6731 | 0.2404 |
| DC blend | over 3.5 | 0.5523 | 0.1843 |
| DC blend | BTTS | 0.6932 | 0.2496 |
| Bookmaker opening | over 2.5 | 0.6650 | 0.2363 |
| Bookmaker closing | over 2.5 | nan | nan |

## Calibration, best variant: xg

### Home win

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.093 | 0.000 | 1 |
| 0.1 to 0.2 | 0.161 | 0.250 | 28 |
| 0.2 to 0.3 | 0.253 | 0.207 | 116 |
| 0.3 to 0.4 | 0.356 | 0.342 | 187 |
| 0.4 to 0.5 | 0.448 | 0.430 | 214 |
| 0.5 to 0.6 | 0.546 | 0.547 | 159 |
| 0.6 to 0.7 | 0.650 | 0.805 | 87 |
| 0.7 to 0.8 | 0.739 | 0.896 | 48 |
| 0.8 to 0.9 | 0.820 | 0.778 | 9 |
| 0.9 to 1.0 | NA | NA | 0 |

### Away win

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.076 | 0.094 | 32 |
| 0.1 to 0.2 | 0.154 | 0.128 | 180 |
| 0.2 to 0.3 | 0.252 | 0.227 | 247 |
| 0.3 to 0.4 | 0.346 | 0.288 | 212 |
| 0.4 to 0.5 | 0.446 | 0.520 | 100 |
| 0.5 to 0.6 | 0.539 | 0.525 | 59 |
| 0.6 to 0.7 | 0.641 | 0.688 | 16 |
| 0.7 to 0.8 | 0.725 | 1.000 | 3 |
| 0.8 to 0.9 | NA | NA | 0 |
| 0.9 to 1.0 | NA | NA | 0 |

### Over 1.5

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | NA | NA | 0 |
| 0.1 to 0.2 | 0.135 | 1.000 | 1 |
| 0.2 to 0.3 | NA | NA | 0 |
| 0.3 to 0.4 | NA | NA | 0 |
| 0.4 to 0.5 | 0.484 | 0.000 | 1 |
| 0.5 to 0.6 | 0.578 | 0.500 | 32 |
| 0.6 to 0.7 | 0.663 | 0.703 | 323 |
| 0.7 to 0.8 | 0.749 | 0.766 | 338 |
| 0.8 to 0.9 | 0.834 | 0.888 | 152 |
| 0.9 to 1.0 | 0.920 | 1.000 | 2 |

### Over 2.5

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.027 | 0.000 | 1 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | 0.271 | 0.000 | 8 |
| 0.3 to 0.4 | 0.362 | 0.399 | 173 |
| 0.4 to 0.5 | 0.443 | 0.482 | 334 |
| 0.5 to 0.6 | 0.546 | 0.544 | 226 |
| 0.6 to 0.7 | 0.641 | 0.653 | 95 |
| 0.7 to 0.8 | 0.733 | 0.833 | 12 |
| 0.8 to 0.9 | NA | NA | 0 |
| 0.9 to 1.0 | NA | NA | 0 |

### BTTS

| Bin | Mean predicted | Actual rate | Count |
|---|---:|---:|---:|
| 0.0 to 0.1 | 0.049 | 1.000 | 1 |
| 0.1 to 0.2 | NA | NA | 0 |
| 0.2 to 0.3 | 0.270 | 0.000 | 3 |
| 0.3 to 0.4 | 0.377 | 0.419 | 62 |
| 0.4 to 0.5 | 0.456 | 0.556 | 439 |
| 0.5 to 0.6 | 0.543 | 0.590 | 283 |
| 0.6 to 0.7 | 0.628 | 0.583 | 60 |
| 0.7 to 0.8 | 0.701 | 1.000 | 1 |
| 0.8 to 0.9 | NA | NA | 0 |
| 0.9 to 1.0 | NA | NA | 0 |

## Confidence buckets

| Market | Threshold | Hit rate | Count |
|---|---:|---:|---:|
| Home win | 0.70 | 87.72% | 57 |
| Home win | 0.75 | 84.62% | 26 |
| Home win | 0.80 | 77.78% | 9 |
| Home win | 0.85 | NA | 0 |
| Home win | 0.90 | NA | 0 |
| Away win | 0.70 | 100.00% | 3 |
| Away win | 0.75 | 100.00% | 1 |
| Away win | 0.80 | NA | 0 |
| Away win | 0.85 | NA | 0 |
| Away win | 0.90 | NA | 0 |
| Over 0.5 | 0.70 | 94.81% | 848 |
| Over 0.5 | 0.75 | 94.81% | 848 |
| Over 0.5 | 0.80 | 94.81% | 848 |
| Over 0.5 | 0.85 | 94.87% | 838 |
| Over 0.5 | 0.90 | 95.99% | 649 |
| Over 1.5 | 0.70 | 80.49% | 492 |
| Over 1.5 | 0.75 | 83.95% | 324 |
| Over 1.5 | 0.80 | 88.96% | 154 |
| Over 1.5 | 0.85 | 90.70% | 43 |
| Over 1.5 | 0.90 | 100.00% | 2 |
| Over 2.5 | 0.70 | 83.33% | 12 |
| Over 2.5 | 0.75 | 50.00% | 2 |
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
| 1X2 home | 254 | 30.71% | -7.03% | 50.00% |
| 1X2 draw | 129 | 12.40% | -41.02% | 46.51% |
| 1X2 away | 322 | 18.94% | -18.81% | 39.13% |
| Goals over25 | 147 | 42.86% | -0.35% | 36.73% |
| Goals under25 | 206 | 38.83% | -11.81% | 47.09% |
