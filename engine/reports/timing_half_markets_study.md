# Goal-timing and team-half markets backtest (PROJECT.md task 20, pre-registered 2026-11-07)

## Pre-registered design and Task 19 prerequisite
- **Task 19 gate**: **PASS** (`332/332 = 100.00%` `< 10:00` agreement with `Understat minute <= 9`, `73/73 = 100.00%` goal-order agreement when `goals.parquet` is sorted by `minute`). Therefore all 5 timing markets are evaluated on the 5 main leagues.
- **Raw probability model**: From `accumulators.bookmaker_implied` lambdas (`league_rho(league)`):
  - First-half share `s` and 10-minute share `w` (fraction of goals with `Understat minute <= 9`) per league from **earlier seasons only** (`< season`).
  - Team goals in a period ~ independent `Poisson(share * lambda)`.
  - `first_goal_home = lam_home / (lam_home + lam_away) * (1 - exp(-(lam_home + lam_away)))` (and mirror for `first_goal_away`).
- **Walk-forward calibration & gates**: Platt (`LogisticRegression(C=1.0)` on `logit(raw)`) fitted per league x market on earlier seasons only; judged with `market_gates.evaluate` unchanged (`bookmaker_probability = raw`, one-sided C1-C4, >= 300 legs, `SEED = 20261029`) on **2024/25+** (primary) and **2019/20-2023/24** (replication). **Strong candidate** = `PASS` in both periods.

## Overall Summary
- **Timing markets (5 main leagues x 5 markets = 25 pairs)**: Primary `2024/25+` **25 PASS / 0 FAIL**; Replication `2019/20-2023/24` **24 PASS / 1 FAIL**; Strong candidates (`PASS` in both): **24 / 25**.
- **Team-half markets (9 live leagues x 8 markets = 72 pairs)**: Primary `2024/25+` **68 PASS / 4 FAIL**; Replication `2019/20-2023/24` **61 PASS / 11 FAIL**; Strong candidates (`PASS` in both): **58 / 72**.
- **Combined (97 pairs)**: Primary **93 PASS / 4 FAIL**; Replication **85 PASS / 12 FAIL**; Strong candidates (`PASS` in both): **82 / 97**.

## Part 1 — Goal-Timing Markets (5 Main Leagues, Understat `goals.parquet`)
| League | Market | 2024/25+ n | 2024/25+ Said | 2024/25+ Won | Fair odds | 2024/25+ Gate | 2019/20-23/24 n | 2019/20-23/24 Said | 2019/20-23/24 Won | 2019/20-23/24 Gate | Verdict |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|---|
| EPL | first_goal_home | 830 | 0.5180 | 0.5108 | 1.94 | **PASS** | 1899 | 0.5108 | 0.5103 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EPL | first_goal_away | 830 | 0.4280 | 0.4313 | 2.38 | **PASS** | 1899 | 0.4252 | 0.4334 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EPL | interval_10_home | 830 | 0.1148 | 0.1169 | 8.96 | **PASS** | 1899 | 0.1104 | 0.1101 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EPL | interval_10_draw | 830 | 0.7903 | 0.7964 | 1.26 | **PASS** | 1899 | 0.8024 | 0.7904 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EPL | interval_10_away | 830 | 0.0941 | 0.0867 | 11.05 | **PASS** | 1899 | 0.0861 | 0.0995 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | first_goal_home | 805 | 0.5195 | 0.5528 | 1.97 | **PASS** | 1900 | 0.5134 | 0.5116 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | first_goal_away | 805 | 0.4014 | 0.3925 | 2.56 | **PASS** | 1900 | 0.4009 | 0.4026 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | interval_10_home | 805 | 0.1047 | 0.1081 | 10.16 | **PASS** | 1900 | 0.0941 | 0.0984 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | interval_10_draw | 805 | 0.8108 | 0.8149 | 1.23 | **PASS** | 1900 | 0.8236 | 0.8121 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | interval_10_away | 805 | 0.0862 | 0.0770 | 12.16 | **PASS** | 1900 | 0.0781 | 0.0895 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | first_goal_home | 803 | 0.4963 | 0.4819 | 2.03 | **PASS** | 1898 | 0.5039 | 0.4989 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | first_goal_away | 803 | 0.4220 | 0.4371 | 2.44 | **PASS** | 1898 | 0.4299 | 0.4420 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | interval_10_home | 803 | 0.1021 | 0.1233 | 10.35 | **PASS** | 1898 | 0.1078 | 0.1112 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | interval_10_draw | 803 | 0.8165 | 0.8020 | 1.22 | **PASS** | 1898 | 0.8053 | 0.8035 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | interval_10_away | 803 | 0.0770 | 0.0747 | 13.94 | **PASS** | 1898 | 0.0830 | 0.0854 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | first_goal_home | 638 | 0.5353 | 0.5157 | 1.89 | **PASS** | 1530 | 0.5346 | 0.5216 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | first_goal_away | 638 | 0.4137 | 0.4248 | 2.44 | **PASS** | 1530 | 0.4114 | 0.4301 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | interval_10_home | 638 | 0.1328 | 0.1113 | 7.90 | **PASS** | 1530 | 0.1269 | 0.1307 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | interval_10_draw | 638 | 0.7656 | 0.8009 | 1.30 | **PASS** | 1530 | 0.7774 | 0.7608 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | interval_10_away | 638 | 0.0989 | 0.0878 | 10.51 | **PASS** | 1530 | 0.0900 | 0.1085 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | first_goal_home | 638 | 0.5089 | 0.4984 | 1.96 | **PASS** | 1725 | 0.5208 | 0.4910 | **FAIL** | stays out |
| LIGUE1 | first_goal_away | 638 | 0.4349 | 0.4357 | 2.35 | **PASS** | 1725 | 0.4151 | 0.4371 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | interval_10_home | 638 | 0.1113 | 0.1034 | 9.42 | **PASS** | 1725 | 0.0995 | 0.1090 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | interval_10_draw | 638 | 0.7959 | 0.7962 | 1.25 | **PASS** | 1725 | 0.8194 | 0.8041 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | interval_10_away | 638 | 0.0957 | 0.1003 | 11.33 | **PASS** | 1725 | 0.0838 | 0.0870 | **PASS** | Strong candidate (pending real Betpawa prices) |

## Part 2 — Team-Half Markets (All 9 Live Leagues, `HTHG`/`HTAG` & `FTHG`/`FTAG`)
| League | Market | 2024/25+ n | 2024/25+ Said | 2024/25+ Won | Fair odds | 2024/25+ Gate | 2019/20-23/24 n | 2019/20-23/24 Said | 2019/20-23/24 Won | 2019/20-23/24 Gate | Verdict |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|---|
| EPL | home_score_both_halves | 830 | 0.3025 | 0.2892 | 3.46 | **PASS** | 1900 | 0.2850 | 0.2868 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EPL | away_score_both_halves | 830 | 0.2415 | 0.2169 | 4.45 | **PASS** | 1900 | 0.2302 | 0.2384 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EPL | home_win_both_halves | 830 | 0.1434 | 0.1265 | 8.67 | **PASS** | 1900 | 0.1470 | 0.1405 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EPL | away_win_both_halves | 830 | 0.0919 | 0.0747 | 13.57 | **PASS** | 1900 | 0.0963 | 0.0958 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EPL | home_fh_over_0.5 | 830 | 0.5081 | 0.5181 | 1.98 | **PASS** | 1900 | 0.4816 | 0.5026 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EPL | away_fh_over_0.5 | 830 | 0.4376 | 0.4060 | 2.33 | **PASS** | 1900 | 0.4233 | 0.4332 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EPL | home_sh_over_0.5 | 830 | 0.5845 | 0.5337 | 1.71 | **FAIL** | 1900 | 0.5749 | 0.5537 | **FAIL** | stays out |
| EPL | away_sh_over_0.5 | 830 | 0.5174 | 0.5542 | 1.96 | **PASS** | 1900 | 0.4974 | 0.5058 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | home_score_both_halves | 849 | 0.2680 | 0.2591 | 4.27 | **PASS** | 1900 | 0.2575 | 0.2553 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | away_score_both_halves | 849 | 0.1900 | 0.1885 | 6.08 | **PASS** | 1900 | 0.1793 | 0.1805 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | home_win_both_halves | 849 | 0.1209 | 0.1166 | 10.96 | **PASS** | 1900 | 0.1159 | 0.1174 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | away_win_both_halves | 849 | 0.0695 | 0.0542 | 20.74 | **FAIL** | 1900 | 0.0680 | 0.0674 | **PASS** | stays out |
| LALIGA | home_fh_over_0.5 | 849 | 0.4684 | 0.4900 | 2.24 | **PASS** | 1900 | 0.4444 | 0.4621 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | away_fh_over_0.5 | 849 | 0.3845 | 0.3828 | 2.73 | **PASS** | 1900 | 0.3706 | 0.3805 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | home_sh_over_0.5 | 849 | 0.5632 | 0.5748 | 1.84 | **PASS** | 1900 | 0.5629 | 0.5479 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | away_sh_over_0.5 | 849 | 0.4749 | 0.5065 | 2.19 | **PASS** | 1900 | 0.4688 | 0.4595 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | home_score_both_halves | 830 | 0.2522 | 0.2398 | 4.40 | **PASS** | 1898 | 0.2849 | 0.2798 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | away_score_both_halves | 830 | 0.1910 | 0.2120 | 6.08 | **PASS** | 1898 | 0.2147 | 0.2371 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | home_win_both_halves | 830 | 0.1197 | 0.1024 | 10.72 | **PASS** | 1898 | 0.1267 | 0.1307 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | away_win_both_halves | 830 | 0.0772 | 0.0867 | 18.43 | **PASS** | 1898 | 0.0829 | 0.0854 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | home_fh_over_0.5 | 830 | 0.4505 | 0.4265 | 2.29 | **PASS** | 1898 | 0.4767 | 0.4879 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | away_fh_over_0.5 | 830 | 0.3956 | 0.4145 | 2.63 | **PASS** | 1898 | 0.4169 | 0.4394 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | home_sh_over_0.5 | 830 | 0.5478 | 0.5301 | 1.86 | **PASS** | 1898 | 0.5848 | 0.5764 | **FAIL** | stays out |
| SERIEA | away_sh_over_0.5 | 830 | 0.4792 | 0.4940 | 2.16 | **PASS** | 1898 | 0.5193 | 0.5184 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | home_score_both_halves | 665 | 0.3410 | 0.3609 | 3.16 | **PASS** | 1530 | 0.3260 | 0.3327 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | away_score_both_halves | 665 | 0.2577 | 0.2902 | 4.25 | **PASS** | 1530 | 0.2585 | 0.2444 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | home_win_both_halves | 665 | 0.1560 | 0.1579 | 7.65 | **PASS** | 1530 | 0.1506 | 0.1569 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | away_win_both_halves | 665 | 0.0956 | 0.0917 | 12.82 | **PASS** | 1530 | 0.1018 | 0.0974 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | home_fh_over_0.5 | 665 | 0.5514 | 0.5248 | 1.86 | **PASS** | 1530 | 0.5351 | 0.5294 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | away_fh_over_0.5 | 665 | 0.4675 | 0.4752 | 2.19 | **PASS** | 1530 | 0.4470 | 0.4660 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | home_sh_over_0.5 | 665 | 0.6067 | 0.6286 | 1.68 | **PASS** | 1530 | 0.5982 | 0.6157 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | away_sh_over_0.5 | 665 | 0.5290 | 0.5594 | 1.92 | **PASS** | 1530 | 0.5424 | 0.5176 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | home_score_both_halves | 675 | 0.3018 | 0.3333 | 3.62 | **PASS** | 1725 | 0.2845 | 0.2684 | **FAIL** | stays out |
| LIGUE1 | away_score_both_halves | 675 | 0.2322 | 0.2222 | 4.70 | **PASS** | 1725 | 0.2105 | 0.2116 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | home_win_both_halves | 675 | 0.1416 | 0.1644 | 8.67 | **PASS** | 1725 | 0.1369 | 0.1275 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | away_win_both_halves | 675 | 0.0883 | 0.0919 | 14.92 | **PASS** | 1725 | 0.0799 | 0.0817 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | home_fh_over_0.5 | 675 | 0.5165 | 0.5067 | 1.98 | **PASS** | 1725 | 0.4911 | 0.4910 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | away_fh_over_0.5 | 675 | 0.4443 | 0.4311 | 2.30 | **PASS** | 1725 | 0.4097 | 0.4342 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | home_sh_over_0.5 | 675 | 0.5694 | 0.6089 | 1.79 | **PASS** | 1725 | 0.5616 | 0.5362 | **FAIL** | stays out |
| LIGUE1 | away_sh_over_0.5 | 675 | 0.5107 | 0.4933 | 1.99 | **PASS** | 1725 | 0.4948 | 0.4899 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EREDIV | home_score_both_halves | 701 | 0.3449 | 0.3524 | 3.14 | **PASS** | 1456 | 0.3386 | 0.3228 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EREDIV | away_score_both_halves | 701 | 0.2416 | 0.2682 | 4.60 | **PASS** | 1456 | 0.2345 | 0.2342 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EREDIV | home_win_both_halves | 701 | 0.1733 | 0.1683 | 7.62 | **PASS** | 1456 | 0.1764 | 0.1724 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EREDIV | away_win_both_halves | 701 | 0.0908 | 0.0870 | 14.88 | **PASS** | 1456 | 0.0973 | 0.0934 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EREDIV | home_fh_over_0.5 | 701 | 0.5349 | 0.5706 | 1.91 | **PASS** | 1456 | 0.5314 | 0.5069 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EREDIV | away_fh_over_0.5 | 701 | 0.4491 | 0.4608 | 2.27 | **PASS** | 1456 | 0.4448 | 0.4361 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EREDIV | home_sh_over_0.5 | 701 | 0.6157 | 0.6191 | 1.64 | **PASS** | 1456 | 0.6039 | 0.6003 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EREDIV | away_sh_over_0.5 | 701 | 0.5168 | 0.5449 | 1.96 | **PASS** | 1456 | 0.5049 | 0.5048 | **PASS** | Strong candidate (pending real Betpawa prices) |
| JUPILER | home_score_both_halves | 702 | 0.2963 | 0.3006 | 3.63 | **PASS** | 1458 | 0.3062 | 0.3045 | **PASS** | Strong candidate (pending real Betpawa prices) |
| JUPILER | away_score_both_halves | 702 | 0.2334 | 0.2080 | 4.56 | **PASS** | 1458 | 0.2492 | 0.2366 | **PASS** | Strong candidate (pending real Betpawa prices) |
| JUPILER | home_win_both_halves | 702 | 0.1363 | 0.1410 | 8.63 | **PASS** | 1458 | 0.1361 | 0.1509 | **PASS** | Strong candidate (pending real Betpawa prices) |
| JUPILER | away_win_both_halves | 702 | 0.0853 | 0.0670 | 14.76 | **FAIL** | 1458 | 0.0899 | 0.0919 | **PASS** | stays out |
| JUPILER | home_fh_over_0.5 | 702 | 0.4960 | 0.5014 | 2.05 | **PASS** | 1458 | 0.4910 | 0.5041 | **PASS** | Strong candidate (pending real Betpawa prices) |
| JUPILER | away_fh_over_0.5 | 702 | 0.4432 | 0.4330 | 2.29 | **PASS** | 1458 | 0.4410 | 0.4458 | **FAIL** | stays out |
| JUPILER | home_sh_over_0.5 | 702 | 0.5820 | 0.5698 | 1.74 | **PASS** | 1458 | 0.6113 | 0.5816 | **FAIL** | stays out |
| JUPILER | away_sh_over_0.5 | 702 | 0.5144 | 0.4516 | 1.96 | **FAIL** | 1458 | 0.5384 | 0.5226 | **PASS** | stays out |
| PRIMEIRA | home_score_both_halves | 693 | 0.2602 | 0.2684 | 4.43 | **PASS** | 1530 | 0.2708 | 0.2458 | **FAIL** | stays out |
| PRIMEIRA | away_score_both_halves | 693 | 0.2051 | 0.1977 | 5.68 | **PASS** | 1530 | 0.2081 | 0.1961 | **PASS** | Strong candidate (pending real Betpawa prices) |
| PRIMEIRA | home_win_both_halves | 693 | 0.1367 | 0.1299 | 10.52 | **PASS** | 1530 | 0.1433 | 0.1235 | **FAIL** | stays out |
| PRIMEIRA | away_win_both_halves | 693 | 0.0876 | 0.0794 | 18.38 | **PASS** | 1530 | 0.0878 | 0.0739 | **FAIL** | stays out |
| PRIMEIRA | home_fh_over_0.5 | 693 | 0.4767 | 0.4733 | 2.14 | **PASS** | 1530 | 0.4989 | 0.4569 | **FAIL** | stays out |
| PRIMEIRA | away_fh_over_0.5 | 693 | 0.4143 | 0.3997 | 2.53 | **PASS** | 1530 | 0.4225 | 0.4072 | **PASS** | Strong candidate (pending real Betpawa prices) |
| PRIMEIRA | home_sh_over_0.5 | 693 | 0.5266 | 0.5339 | 1.92 | **PASS** | 1530 | 0.5263 | 0.5359 | **PASS** | Strong candidate (pending real Betpawa prices) |
| PRIMEIRA | away_sh_over_0.5 | 693 | 0.4610 | 0.4820 | 2.25 | **PASS** | 1530 | 0.4554 | 0.4575 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SUPERLIG | home_score_both_halves | 728 | 0.3082 | 0.2912 | 3.50 | **PASS** | 1798 | 0.3106 | 0.3003 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SUPERLIG | away_score_both_halves | 728 | 0.2126 | 0.2088 | 5.41 | **PASS** | 1798 | 0.2120 | 0.2069 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SUPERLIG | home_win_both_halves | 728 | 0.1400 | 0.1250 | 8.25 | **PASS** | 1798 | 0.1314 | 0.1407 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SUPERLIG | away_win_both_halves | 728 | 0.0793 | 0.0646 | 19.45 | **PASS** | 1798 | 0.0757 | 0.0695 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SUPERLIG | home_fh_over_0.5 | 728 | 0.5164 | 0.5096 | 1.97 | **PASS** | 1798 | 0.5173 | 0.5033 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SUPERLIG | away_fh_over_0.5 | 728 | 0.4256 | 0.4093 | 2.46 | **PASS** | 1798 | 0.4273 | 0.4121 | **FAIL** | stays out |
| SUPERLIG | home_sh_over_0.5 | 728 | 0.5760 | 0.5591 | 1.76 | **PASS** | 1798 | 0.5818 | 0.5895 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SUPERLIG | away_sh_over_0.5 | 728 | 0.4912 | 0.4890 | 2.11 | **PASS** | 1798 | 0.4941 | 0.5056 | **PASS** | Strong candidate (pending real Betpawa prices) |

