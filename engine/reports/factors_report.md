# Factor study

Walk-forward: each season's adjustment is fitted only on earlier seasons (from 2017/18).
Evaluated on 2021/22, 2022/23, 2023/24, 2024/25, 2025/26, 2026/27 (1970 matches).

## Log loss (lower is better), match-weighted

| Variant | 1X2 | Over 1.5 | Over 2.5 | Under 3.5 | Home win (1Up proxy) |
|---|---:|---:|---:|---:|---:|
| all | 0.9743 | 0.5080 | 0.6799 | 0.6425 | 0.6082 |
| baseline | 0.9737 | 0.5059 | 0.6776 | 0.6377 | 0.6080 |
| derby | 0.9745 | 0.5062 | 0.6780 | 0.6385 | 0.6086 |
| home | 0.9736 | 0.5060 | 0.6777 | 0.6384 | 0.6079 |
| rest | 0.9742 | 0.5074 | 0.6797 | 0.6401 | 0.6083 |
| table | 0.9747 | 0.5057 | 0.6778 | 0.6391 | 0.6083 |

## Improvement vs baseline (positive = better)

| Variant | 1X2 | Over 1.5 | Over 2.5 | Under 3.5 | Home win |
|---|---:|---:|---:|---:|---:|
| all | -0.0007 | -0.0022 | -0.0023 | -0.0048 | -0.0002 |
| derby | -0.0008 | -0.0004 | -0.0004 | -0.0008 | -0.0006 |
| home | +0.0001 | -0.0002 | -0.0000 | -0.0007 | +0.0001 |
| rest | -0.0005 | -0.0016 | -0.0020 | -0.0025 | -0.0003 |
| table | -0.0010 | +0.0002 | -0.0001 | -0.0015 | -0.0003 |

## By season: 1X2 log loss

| Season | all | baseline | derby | home | rest | table |
|---|---:|---:|---:|---:|---:|---:|
| 2021/22 | 0.9608 | 0.9574 | 0.9588 | 0.9578 | 0.9596 | 0.9594 |
| 2022/23 | 0.9848 | 0.9837 | 0.9853 | 0.9843 | 0.9844 | 0.9846 |
| 2023/24 | 0.9289 | 0.9290 | 0.9288 | 0.9278 | 0.9286 | 0.9312 |
| 2024/25 | 0.9626 | 0.9647 | 0.9657 | 0.9650 | 0.9636 | 0.9628 |
| 2025/26 | 1.0275 | 1.0267 | 1.0272 | 1.0259 | 1.0281 | 1.0283 |
| 2026/27 | 1.0124 | 1.0105 | 1.0103 | 1.0115 | 1.0101 | 1.0129 |

## Fitted effects, home goals (all factors, trained to 2025/26)

| Feature | Coefficient | Std. error | Goals multiplier |
|---|---:|---:|---:|
| const | -0.035 | 0.036 | x0.966 |
| ppg_diff | -0.026 | 0.033 | x0.974 |
| relegation_self | -0.034 | 0.056 | x0.967 |
| relegation_opp | -0.036 | 0.047 | x0.965 |
| title_self | +0.110 | 0.073 | x1.116 |
| title_opp | -0.123 | 0.117 | x0.884 |
| dead_rubber_self | +0.075 | 0.065 | x1.078 |
| dead_rubber_opp | -0.043 | 0.065 | x0.958 |
| derby | -0.042 | 0.056 | x0.959 |
| att_resid | -0.067 | 0.181 | x0.935 |
| opp_def_resid | -0.246 | 0.191 | x0.782 |
| rest_diff | -0.007 | 0.007 | x0.993 |
| short_rest | +0.042 | 0.036 | x1.043 |

## Fitted effects, away goals (all factors, trained to 2025/26)

| Feature | Coefficient | Std. error | Goals multiplier |
|---|---:|---:|---:|
| const | -0.105 | 0.047 | x0.900 |
| ppg_diff | -0.007 | 0.036 | x0.993 |
| relegation_self | -0.011 | 0.060 | x0.989 |
| relegation_opp | +0.132 | 0.050 | x1.141 |
| title_self | -0.051 | 0.082 | x0.951 |
| title_opp | +0.079 | 0.122 | x1.082 |
| dead_rubber_self | +0.027 | 0.072 | x1.027 |
| dead_rubber_opp | +0.012 | 0.070 | x1.012 |
| derby | +0.005 | 0.061 | x1.005 |
| att_resid | -0.257 | 0.224 | x0.773 |
| opp_def_resid | -0.427 | 0.214 | x0.653 |
| rest_diff | -0.001 | 0.008 | x0.999 |
| short_rest | +0.007 | 0.039 | x1.007 |

## Absences (missing regular starters), evaluated 2022/23 onwards

1564 matches with lineup data. Uses actual starting XIs, so it is an upper bound for live injury news.

| Variant | 1X2 | Over 1.5 | Over 2.5 | Under 3.5 | Home win |
|---|---:|---:|---:|---:|---:|
| absences | 0.9793 | 0.4978 | 0.6782 | 0.6455 | 0.6106 |
| baseline | 0.9776 | 0.4964 | 0.6775 | 0.6460 | 0.6105 |

### Absence effects, home goals

| Feature | Coefficient | Std. error | Goals multiplier |
|---|---:|---:|---:|
| const | +0.063 | 0.050 | x1.065 |
| att_missing_self | -0.264 | 0.150 | x0.768 |
| def_missing_opp | +0.020 | 0.020 | x1.020 |
| att_missing_opp | +0.032 | 0.143 | x1.032 |
| def_missing_self | -0.029 | 0.021 | x0.972 |

### Absence effects, away goals

| Feature | Coefficient | Std. error | Goals multiplier |
|---|---:|---:|---:|
| const | -0.023 | 0.054 | x0.978 |
| att_missing_self | +0.036 | 0.157 | x1.037 |
| def_missing_opp | +0.018 | 0.022 | x1.019 |
| att_missing_opp | -0.076 | 0.160 | x0.927 |
| def_missing_self | +0.011 | 0.022 | x1.011 |