## Coverage and Walk-Forward Shares (`w` and `s`)
### Timing markets coverage & 10-minute share `w`
```json
{
  "EPL": {
    "total_rows": 4630,
    "dropped_missing_odds": 0,
    "dropped_unreconciled_goals": 0,
    "dropped_tied_first_goal": 2,
    "kept_rows": 4628,
    "share_10_2019_20": 0.0771,
    "share_10_2024_25": 0.08,
    "share_10_2026_27": 0.08
  },
  "LALIGA": {
    "total_rows": 4649,
    "dropped_missing_odds": 0,
    "dropped_unreconciled_goals": 45,
    "dropped_tied_first_goal": 0,
    "kept_rows": 4604,
    "share_10_2019_20": 0.0767,
    "share_10_2024_25": 0.0798,
    "share_10_2026_27": 0.0798
  },
  "SERIEA": {
    "total_rows": 4630,
    "dropped_missing_odds": 2,
    "dropped_unreconciled_goals": 28,
    "dropped_tied_first_goal": 0,
    "kept_rows": 4600,
    "share_10_2019_20": 0.083,
    "share_10_2024_25": 0.0788,
    "share_10_2026_27": 0.0798
  },
  "BUNDES": {
    "total_rows": 3726,
    "dropped_missing_odds": 0,
    "dropped_unreconciled_goals": 29,
    "dropped_tied_first_goal": 0,
    "kept_rows": 3697,
    "share_10_2019_20": 0.0748,
    "share_10_2024_25": 0.0821,
    "share_10_2026_27": 0.0804
  },
  "LIGUE1": {
    "total_rows": 4300,
    "dropped_missing_odds": 0,
    "dropped_unreconciled_goals": 41,
    "dropped_tied_first_goal": 1,
    "kept_rows": 4258,
    "share_10_2019_20": 0.0806,
    "share_10_2024_25": 0.0823,
    "share_10_2026_27": 0.0815
  }
}
```

### Team-half markets coverage & first-half share `s`
```json
{
  "EPL": {
    "kept_rows": 4630,
    "share_fh_2019_20": 0.4431,
    "share_fh_2024_25": 0.4471,
    "share_fh_2026_27": 0.4474
  },
  "LALIGA": {
    "kept_rows": 4649,
    "share_fh_2019_20": 0.4344,
    "share_fh_2024_25": 0.439,
    "share_fh_2026_27": 0.4381
  },
  "SERIEA": {
    "kept_rows": 4627,
    "share_fh_2019_20": 0.4375,
    "share_fh_2024_25": 0.4385,
    "share_fh_2026_27": 0.4376
  },
  "BUNDES": {
    "kept_rows": 3725,
    "share_fh_2019_20": 0.4348,
    "share_fh_2024_25": 0.4437,
    "share_fh_2026_27": 0.4459
  },
  "LIGUE1": {
    "kept_rows": 4299,
    "share_fh_2019_20": 0.4259,
    "share_fh_2024_25": 0.4415,
    "share_fh_2026_27": 0.4406
  },
  "EREDIV": {
    "kept_rows": 3687,
    "share_fh_2019_20": 0.4335,
    "share_fh_2024_25": 0.4364,
    "share_fh_2026_27": 0.4386
  },
  "JUPILER": {
    "kept_rows": 3360,
    "share_fh_2019_20": 0.4258,
    "share_fh_2024_25": 0.4329,
    "share_fh_2026_27": 0.4385
  },
  "PRIMEIRA": {
    "kept_rows": 3752,
    "share_fh_2019_20": 0.4456,
    "share_fh_2024_25": 0.4486,
    "share_fh_2026_27": 0.4487
  },
  "SUPERLIG": {
    "kept_rows": 4056,
    "share_fh_2019_20": 0.4309,
    "share_fh_2024_25": 0.4346,
    "share_fh_2026_27": 0.4357
  }
}
```

## Full Gate Details
```json
[
  {
    "league": "EPL",
    "market": "first_goal_home",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "first_goal_home",
      "n": 830,
      "status": "PASS",
      "C1_slope": 1.083,
      "C1_ci": [
        0.816,
        1.35
      ],
      "C1": true,
      "C2_level": -0.0072,
      "C2_ci": [
        -0.038,
        0.0261
      ],
      "C2": true,
      "C3_min_z": -1.14,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0004,
      "logloss_vs_book_ci": [
        -0.0002,
        0.0009
      ],
      "mean_p": 0.518,
      "actual": 0.5108,
      "fair_odds": 1.94
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "first_goal_home",
      "n": 1899,
      "status": "PASS",
      "C1_slope": 0.873,
      "C1_ci": [
        0.728,
        1.019
      ],
      "C1": true,
      "C2_level": -0.0005,
      "C2_ci": [
        -0.0221,
        0.0217
      ],
      "C2": true,
      "C3_min_z": -2.09,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0009,
      "logloss_vs_book_ci": [
        -0.0002,
        0.002
      ],
      "mean_p": 0.5108,
      "actual": 0.5103,
      "fair_odds": 1.98
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "EPL",
    "market": "first_goal_away",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "first_goal_away",
      "n": 830,
      "status": "PASS",
      "C1_slope": 1.02,
      "C1_ci": [
        0.752,
        1.288
      ],
      "C1": true,
      "C2_level": 0.0033,
      "C2_ci": [
        -0.031,
        0.035
      ],
      "C2": true,
      "C3_min_z": -2.11,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0006,
      "logloss_vs_book_ci": [
        -0.0,
        0.0011
      ],
      "mean_p": 0.428,
      "actual": 0.4313,
      "fair_odds": 2.38
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "first_goal_away",
      "n": 1899,
      "status": "PASS",
      "C1_slope": 0.826,
      "C1_ci": [
        0.682,
        0.97
      ],
      "C1": true,
      "C2_level": 0.0082,
      "C2_ci": [
        -0.0137,
        0.0285
      ],
      "C2": true,
      "C3_min_z": -1.35,
      "C3": true,
      "C4_lifted_legs": 27,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0016,
      "logloss_vs_book_ci": [
        0.0001,
        0.0031
      ],
      "mean_p": 0.4252,
      "actual": 0.4334,
      "fair_odds": 2.4
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "EPL",
    "market": "interval_10_home",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "interval_10_home",
      "n": 830,
      "status": "PASS",
      "C1_slope": 0.688,
      "C1_ci": [
        -0.056,
        1.431
      ],
      "C1": true,
      "C2_level": 0.002,
      "C2_ci": [
        -0.0193,
        0.0227
      ],
      "C2": true,
      "C3_min_z": -1.21,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0004,
      "logloss_vs_book_ci": [
        -0.0022,
        0.0013
      ],
      "mean_p": 0.1148,
      "actual": 0.1169,
      "fair_odds": 8.96
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "interval_10_home",
      "n": 1899,
      "status": "PASS",
      "C1_slope": 0.779,
      "C1_ci": [
        0.404,
        1.153
      ],
      "C1": true,
      "C2_level": -0.0003,
      "C2_ci": [
        -0.0135,
        0.0131
      ],
      "C2": true,
      "C3_min_z": -1.05,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0005,
        0.0009
      ],
      "mean_p": 0.1104,
      "actual": 0.1101,
      "fair_odds": 9.6
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "EPL",
    "market": "interval_10_draw",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "interval_10_draw",
      "n": 830,
      "status": "PASS",
      "C1_slope": 1.42,
      "C1_ci": [
        -0.126,
        2.966
      ],
      "C1": true,
      "C2_level": 0.006,
      "C2_ci": [
        -0.0209,
        0.0331
      ],
      "C2": true,
      "C3_min_z": -2.05,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0014,
        0.0017
      ],
      "mean_p": 0.7903,
      "actual": 0.7964,
      "fair_odds": 1.26
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "interval_10_draw",
      "n": 1899,
      "status": "PASS",
      "C1_slope": 0.777,
      "C1_ci": [
        0.069,
        1.486
      ],
      "C1": true,
      "C2_level": -0.012,
      "C2_ci": [
        -0.0298,
        0.0056
      ],
      "C2": true,
      "C3_min_z": -1.66,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0004,
      "logloss_vs_book_ci": [
        -0.0007,
        0.0014
      ],
      "mean_p": 0.8024,
      "actual": 0.7904,
      "fair_odds": 1.24
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "EPL",
    "market": "interval_10_away",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "interval_10_away",
      "n": 830,
      "status": "PASS",
      "C1_slope": 1.22,
      "C1_ci": [
        0.358,
        2.081
      ],
      "C1": true,
      "C2_level": -0.0073,
      "C2_ci": [
        -0.0248,
        0.0108
      ],
      "C2": true,
      "C3_min_z": -1.62,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0005,
      "logloss_vs_book_ci": [
        -0.0014,
        0.0021
      ],
      "mean_p": 0.0941,
      "actual": 0.0867,
      "fair_odds": 11.05
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "interval_10_away",
      "n": 1899,
      "status": "PASS",
      "C1_slope": 0.722,
      "C1_ci": [
        0.303,
        1.14
      ],
      "C1": true,
      "C2_level": 0.0135,
      "C2_ci": [
        0.0014,
        0.0259
      ],
      "C2": true,
      "C3_min_z": -0.88,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0001,
      "logloss_vs_book_ci": [
        -0.0011,
        0.0014
      ],
      "mean_p": 0.0861,
      "actual": 0.0995,
      "fair_odds": 12.31
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LALIGA",
    "market": "first_goal_home",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "first_goal_home",
      "n": 805,
      "status": "PASS",
      "C1_slope": 1.017,
      "C1_ci": [
        0.757,
        1.277
      ],
      "C1": true,
      "C2_level": 0.0333,
      "C2_ci": [
        0.0007,
        0.0674
      ],
      "C2": true,
      "C3_min_z": -0.94,
      "C3": true,
      "C4_lifted_legs": 5,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0007,
      "logloss_vs_book_ci": [
        -0.0029,
        0.0015
      ],
      "mean_p": 0.5195,
      "actual": 0.5528,
      "fair_odds": 1.97
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "first_goal_home",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.055,
      "C1_ci": [
        0.885,
        1.224
      ],
      "C1": true,
      "C2_level": -0.0018,
      "C2_ci": [
        -0.0244,
        0.0185
      ],
      "C2": true,
      "C3_min_z": -2.1,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0008,
      "logloss_vs_book_ci": [
        -0.0022,
        0.0006
      ],
      "mean_p": 0.5134,
      "actual": 0.5116,
      "fair_odds": 1.96
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LALIGA",
    "market": "first_goal_away",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "first_goal_away",
      "n": 805,
      "status": "PASS",
      "C1_slope": 0.998,
      "C1_ci": [
        0.733,
        1.263
      ],
      "C1": true,
      "C2_level": -0.0089,
      "C2_ci": [
        -0.0377,
        0.0221
      ],
      "C2": true,
      "C3_min_z": -1.0,
      "C3": true,
      "C4_lifted_legs": 6,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0004,
      "logloss_vs_book_ci": [
        -0.0022,
        0.0014
      ],
      "mean_p": 0.4014,
      "actual": 0.3925,
      "fair_odds": 2.56
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "first_goal_away",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.004,
      "C1_ci": [
        0.831,
        1.177
      ],
      "C1": true,
      "C2_level": 0.0017,
      "C2_ci": [
        -0.0191,
        0.0232
      ],
      "C2": true,
      "C3_min_z": -1.85,
      "C3": true,
      "C4_lifted_legs": 17,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0003,
      "logloss_vs_book_ci": [
        -0.0016,
        0.0009
      ],
      "mean_p": 0.4009,
      "actual": 0.4026,
      "fair_odds": 2.55
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LALIGA",
    "market": "interval_10_home",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "interval_10_home",
      "n": 805,
      "status": "PASS",
      "C1_slope": 1.281,
      "C1_ci": [
        0.533,
        2.029
      ],
      "C1": true,
      "C2_level": 0.0034,
      "C2_ci": [
        -0.0179,
        0.0259
      ],
      "C2": true,
      "C3_min_z": -1.32,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0006,
      "logloss_vs_book_ci": [
        -0.0007,
        0.0018
      ],
      "mean_p": 0.1047,
      "actual": 0.1081,
      "fair_odds": 10.16
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "interval_10_home",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.752,
      "C1_ci": [
        0.26,
        1.245
      ],
      "C1": true,
      "C2_level": 0.0043,
      "C2_ci": [
        -0.0098,
        0.019
      ],
      "C2": true,
      "C3_min_z": -1.44,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0001,
      "logloss_vs_book_ci": [
        -0.0009,
        0.0007
      ],
      "mean_p": 0.0941,
      "actual": 0.0984,
      "fair_odds": 11.2
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LALIGA",
    "market": "interval_10_draw",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "interval_10_draw",
      "n": 805,
      "status": "PASS",
      "C1_slope": 2.334,
      "C1_ci": [
        -0.158,
        4.827
      ],
      "C1": true,
      "C2_level": 0.0041,
      "C2_ci": [
        -0.0258,
        0.0307
      ],
      "C2": true,
      "C3_min_z": -1.05,
      "C3": true,
      "C4_lifted_legs": 40,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0009,
      "logloss_vs_book_ci": [
        -0.0026,
        0.0045
      ],
      "mean_p": 0.8108,
      "actual": 0.8149,
      "fair_odds": 1.23
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "interval_10_draw",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.356,
      "C1_ci": [
        -1.18,
        1.892
      ],
      "C1": true,
      "C2_level": -0.0115,
      "C2_ci": [
        -0.0287,
        0.0056
      ],
      "C2": true,
      "C3_min_z": -2.61,
      "C3": true,
      "C4_lifted_legs": 20,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0011,
      "logloss_vs_book_ci": [
        -0.0029,
        0.0005
      ],
      "mean_p": 0.8236,
      "actual": 0.8121,
      "fair_odds": 1.21
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LALIGA",
    "market": "interval_10_away",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "interval_10_away",
      "n": 805,
      "status": "PASS",
      "C1_slope": 1.79,
      "C1_ci": [
        0.821,
        2.759
      ],
      "C1": true,
      "C2_level": -0.0092,
      "C2_ci": [
        -0.0261,
        0.0095
      ],
      "C2": true,
      "C3_min_z": -1.51,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0018,
      "logloss_vs_book_ci": [
        -0.0011,
        0.0044
      ],
      "mean_p": 0.0862,
      "actual": 0.077,
      "fair_odds": 12.16
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "interval_10_away",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.907,
      "C1_ci": [
        0.313,
        1.501
      ],
      "C1": true,
      "C2_level": 0.0114,
      "C2_ci": [
        -0.0007,
        0.0228
      ],
      "C2": true,
      "C3_min_z": -1.54,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0014,
      "logloss_vs_book_ci": [
        -0.0028,
        -0.0001
      ],
      "mean_p": 0.0781,
      "actual": 0.0895,
      "fair_odds": 13.35
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "SERIEA",
    "market": "first_goal_home",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "first_goal_home",
      "n": 803,
      "status": "PASS",
      "C1_slope": 0.982,
      "C1_ci": [
        0.753,
        1.21
      ],
      "C1": true,
      "C2_level": -0.0144,
      "C2_ci": [
        -0.0467,
        0.0203
      ],
      "C2": true,
      "C3_min_z": -2.28,
      "C3": true,
      "C4_lifted_legs": 1,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0011,
      "logloss_vs_book_ci": [
        -0.0041,
        0.0018
      ],
      "mean_p": 0.4963,
      "actual": 0.4819,
      "fair_odds": 2.03
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "first_goal_home",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 1.021,
      "C1_ci": [
        0.868,
        1.174
      ],
      "C1": true,
      "C2_level": -0.005,
      "C2_ci": [
        -0.0264,
        0.0153
      ],
      "C2": true,
      "C3_min_z": -1.65,
      "C3": true,
      "C4_lifted_legs": 5,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0008,
      "logloss_vs_book_ci": [
        -0.0026,
        0.0009
      ],
      "mean_p": 0.5039,
      "actual": 0.4989,
      "fair_odds": 2.01
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "SERIEA",
    "market": "first_goal_away",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "first_goal_away",
      "n": 803,
      "status": "PASS",
      "C1_slope": 0.977,
      "C1_ci": [
        0.741,
        1.212
      ],
      "C1": true,
      "C2_level": 0.0151,
      "C2_ci": [
        -0.0212,
        0.0501
      ],
      "C2": true,
      "C3_min_z": -1.0,
      "C3": true,
      "C4_lifted_legs": 64,
      "C4_z": 1.72,
      "C4": true,
      "logloss_vs_book": -0.0007,
      "logloss_vs_book_ci": [
        -0.0032,
        0.0016
      ],
      "mean_p": 0.422,
      "actual": 0.4371,
      "fair_odds": 2.44
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "first_goal_away",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 1.05,
      "C1_ci": [
        0.89,
        1.21
      ],
      "C1": true,
      "C2_level": 0.0122,
      "C2_ci": [
        -0.0084,
        0.0309
      ],
      "C2": true,
      "C3_min_z": -1.16,
      "C3": true,
      "C4_lifted_legs": 48,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0004,
      "logloss_vs_book_ci": [
        -0.0018,
        0.0009
      ],
      "mean_p": 0.4299,
      "actual": 0.442,
      "fair_odds": 2.36
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "SERIEA",
    "market": "interval_10_home",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "interval_10_home",
      "n": 803,
      "status": "PASS",
      "C1_slope": 0.897,
      "C1_ci": [
        0.289,
        1.505
      ],
      "C1": true,
      "C2_level": 0.0211,
      "C2_ci": [
        -0.0015,
        0.045
      ],
      "C2": true,
      "C3_min_z": -0.98,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0015,
      "logloss_vs_book_ci": [
        -0.0028,
        -0.0002
      ],
      "mean_p": 0.1021,
      "actual": 0.1233,
      "fair_odds": 10.35
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "interval_10_home",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 0.709,
      "C1_ci": [
        0.344,
        1.074
      ],
      "C1": true,
      "C2_level": 0.0034,
      "C2_ci": [
        -0.0111,
        0.0189
      ],
      "C2": true,
      "C3_min_z": -0.85,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0003,
      "logloss_vs_book_ci": [
        -0.0004,
        0.001
      ],
      "mean_p": 0.1078,
      "actual": 0.1112,
      "fair_odds": 9.89
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "SERIEA",
    "market": "interval_10_draw",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "interval_10_draw",
      "n": 803,
      "status": "PASS",
      "C1_slope": 1.032,
      "C1_ci": [
        -1.065,
        3.13
      ],
      "C1": true,
      "C2_level": -0.0145,
      "C2_ci": [
        -0.0397,
        0.011
      ],
      "C2": true,
      "C3_min_z": -1.71,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0007,
      "logloss_vs_book_ci": [
        -0.0023,
        0.0009
      ],
      "mean_p": 0.8165,
      "actual": 0.802,
      "fair_odds": 1.22
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "interval_10_draw",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 0.936,
      "C1_ci": [
        -0.638,
        2.51
      ],
      "C1": true,
      "C2_level": -0.0018,
      "C2_ci": [
        -0.0208,
        0.0163
      ],
      "C2": true,
      "C3_min_z": -2.12,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0005,
      "logloss_vs_book_ci": [
        -0.0007,
        0.0016
      ],
      "mean_p": 0.8053,
      "actual": 0.8035,
      "fair_odds": 1.24
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "SERIEA",
    "market": "interval_10_away",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "interval_10_away",
      "n": 803,
      "status": "PASS",
      "C1_slope": 1.021,
      "C1_ci": [
        0.276,
        1.767
      ],
      "C1": true,
      "C2_level": -0.0022,
      "C2_ci": [
        -0.0191,
        0.0171
      ],
      "C2": true,
      "C3_min_z": -1.42,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0001,
      "logloss_vs_book_ci": [
        -0.0007,
        0.0006
      ],
      "mean_p": 0.077,
      "actual": 0.0747,
      "fair_odds": 13.94
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "interval_10_away",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 1.214,
      "C1_ci": [
        0.726,
        1.701
      ],
      "C1": true,
      "C2_level": 0.0024,
      "C2_ci": [
        -0.0099,
        0.0161
      ],
      "C2": true,
      "C3_min_z": -1.23,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0005,
      "logloss_vs_book_ci": [
        -0.0004,
        0.0014
      ],
      "mean_p": 0.083,
      "actual": 0.0854,
      "fair_odds": 12.59
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "BUNDES",
    "market": "first_goal_home",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "first_goal_home",
      "n": 638,
      "status": "PASS",
      "C1_slope": 1.221,
      "C1_ci": [
        0.899,
        1.543
      ],
      "C1": true,
      "C2_level": -0.0196,
      "C2_ci": [
        -0.0532,
        0.0138
      ],
      "C2": true,
      "C3_min_z": -1.91,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0008,
      "logloss_vs_book_ci": [
        -0.0007,
        0.0023
      ],
      "mean_p": 0.5353,
      "actual": 0.5157,
      "fair_odds": 1.89
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "first_goal_home",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.028,
      "C1_ci": [
        0.833,
        1.222
      ],
      "C1": true,
      "C2_level": -0.013,
      "C2_ci": [
        -0.0376,
        0.012
      ],
      "C2": true,
      "C3_min_z": -1.63,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0013,
      "logloss_vs_book_ci": [
        -0.0004,
        0.0031
      ],
      "mean_p": 0.5346,
      "actual": 0.5216,
      "fair_odds": 1.88
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "BUNDES",
    "market": "first_goal_away",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "first_goal_away",
      "n": 638,
      "status": "PASS",
      "C1_slope": 1.109,
      "C1_ci": [
        0.797,
        1.42
      ],
      "C1": true,
      "C2_level": 0.0111,
      "C2_ci": [
        -0.0231,
        0.0401
      ],
      "C2": true,
      "C3_min_z": -1.28,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0003,
      "logloss_vs_book_ci": [
        -0.0018,
        0.0027
      ],
      "mean_p": 0.4137,
      "actual": 0.4248,
      "fair_odds": 2.44
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "first_goal_away",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.079,
      "C1_ci": [
        0.881,
        1.277
      ],
      "C1": true,
      "C2_level": 0.0187,
      "C2_ci": [
        -0.0065,
        0.0422
      ],
      "C2": true,
      "C3_min_z": -2.85,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0017,
      "logloss_vs_book_ci": [
        -0.0006,
        0.0041
      ],
      "mean_p": 0.4114,
      "actual": 0.4301,
      "fair_odds": 2.48
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "BUNDES",
    "market": "interval_10_home",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "interval_10_home",
      "n": 638,
      "status": "PASS",
      "C1_slope": 1.14,
      "C1_ci": [
        0.285,
        1.996
      ],
      "C1": true,
      "C2_level": -0.0215,
      "C2_ci": [
        -0.0458,
        0.0023
      ],
      "C2": true,
      "C3_min_z": -1.26,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0025,
      "logloss_vs_book_ci": [
        -0.0003,
        0.0054
      ],
      "mean_p": 0.1328,
      "actual": 0.1113,
      "fair_odds": 7.9
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "interval_10_home",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 0.87,
      "C1_ci": [
        0.394,
        1.346
      ],
      "C1": true,
      "C2_level": 0.0039,
      "C2_ci": [
        -0.0119,
        0.0194
      ],
      "C2": true,
      "C3_min_z": -0.77,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0016,
      "logloss_vs_book_ci": [
        -0.0039,
        0.0009
      ],
      "mean_p": 0.1269,
      "actual": 0.1307,
      "fair_odds": 8.22
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "BUNDES",
    "market": "interval_10_draw",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "interval_10_draw",
      "n": 638,
      "status": "PASS",
      "C1_slope": 1.003,
      "C1_ci": [
        -0.44,
        2.446
      ],
      "C1": true,
      "C2_level": 0.0353,
      "C2_ci": [
        0.0034,
        0.0661
      ],
      "C2": true,
      "C3_min_z": -1.17,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0032,
      "logloss_vs_book_ci": [
        -0.0007,
        0.0069
      ],
      "mean_p": 0.7656,
      "actual": 0.8009,
      "fair_odds": 1.3
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "interval_10_draw",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 0.596,
      "C1_ci": [
        -0.128,
        1.32
      ],
      "C1": true,
      "C2_level": -0.0166,
      "C2_ci": [
        -0.0365,
        0.0026
      ],
      "C2": true,
      "C3_min_z": -1.62,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0017,
      "logloss_vs_book_ci": [
        -0.0039,
        0.0006
      ],
      "mean_p": 0.7774,
      "actual": 0.7608,
      "fair_odds": 1.28
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "BUNDES",
    "market": "interval_10_away",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "interval_10_away",
      "n": 638,
      "status": "PASS",
      "C1_slope": 0.838,
      "C1_ci": [
        -0.195,
        1.87
      ],
      "C1": true,
      "C2_level": -0.0111,
      "C2_ci": [
        -0.0316,
        0.0099
      ],
      "C2": true,
      "C3_min_z": -1.61,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0003,
      "logloss_vs_book_ci": [
        -0.0027,
        0.0018
      ],
      "mean_p": 0.0989,
      "actual": 0.0878,
      "fair_odds": 10.51
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "interval_10_away",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.157,
      "C1_ci": [
        0.459,
        1.855
      ],
      "C1": true,
      "C2_level": 0.0185,
      "C2_ci": [
        0.0047,
        0.0325
      ],
      "C2": true,
      "C3_min_z": -0.92,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0018,
      "logloss_vs_book_ci": [
        -0.0013,
        0.0048
      ],
      "mean_p": 0.09,
      "actual": 0.1085,
      "fair_odds": 11.43
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LIGUE1",
    "market": "first_goal_home",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "first_goal_home",
      "n": 638,
      "status": "PASS",
      "C1_slope": 1.135,
      "C1_ci": [
        0.844,
        1.425
      ],
      "C1": true,
      "C2_level": -0.0105,
      "C2_ci": [
        -0.0505,
        0.0299
      ],
      "C2": true,
      "C3_min_z": -1.78,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.002,
      "logloss_vs_book_ci": [
        -0.0044,
        0.0003
      ],
      "mean_p": 0.5089,
      "actual": 0.4984,
      "fair_odds": 1.96
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "first_goal_home",
      "n": 1725,
      "status": "FAIL",
      "C1_slope": 1.039,
      "C1_ci": [
        0.854,
        1.224
      ],
      "C1": true,
      "C2_level": -0.0298,
      "C2_ci": [
        -0.0516,
        -0.0066
      ],
      "C2": false,
      "C3_min_z": -2.36,
      "C3": true,
      "C4_lifted_legs": 49,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0004,
      "logloss_vs_book_ci": [
        -0.001,
        0.0019
      ],
      "mean_p": 0.5208,
      "actual": 0.491,
      "fair_odds": 1.92
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "league": "LIGUE1",
    "market": "first_goal_away",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "first_goal_away",
      "n": 638,
      "status": "PASS",
      "C1_slope": 1.068,
      "C1_ci": [
        0.772,
        1.364
      ],
      "C1": true,
      "C2_level": 0.0008,
      "C2_ci": [
        -0.0362,
        0.0438
      ],
      "C2": true,
      "C3_min_z": -1.43,
      "C3": true,
      "C4_lifted_legs": 17,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0009,
      "logloss_vs_book_ci": [
        -0.0034,
        0.0016
      ],
      "mean_p": 0.4349,
      "actual": 0.4357,
      "fair_odds": 2.35
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "first_goal_away",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 0.95,
      "C1_ci": [
        0.769,
        1.131
      ],
      "C1": true,
      "C2_level": 0.022,
      "C2_ci": [
        -0.0002,
        0.0452
      ],
      "C2": true,
      "C3_min_z": -2.06,
      "C3": true,
      "C4_lifted_legs": 11,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0005,
      "logloss_vs_book_ci": [
        -0.0009,
        0.0018
      ],
      "mean_p": 0.4151,
      "actual": 0.4371,
      "fair_odds": 2.49
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LIGUE1",
    "market": "interval_10_home",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "interval_10_home",
      "n": 638,
      "status": "PASS",
      "C1_slope": 0.985,
      "C1_ci": [
        0.217,
        1.753
      ],
      "C1": true,
      "C2_level": -0.0078,
      "C2_ci": [
        -0.0311,
        0.0168
      ],
      "C2": true,
      "C3_min_z": -1.22,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0001,
      "logloss_vs_book_ci": [
        -0.0002,
        0.0003
      ],
      "mean_p": 0.1113,
      "actual": 0.1034,
      "fair_odds": 9.42
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "interval_10_home",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 0.974,
      "C1_ci": [
        0.521,
        1.426
      ],
      "C1": true,
      "C2_level": 0.0095,
      "C2_ci": [
        -0.0043,
        0.0245
      ],
      "C2": true,
      "C3_min_z": -0.98,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0004,
      "logloss_vs_book_ci": [
        -0.0004,
        0.0012
      ],
      "mean_p": 0.0995,
      "actual": 0.109,
      "fair_odds": 10.62
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LIGUE1",
    "market": "interval_10_draw",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "interval_10_draw",
      "n": 638,
      "status": "PASS",
      "C1_slope": 0.816,
      "C1_ci": [
        -0.851,
        2.482
      ],
      "C1": true,
      "C2_level": 0.0003,
      "C2_ci": [
        -0.0318,
        0.0312
      ],
      "C2": true,
      "C3_min_z": -1.5,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0007,
        0.001
      ],
      "mean_p": 0.7959,
      "actual": 0.7962,
      "fair_odds": 1.25
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "interval_10_draw",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 1.778,
      "C1_ci": [
        0.539,
        3.016
      ],
      "C1": true,
      "C2_level": -0.0154,
      "C2_ci": [
        -0.0335,
        0.0022
      ],
      "C2": true,
      "C3_min_z": -2.36,
      "C3": true,
      "C4_lifted_legs": 23,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0006,
      "logloss_vs_book_ci": [
        -0.0005,
        0.0018
      ],
      "mean_p": 0.8194,
      "actual": 0.8041,
      "fair_odds": 1.22
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LIGUE1",
    "market": "interval_10_away",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "interval_10_away",
      "n": 638,
      "status": "PASS",
      "C1_slope": 0.897,
      "C1_ci": [
        0.28,
        1.514
      ],
      "C1": true,
      "C2_level": 0.0047,
      "C2_ci": [
        -0.0167,
        0.0274
      ],
      "C2": true,
      "C3_min_z": -0.84,
      "C3": true,
      "C4_lifted_legs": 13,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0003,
      "logloss_vs_book_ci": [
        -0.0025,
        0.0019
      ],
      "mean_p": 0.0957,
      "actual": 0.1003,
      "fair_odds": 11.33
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "interval_10_away",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 0.843,
      "C1_ci": [
        0.463,
        1.223
      ],
      "C1": true,
      "C2_level": 0.0032,
      "C2_ci": [
        -0.0096,
        0.0165
      ],
      "C2": true,
      "C3_min_z": -1.57,
      "C3": true,
      "C4_lifted_legs": 25,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0004,
      "logloss_vs_book_ci": [
        -0.0008,
        0.0016
      ],
      "mean_p": 0.0838,
      "actual": 0.087,
      "fair_odds": 13.27
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "EPL",
    "market": "home_score_both_halves",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "home_score_both_halves",
      "n": 830,
      "status": "PASS",
      "C1_slope": 0.758,
      "C1_ci": [
        0.49,
        1.026
      ],
      "C1": true,
      "C2_level": -0.0133,
      "C2_ci": [
        -0.0433,
        0.0176
      ],
      "C2": true,
      "C3_min_z": -1.86,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0007,
      "logloss_vs_book_ci": [
        -0.0002,
        0.0016
      ],
      "mean_p": 0.3025,
      "actual": 0.2892,
      "fair_odds": 3.46
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "home_score_both_halves",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.994,
      "C1_ci": [
        0.832,
        1.156
      ],
      "C1": true,
      "C2_level": 0.0018,
      "C2_ci": [
        -0.0188,
        0.0234
      ],
      "C2": true,
      "C3_min_z": -1.19,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0005,
      "logloss_vs_book_ci": [
        -0.0003,
        0.0014
      ],
      "mean_p": 0.285,
      "actual": 0.2868,
      "fair_odds": 3.86
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "EPL",
    "market": "away_score_both_halves",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "away_score_both_halves",
      "n": 830,
      "status": "PASS",
      "C1_slope": 0.843,
      "C1_ci": [
        0.537,
        1.149
      ],
      "C1": true,
      "C2_level": -0.0247,
      "C2_ci": [
        -0.0513,
        0.0032
      ],
      "C2": true,
      "C3_min_z": -1.55,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0008,
      "logloss_vs_book_ci": [
        -0.0006,
        0.0023
      ],
      "mean_p": 0.2415,
      "actual": 0.2169,
      "fair_odds": 4.45
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "away_score_both_halves",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.977,
      "C1_ci": [
        0.801,
        1.153
      ],
      "C1": true,
      "C2_level": 0.0082,
      "C2_ci": [
        -0.0095,
        0.0263
      ],
      "C2": true,
      "C3_min_z": -1.5,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0002,
      "logloss_vs_book_ci": [
        -0.001,
        0.0006
      ],
      "mean_p": 0.2302,
      "actual": 0.2384,
      "fair_odds": 4.82
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "EPL",
    "market": "home_win_both_halves",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "home_win_both_halves",
      "n": 830,
      "status": "PASS",
      "C1_slope": 0.786,
      "C1_ci": [
        0.521,
        1.051
      ],
      "C1": true,
      "C2_level": -0.0169,
      "C2_ci": [
        -0.0392,
        0.0073
      ],
      "C2": true,
      "C3_min_z": -1.78,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0008,
        0.0012
      ],
      "mean_p": 0.1434,
      "actual": 0.1265,
      "fair_odds": 8.67
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "home_win_both_halves",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.934,
      "C1_ci": [
        0.78,
        1.087
      ],
      "C1": true,
      "C2_level": -0.0065,
      "C2_ci": [
        -0.0199,
        0.0087
      ],
      "C2": true,
      "C3_min_z": -1.61,
      "C3": true,
      "C4_lifted_legs": 30,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0005,
      "logloss_vs_book_ci": [
        -0.0006,
        0.0016
      ],
      "mean_p": 0.147,
      "actual": 0.1405,
      "fair_odds": 9.04
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "EPL",
    "market": "away_win_both_halves",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "away_win_both_halves",
      "n": 830,
      "status": "PASS",
      "C1_slope": 1.015,
      "C1_ci": [
        0.66,
        1.369
      ],
      "C1": true,
      "C2_level": -0.0172,
      "C2_ci": [
        -0.0343,
        0.0025
      ],
      "C2": true,
      "C3_min_z": -2.48,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0004,
      "logloss_vs_book_ci": [
        -0.0006,
        0.0014
      ],
      "mean_p": 0.0919,
      "actual": 0.0747,
      "fair_odds": 13.57
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "away_win_both_halves",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.939,
      "C1_ci": [
        0.75,
        1.128
      ],
      "C1": true,
      "C2_level": -0.0005,
      "C2_ci": [
        -0.013,
        0.0107
      ],
      "C2": true,
      "C3_min_z": -1.59,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0007,
        0.001
      ],
      "mean_p": 0.0963,
      "actual": 0.0958,
      "fair_odds": 13.66
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "EPL",
    "market": "home_fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "home_fh_over_0.5",
      "n": 830,
      "status": "PASS",
      "C1_slope": 1.098,
      "C1_ci": [
        0.761,
        1.436
      ],
      "C1": true,
      "C2_level": 0.01,
      "C2_ci": [
        -0.0241,
        0.046
      ],
      "C2": true,
      "C3_min_z": -0.91,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0001,
      "logloss_vs_book_ci": [
        -0.0005,
        0.0002
      ],
      "mean_p": 0.5081,
      "actual": 0.5181,
      "fair_odds": 1.98
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "home_fh_over_0.5",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.027,
      "C1_ci": [
        0.829,
        1.225
      ],
      "C1": true,
      "C2_level": 0.021,
      "C2_ci": [
        -0.0001,
        0.0435
      ],
      "C2": true,
      "C3_min_z": -1.11,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0006,
      "logloss_vs_book_ci": [
        -0.0003,
        0.0015
      ],
      "mean_p": 0.4816,
      "actual": 0.5026,
      "fair_odds": 2.12
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "EPL",
    "market": "away_fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "away_fh_over_0.5",
      "n": 830,
      "status": "PASS",
      "C1_slope": 0.844,
      "C1_ci": [
        0.512,
        1.176
      ],
      "C1": true,
      "C2_level": -0.0316,
      "C2_ci": [
        -0.0652,
        0.0037
      ],
      "C2": true,
      "C3_min_z": -2.29,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0001,
      "logloss_vs_book_ci": [
        -0.0005,
        0.0008
      ],
      "mean_p": 0.4376,
      "actual": 0.406,
      "fair_odds": 2.33
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "away_fh_over_0.5",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.89,
      "C1_ci": [
        0.703,
        1.077
      ],
      "C1": true,
      "C2_level": 0.0099,
      "C2_ci": [
        -0.0121,
        0.0318
      ],
      "C2": true,
      "C3_min_z": -1.67,
      "C3": true,
      "C4_lifted_legs": 2,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0006,
      "logloss_vs_book_ci": [
        -0.0004,
        0.0017
      ],
      "mean_p": 0.4233,
      "actual": 0.4332,
      "fair_odds": 2.44
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "EPL",
    "market": "home_sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "home_sh_over_0.5",
      "n": 830,
      "status": "FAIL",
      "C1_slope": 0.763,
      "C1_ci": [
        0.468,
        1.058
      ],
      "C1": true,
      "C2_level": -0.0508,
      "C2_ci": [
        -0.0842,
        -0.0158
      ],
      "C2": false,
      "C3_min_z": -3.33,
      "C3": false,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0026,
      "logloss_vs_book_ci": [
        0.0011,
        0.0041
      ],
      "mean_p": 0.5845,
      "actual": 0.5337,
      "fair_odds": 1.71
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "home_sh_over_0.5",
      "n": 1900,
      "status": "FAIL",
      "C1_slope": 0.964,
      "C1_ci": [
        0.782,
        1.147
      ],
      "C1": true,
      "C2_level": -0.0212,
      "C2_ci": [
        -0.044,
        0.001
      ],
      "C2": true,
      "C3_min_z": -1.68,
      "C3": true,
      "C4_lifted_legs": 256,
      "C4_z": -2.86,
      "C4": false,
      "logloss_vs_book": 0.003,
      "logloss_vs_book_ci": [
        0.001,
        0.0049
      ],
      "mean_p": 0.5749,
      "actual": 0.5537,
      "fair_odds": 1.76
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "league": "EPL",
    "market": "away_sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "away_sh_over_0.5",
      "n": 830,
      "status": "PASS",
      "C1_slope": 0.885,
      "C1_ci": [
        0.538,
        1.233
      ],
      "C1": true,
      "C2_level": 0.0369,
      "C2_ci": [
        0.0019,
        0.072
      ],
      "C2": true,
      "C3_min_z": -0.09,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0022,
      "logloss_vs_book_ci": [
        -0.0042,
        -0.0004
      ],
      "mean_p": 0.5174,
      "actual": 0.5542,
      "fair_odds": 1.96
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "away_sh_over_0.5",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.016,
      "C1_ci": [
        0.807,
        1.225
      ],
      "C1": true,
      "C2_level": 0.0084,
      "C2_ci": [
        -0.0123,
        0.0311
      ],
      "C2": true,
      "C3_min_z": -0.99,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0007,
        0.0011
      ],
      "mean_p": 0.4974,
      "actual": 0.5058,
      "fair_odds": 2.05
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LALIGA",
    "market": "home_score_both_halves",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "home_score_both_halves",
      "n": 849,
      "status": "PASS",
      "C1_slope": 1.406,
      "C1_ci": [
        1.124,
        1.689
      ],
      "C1": true,
      "C2_level": -0.0089,
      "C2_ci": [
        -0.0341,
        0.0175
      ],
      "C2": true,
      "C3_min_z": -2.34,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0009,
      "logloss_vs_book_ci": [
        -0.0016,
        -0.0002
      ],
      "mean_p": 0.268,
      "actual": 0.2591,
      "fair_odds": 4.27
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "home_score_both_halves",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.014,
      "C1_ci": [
        0.821,
        1.207
      ],
      "C1": true,
      "C2_level": -0.0022,
      "C2_ci": [
        -0.0191,
        0.0151
      ],
      "C2": true,
      "C3_min_z": -1.04,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0,
        0.0003
      ],
      "mean_p": 0.2575,
      "actual": 0.2553,
      "fair_odds": 4.25
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LALIGA",
    "market": "away_score_both_halves",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "away_score_both_halves",
      "n": 849,
      "status": "PASS",
      "C1_slope": 0.836,
      "C1_ci": [
        0.556,
        1.116
      ],
      "C1": true,
      "C2_level": -0.0016,
      "C2_ci": [
        -0.0249,
        0.0224
      ],
      "C2": true,
      "C3_min_z": -0.97,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0004,
      "logloss_vs_book_ci": [
        -0.0,
        0.0007
      ],
      "mean_p": 0.19,
      "actual": 0.1885,
      "fair_odds": 6.08
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "away_score_both_halves",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.898,
      "C1_ci": [
        0.694,
        1.101
      ],
      "C1": true,
      "C2_level": 0.0012,
      "C2_ci": [
        -0.0144,
        0.0182
      ],
      "C2": true,
      "C3_min_z": -0.95,
      "C3": true,
      "C4_lifted_legs": 3,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0007,
      "logloss_vs_book_ci": [
        0.0001,
        0.0013
      ],
      "mean_p": 0.1793,
      "actual": 0.1805,
      "fair_odds": 6.31
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LALIGA",
    "market": "home_win_both_halves",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "home_win_both_halves",
      "n": 849,
      "status": "PASS",
      "C1_slope": 1.401,
      "C1_ci": [
        1.101,
        1.702
      ],
      "C1": true,
      "C2_level": -0.0043,
      "C2_ci": [
        -0.0258,
        0.0166
      ],
      "C2": true,
      "C3_min_z": -1.88,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0036,
      "logloss_vs_book_ci": [
        -0.0073,
        -0.0001
      ],
      "mean_p": 0.1209,
      "actual": 0.1166,
      "fair_odds": 10.96
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "home_win_both_halves",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.135,
      "C1_ci": [
        0.927,
        1.343
      ],
      "C1": true,
      "C2_level": 0.0015,
      "C2_ci": [
        -0.0118,
        0.0157
      ],
      "C2": true,
      "C3_min_z": -1.61,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0012,
      "logloss_vs_book_ci": [
        -0.0036,
        0.0014
      ],
      "mean_p": 0.1159,
      "actual": 0.1174,
      "fair_odds": 10.49
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LALIGA",
    "market": "away_win_both_halves",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "away_win_both_halves",
      "n": 849,
      "status": "FAIL",
      "C1_slope": 0.984,
      "C1_ci": [
        0.657,
        1.311
      ],
      "C1": true,
      "C2_level": -0.0153,
      "C2_ci": [
        -0.0288,
        -0.0001
      ],
      "C2": false,
      "C3_min_z": -2.17,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.002,
      "logloss_vs_book_ci": [
        -0.0039,
        0.0003
      ],
      "mean_p": 0.0695,
      "actual": 0.0542,
      "fair_odds": 20.74
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "away_win_both_halves",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.981,
      "C1_ci": [
        0.765,
        1.197
      ],
      "C1": true,
      "C2_level": -0.0006,
      "C2_ci": [
        -0.0112,
        0.0097
      ],
      "C2": true,
      "C3_min_z": -1.53,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0001,
      "logloss_vs_book_ci": [
        -0.0015,
        0.0013
      ],
      "mean_p": 0.068,
      "actual": 0.0674,
      "fair_odds": 20.12
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "league": "LALIGA",
    "market": "home_fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "home_fh_over_0.5",
      "n": 849,
      "status": "PASS",
      "C1_slope": 1.345,
      "C1_ci": [
        0.995,
        1.695
      ],
      "C1": true,
      "C2_level": 0.0216,
      "C2_ci": [
        -0.0091,
        0.0523
      ],
      "C2": true,
      "C3_min_z": -1.47,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0,
      "logloss_vs_book_ci": [
        -0.0003,
        0.0003
      ],
      "mean_p": 0.4684,
      "actual": 0.49,
      "fair_odds": 2.24
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "home_fh_over_0.5",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.891,
      "C1_ci": [
        0.671,
        1.112
      ],
      "C1": true,
      "C2_level": 0.0177,
      "C2_ci": [
        -0.0025,
        0.0393
      ],
      "C2": true,
      "C3_min_z": -1.17,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0007,
      "logloss_vs_book_ci": [
        -0.0004,
        0.0019
      ],
      "mean_p": 0.4444,
      "actual": 0.4621,
      "fair_odds": 2.32
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LALIGA",
    "market": "away_fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "away_fh_over_0.5",
      "n": 849,
      "status": "PASS",
      "C1_slope": 0.931,
      "C1_ci": [
        0.59,
        1.272
      ],
      "C1": true,
      "C2_level": -0.0017,
      "C2_ci": [
        -0.0305,
        0.0278
      ],
      "C2": true,
      "C3_min_z": -1.33,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0001,
      "logloss_vs_book_ci": [
        -0.0003,
        0.0004
      ],
      "mean_p": 0.3845,
      "actual": 0.3828,
      "fair_odds": 2.73
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "away_fh_over_0.5",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.917,
      "C1_ci": [
        0.677,
        1.156
      ],
      "C1": true,
      "C2_level": 0.0099,
      "C2_ci": [
        -0.0106,
        0.0294
      ],
      "C2": true,
      "C3_min_z": -1.2,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0006,
      "logloss_vs_book_ci": [
        -0.0002,
        0.0013
      ],
      "mean_p": 0.3706,
      "actual": 0.3805,
      "fair_odds": 2.8
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LALIGA",
    "market": "home_sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "home_sh_over_0.5",
      "n": 849,
      "status": "PASS",
      "C1_slope": 1.036,
      "C1_ci": [
        0.732,
        1.34
      ],
      "C1": true,
      "C2_level": 0.0116,
      "C2_ci": [
        -0.022,
        0.0423
      ],
      "C2": true,
      "C3_min_z": -1.92,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0012,
      "logloss_vs_book_ci": [
        -0.0032,
        0.0009
      ],
      "mean_p": 0.5632,
      "actual": 0.5748,
      "fair_odds": 1.84
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "home_sh_over_0.5",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.246,
      "C1_ci": [
        1.016,
        1.477
      ],
      "C1": true,
      "C2_level": -0.015,
      "C2_ci": [
        -0.037,
        0.0076
      ],
      "C2": true,
      "C3_min_z": -2.02,
      "C3": true,
      "C4_lifted_legs": 178,
      "C4_z": -1.57,
      "C4": true,
      "logloss_vs_book": 0.0005,
      "logloss_vs_book_ci": [
        -0.0016,
        0.0026
      ],
      "mean_p": 0.5629,
      "actual": 0.5479,
      "fair_odds": 1.81
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LALIGA",
    "market": "away_sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "away_sh_over_0.5",
      "n": 849,
      "status": "PASS",
      "C1_slope": 0.898,
      "C1_ci": [
        0.599,
        1.197
      ],
      "C1": true,
      "C2_level": 0.0316,
      "C2_ci": [
        -0.0018,
        0.0646
      ],
      "C2": true,
      "C3_min_z": -0.39,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0016,
      "logloss_vs_book_ci": [
        -0.0036,
        0.0006
      ],
      "mean_p": 0.4749,
      "actual": 0.5065,
      "fair_odds": 2.19
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "away_sh_over_0.5",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.99,
      "C1_ci": [
        0.774,
        1.207
      ],
      "C1": true,
      "C2_level": -0.0093,
      "C2_ci": [
        -0.0301,
        0.0116
      ],
      "C2": true,
      "C3_min_z": -1.36,
      "C3": true,
      "C4_lifted_legs": 45,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0005,
      "logloss_vs_book_ci": [
        -0.0008,
        0.0018
      ],
      "mean_p": 0.4688,
      "actual": 0.4595,
      "fair_odds": 2.19
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "SERIEA",
    "market": "home_score_both_halves",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "home_score_both_halves",
      "n": 830,
      "status": "PASS",
      "C1_slope": 0.979,
      "C1_ci": [
        0.707,
        1.251
      ],
      "C1": true,
      "C2_level": -0.0125,
      "C2_ci": [
        -0.0424,
        0.0185
      ],
      "C2": true,
      "C3_min_z": -2.06,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0,
      "logloss_vs_book_ci": [
        -0.0011,
        0.001
      ],
      "mean_p": 0.2522,
      "actual": 0.2398,
      "fair_odds": 4.4
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "home_score_both_halves",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 1.13,
      "C1_ci": [
        0.947,
        1.312
      ],
      "C1": true,
      "C2_level": -0.0052,
      "C2_ci": [
        -0.024,
        0.0153
      ],
      "C2": true,
      "C3_min_z": -2.07,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0004,
        0.0008
      ],
      "mean_p": 0.2849,
      "actual": 0.2798,
      "fair_odds": 3.79
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "SERIEA",
    "market": "away_score_both_halves",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "away_score_both_halves",
      "n": 830,
      "status": "PASS",
      "C1_slope": 0.735,
      "C1_ci": [
        0.474,
        0.996
      ],
      "C1": true,
      "C2_level": 0.0211,
      "C2_ci": [
        -0.0047,
        0.0484
      ],
      "C2": true,
      "C3_min_z": -0.44,
      "C3": true,
      "C4_lifted_legs": 4,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0015,
      "logloss_vs_book_ci": [
        -0.0001,
        0.003
      ],
      "mean_p": 0.191,
      "actual": 0.212,
      "fair_odds": 6.08
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "away_score_both_halves",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 0.944,
      "C1_ci": [
        0.768,
        1.121
      ],
      "C1": true,
      "C2_level": 0.0224,
      "C2_ci": [
        0.0033,
        0.0417
      ],
      "C2": true,
      "C3_min_z": -0.73,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0023,
      "logloss_vs_book_ci": [
        0.0007,
        0.004
      ],
      "mean_p": 0.2147,
      "actual": 0.2371,
      "fair_odds": 5.2
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "SERIEA",
    "market": "home_win_both_halves",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "home_win_both_halves",
      "n": 830,
      "status": "PASS",
      "C1_slope": 1.038,
      "C1_ci": [
        0.743,
        1.332
      ],
      "C1": true,
      "C2_level": -0.0173,
      "C2_ci": [
        -0.0377,
        0.0041
      ],
      "C2": true,
      "C3_min_z": -2.56,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0027,
      "logloss_vs_book_ci": [
        -0.0052,
        -0.0001
      ],
      "mean_p": 0.1197,
      "actual": 0.1024,
      "fair_odds": 10.72
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "home_win_both_halves",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 1.125,
      "C1_ci": [
        0.94,
        1.309
      ],
      "C1": true,
      "C2_level": 0.004,
      "C2_ci": [
        -0.01,
        0.0187
      ],
      "C2": true,
      "C3_min_z": -1.17,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0003,
      "logloss_vs_book_ci": [
        -0.0021,
        0.0017
      ],
      "mean_p": 0.1267,
      "actual": 0.1307,
      "fair_odds": 9.99
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "SERIEA",
    "market": "away_win_both_halves",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "away_win_both_halves",
      "n": 830,
      "status": "PASS",
      "C1_slope": 0.896,
      "C1_ci": [
        0.612,
        1.18
      ],
      "C1": true,
      "C2_level": 0.0095,
      "C2_ci": [
        -0.0085,
        0.0289
      ],
      "C2": true,
      "C3_min_z": -0.94,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0009,
      "logloss_vs_book_ci": [
        -0.0013,
        0.0032
      ],
      "mean_p": 0.0772,
      "actual": 0.0867,
      "fair_odds": 18.43
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "away_win_both_halves",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 1.013,
      "C1_ci": [
        0.808,
        1.218
      ],
      "C1": true,
      "C2_level": 0.0024,
      "C2_ci": [
        -0.01,
        0.0136
      ],
      "C2": true,
      "C3_min_z": -1.07,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0001,
      "logloss_vs_book_ci": [
        -0.0012,
        0.0016
      ],
      "mean_p": 0.0829,
      "actual": 0.0854,
      "fair_odds": 16.13
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "SERIEA",
    "market": "home_fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "home_fh_over_0.5",
      "n": 830,
      "status": "PASS",
      "C1_slope": 1.277,
      "C1_ci": [
        0.942,
        1.611
      ],
      "C1": true,
      "C2_level": -0.024,
      "C2_ci": [
        -0.0566,
        0.0079
      ],
      "C2": true,
      "C3_min_z": -1.61,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0005,
      "logloss_vs_book_ci": [
        -0.0011,
        0.0002
      ],
      "mean_p": 0.4505,
      "actual": 0.4265,
      "fair_odds": 2.29
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "home_fh_over_0.5",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 1.133,
      "C1_ci": [
        0.903,
        1.363
      ],
      "C1": true,
      "C2_level": 0.0112,
      "C2_ci": [
        -0.0109,
        0.0326
      ],
      "C2": true,
      "C3_min_z": -1.07,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0003,
      "logloss_vs_book_ci": [
        -0.0002,
        0.0009
      ],
      "mean_p": 0.4767,
      "actual": 0.4879,
      "fair_odds": 2.14
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "SERIEA",
    "market": "away_fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "away_fh_over_0.5",
      "n": 830,
      "status": "PASS",
      "C1_slope": 0.796,
      "C1_ci": [
        0.465,
        1.127
      ],
      "C1": true,
      "C2_level": 0.0188,
      "C2_ci": [
        -0.0131,
        0.0559
      ],
      "C2": true,
      "C3_min_z": -1.28,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0001,
      "logloss_vs_book_ci": [
        -0.0011,
        0.0009
      ],
      "mean_p": 0.3956,
      "actual": 0.4145,
      "fair_odds": 2.63
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "away_fh_over_0.5",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 1.157,
      "C1_ci": [
        0.92,
        1.395
      ],
      "C1": true,
      "C2_level": 0.0225,
      "C2_ci": [
        0.0008,
        0.0427
      ],
      "C2": true,
      "C3_min_z": -0.92,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.001,
      "logloss_vs_book_ci": [
        0.0001,
        0.0019
      ],
      "mean_p": 0.4169,
      "actual": 0.4394,
      "fair_odds": 2.46
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "SERIEA",
    "market": "home_sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "home_sh_over_0.5",
      "n": 830,
      "status": "PASS",
      "C1_slope": 1.06,
      "C1_ci": [
        0.774,
        1.346
      ],
      "C1": true,
      "C2_level": -0.0177,
      "C2_ci": [
        -0.0501,
        0.0133
      ],
      "C2": true,
      "C3_min_z": -2.49,
      "C3": true,
      "C4_lifted_legs": 43,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0001,
      "logloss_vs_book_ci": [
        -0.0026,
        0.0024
      ],
      "mean_p": 0.5478,
      "actual": 0.5301,
      "fair_odds": 1.86
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "home_sh_over_0.5",
      "n": 1898,
      "status": "FAIL",
      "C1_slope": 0.864,
      "C1_ci": [
        0.686,
        1.043
      ],
      "C1": true,
      "C2_level": -0.0084,
      "C2_ci": [
        -0.0316,
        0.0133
      ],
      "C2": true,
      "C3_min_z": -1.71,
      "C3": true,
      "C4_lifted_legs": 493,
      "C4_z": -2.38,
      "C4": false,
      "logloss_vs_book": 0.0009,
      "logloss_vs_book_ci": [
        -0.0018,
        0.0036
      ],
      "mean_p": 0.5848,
      "actual": 0.5764,
      "fair_odds": 1.73
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "league": "SERIEA",
    "market": "away_sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "away_sh_over_0.5",
      "n": 830,
      "status": "PASS",
      "C1_slope": 1.005,
      "C1_ci": [
        0.717,
        1.294
      ],
      "C1": true,
      "C2_level": 0.0148,
      "C2_ci": [
        -0.0186,
        0.0472
      ],
      "C2": true,
      "C3_min_z": -0.55,
      "C3": true,
      "C4_lifted_legs": 120,
      "C4_z": 0.86,
      "C4": true,
      "logloss_vs_book": -0.0016,
      "logloss_vs_book_ci": [
        -0.0042,
        0.001
      ],
      "mean_p": 0.4792,
      "actual": 0.494,
      "fair_odds": 2.16
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "away_sh_over_0.5",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 1.049,
      "C1_ci": [
        0.854,
        1.244
      ],
      "C1": true,
      "C2_level": -0.0009,
      "C2_ci": [
        -0.0225,
        0.0198
      ],
      "C2": true,
      "C3_min_z": -1.77,
      "C3": true,
      "C4_lifted_legs": 240,
      "C4_z": -0.47,
      "C4": true,
      "logloss_vs_book": -0.0008,
      "logloss_vs_book_ci": [
        -0.0026,
        0.0013
      ],
      "mean_p": 0.5193,
      "actual": 0.5184,
      "fair_odds": 1.95
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "BUNDES",
    "market": "home_score_both_halves",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "home_score_both_halves",
      "n": 665,
      "status": "PASS",
      "C1_slope": 1.325,
      "C1_ci": [
        0.994,
        1.657
      ],
      "C1": true,
      "C2_level": 0.0199,
      "C2_ci": [
        -0.0168,
        0.0591
      ],
      "C2": true,
      "C3_min_z": -1.12,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0012,
      "logloss_vs_book_ci": [
        -0.0032,
        0.0009
      ],
      "mean_p": 0.341,
      "actual": 0.3609,
      "fair_odds": 3.16
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "home_score_both_halves",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.046,
      "C1_ci": [
        0.84,
        1.253
      ],
      "C1": true,
      "C2_level": 0.0067,
      "C2_ci": [
        -0.0189,
        0.0307
      ],
      "C2": true,
      "C3_min_z": -0.92,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0001,
      "logloss_vs_book_ci": [
        -0.0013,
        0.001
      ],
      "mean_p": 0.326,
      "actual": 0.3327,
      "fair_odds": 3.29
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "BUNDES",
    "market": "away_score_both_halves",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "away_score_both_halves",
      "n": 665,
      "status": "PASS",
      "C1_slope": 1.013,
      "C1_ci": [
        0.715,
        1.311
      ],
      "C1": true,
      "C2_level": 0.0326,
      "C2_ci": [
        -0.0003,
        0.0655
      ],
      "C2": true,
      "C3_min_z": -0.71,
      "C3": true,
      "C4_lifted_legs": 18,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.001,
      "logloss_vs_book_ci": [
        -0.003,
        0.001
      ],
      "mean_p": 0.2577,
      "actual": 0.2902,
      "fair_odds": 4.25
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "away_score_both_halves",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.286,
      "C1_ci": [
        1.064,
        1.509
      ],
      "C1": true,
      "C2_level": -0.014,
      "C2_ci": [
        -0.036,
        0.0083
      ],
      "C2": true,
      "C3_min_z": -2.22,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0011,
      "logloss_vs_book_ci": [
        -0.0003,
        0.0024
      ],
      "mean_p": 0.2585,
      "actual": 0.2444,
      "fair_odds": 4.23
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "BUNDES",
    "market": "home_win_both_halves",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "home_win_both_halves",
      "n": 665,
      "status": "PASS",
      "C1_slope": 1.22,
      "C1_ci": [
        0.898,
        1.541
      ],
      "C1": true,
      "C2_level": 0.0019,
      "C2_ci": [
        -0.027,
        0.0284
      ],
      "C2": true,
      "C3_min_z": -1.57,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0009,
      "logloss_vs_book_ci": [
        -0.0005,
        0.0021
      ],
      "mean_p": 0.156,
      "actual": 0.1579,
      "fair_odds": 7.65
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "home_win_both_halves",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 0.994,
      "C1_ci": [
        0.798,
        1.19
      ],
      "C1": true,
      "C2_level": 0.0063,
      "C2_ci": [
        -0.0103,
        0.0252
      ],
      "C2": true,
      "C3_min_z": -1.03,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0001,
      "logloss_vs_book_ci": [
        -0.0015,
        0.0011
      ],
      "mean_p": 0.1506,
      "actual": 0.1569,
      "fair_odds": 7.94
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "BUNDES",
    "market": "away_win_both_halves",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "away_win_both_halves",
      "n": 665,
      "status": "PASS",
      "C1_slope": 0.93,
      "C1_ci": [
        0.589,
        1.271
      ],
      "C1": true,
      "C2_level": -0.0039,
      "C2_ci": [
        -0.0252,
        0.0185
      ],
      "C2": true,
      "C3_min_z": -0.89,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0001,
      "logloss_vs_book_ci": [
        -0.0017,
        0.0014
      ],
      "mean_p": 0.0956,
      "actual": 0.0917,
      "fair_odds": 12.82
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "away_win_both_halves",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.269,
      "C1_ci": [
        1.019,
        1.519
      ],
      "C1": true,
      "C2_level": -0.0044,
      "C2_ci": [
        -0.0197,
        0.0109
      ],
      "C2": true,
      "C3_min_z": -1.73,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0019,
      "logloss_vs_book_ci": [
        -0.0002,
        0.0038
      ],
      "mean_p": 0.1018,
      "actual": 0.0974,
      "fair_odds": 11.91
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "BUNDES",
    "market": "home_fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "home_fh_over_0.5",
      "n": 665,
      "status": "PASS",
      "C1_slope": 1.497,
      "C1_ci": [
        1.089,
        1.905
      ],
      "C1": true,
      "C2_level": -0.0266,
      "C2_ci": [
        -0.0592,
        0.0075
      ],
      "C2": true,
      "C3_min_z": -2.02,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0011,
      "logloss_vs_book_ci": [
        -0.0022,
        0.0044
      ],
      "mean_p": 0.5514,
      "actual": 0.5248,
      "fair_odds": 1.86
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "home_fh_over_0.5",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.031,
      "C1_ci": [
        0.786,
        1.276
      ],
      "C1": true,
      "C2_level": -0.0057,
      "C2_ci": [
        -0.0298,
        0.0191
      ],
      "C2": true,
      "C3_min_z": -1.29,
      "C3": true,
      "C4_lifted_legs": 268,
      "C4_z": -1.98,
      "C4": true,
      "logloss_vs_book": 0.0003,
      "logloss_vs_book_ci": [
        -0.0025,
        0.0028
      ],
      "mean_p": 0.5351,
      "actual": 0.5294,
      "fair_odds": 1.91
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "BUNDES",
    "market": "away_fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "away_fh_over_0.5",
      "n": 665,
      "status": "PASS",
      "C1_slope": 0.977,
      "C1_ci": [
        0.625,
        1.329
      ],
      "C1": true,
      "C2_level": 0.0077,
      "C2_ci": [
        -0.0269,
        0.0425
      ],
      "C2": true,
      "C3_min_z": -1.89,
      "C3": true,
      "C4_lifted_legs": 50,
      "C4_z": -1.27,
      "C4": true,
      "logloss_vs_book": -0.0006,
      "logloss_vs_book_ci": [
        -0.003,
        0.002
      ],
      "mean_p": 0.4675,
      "actual": 0.4752,
      "fair_odds": 2.19
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "away_fh_over_0.5",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.436,
      "C1_ci": [
        1.161,
        1.711
      ],
      "C1": true,
      "C2_level": 0.019,
      "C2_ci": [
        -0.0054,
        0.0419
      ],
      "C2": true,
      "C3_min_z": -0.98,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0009,
      "logloss_vs_book_ci": [
        -0.0003,
        0.0021
      ],
      "mean_p": 0.447,
      "actual": 0.466,
      "fair_odds": 2.3
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "BUNDES",
    "market": "home_sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "home_sh_over_0.5",
      "n": 665,
      "status": "PASS",
      "C1_slope": 1.212,
      "C1_ci": [
        0.821,
        1.602
      ],
      "C1": true,
      "C2_level": 0.0218,
      "C2_ci": [
        -0.0147,
        0.0611
      ],
      "C2": true,
      "C3_min_z": -1.37,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0002,
      "logloss_vs_book_ci": [
        -0.0005,
        0.0002
      ],
      "mean_p": 0.6067,
      "actual": 0.6286,
      "fair_odds": 1.68
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "home_sh_over_0.5",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 0.984,
      "C1_ci": [
        0.751,
        1.216
      ],
      "C1": true,
      "C2_level": 0.0175,
      "C2_ci": [
        -0.0082,
        0.0425
      ],
      "C2": true,
      "C3_min_z": -0.99,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0008,
      "logloss_vs_book_ci": [
        -0.0,
        0.0016
      ],
      "mean_p": 0.5982,
      "actual": 0.6157,
      "fair_odds": 1.7
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "BUNDES",
    "market": "away_sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "away_sh_over_0.5",
      "n": 665,
      "status": "PASS",
      "C1_slope": 1.168,
      "C1_ci": [
        0.785,
        1.551
      ],
      "C1": true,
      "C2_level": 0.0304,
      "C2_ci": [
        -0.0078,
        0.068
      ],
      "C2": true,
      "C3_min_z": -0.54,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0001,
      "logloss_vs_book_ci": [
        -0.0006,
        0.0004
      ],
      "mean_p": 0.529,
      "actual": 0.5594,
      "fair_odds": 1.92
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "away_sh_over_0.5",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.016,
      "C1_ci": [
        0.784,
        1.248
      ],
      "C1": true,
      "C2_level": -0.0247,
      "C2_ci": [
        -0.0502,
        0.0006
      ],
      "C2": true,
      "C3_min_z": -1.88,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0013,
      "logloss_vs_book_ci": [
        0.0,
        0.0027
      ],
      "mean_p": 0.5424,
      "actual": 0.5176,
      "fair_odds": 1.88
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LIGUE1",
    "market": "home_score_both_halves",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "home_score_both_halves",
      "n": 675,
      "status": "PASS",
      "C1_slope": 0.843,
      "C1_ci": [
        0.567,
        1.118
      ],
      "C1": true,
      "C2_level": 0.0315,
      "C2_ci": [
        -0.0038,
        0.0672
      ],
      "C2": true,
      "C3_min_z": -0.21,
      "C3": true,
      "C4_lifted_legs": 67,
      "C4_z": 0.66,
      "C4": true,
      "logloss_vs_book": -0.0007,
      "logloss_vs_book_ci": [
        -0.0035,
        0.002
      ],
      "mean_p": 0.3018,
      "actual": 0.3333,
      "fair_odds": 3.62
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "home_score_both_halves",
      "n": 1725,
      "status": "FAIL",
      "C1_slope": 1.038,
      "C1_ci": [
        0.845,
        1.23
      ],
      "C1": true,
      "C2_level": -0.0161,
      "C2_ci": [
        -0.0366,
        0.004
      ],
      "C2": true,
      "C3_min_z": -3.4,
      "C3": false,
      "C4_lifted_legs": 116,
      "C4_z": -0.62,
      "C4": true,
      "logloss_vs_book": 0.0004,
      "logloss_vs_book_ci": [
        -0.0012,
        0.002
      ],
      "mean_p": 0.2845,
      "actual": 0.2684,
      "fair_odds": 3.84
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "league": "LIGUE1",
    "market": "away_score_both_halves",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "away_score_both_halves",
      "n": 675,
      "status": "PASS",
      "C1_slope": 0.793,
      "C1_ci": [
        0.47,
        1.115
      ],
      "C1": true,
      "C2_level": -0.01,
      "C2_ci": [
        -0.0375,
        0.0223
      ],
      "C2": true,
      "C3_min_z": -1.11,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0004,
      "logloss_vs_book_ci": [
        -0.001,
        0.0017
      ],
      "mean_p": 0.2322,
      "actual": 0.2222,
      "fair_odds": 4.7
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "away_score_both_halves",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 1.076,
      "C1_ci": [
        0.861,
        1.29
      ],
      "C1": true,
      "C2_level": 0.0011,
      "C2_ci": [
        -0.0172,
        0.0204
      ],
      "C2": true,
      "C3_min_z": -0.92,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0007,
        0.0011
      ],
      "mean_p": 0.2105,
      "actual": 0.2116,
      "fair_odds": 5.36
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LIGUE1",
    "market": "home_win_both_halves",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "home_win_both_halves",
      "n": 675,
      "status": "PASS",
      "C1_slope": 0.703,
      "C1_ci": [
        0.456,
        0.95
      ],
      "C1": true,
      "C2_level": 0.0229,
      "C2_ci": [
        -0.0038,
        0.0506
      ],
      "C2": true,
      "C3_min_z": -1.08,
      "C3": true,
      "C4_lifted_legs": 13,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0029,
      "logloss_vs_book_ci": [
        0.0004,
        0.0054
      ],
      "mean_p": 0.1416,
      "actual": 0.1644,
      "fair_odds": 8.67
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "home_win_both_halves",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 0.951,
      "C1_ci": [
        0.773,
        1.128
      ],
      "C1": true,
      "C2_level": -0.0094,
      "C2_ci": [
        -0.0238,
        0.0047
      ],
      "C2": true,
      "C3_min_z": -1.98,
      "C3": true,
      "C4_lifted_legs": 104,
      "C4_z": -1.82,
      "C4": true,
      "logloss_vs_book": 0.0001,
      "logloss_vs_book_ci": [
        -0.0016,
        0.0018
      ],
      "mean_p": 0.1369,
      "actual": 0.1275,
      "fair_odds": 9.18
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LIGUE1",
    "market": "away_win_both_halves",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "away_win_both_halves",
      "n": 675,
      "status": "PASS",
      "C1_slope": 0.854,
      "C1_ci": [
        0.533,
        1.175
      ],
      "C1": true,
      "C2_level": 0.0035,
      "C2_ci": [
        -0.0172,
        0.0238
      ],
      "C2": true,
      "C3_min_z": -1.18,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0008,
      "logloss_vs_book_ci": [
        0.0001,
        0.0015
      ],
      "mean_p": 0.0883,
      "actual": 0.0919,
      "fair_odds": 14.92
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "away_win_both_halves",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 1.15,
      "C1_ci": [
        0.913,
        1.387
      ],
      "C1": true,
      "C2_level": 0.0018,
      "C2_ci": [
        -0.0097,
        0.0153
      ],
      "C2": true,
      "C3_min_z": -1.4,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0008,
      "logloss_vs_book_ci": [
        0.0,
        0.0018
      ],
      "mean_p": 0.0799,
      "actual": 0.0817,
      "fair_odds": 16.04
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LIGUE1",
    "market": "home_fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "home_fh_over_0.5",
      "n": 675,
      "status": "PASS",
      "C1_slope": 0.824,
      "C1_ci": [
        0.514,
        1.134
      ],
      "C1": true,
      "C2_level": -0.0098,
      "C2_ci": [
        -0.0456,
        0.0302
      ],
      "C2": true,
      "C3_min_z": -1.22,
      "C3": true,
      "C4_lifted_legs": 267,
      "C4_z": -0.92,
      "C4": true,
      "logloss_vs_book": 0.0008,
      "logloss_vs_book_ci": [
        -0.0041,
        0.0068
      ],
      "mean_p": 0.5165,
      "actual": 0.5067,
      "fair_odds": 1.98
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "home_fh_over_0.5",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 1.068,
      "C1_ci": [
        0.855,
        1.28
      ],
      "C1": true,
      "C2_level": -0.0001,
      "C2_ci": [
        -0.0229,
        0.0227
      ],
      "C2": true,
      "C3_min_z": -1.85,
      "C3": true,
      "C4_lifted_legs": 541,
      "C4_z": -0.48,
      "C4": true,
      "logloss_vs_book": -0.002,
      "logloss_vs_book_ci": [
        -0.0048,
        0.0004
      ],
      "mean_p": 0.4911,
      "actual": 0.491,
      "fair_odds": 2.09
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LIGUE1",
    "market": "away_fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "away_fh_over_0.5",
      "n": 675,
      "status": "PASS",
      "C1_slope": 0.84,
      "C1_ci": [
        0.449,
        1.231
      ],
      "C1": true,
      "C2_level": -0.0131,
      "C2_ci": [
        -0.0471,
        0.0225
      ],
      "C2": true,
      "C3_min_z": -2.52,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0003,
      "logloss_vs_book_ci": [
        -0.0023,
        0.0027
      ],
      "mean_p": 0.4443,
      "actual": 0.4311,
      "fair_odds": 2.3
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "away_fh_over_0.5",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 1.134,
      "C1_ci": [
        0.867,
        1.402
      ],
      "C1": true,
      "C2_level": 0.0245,
      "C2_ci": [
        0.0033,
        0.0479
      ],
      "C2": true,
      "C3_min_z": -0.93,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0008,
      "logloss_vs_book_ci": [
        -0.0008,
        0.0022
      ],
      "mean_p": 0.4097,
      "actual": 0.4342,
      "fair_odds": 2.55
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "LIGUE1",
    "market": "home_sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "home_sh_over_0.5",
      "n": 675,
      "status": "PASS",
      "C1_slope": 1.153,
      "C1_ci": [
        0.766,
        1.54
      ],
      "C1": true,
      "C2_level": 0.0395,
      "C2_ci": [
        0.0023,
        0.0785
      ],
      "C2": true,
      "C3_min_z": -0.7,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0007,
      "logloss_vs_book_ci": [
        -0.0001,
        0.0016
      ],
      "mean_p": 0.5694,
      "actual": 0.6089,
      "fair_odds": 1.79
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "home_sh_over_0.5",
      "n": 1725,
      "status": "FAIL",
      "C1_slope": 0.927,
      "C1_ci": [
        0.689,
        1.164
      ],
      "C1": true,
      "C2_level": -0.0254,
      "C2_ci": [
        -0.0483,
        -0.0029
      ],
      "C2": false,
      "C3_min_z": -2.0,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0009,
      "logloss_vs_book_ci": [
        0.0001,
        0.0017
      ],
      "mean_p": 0.5616,
      "actual": 0.5362,
      "fair_odds": 1.8
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "league": "LIGUE1",
    "market": "away_sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "away_sh_over_0.5",
      "n": 675,
      "status": "PASS",
      "C1_slope": 0.775,
      "C1_ci": [
        0.436,
        1.114
      ],
      "C1": true,
      "C2_level": -0.0173,
      "C2_ci": [
        -0.0534,
        0.017
      ],
      "C2": true,
      "C3_min_z": -1.88,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0012,
      "logloss_vs_book_ci": [
        -0.0006,
        0.003
      ],
      "mean_p": 0.5107,
      "actual": 0.4933,
      "fair_odds": 1.99
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "away_sh_over_0.5",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 0.71,
      "C1_ci": [
        0.518,
        0.901
      ],
      "C1": true,
      "C2_level": -0.0049,
      "C2_ci": [
        -0.0296,
        0.0188
      ],
      "C2": true,
      "C3_min_z": -2.55,
      "C3": true,
      "C4_lifted_legs": 278,
      "C4_z": -1.47,
      "C4": true,
      "logloss_vs_book": 0.0025,
      "logloss_vs_book_ci": [
        -0.0001,
        0.0053
      ],
      "mean_p": 0.4948,
      "actual": 0.4899,
      "fair_odds": 2.09
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "EREDIV",
    "market": "home_score_both_halves",
    "primary_2024_25_plus": {
      "league": "EREDIV",
      "market": "home_score_both_halves",
      "n": 701,
      "status": "PASS",
      "C1_slope": 0.955,
      "C1_ci": [
        0.699,
        1.21
      ],
      "C1": true,
      "C2_level": 0.0075,
      "C2_ci": [
        -0.0251,
        0.0399
      ],
      "C2": true,
      "C3_min_z": -0.88,
      "C3": true,
      "C4_lifted_legs": 166,
      "C4_z": -0.51,
      "C4": true,
      "logloss_vs_book": -0.0012,
      "logloss_vs_book_ci": [
        -0.0047,
        0.0022
      ],
      "mean_p": 0.3449,
      "actual": 0.3524,
      "fair_odds": 3.14
    },
    "replication_2019_20_to_2023_24": {
      "league": "EREDIV",
      "market": "home_score_both_halves",
      "n": 1456,
      "status": "PASS",
      "C1_slope": 1.028,
      "C1_ci": [
        0.856,
        1.199
      ],
      "C1": true,
      "C2_level": -0.0158,
      "C2_ci": [
        -0.0377,
        0.0062
      ],
      "C2": true,
      "C3_min_z": -2.21,
      "C3": true,
      "C4_lifted_legs": 411,
      "C4_z": -0.47,
      "C4": true,
      "logloss_vs_book": 0.0011,
      "logloss_vs_book_ci": [
        -0.0015,
        0.0038
      ],
      "mean_p": 0.3386,
      "actual": 0.3228,
      "fair_odds": 3.25
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "EREDIV",
    "market": "away_score_both_halves",
    "primary_2024_25_plus": {
      "league": "EREDIV",
      "market": "away_score_both_halves",
      "n": 701,
      "status": "PASS",
      "C1_slope": 0.888,
      "C1_ci": [
        0.641,
        1.136
      ],
      "C1": true,
      "C2_level": 0.0266,
      "C2_ci": [
        -0.0019,
        0.0594
      ],
      "C2": true,
      "C3_min_z": -1.17,
      "C3": true,
      "C4_lifted_legs": 48,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0011,
      "logloss_vs_book_ci": [
        -0.0027,
        0.0051
      ],
      "mean_p": 0.2416,
      "actual": 0.2682,
      "fair_odds": 4.6
    },
    "replication_2019_20_to_2023_24": {
      "league": "EREDIV",
      "market": "away_score_both_halves",
      "n": 1456,
      "status": "PASS",
      "C1_slope": 1.147,
      "C1_ci": [
        0.966,
        1.328
      ],
      "C1": true,
      "C2_level": -0.0003,
      "C2_ci": [
        -0.0197,
        0.0205
      ],
      "C2": true,
      "C3_min_z": -1.33,
      "C3": true,
      "C4_lifted_legs": 48,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0015,
      "logloss_vs_book_ci": [
        -0.0035,
        0.0007
      ],
      "mean_p": 0.2345,
      "actual": 0.2342,
      "fair_odds": 5.01
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "EREDIV",
    "market": "home_win_both_halves",
    "primary_2024_25_plus": {
      "league": "EREDIV",
      "market": "home_win_both_halves",
      "n": 701,
      "status": "PASS",
      "C1_slope": 0.918,
      "C1_ci": [
        0.677,
        1.16
      ],
      "C1": true,
      "C2_level": -0.0049,
      "C2_ci": [
        -0.0336,
        0.0259
      ],
      "C2": true,
      "C3_min_z": -1.08,
      "C3": true,
      "C4_lifted_legs": 131,
      "C4_z": -0.25,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0037,
        0.0044
      ],
      "mean_p": 0.1733,
      "actual": 0.1683,
      "fair_odds": 7.62
    },
    "replication_2019_20_to_2023_24": {
      "league": "EREDIV",
      "market": "home_win_both_halves",
      "n": 1456,
      "status": "PASS",
      "C1_slope": 1.079,
      "C1_ci": [
        0.911,
        1.246
      ],
      "C1": true,
      "C2_level": -0.0041,
      "C2_ci": [
        -0.0205,
        0.0148
      ],
      "C2": true,
      "C3_min_z": -1.79,
      "C3": true,
      "C4_lifted_legs": 285,
      "C4_z": 0.1,
      "C4": true,
      "logloss_vs_book": -0.0011,
      "logloss_vs_book_ci": [
        -0.0038,
        0.0014
      ],
      "mean_p": 0.1764,
      "actual": 0.1724,
      "fair_odds": 7.46
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "EREDIV",
    "market": "away_win_both_halves",
    "primary_2024_25_plus": {
      "league": "EREDIV",
      "market": "away_win_both_halves",
      "n": 701,
      "status": "PASS",
      "C1_slope": 1.007,
      "C1_ci": [
        0.695,
        1.32
      ],
      "C1": true,
      "C2_level": -0.0038,
      "C2_ci": [
        -0.0245,
        0.0192
      ],
      "C2": true,
      "C3_min_z": -1.21,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0001,
      "logloss_vs_book_ci": [
        -0.001,
        0.0012
      ],
      "mean_p": 0.0908,
      "actual": 0.087,
      "fair_odds": 14.88
    },
    "replication_2019_20_to_2023_24": {
      "league": "EREDIV",
      "market": "away_win_both_halves",
      "n": 1456,
      "status": "PASS",
      "C1_slope": 1.005,
      "C1_ci": [
        0.807,
        1.202
      ],
      "C1": true,
      "C2_level": -0.0039,
      "C2_ci": [
        -0.0168,
        0.0092
      ],
      "C2": true,
      "C3_min_z": -1.6,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0001,
      "logloss_vs_book_ci": [
        -0.0004,
        0.0007
      ],
      "mean_p": 0.0973,
      "actual": 0.0934,
      "fair_odds": 15.13
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "EREDIV",
    "market": "home_fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "EREDIV",
      "market": "home_fh_over_0.5",
      "n": 701,
      "status": "PASS",
      "C1_slope": 1.187,
      "C1_ci": [
        0.842,
        1.532
      ],
      "C1": true,
      "C2_level": 0.0357,
      "C2_ci": [
        0.0046,
        0.0678
      ],
      "C2": true,
      "C3_min_z": -0.67,
      "C3": true,
      "C4_lifted_legs": 35,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0029,
      "logloss_vs_book_ci": [
        -0.0052,
        -0.0003
      ],
      "mean_p": 0.5349,
      "actual": 0.5706,
      "fair_odds": 1.91
    },
    "replication_2019_20_to_2023_24": {
      "league": "EREDIV",
      "market": "home_fh_over_0.5",
      "n": 1456,
      "status": "PASS",
      "C1_slope": 0.99,
      "C1_ci": [
        0.776,
        1.204
      ],
      "C1": true,
      "C2_level": -0.0245,
      "C2_ci": [
        -0.0491,
        0.0007
      ],
      "C2": true,
      "C3_min_z": -1.82,
      "C3": true,
      "C4_lifted_legs": 190,
      "C4_z": -0.9,
      "C4": true,
      "logloss_vs_book": 0.0017,
      "logloss_vs_book_ci": [
        -0.0009,
        0.0042
      ],
      "mean_p": 0.5314,
      "actual": 0.5069,
      "fair_odds": 1.93
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "EREDIV",
    "market": "away_fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "EREDIV",
      "market": "away_fh_over_0.5",
      "n": 701,
      "status": "PASS",
      "C1_slope": 0.856,
      "C1_ci": [
        0.538,
        1.174
      ],
      "C1": true,
      "C2_level": 0.0117,
      "C2_ci": [
        -0.0192,
        0.0437
      ],
      "C2": true,
      "C3_min_z": -0.86,
      "C3": true,
      "C4_lifted_legs": 9,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0004,
      "logloss_vs_book_ci": [
        -0.0015,
        0.0025
      ],
      "mean_p": 0.4491,
      "actual": 0.4608,
      "fair_odds": 2.27
    },
    "replication_2019_20_to_2023_24": {
      "league": "EREDIV",
      "market": "away_fh_over_0.5",
      "n": 1456,
      "status": "PASS",
      "C1_slope": 1.08,
      "C1_ci": [
        0.868,
        1.292
      ],
      "C1": true,
      "C2_level": -0.0087,
      "C2_ci": [
        -0.0329,
        0.0184
      ],
      "C2": true,
      "C3_min_z": -1.81,
      "C3": true,
      "C4_lifted_legs": 35,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0007,
      "logloss_vs_book_ci": [
        -0.0007,
        0.0023
      ],
      "mean_p": 0.4448,
      "actual": 0.4361,
      "fair_odds": 2.34
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "EREDIV",
    "market": "home_sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "EREDIV",
      "market": "home_sh_over_0.5",
      "n": 701,
      "status": "PASS",
      "C1_slope": 0.77,
      "C1_ci": [
        0.475,
        1.065
      ],
      "C1": true,
      "C2_level": 0.0034,
      "C2_ci": [
        -0.0316,
        0.0389
      ],
      "C2": true,
      "C3_min_z": -1.2,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0011,
      "logloss_vs_book_ci": [
        -0.0011,
        0.0034
      ],
      "mean_p": 0.6157,
      "actual": 0.6191,
      "fair_odds": 1.64
    },
    "replication_2019_20_to_2023_24": {
      "league": "EREDIV",
      "market": "home_sh_over_0.5",
      "n": 1456,
      "status": "PASS",
      "C1_slope": 1.025,
      "C1_ci": [
        0.825,
        1.224
      ],
      "C1": true,
      "C2_level": -0.0036,
      "C2_ci": [
        -0.0261,
        0.0192
      ],
      "C2": true,
      "C3_min_z": -1.48,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0012,
        0.0017
      ],
      "mean_p": 0.6039,
      "actual": 0.6003,
      "fair_odds": 1.69
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "EREDIV",
    "market": "away_sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "EREDIV",
      "market": "away_sh_over_0.5",
      "n": 701,
      "status": "PASS",
      "C1_slope": 1.025,
      "C1_ci": [
        0.735,
        1.314
      ],
      "C1": true,
      "C2_level": 0.0281,
      "C2_ci": [
        -0.0041,
        0.0654
      ],
      "C2": true,
      "C3_min_z": -0.83,
      "C3": true,
      "C4_lifted_legs": 7,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0,
      "logloss_vs_book_ci": [
        -0.0034,
        0.0038
      ],
      "mean_p": 0.5168,
      "actual": 0.5449,
      "fair_odds": 1.96
    },
    "replication_2019_20_to_2023_24": {
      "league": "EREDIV",
      "market": "away_sh_over_0.5",
      "n": 1456,
      "status": "PASS",
      "C1_slope": 0.988,
      "C1_ci": [
        0.802,
        1.174
      ],
      "C1": true,
      "C2_level": -0.0001,
      "C2_ci": [
        -0.0266,
        0.0248
      ],
      "C2": true,
      "C3_min_z": -1.59,
      "C3": true,
      "C4_lifted_legs": 9,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0003,
      "logloss_vs_book_ci": [
        -0.0031,
        0.0024
      ],
      "mean_p": 0.5049,
      "actual": 0.5048,
      "fair_odds": 2.05
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "JUPILER",
    "market": "home_score_both_halves",
    "primary_2024_25_plus": {
      "league": "JUPILER",
      "market": "home_score_both_halves",
      "n": 702,
      "status": "PASS",
      "C1_slope": 1.329,
      "C1_ci": [
        1.008,
        1.65
      ],
      "C1": true,
      "C2_level": 0.0042,
      "C2_ci": [
        -0.0288,
        0.0376
      ],
      "C2": true,
      "C3_min_z": -1.55,
      "C3": true,
      "C4_lifted_legs": 113,
      "C4_z": 0.21,
      "C4": true,
      "logloss_vs_book": -0.0049,
      "logloss_vs_book_ci": [
        -0.0087,
        -0.0014
      ],
      "mean_p": 0.2963,
      "actual": 0.3006,
      "fair_odds": 3.63
    },
    "replication_2019_20_to_2023_24": {
      "league": "JUPILER",
      "market": "home_score_both_halves",
      "n": 1458,
      "status": "PASS",
      "C1_slope": 1.257,
      "C1_ci": [
        1.024,
        1.49
      ],
      "C1": true,
      "C2_level": -0.0016,
      "C2_ci": [
        -0.024,
        0.0212
      ],
      "C2": true,
      "C3_min_z": -1.47,
      "C3": true,
      "C4_lifted_legs": 42,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0011,
      "logloss_vs_book_ci": [
        -0.0024,
        0.0002
      ],
      "mean_p": 0.3062,
      "actual": 0.3045,
      "fair_odds": 3.42
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "JUPILER",
    "market": "away_score_both_halves",
    "primary_2024_25_plus": {
      "league": "JUPILER",
      "market": "away_score_both_halves",
      "n": 702,
      "status": "PASS",
      "C1_slope": 0.984,
      "C1_ci": [
        0.597,
        1.371
      ],
      "C1": true,
      "C2_level": -0.0254,
      "C2_ci": [
        -0.0585,
        0.0072
      ],
      "C2": true,
      "C3_min_z": -1.1,
      "C3": true,
      "C4_lifted_legs": 20,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0015,
      "logloss_vs_book_ci": [
        -0.0006,
        0.0037
      ],
      "mean_p": 0.2334,
      "actual": 0.208,
      "fair_odds": 4.56
    },
    "replication_2019_20_to_2023_24": {
      "league": "JUPILER",
      "market": "away_score_both_halves",
      "n": 1458,
      "status": "PASS",
      "C1_slope": 1.433,
      "C1_ci": [
        1.146,
        1.72
      ],
      "C1": true,
      "C2_level": -0.0125,
      "C2_ci": [
        -0.0323,
        0.009
      ],
      "C2": true,
      "C3_min_z": -2.5,
      "C3": true,
      "C4_lifted_legs": 125,
      "C4_z": -0.7,
      "C4": true,
      "logloss_vs_book": 0.0023,
      "logloss_vs_book_ci": [
        -0.0004,
        0.0047
      ],
      "mean_p": 0.2492,
      "actual": 0.2366,
      "fair_odds": 4.15
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "JUPILER",
    "market": "home_win_both_halves",
    "primary_2024_25_plus": {
      "league": "JUPILER",
      "market": "home_win_both_halves",
      "n": 702,
      "status": "PASS",
      "C1_slope": 0.986,
      "C1_ci": [
        0.673,
        1.3
      ],
      "C1": true,
      "C2_level": 0.0047,
      "C2_ci": [
        -0.0212,
        0.0295
      ],
      "C2": true,
      "C3_min_z": -1.06,
      "C3": true,
      "C4_lifted_legs": 26,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0001,
      "logloss_vs_book_ci": [
        -0.0022,
        0.002
      ],
      "mean_p": 0.1363,
      "actual": 0.141,
      "fair_odds": 8.63
    },
    "replication_2019_20_to_2023_24": {
      "league": "JUPILER",
      "market": "home_win_both_halves",
      "n": 1458,
      "status": "PASS",
      "C1_slope": 1.101,
      "C1_ci": [
        0.891,
        1.311
      ],
      "C1": true,
      "C2_level": 0.0148,
      "C2_ci": [
        -0.0031,
        0.033
      ],
      "C2": true,
      "C3_min_z": -0.76,
      "C3": true,
      "C4_lifted_legs": 3,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0001,
      "logloss_vs_book_ci": [
        -0.001,
        0.0014
      ],
      "mean_p": 0.1361,
      "actual": 0.1509,
      "fair_odds": 8.73
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "JUPILER",
    "market": "away_win_both_halves",
    "primary_2024_25_plus": {
      "league": "JUPILER",
      "market": "away_win_both_halves",
      "n": 702,
      "status": "FAIL",
      "C1_slope": 0.944,
      "C1_ci": [
        0.534,
        1.354
      ],
      "C1": true,
      "C2_level": -0.0183,
      "C2_ci": [
        -0.0369,
        -0.0018
      ],
      "C2": false,
      "C3_min_z": -1.69,
      "C3": true,
      "C4_lifted_legs": 8,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0009,
      "logloss_vs_book_ci": [
        -0.0005,
        0.0026
      ],
      "mean_p": 0.0853,
      "actual": 0.067,
      "fair_odds": 14.76
    },
    "replication_2019_20_to_2023_24": {
      "league": "JUPILER",
      "market": "away_win_both_halves",
      "n": 1458,
      "status": "PASS",
      "C1_slope": 1.519,
      "C1_ci": [
        1.199,
        1.838
      ],
      "C1": true,
      "C2_level": 0.002,
      "C2_ci": [
        -0.012,
        0.016
      ],
      "C2": true,
      "C3_min_z": -1.75,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0013,
      "logloss_vs_book_ci": [
        -0.0007,
        0.0031
      ],
      "mean_p": 0.0899,
      "actual": 0.0919,
      "fair_odds": 12.96
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "league": "JUPILER",
    "market": "home_fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "JUPILER",
      "market": "home_fh_over_0.5",
      "n": 702,
      "status": "PASS",
      "C1_slope": 1.206,
      "C1_ci": [
        0.793,
        1.618
      ],
      "C1": true,
      "C2_level": 0.0055,
      "C2_ci": [
        -0.0281,
        0.0431
      ],
      "C2": true,
      "C3_min_z": -1.16,
      "C3": true,
      "C4_lifted_legs": 14,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.001,
      "logloss_vs_book_ci": [
        -0.0029,
        0.0008
      ],
      "mean_p": 0.496,
      "actual": 0.5014,
      "fair_odds": 2.05
    },
    "replication_2019_20_to_2023_24": {
      "league": "JUPILER",
      "market": "home_fh_over_0.5",
      "n": 1458,
      "status": "PASS",
      "C1_slope": 1.393,
      "C1_ci": [
        1.068,
        1.717
      ],
      "C1": true,
      "C2_level": 0.0132,
      "C2_ci": [
        -0.0111,
        0.0375
      ],
      "C2": true,
      "C3_min_z": -1.46,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0006,
      "logloss_vs_book_ci": [
        -0.0004,
        0.0015
      ],
      "mean_p": 0.491,
      "actual": 0.5041,
      "fair_odds": 2.06
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "JUPILER",
    "market": "away_fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "JUPILER",
      "market": "away_fh_over_0.5",
      "n": 702,
      "status": "PASS",
      "C1_slope": 0.904,
      "C1_ci": [
        0.488,
        1.319
      ],
      "C1": true,
      "C2_level": -0.0102,
      "C2_ci": [
        -0.0465,
        0.0282
      ],
      "C2": true,
      "C3_min_z": -1.98,
      "C3": true,
      "C4_lifted_legs": 113,
      "C4_z": 0.04,
      "C4": true,
      "logloss_vs_book": 0.0004,
      "logloss_vs_book_ci": [
        -0.0029,
        0.0035
      ],
      "mean_p": 0.4432,
      "actual": 0.433,
      "fair_odds": 2.29
    },
    "replication_2019_20_to_2023_24": {
      "league": "JUPILER",
      "market": "away_fh_over_0.5",
      "n": 1458,
      "status": "FAIL",
      "C1_slope": 1.386,
      "C1_ci": [
        1.076,
        1.696
      ],
      "C1": true,
      "C2_level": 0.0048,
      "C2_ci": [
        -0.0204,
        0.0287
      ],
      "C2": true,
      "C3_min_z": -3.17,
      "C3": false,
      "C4_lifted_legs": 150,
      "C4_z": -0.89,
      "C4": true,
      "logloss_vs_book": 0.0006,
      "logloss_vs_book_ci": [
        -0.0015,
        0.0028
      ],
      "mean_p": 0.441,
      "actual": 0.4458,
      "fair_odds": 2.29
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "league": "JUPILER",
    "market": "home_sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "JUPILER",
      "market": "home_sh_over_0.5",
      "n": 702,
      "status": "PASS",
      "C1_slope": 1.173,
      "C1_ci": [
        0.823,
        1.524
      ],
      "C1": true,
      "C2_level": -0.0122,
      "C2_ci": [
        -0.0483,
        0.0285
      ],
      "C2": true,
      "C3_min_z": -1.13,
      "C3": true,
      "C4_lifted_legs": 92,
      "C4_z": 0.21,
      "C4": true,
      "logloss_vs_book": -0.0027,
      "logloss_vs_book_ci": [
        -0.0058,
        0.0006
      ],
      "mean_p": 0.582,
      "actual": 0.5698,
      "fair_odds": 1.74
    },
    "replication_2019_20_to_2023_24": {
      "league": "JUPILER",
      "market": "home_sh_over_0.5",
      "n": 1458,
      "status": "FAIL",
      "C1_slope": 0.98,
      "C1_ci": [
        0.76,
        1.2
      ],
      "C1": true,
      "C2_level": -0.0297,
      "C2_ci": [
        -0.0536,
        -0.0038
      ],
      "C2": false,
      "C3_min_z": -2.81,
      "C3": true,
      "C4_lifted_legs": 516,
      "C4_z": -2.34,
      "C4": false,
      "logloss_vs_book": 0.0011,
      "logloss_vs_book_ci": [
        -0.0024,
        0.0045
      ],
      "mean_p": 0.6113,
      "actual": 0.5816,
      "fair_odds": 1.63
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "league": "JUPILER",
    "market": "away_sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "JUPILER",
      "market": "away_sh_over_0.5",
      "n": 702,
      "status": "FAIL",
      "C1_slope": 1.047,
      "C1_ci": [
        0.566,
        1.528
      ],
      "C1": true,
      "C2_level": -0.0629,
      "C2_ci": [
        -0.1015,
        -0.0246
      ],
      "C2": false,
      "C3_min_z": -2.3,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0015,
      "logloss_vs_book_ci": [
        -0.0001,
        0.0031
      ],
      "mean_p": 0.5144,
      "actual": 0.4516,
      "fair_odds": 1.96
    },
    "replication_2019_20_to_2023_24": {
      "league": "JUPILER",
      "market": "away_sh_over_0.5",
      "n": 1458,
      "status": "PASS",
      "C1_slope": 1.119,
      "C1_ci": [
        0.808,
        1.43
      ],
      "C1": true,
      "C2_level": -0.0158,
      "C2_ci": [
        -0.0428,
        0.0096
      ],
      "C2": true,
      "C3_min_z": -1.84,
      "C3": true,
      "C4_lifted_legs": 174,
      "C4_z": -1.63,
      "C4": true,
      "logloss_vs_book": 0.0014,
      "logloss_vs_book_ci": [
        -0.0008,
        0.0037
      ],
      "mean_p": 0.5384,
      "actual": 0.5226,
      "fair_odds": 1.85
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "league": "PRIMEIRA",
    "market": "home_score_both_halves",
    "primary_2024_25_plus": {
      "league": "PRIMEIRA",
      "market": "home_score_both_halves",
      "n": 693,
      "status": "PASS",
      "C1_slope": 1.044,
      "C1_ci": [
        0.821,
        1.268
      ],
      "C1": true,
      "C2_level": 0.0082,
      "C2_ci": [
        -0.0205,
        0.0377
      ],
      "C2": true,
      "C3_min_z": -1.33,
      "C3": true,
      "C4_lifted_legs": 111,
      "C4_z": 0.58,
      "C4": true,
      "logloss_vs_book": -0.0031,
      "logloss_vs_book_ci": [
        -0.0078,
        0.0017
      ],
      "mean_p": 0.2602,
      "actual": 0.2684,
      "fair_odds": 4.43
    },
    "replication_2019_20_to_2023_24": {
      "league": "PRIMEIRA",
      "market": "home_score_both_halves",
      "n": 1530,
      "status": "FAIL",
      "C1_slope": 0.922,
      "C1_ci": [
        0.77,
        1.074
      ],
      "C1": true,
      "C2_level": -0.025,
      "C2_ci": [
        -0.0457,
        -0.0042
      ],
      "C2": false,
      "C3_min_z": -2.66,
      "C3": true,
      "C4_lifted_legs": 339,
      "C4_z": -1.78,
      "C4": true,
      "logloss_vs_book": 0.0008,
      "logloss_vs_book_ci": [
        -0.0033,
        0.0046
      ],
      "mean_p": 0.2708,
      "actual": 0.2458,
      "fair_odds": 4.37
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "league": "PRIMEIRA",
    "market": "away_score_both_halves",
    "primary_2024_25_plus": {
      "league": "PRIMEIRA",
      "market": "away_score_both_halves",
      "n": 693,
      "status": "PASS",
      "C1_slope": 0.982,
      "C1_ci": [
        0.704,
        1.259
      ],
      "C1": true,
      "C2_level": -0.0074,
      "C2_ci": [
        -0.0346,
        0.0235
      ],
      "C2": true,
      "C3_min_z": -1.17,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0004,
        0.001
      ],
      "mean_p": 0.2051,
      "actual": 0.1977,
      "fair_odds": 5.68
    },
    "replication_2019_20_to_2023_24": {
      "league": "PRIMEIRA",
      "market": "away_score_both_halves",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.0,
      "C1_ci": [
        0.8,
        1.2
      ],
      "C1": true,
      "C2_level": -0.012,
      "C2_ci": [
        -0.03,
        0.0063
      ],
      "C2": true,
      "C3_min_z": -1.66,
      "C3": true,
      "C4_lifted_legs": 17,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0008,
      "logloss_vs_book_ci": [
        -0.0006,
        0.0021
      ],
      "mean_p": 0.2081,
      "actual": 0.1961,
      "fair_odds": 5.58
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "PRIMEIRA",
    "market": "home_win_both_halves",
    "primary_2024_25_plus": {
      "league": "PRIMEIRA",
      "market": "home_win_both_halves",
      "n": 693,
      "status": "PASS",
      "C1_slope": 1.064,
      "C1_ci": [
        0.818,
        1.311
      ],
      "C1": true,
      "C2_level": -0.0068,
      "C2_ci": [
        -0.0285,
        0.017
      ],
      "C2": true,
      "C3_min_z": -1.79,
      "C3": true,
      "C4_lifted_legs": 60,
      "C4_z": 0.11,
      "C4": true,
      "logloss_vs_book": -0.002,
      "logloss_vs_book_ci": [
        -0.0058,
        0.0022
      ],
      "mean_p": 0.1367,
      "actual": 0.1299,
      "fair_odds": 10.52
    },
    "replication_2019_20_to_2023_24": {
      "league": "PRIMEIRA",
      "market": "home_win_both_halves",
      "n": 1530,
      "status": "FAIL",
      "C1_slope": 0.902,
      "C1_ci": [
        0.742,
        1.062
      ],
      "C1": true,
      "C2_level": -0.0198,
      "C2_ci": [
        -0.0362,
        -0.0045
      ],
      "C2": false,
      "C3_min_z": -1.8,
      "C3": true,
      "C4_lifted_legs": 228,
      "C4_z": -2.56,
      "C4": false,
      "logloss_vs_book": 0.0016,
      "logloss_vs_book_ci": [
        -0.0012,
        0.0044
      ],
      "mean_p": 0.1433,
      "actual": 0.1235,
      "fair_odds": 10.04
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "league": "PRIMEIRA",
    "market": "away_win_both_halves",
    "primary_2024_25_plus": {
      "league": "PRIMEIRA",
      "market": "away_win_both_halves",
      "n": 693,
      "status": "PASS",
      "C1_slope": 1.143,
      "C1_ci": [
        0.837,
        1.448
      ],
      "C1": true,
      "C2_level": -0.0083,
      "C2_ci": [
        -0.0266,
        0.0121
      ],
      "C2": true,
      "C3_min_z": -2.08,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0015,
      "logloss_vs_book_ci": [
        -0.0033,
        0.0005
      ],
      "mean_p": 0.0876,
      "actual": 0.0794,
      "fair_odds": 18.38
    },
    "replication_2019_20_to_2023_24": {
      "league": "PRIMEIRA",
      "market": "away_win_both_halves",
      "n": 1530,
      "status": "FAIL",
      "C1_slope": 0.984,
      "C1_ci": [
        0.773,
        1.194
      ],
      "C1": true,
      "C2_level": -0.0139,
      "C2_ci": [
        -0.0269,
        -0.0009
      ],
      "C2": false,
      "C3_min_z": -1.7,
      "C3": true,
      "C4_lifted_legs": 13,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0001,
      "logloss_vs_book_ci": [
        -0.0008,
        0.0011
      ],
      "mean_p": 0.0878,
      "actual": 0.0739,
      "fair_odds": 17.08
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "league": "PRIMEIRA",
    "market": "home_fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "PRIMEIRA",
      "market": "home_fh_over_0.5",
      "n": 693,
      "status": "PASS",
      "C1_slope": 1.222,
      "C1_ci": [
        0.918,
        1.525
      ],
      "C1": true,
      "C2_level": -0.0034,
      "C2_ci": [
        -0.0364,
        0.0331
      ],
      "C2": true,
      "C3_min_z": -1.39,
      "C3": true,
      "C4_lifted_legs": 13,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0013,
      "logloss_vs_book_ci": [
        -0.0043,
        0.0014
      ],
      "mean_p": 0.4767,
      "actual": 0.4733,
      "fair_odds": 2.14
    },
    "replication_2019_20_to_2023_24": {
      "league": "PRIMEIRA",
      "market": "home_fh_over_0.5",
      "n": 1530,
      "status": "FAIL",
      "C1_slope": 0.871,
      "C1_ci": [
        0.672,
        1.07
      ],
      "C1": true,
      "C2_level": -0.0421,
      "C2_ci": [
        -0.0647,
        -0.0188
      ],
      "C2": false,
      "C3_min_z": -2.79,
      "C3": true,
      "C4_lifted_legs": 971,
      "C4_z": -3.19,
      "C4": false,
      "logloss_vs_book": 0.0044,
      "logloss_vs_book_ci": [
        0.0005,
        0.0083
      ],
      "mean_p": 0.4989,
      "actual": 0.4569,
      "fair_odds": 2.07
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "league": "PRIMEIRA",
    "market": "away_fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "PRIMEIRA",
      "market": "away_fh_over_0.5",
      "n": 693,
      "status": "PASS",
      "C1_slope": 0.977,
      "C1_ci": [
        0.683,
        1.271
      ],
      "C1": true,
      "C2_level": -0.0146,
      "C2_ci": [
        -0.0501,
        0.0225
      ],
      "C2": true,
      "C3_min_z": -1.44,
      "C3": true,
      "C4_lifted_legs": 79,
      "C4_z": -1.09,
      "C4": true,
      "logloss_vs_book": 0.0005,
      "logloss_vs_book_ci": [
        -0.0023,
        0.0031
      ],
      "mean_p": 0.4143,
      "actual": 0.3997,
      "fair_odds": 2.53
    },
    "replication_2019_20_to_2023_24": {
      "league": "PRIMEIRA",
      "market": "away_fh_over_0.5",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.033,
      "C1_ci": [
        0.825,
        1.242
      ],
      "C1": true,
      "C2_level": -0.0153,
      "C2_ci": [
        -0.0381,
        0.0083
      ],
      "C2": true,
      "C3_min_z": -1.93,
      "C3": true,
      "C4_lifted_legs": 372,
      "C4_z": -0.27,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0025,
        0.0029
      ],
      "mean_p": 0.4225,
      "actual": 0.4072,
      "fair_odds": 2.48
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "PRIMEIRA",
    "market": "home_sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "PRIMEIRA",
      "market": "home_sh_over_0.5",
      "n": 693,
      "status": "PASS",
      "C1_slope": 0.993,
      "C1_ci": [
        0.749,
        1.237
      ],
      "C1": true,
      "C2_level": 0.0073,
      "C2_ci": [
        -0.0251,
        0.0424
      ],
      "C2": true,
      "C3_min_z": -1.31,
      "C3": true,
      "C4_lifted_legs": 132,
      "C4_z": 0.67,
      "C4": true,
      "logloss_vs_book": -0.0019,
      "logloss_vs_book_ci": [
        -0.0077,
        0.0037
      ],
      "mean_p": 0.5266,
      "actual": 0.5339,
      "fair_odds": 1.92
    },
    "replication_2019_20_to_2023_24": {
      "league": "PRIMEIRA",
      "market": "home_sh_over_0.5",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.068,
      "C1_ci": [
        0.884,
        1.252
      ],
      "C1": true,
      "C2_level": 0.0097,
      "C2_ci": [
        -0.0142,
        0.0321
      ],
      "C2": true,
      "C3_min_z": -1.25,
      "C3": true,
      "C4_lifted_legs": 203,
      "C4_z": 1.08,
      "C4": true,
      "logloss_vs_book": -0.0022,
      "logloss_vs_book_ci": [
        -0.005,
        0.0005
      ],
      "mean_p": 0.5263,
      "actual": 0.5359,
      "fair_odds": 1.97
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "PRIMEIRA",
    "market": "away_sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "PRIMEIRA",
      "market": "away_sh_over_0.5",
      "n": 693,
      "status": "PASS",
      "C1_slope": 1.104,
      "C1_ci": [
        0.787,
        1.422
      ],
      "C1": true,
      "C2_level": 0.021,
      "C2_ci": [
        -0.0138,
        0.0555
      ],
      "C2": true,
      "C3_min_z": -0.92,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0005,
      "logloss_vs_book_ci": [
        -0.0002,
        0.0013
      ],
      "mean_p": 0.461,
      "actual": 0.482,
      "fair_odds": 2.25
    },
    "replication_2019_20_to_2023_24": {
      "league": "PRIMEIRA",
      "market": "away_sh_over_0.5",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.002,
      "C1_ci": [
        0.779,
        1.226
      ],
      "C1": true,
      "C2_level": 0.0021,
      "C2_ci": [
        -0.023,
        0.0253
      ],
      "C2": true,
      "C3_min_z": -1.03,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0008,
        0.0013
      ],
      "mean_p": 0.4554,
      "actual": 0.4575,
      "fair_odds": 2.29
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "SUPERLIG",
    "market": "home_score_both_halves",
    "primary_2024_25_plus": {
      "league": "SUPERLIG",
      "market": "home_score_both_halves",
      "n": 728,
      "status": "PASS",
      "C1_slope": 1.017,
      "C1_ci": [
        0.741,
        1.292
      ],
      "C1": true,
      "C2_level": -0.017,
      "C2_ci": [
        -0.0495,
        0.0157
      ],
      "C2": true,
      "C3_min_z": -2.5,
      "C3": true,
      "C4_lifted_legs": 175,
      "C4_z": -0.59,
      "C4": true,
      "logloss_vs_book": -0.0,
      "logloss_vs_book_ci": [
        -0.0043,
        0.0042
      ],
      "mean_p": 0.3082,
      "actual": 0.2912,
      "fair_odds": 3.5
    },
    "replication_2019_20_to_2023_24": {
      "league": "SUPERLIG",
      "market": "home_score_both_halves",
      "n": 1798,
      "status": "PASS",
      "C1_slope": 1.01,
      "C1_ci": [
        0.8,
        1.22
      ],
      "C1": true,
      "C2_level": -0.0103,
      "C2_ci": [
        -0.0304,
        0.01
      ],
      "C2": true,
      "C3_min_z": -1.43,
      "C3": true,
      "C4_lifted_legs": 504,
      "C4_z": -1.15,
      "C4": true,
      "logloss_vs_book": -0.0,
      "logloss_vs_book_ci": [
        -0.0026,
        0.003
      ],
      "mean_p": 0.3106,
      "actual": 0.3003,
      "fair_odds": 3.4
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "SUPERLIG",
    "market": "away_score_both_halves",
    "primary_2024_25_plus": {
      "league": "SUPERLIG",
      "market": "away_score_both_halves",
      "n": 728,
      "status": "PASS",
      "C1_slope": 1.011,
      "C1_ci": [
        0.698,
        1.323
      ],
      "C1": true,
      "C2_level": -0.0039,
      "C2_ci": [
        -0.031,
        0.0243
      ],
      "C2": true,
      "C3_min_z": -2.16,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0003,
      "logloss_vs_book_ci": [
        -0.0019,
        0.0011
      ],
      "mean_p": 0.2126,
      "actual": 0.2088,
      "fair_odds": 5.41
    },
    "replication_2019_20_to_2023_24": {
      "league": "SUPERLIG",
      "market": "away_score_both_halves",
      "n": 1798,
      "status": "PASS",
      "C1_slope": 0.983,
      "C1_ci": [
        0.737,
        1.229
      ],
      "C1": true,
      "C2_level": -0.0051,
      "C2_ci": [
        -0.024,
        0.0128
      ],
      "C2": true,
      "C3_min_z": -1.78,
      "C3": true,
      "C4_lifted_legs": 1,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0,
      "logloss_vs_book_ci": [
        -0.0007,
        0.0008
      ],
      "mean_p": 0.212,
      "actual": 0.2069,
      "fair_odds": 5.05
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "SUPERLIG",
    "market": "home_win_both_halves",
    "primary_2024_25_plus": {
      "league": "SUPERLIG",
      "market": "home_win_both_halves",
      "n": 728,
      "status": "PASS",
      "C1_slope": 1.159,
      "C1_ci": [
        0.833,
        1.486
      ],
      "C1": true,
      "C2_level": -0.015,
      "C2_ci": [
        -0.0387,
        0.0089
      ],
      "C2": true,
      "C3_min_z": -1.55,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0001,
      "logloss_vs_book_ci": [
        -0.0004,
        0.0006
      ],
      "mean_p": 0.14,
      "actual": 0.125,
      "fair_odds": 8.25
    },
    "replication_2019_20_to_2023_24": {
      "league": "SUPERLIG",
      "market": "home_win_both_halves",
      "n": 1798,
      "status": "PASS",
      "C1_slope": 0.99,
      "C1_ci": [
        0.762,
        1.217
      ],
      "C1": true,
      "C2_level": 0.0093,
      "C2_ci": [
        -0.0048,
        0.0244
      ],
      "C2": true,
      "C3_min_z": -0.83,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0007,
      "logloss_vs_book_ci": [
        -0.0002,
        0.0017
      ],
      "mean_p": 0.1314,
      "actual": 0.1407,
      "fair_odds": 8.54
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "SUPERLIG",
    "market": "away_win_both_halves",
    "primary_2024_25_plus": {
      "league": "SUPERLIG",
      "market": "away_win_both_halves",
      "n": 728,
      "status": "PASS",
      "C1_slope": 1.335,
      "C1_ci": [
        0.975,
        1.694
      ],
      "C1": true,
      "C2_level": -0.0147,
      "C2_ci": [
        -0.0314,
        0.0021
      ],
      "C2": true,
      "C3_min_z": -1.49,
      "C3": true,
      "C4_lifted_legs": 18,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0046,
      "logloss_vs_book_ci": [
        -0.0068,
        -0.0023
      ],
      "mean_p": 0.0793,
      "actual": 0.0646,
      "fair_odds": 19.45
    },
    "replication_2019_20_to_2023_24": {
      "league": "SUPERLIG",
      "market": "away_win_both_halves",
      "n": 1798,
      "status": "PASS",
      "C1_slope": 0.982,
      "C1_ci": [
        0.743,
        1.22
      ],
      "C1": true,
      "C2_level": -0.0062,
      "C2_ci": [
        -0.0179,
        0.0051
      ],
      "C2": true,
      "C3_min_z": -1.83,
      "C3": true,
      "C4_lifted_legs": 30,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0006,
      "logloss_vs_book_ci": [
        -0.002,
        0.0009
      ],
      "mean_p": 0.0757,
      "actual": 0.0695,
      "fair_odds": 16.49
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "SUPERLIG",
    "market": "home_fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "SUPERLIG",
      "market": "home_fh_over_0.5",
      "n": 728,
      "status": "PASS",
      "C1_slope": 1.103,
      "C1_ci": [
        0.781,
        1.426
      ],
      "C1": true,
      "C2_level": -0.0068,
      "C2_ci": [
        -0.0428,
        0.026
      ],
      "C2": true,
      "C3_min_z": -1.74,
      "C3": true,
      "C4_lifted_legs": 366,
      "C4_z": 0.04,
      "C4": true,
      "logloss_vs_book": -0.0029,
      "logloss_vs_book_ci": [
        -0.0083,
        0.003
      ],
      "mean_p": 0.5164,
      "actual": 0.5096,
      "fair_odds": 1.97
    },
    "replication_2019_20_to_2023_24": {
      "league": "SUPERLIG",
      "market": "home_fh_over_0.5",
      "n": 1798,
      "status": "PASS",
      "C1_slope": 0.999,
      "C1_ci": [
        0.75,
        1.247
      ],
      "C1": true,
      "C2_level": -0.014,
      "C2_ci": [
        -0.0351,
        0.0072
      ],
      "C2": true,
      "C3_min_z": -1.98,
      "C3": true,
      "C4_lifted_legs": 988,
      "C4_z": -1.05,
      "C4": true,
      "logloss_vs_book": -0.0001,
      "logloss_vs_book_ci": [
        -0.0035,
        0.0033
      ],
      "mean_p": 0.5173,
      "actual": 0.5033,
      "fair_odds": 1.96
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "SUPERLIG",
    "market": "away_fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "SUPERLIG",
      "market": "away_fh_over_0.5",
      "n": 728,
      "status": "PASS",
      "C1_slope": 1.32,
      "C1_ci": [
        0.932,
        1.709
      ],
      "C1": true,
      "C2_level": -0.0162,
      "C2_ci": [
        -0.0551,
        0.0205
      ],
      "C2": true,
      "C3_min_z": -1.99,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0003,
      "logloss_vs_book_ci": [
        -0.0018,
        0.0013
      ],
      "mean_p": 0.4256,
      "actual": 0.4093,
      "fair_odds": 2.46
    },
    "replication_2019_20_to_2023_24": {
      "league": "SUPERLIG",
      "market": "away_fh_over_0.5",
      "n": 1798,
      "status": "FAIL",
      "C1_slope": 0.975,
      "C1_ci": [
        0.681,
        1.269
      ],
      "C1": true,
      "C2_level": -0.0152,
      "C2_ci": [
        -0.0373,
        0.0063
      ],
      "C2": true,
      "C3_min_z": -3.42,
      "C3": false,
      "C4_lifted_legs": 87,
      "C4_z": -1.07,
      "C4": true,
      "logloss_vs_book": 0.0013,
      "logloss_vs_book_ci": [
        -0.0003,
        0.0028
      ],
      "mean_p": 0.4273,
      "actual": 0.4121,
      "fair_odds": 2.39
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "league": "SUPERLIG",
    "market": "home_sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "SUPERLIG",
      "market": "home_sh_over_0.5",
      "n": 728,
      "status": "PASS",
      "C1_slope": 1.135,
      "C1_ci": [
        0.778,
        1.491
      ],
      "C1": true,
      "C2_level": -0.0169,
      "C2_ci": [
        -0.0486,
        0.0157
      ],
      "C2": true,
      "C3_min_z": -1.84,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0,
      "logloss_vs_book_ci": [
        -0.0007,
        0.0008
      ],
      "mean_p": 0.576,
      "actual": 0.5591,
      "fair_odds": 1.76
    },
    "replication_2019_20_to_2023_24": {
      "league": "SUPERLIG",
      "market": "home_sh_over_0.5",
      "n": 1798,
      "status": "PASS",
      "C1_slope": 1.001,
      "C1_ci": [
        0.729,
        1.273
      ],
      "C1": true,
      "C2_level": 0.0078,
      "C2_ci": [
        -0.0138,
        0.0297
      ],
      "C2": true,
      "C3_min_z": -1.93,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0001,
      "logloss_vs_book_ci": [
        -0.0004,
        0.0005
      ],
      "mean_p": 0.5818,
      "actual": 0.5895,
      "fair_odds": 1.73
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "league": "SUPERLIG",
    "market": "away_sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "SUPERLIG",
      "market": "away_sh_over_0.5",
      "n": 728,
      "status": "PASS",
      "C1_slope": 0.806,
      "C1_ci": [
        0.428,
        1.184
      ],
      "C1": true,
      "C2_level": -0.0022,
      "C2_ci": [
        -0.0372,
        0.0316
      ],
      "C2": true,
      "C3_min_z": -1.07,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0007,
      "logloss_vs_book_ci": [
        -0.0024,
        0.0009
      ],
      "mean_p": 0.4912,
      "actual": 0.489,
      "fair_odds": 2.11
    },
    "replication_2019_20_to_2023_24": {
      "league": "SUPERLIG",
      "market": "away_sh_over_0.5",
      "n": 1798,
      "status": "PASS",
      "C1_slope": 0.922,
      "C1_ci": [
        0.626,
        1.219
      ],
      "C1": true,
      "C2_level": 0.0114,
      "C2_ci": [
        -0.0106,
        0.0353
      ],
      "C2": true,
      "C3_min_z": -0.8,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0012,
      "logloss_vs_book_ci": [
        0.0,
        0.0025
      ],
      "mean_p": 0.4941,
      "actual": 0.5056,
      "fair_odds": 2.05
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  }
]
```
