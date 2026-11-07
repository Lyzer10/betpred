# Replication of Tasks 16 and 17 on 2019/20-2023/24 (PROJECT.md task 21, pre-registered 2026-11-07)

## Design
- Re-judges every league x market pair from Task 16 (9 leagues x 6 half markets = 54 pairs) and Task 17 (5 main leagues x 5 UP markets = 25 pairs) on **`2019/20-2023/24`** using the exact same raw-probability formulas, walk-forward Platt calibration (`LogisticRegression(C=1.0)` on `logit(raw)` fitted on earlier seasons only), and `market_gates.evaluate` (`SEED = 20261029`).
- Earlier reports (`reports/half_markets_study.md` and `reports/up_markets_study.md`) are unchanged; their `2024/25+` numbers are reproduced identically below alongside the `2019/20-2023/24` replication.
- **Strong candidate** = `PASS` in both `2024/25+` and `2019/20-2023/24` (pending real Betpawa prices); otherwise `stays out`.

## Summary
- **Task 16 (Goals by half & Win Either Half, 54 pairs)**: Primary `2024/25+` **49 PASS / 5 FAIL**; Replication `2019/20-2023/24` **48 PASS / 6 FAIL**; Strong candidates (`PASS` in both): **44 / 54**.
- **Task 17 (Double Chance 1UP & 1X2 2UP, 25 pairs)**: Primary `2024/25+` **24 PASS / 1 FAIL**; Replication `2019/20-2023/24` **25 PASS / 0 FAIL**; Strong candidates (`PASS` in both): **24 / 25**.
- **Combined (79 pairs)**: Primary **73 PASS / 6 FAIL**; Replication **73 PASS / 6 FAIL**; Strong candidates (`PASS` in both): **68 / 79**.

## Part 1 — Task 16 Replication (Goals by Half & Win Either Half, 9 Live Leagues)
| League | Market | 2024/25+ n | 2024/25+ Said | 2024/25+ Won | Fair odds | 2024/25+ Gate | 2019/20-23/24 n | 2019/20-23/24 Said | 2019/20-23/24 Won | 2019/20-23/24 Gate | Verdict |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|---|
| EPL | fh_over_0.5 | 830 | 0.7357 | 0.7289 | 1.36 | **PASS** | 1900 | 0.7120 | 0.7300 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EPL | fh_over_1.5 | 830 | 0.3843 | 0.3494 | 2.64 | **FAIL** | 1900 | 0.3659 | 0.3763 | **PASS** | stays out |
| EPL | sh_over_0.5 | 830 | 0.8195 | 0.8133 | 1.22 | **FAIL** | 1900 | 0.8048 | 0.8074 | **PASS** | stays out |
| EPL | sh_over_1.5 | 830 | 0.4965 | 0.4904 | 2.04 | **PASS** | 1900 | 0.4748 | 0.4700 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EPL | home_win_either_half | 830 | 0.5881 | 0.5783 | 1.70 | **PASS** | 1900 | 0.5730 | 0.5758 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EPL | away_win_either_half | 830 | 0.4707 | 0.4976 | 2.15 | **PASS** | 1900 | 0.4616 | 0.4779 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | fh_over_0.5 | 849 | 0.6707 | 0.6867 | 1.51 | **PASS** | 1900 | 0.6516 | 0.6574 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | fh_over_1.5 | 849 | 0.3175 | 0.3251 | 3.31 | **PASS** | 1900 | 0.2916 | 0.3111 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | sh_over_0.5 | 849 | 0.7785 | 0.8057 | 1.29 | **PASS** | 1900 | 0.7772 | 0.7647 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | sh_over_1.5 | 849 | 0.4387 | 0.4441 | 2.36 | **PASS** | 1900 | 0.4385 | 0.4105 | **FAIL** | stays out |
| LALIGA | home_win_either_half | 849 | 0.5831 | 0.6243 | 1.75 | **PASS** | 1900 | 0.5743 | 0.5758 | **FAIL** | stays out |
| LALIGA | away_win_either_half | 849 | 0.4306 | 0.4370 | 2.40 | **PASS** | 1900 | 0.4280 | 0.4237 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | fh_over_0.5 | 830 | 0.6787 | 0.6699 | 1.48 | **PASS** | 1898 | 0.6999 | 0.7297 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | fh_over_1.5 | 830 | 0.3090 | 0.2988 | 3.28 | **PASS** | 1898 | 0.3393 | 0.3546 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | sh_over_0.5 | 830 | 0.7805 | 0.7807 | 1.28 | **PASS** | 1898 | 0.8156 | 0.8130 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | sh_over_1.5 | 830 | 0.4351 | 0.4253 | 2.32 | **PASS** | 1898 | 0.4942 | 0.4784 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | home_win_either_half | 830 | 0.5558 | 0.5386 | 1.79 | **PASS** | 1898 | 0.5705 | 0.5685 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | away_win_either_half | 830 | 0.4660 | 0.4892 | 2.19 | **PASS** | 1898 | 0.4788 | 0.4942 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | fh_over_0.5 | 665 | 0.7754 | 0.7744 | 1.29 | **PASS** | 1530 | 0.7559 | 0.7601 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | fh_over_1.5 | 665 | 0.4359 | 0.4346 | 2.32 | **PASS** | 1530 | 0.4020 | 0.4235 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | sh_over_0.5 | 665 | 0.8290 | 0.8436 | 1.21 | **PASS** | 1530 | 0.8255 | 0.8346 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | sh_over_1.5 | 665 | 0.5363 | 0.5398 | 1.87 | **PASS** | 1530 | 0.5493 | 0.5353 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | home_win_either_half | 665 | 0.5917 | 0.5714 | 1.71 | **PASS** | 1530 | 0.5824 | 0.5804 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | away_win_either_half | 665 | 0.4618 | 0.4872 | 2.17 | **PASS** | 1530 | 0.4574 | 0.4725 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | fh_over_0.5 | 675 | 0.7438 | 0.7274 | 1.35 | **PASS** | 1725 | 0.7103 | 0.7171 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | fh_over_1.5 | 675 | 0.3801 | 0.3511 | 2.69 | **PASS** | 1725 | 0.3401 | 0.3496 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | sh_over_0.5 | 675 | 0.8094 | 0.8104 | 1.24 | **PASS** | 1725 | 0.7990 | 0.7814 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | sh_over_1.5 | 675 | 0.4826 | 0.4770 | 2.10 | **PASS** | 1725 | 0.4655 | 0.4493 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | home_win_either_half | 675 | 0.5804 | 0.5867 | 1.71 | **PASS** | 1725 | 0.5824 | 0.5652 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | away_win_either_half | 675 | 0.4780 | 0.4578 | 2.12 | **PASS** | 1725 | 0.4564 | 0.4841 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EREDIV | fh_over_0.5 | 701 | 0.7562 | 0.7803 | 1.33 | **PASS** | 1456 | 0.7554 | 0.7383 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EREDIV | fh_over_1.5 | 701 | 0.4138 | 0.4251 | 2.48 | **PASS** | 1456 | 0.4080 | 0.3942 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EREDIV | sh_over_0.5 | 701 | 0.8420 | 0.8459 | 1.19 | **PASS** | 1456 | 0.8363 | 0.8310 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EREDIV | sh_over_1.5 | 701 | 0.5336 | 0.5264 | 1.90 | **FAIL** | 1456 | 0.5227 | 0.5220 | **PASS** | stays out |
| EREDIV | home_win_either_half | 701 | 0.5948 | 0.5863 | 1.70 | **PASS** | 1456 | 0.5953 | 0.5783 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EREDIV | away_win_either_half | 701 | 0.4645 | 0.4679 | 2.17 | **PASS** | 1456 | 0.4592 | 0.4698 | **PASS** | Strong candidate (pending real Betpawa prices) |
| JUPILER | fh_over_0.5 | 702 | 0.7259 | 0.7279 | 1.37 | **PASS** | 1458 | 0.7228 | 0.7414 | **PASS** | Strong candidate (pending real Betpawa prices) |
| JUPILER | fh_over_1.5 | 702 | 0.3645 | 0.3632 | 2.77 | **PASS** | 1458 | 0.3697 | 0.3608 | **PASS** | Strong candidate (pending real Betpawa prices) |
| JUPILER | sh_over_0.5 | 702 | 0.8117 | 0.7650 | 1.23 | **FAIL** | 1458 | 0.8324 | 0.8196 | **PASS** | stays out |
| JUPILER | sh_over_1.5 | 702 | 0.4831 | 0.4516 | 2.07 | **PASS** | 1458 | 0.5164 | 0.4938 | **PASS** | Strong candidate (pending real Betpawa prices) |
| JUPILER | home_win_either_half | 702 | 0.5750 | 0.5769 | 1.74 | **PASS** | 1458 | 0.5761 | 0.5823 | **PASS** | Strong candidate (pending real Betpawa prices) |
| JUPILER | away_win_either_half | 702 | 0.4632 | 0.4459 | 2.20 | **PASS** | 1458 | 0.4612 | 0.4801 | **PASS** | Strong candidate (pending real Betpawa prices) |
| PRIMEIRA | fh_over_0.5 | 693 | 0.7061 | 0.6941 | 1.43 | **FAIL** | 1530 | 0.7179 | 0.6908 | **FAIL** | stays out |
| PRIMEIRA | fh_over_1.5 | 693 | 0.3429 | 0.3362 | 3.06 | **PASS** | 1530 | 0.3501 | 0.3320 | **FAIL** | stays out |
| PRIMEIRA | sh_over_0.5 | 693 | 0.7676 | 0.7879 | 1.32 | **PASS** | 1530 | 0.7628 | 0.7660 | **PASS** | Strong candidate (pending real Betpawa prices) |
| PRIMEIRA | sh_over_1.5 | 693 | 0.4143 | 0.4315 | 2.52 | **PASS** | 1530 | 0.4025 | 0.4196 | **PASS** | Strong candidate (pending real Betpawa prices) |
| PRIMEIRA | home_win_either_half | 693 | 0.5618 | 0.5613 | 1.75 | **PASS** | 1530 | 0.5721 | 0.5562 | **PASS** | Strong candidate (pending real Betpawa prices) |
| PRIMEIRA | away_win_either_half | 693 | 0.4687 | 0.4646 | 2.20 | **PASS** | 1530 | 0.4639 | 0.4673 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SUPERLIG | fh_over_0.5 | 728 | 0.7295 | 0.7212 | 1.38 | **PASS** | 1798 | 0.7248 | 0.7119 | **FAIL** | stays out |
| SUPERLIG | fh_over_1.5 | 728 | 0.3658 | 0.3503 | 2.81 | **PASS** | 1798 | 0.3681 | 0.3454 | **FAIL** | stays out |
| SUPERLIG | sh_over_0.5 | 728 | 0.7958 | 0.7802 | 1.26 | **PASS** | 1798 | 0.7996 | 0.8053 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SUPERLIG | sh_over_1.5 | 728 | 0.4702 | 0.4794 | 2.18 | **PASS** | 1798 | 0.4651 | 0.4811 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SUPERLIG | home_win_either_half | 728 | 0.5960 | 0.6113 | 1.64 | **PASS** | 1798 | 0.6000 | 0.5951 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SUPERLIG | away_win_either_half | 728 | 0.4538 | 0.4492 | 2.30 | **PASS** | 1798 | 0.4536 | 0.4549 | **PASS** | Strong candidate (pending real Betpawa prices) |

## Part 2 — Task 17 Replication (Double Chance 1UP & 1X2 2UP, 5 Main Leagues)
| League | Market | 2024/25+ n | 2024/25+ Said | 2024/25+ Won | Fair odds | 2024/25+ Gate | 2019/20-23/24 n | 2019/20-23/24 Said | 2019/20-23/24 Won | 2019/20-23/24 Gate | Verdict |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|---|---|
| EPL | dc1up_1x | 830 | 0.7410 | 0.7398 | 1.31 | **PASS** | 1900 | 0.7294 | 0.7305 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EPL | dc1up_x2 | 830 | 0.6305 | 0.6627 | 1.55 | **PASS** | 1900 | 0.6257 | 0.6379 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EPL | dc1up_12 | 830 | 0.9462 | 0.9422 | 1.06 | **PASS** | 1900 | 0.9351 | 0.9437 | **PASS** | Strong candidate (pending real Betpawa prices) |
| EPL | home_2up | 830 | 0.4680 | 0.4337 | 2.19 | **FAIL** | 1900 | 0.4611 | 0.4579 | **PASS** | stays out |
| EPL | away_2up | 830 | 0.3418 | 0.3434 | 3.10 | **PASS** | 1900 | 0.3432 | 0.3489 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | dc1up_1x | 805 | 0.7572 | 0.7801 | 1.29 | **PASS** | 1900 | 0.7492 | 0.7621 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | dc1up_x2 | 805 | 0.6192 | 0.6037 | 1.57 | **PASS** | 1900 | 0.6251 | 0.6184 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | dc1up_12 | 805 | 0.9209 | 0.9453 | 1.09 | **PASS** | 1900 | 0.9149 | 0.9142 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | home_2up | 805 | 0.4628 | 0.4807 | 2.27 | **PASS** | 1900 | 0.4544 | 0.4547 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LALIGA | away_2up | 805 | 0.3027 | 0.3006 | 3.58 | **PASS** | 1900 | 0.3049 | 0.2953 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | dc1up_1x | 803 | 0.7351 | 0.7173 | 1.30 | **PASS** | 1898 | 0.7335 | 0.7323 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | dc1up_x2 | 803 | 0.6530 | 0.6588 | 1.49 | **PASS** | 1898 | 0.6524 | 0.6596 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | dc1up_12 | 803 | 0.9202 | 0.9191 | 1.09 | **PASS** | 1898 | 0.9355 | 0.9410 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | home_2up | 803 | 0.4234 | 0.4159 | 2.45 | **PASS** | 1898 | 0.4363 | 0.4299 | **PASS** | Strong candidate (pending real Betpawa prices) |
| SERIEA | away_2up | 803 | 0.3381 | 0.3624 | 3.25 | **PASS** | 1898 | 0.3509 | 0.3567 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | dc1up_1x | 638 | 0.7542 | 0.7429 | 1.30 | **PASS** | 1530 | 0.7476 | 0.7386 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | dc1up_x2 | 638 | 0.6220 | 0.6458 | 1.57 | **PASS** | 1530 | 0.6209 | 0.6346 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | dc1up_12 | 638 | 0.9475 | 0.9404 | 1.05 | **PASS** | 1530 | 0.9420 | 0.9516 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | home_2up | 638 | 0.4754 | 0.4561 | 2.17 | **PASS** | 1530 | 0.4718 | 0.4595 | **PASS** | Strong candidate (pending real Betpawa prices) |
| BUNDES | away_2up | 638 | 0.3251 | 0.3589 | 3.23 | **PASS** | 1530 | 0.3298 | 0.3359 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | dc1up_1x | 638 | 0.7340 | 0.7304 | 1.31 | **PASS** | 1725 | 0.7439 | 0.7316 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | dc1up_x2 | 638 | 0.6408 | 0.6254 | 1.53 | **PASS** | 1725 | 0.6285 | 0.6586 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | dc1up_12 | 638 | 0.9430 | 0.9342 | 1.06 | **PASS** | 1725 | 0.9354 | 0.9281 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | home_2up | 638 | 0.4559 | 0.4718 | 2.21 | **PASS** | 1725 | 0.4577 | 0.4371 | **PASS** | Strong candidate (pending real Betpawa prices) |
| LIGUE1 | away_2up | 638 | 0.3452 | 0.3386 | 3.10 | **PASS** | 1725 | 0.3273 | 0.3467 | **PASS** | Strong candidate (pending real Betpawa prices) |

## Full Gate Details
```json
[
  {
    "task": 16,
    "league": "EPL",
    "market": "fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "fh_over_0.5",
      "n": 830,
      "status": "PASS",
      "C1_slope": 1.096,
      "C1_ci": [
        0.461,
        1.731
      ],
      "C1": true,
      "C2_level": -0.0067,
      "C2_ci": [
        -0.0402,
        0.0248
      ],
      "C2": true,
      "C3_min_z": -1.24,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0004,
      "logloss_vs_book_ci": [
        -0.002,
        0.0013
      ],
      "mean_p": 0.7357,
      "actual": 0.7289,
      "fair_odds": 1.36
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "fh_over_0.5",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.27,
      "C1_ci": [
        0.864,
        1.676
      ],
      "C1": true,
      "C2_level": 0.018,
      "C2_ci": [
        -0.0014,
        0.0376
      ],
      "C2": true,
      "C3_min_z": -1.17,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0003,
      "logloss_vs_book_ci": [
        -0.0008,
        0.0015
      ],
      "mean_p": 0.712,
      "actual": 0.73,
      "fair_odds": 1.41
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "EPL",
    "market": "fh_over_1.5",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "fh_over_1.5",
      "n": 830,
      "status": "FAIL",
      "C1_slope": 0.885,
      "C1_ci": [
        0.202,
        1.568
      ],
      "C1": true,
      "C2_level": -0.0349,
      "C2_ci": [
        -0.0711,
        -0.0007
      ],
      "C2": false,
      "C3_min_z": -2.77,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0006,
      "logloss_vs_book_ci": [
        -0.0002,
        0.0013
      ],
      "mean_p": 0.3843,
      "actual": 0.3494,
      "fair_odds": 2.64
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "fh_over_1.5",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.231,
      "C1_ci": [
        0.827,
        1.634
      ],
      "C1": true,
      "C2_level": 0.0104,
      "C2_ci": [
        -0.011,
        0.0321
      ],
      "C2": true,
      "C3_min_z": -1.46,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0008,
      "logloss_vs_book_ci": [
        -0.0001,
        0.0016
      ],
      "mean_p": 0.3659,
      "actual": 0.3763,
      "fair_odds": 2.78
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "task": 16,
    "league": "EPL",
    "market": "sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "sh_over_0.5",
      "n": 830,
      "status": "FAIL",
      "C1_slope": -0.138,
      "C1_ci": [
        -0.894,
        0.619
      ],
      "C1": false,
      "C2_level": -0.0063,
      "C2_ci": [
        -0.0317,
        0.0198
      ],
      "C2": true,
      "C3_min_z": -3.31,
      "C3": false,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0001,
      "logloss_vs_book_ci": [
        -0.0032,
        0.0032
      ],
      "mean_p": 0.8195,
      "actual": 0.8133,
      "fair_odds": 1.22
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "sh_over_0.5",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.153,
      "C1_ci": [
        0.648,
        1.658
      ],
      "C1": true,
      "C2_level": 0.0026,
      "C2_ci": [
        -0.0169,
        0.0204
      ],
      "C2": true,
      "C3_min_z": -1.45,
      "C3": true,
      "C4_lifted_legs": 3,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0001,
      "logloss_vs_book_ci": [
        -0.0017,
        0.0017
      ],
      "mean_p": 0.8048,
      "actual": 0.8074,
      "fair_odds": 1.24
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "task": 16,
    "league": "EPL",
    "market": "sh_over_1.5",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "sh_over_1.5",
      "n": 830,
      "status": "PASS",
      "C1_slope": 0.518,
      "C1_ci": [
        -0.103,
        1.14
      ],
      "C1": true,
      "C2_level": -0.0061,
      "C2_ci": [
        -0.0407,
        0.0297
      ],
      "C2": true,
      "C3_min_z": -2.22,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0001,
      "logloss_vs_book_ci": [
        -0.0019,
        0.0017
      ],
      "mean_p": 0.4965,
      "actual": 0.4904,
      "fair_odds": 2.04
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "sh_over_1.5",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.045,
      "C1_ci": [
        0.654,
        1.436
      ],
      "C1": true,
      "C2_level": -0.0048,
      "C2_ci": [
        -0.0257,
        0.0177
      ],
      "C2": true,
      "C3_min_z": -1.53,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0018,
      "logloss_vs_book_ci": [
        0.0003,
        0.0032
      ],
      "mean_p": 0.4748,
      "actual": 0.47,
      "fair_odds": 2.13
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "EPL",
    "market": "home_win_either_half",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "home_win_either_half",
      "n": 830,
      "status": "PASS",
      "C1_slope": 1.041,
      "C1_ci": [
        0.825,
        1.257
      ],
      "C1": true,
      "C2_level": -0.0098,
      "C2_ci": [
        -0.0408,
        0.0227
      ],
      "C2": true,
      "C3_min_z": -1.8,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0003,
      "logloss_vs_book_ci": [
        -0.0024,
        0.002
      ],
      "mean_p": 0.5881,
      "actual": 0.5783,
      "fair_odds": 1.7
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "home_win_either_half",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.0,
      "C1_ci": [
        0.868,
        1.131
      ],
      "C1": true,
      "C2_level": 0.0027,
      "C2_ci": [
        -0.0161,
        0.0241
      ],
      "C2": true,
      "C3_min_z": -1.12,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0,
      "logloss_vs_book_ci": [
        -0.0011,
        0.0014
      ],
      "mean_p": 0.573,
      "actual": 0.5758,
      "fair_odds": 1.75
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "EPL",
    "market": "away_win_either_half",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "away_win_either_half",
      "n": 830,
      "status": "PASS",
      "C1_slope": 0.917,
      "C1_ci": [
        0.696,
        1.139
      ],
      "C1": true,
      "C2_level": 0.0269,
      "C2_ci": [
        -0.0071,
        0.0619
      ],
      "C2": true,
      "C3_min_z": -1.47,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0004,
      "logloss_vs_book_ci": [
        -0.0014,
        0.0007
      ],
      "mean_p": 0.4707,
      "actual": 0.4976,
      "fair_odds": 2.15
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "away_win_either_half",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.854,
      "C1_ci": [
        0.728,
        0.981
      ],
      "C1": true,
      "C2_level": 0.0163,
      "C2_ci": [
        -0.0051,
        0.0381
      ],
      "C2": true,
      "C3_min_z": -1.27,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0017,
      "logloss_vs_book_ci": [
        0.0005,
        0.0029
      ],
      "mean_p": 0.4616,
      "actual": 0.4779,
      "fair_odds": 2.21
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "LALIGA",
    "market": "fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "fh_over_0.5",
      "n": 849,
      "status": "PASS",
      "C1_slope": 1.403,
      "C1_ci": [
        0.803,
        2.004
      ],
      "C1": true,
      "C2_level": 0.016,
      "C2_ci": [
        -0.0116,
        0.045
      ],
      "C2": true,
      "C3_min_z": -1.95,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0011,
      "logloss_vs_book_ci": [
        -0.0004,
        0.0024
      ],
      "mean_p": 0.6707,
      "actual": 0.6867,
      "fair_odds": 1.51
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "fh_over_0.5",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.511,
      "C1_ci": [
        0.098,
        0.924
      ],
      "C1": true,
      "C2_level": 0.0058,
      "C2_ci": [
        -0.0155,
        0.0255
      ],
      "C2": true,
      "C3_min_z": -1.85,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0001,
      "logloss_vs_book_ci": [
        -0.0013,
        0.0018
      ],
      "mean_p": 0.6516,
      "actual": 0.6574,
      "fair_odds": 1.55
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "LALIGA",
    "market": "fh_over_1.5",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "fh_over_1.5",
      "n": 849,
      "status": "PASS",
      "C1_slope": 1.449,
      "C1_ci": [
        1.024,
        1.875
      ],
      "C1": true,
      "C2_level": 0.0076,
      "C2_ci": [
        -0.024,
        0.0374
      ],
      "C2": true,
      "C3_min_z": -2.17,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0005,
      "logloss_vs_book_ci": [
        -0.0012,
        0.0003
      ],
      "mean_p": 0.3175,
      "actual": 0.3251,
      "fair_odds": 3.31
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "fh_over_1.5",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.867,
      "C1_ci": [
        0.535,
        1.199
      ],
      "C1": true,
      "C2_level": 0.0194,
      "C2_ci": [
        -0.0001,
        0.0415
      ],
      "C2": true,
      "C3_min_z": -0.68,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0012,
      "logloss_vs_book_ci": [
        -0.0005,
        0.0028
      ],
      "mean_p": 0.2916,
      "actual": 0.3111,
      "fair_odds": 3.55
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "LALIGA",
    "market": "sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "sh_over_0.5",
      "n": 849,
      "status": "PASS",
      "C1_slope": 0.996,
      "C1_ci": [
        0.453,
        1.54
      ],
      "C1": true,
      "C2_level": 0.0272,
      "C2_ci": [
        -0.0005,
        0.0512
      ],
      "C2": true,
      "C3_min_z": -0.88,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0027,
      "logloss_vs_book_ci": [
        -0.0048,
        -0.0005
      ],
      "mean_p": 0.7785,
      "actual": 0.8057,
      "fair_odds": 1.29
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "sh_over_0.5",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.369,
      "C1_ci": [
        0.887,
        1.851
      ],
      "C1": true,
      "C2_level": -0.0125,
      "C2_ci": [
        -0.0305,
        0.0042
      ],
      "C2": true,
      "C3_min_z": -2.89,
      "C3": true,
      "C4_lifted_legs": 181,
      "C4_z": -0.32,
      "C4": true,
      "logloss_vs_book": 0.0008,
      "logloss_vs_book_ci": [
        -0.0013,
        0.0029
      ],
      "mean_p": 0.7772,
      "actual": 0.7647,
      "fair_odds": 1.29
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "LALIGA",
    "market": "sh_over_1.5",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "sh_over_1.5",
      "n": 849,
      "status": "PASS",
      "C1_slope": 0.727,
      "C1_ci": [
        0.343,
        1.111
      ],
      "C1": true,
      "C2_level": 0.0053,
      "C2_ci": [
        -0.0264,
        0.0421
      ],
      "C2": true,
      "C3_min_z": -2.04,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0,
      "logloss_vs_book_ci": [
        -0.0011,
        0.001
      ],
      "mean_p": 0.4387,
      "actual": 0.4441,
      "fair_odds": 2.36
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "sh_over_1.5",
      "n": 1900,
      "status": "FAIL",
      "C1_slope": 1.246,
      "C1_ci": [
        0.887,
        1.605
      ],
      "C1": true,
      "C2_level": -0.028,
      "C2_ci": [
        -0.0507,
        -0.0044
      ],
      "C2": false,
      "C3_min_z": -2.17,
      "C3": true,
      "C4_lifted_legs": 367,
      "C4_z": -1.37,
      "C4": true,
      "logloss_vs_book": 0.0016,
      "logloss_vs_book_ci": [
        -0.0003,
        0.0036
      ],
      "mean_p": 0.4385,
      "actual": 0.4105,
      "fair_odds": 2.33
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "task": 16,
    "league": "LALIGA",
    "market": "home_win_either_half",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "home_win_either_half",
      "n": 849,
      "status": "PASS",
      "C1_slope": 1.001,
      "C1_ci": [
        0.772,
        1.23
      ],
      "C1": true,
      "C2_level": 0.0412,
      "C2_ci": [
        0.0121,
        0.0741
      ],
      "C2": true,
      "C3_min_z": -0.3,
      "C3": true,
      "C4_lifted_legs": 12,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0033,
      "logloss_vs_book_ci": [
        -0.0059,
        -0.0008
      ],
      "mean_p": 0.5831,
      "actual": 0.6243,
      "fair_odds": 1.75
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "home_win_either_half",
      "n": 1900,
      "status": "FAIL",
      "C1_slope": 1.054,
      "C1_ci": [
        0.898,
        1.21
      ],
      "C1": true,
      "C2_level": 0.0015,
      "C2_ci": [
        -0.0199,
        0.0205
      ],
      "C2": true,
      "C3_min_z": -3.21,
      "C3": false,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0006,
      "logloss_vs_book_ci": [
        -0.0019,
        0.0008
      ],
      "mean_p": 0.5743,
      "actual": 0.5758,
      "fair_odds": 1.75
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "task": 16,
    "league": "LALIGA",
    "market": "away_win_either_half",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "away_win_either_half",
      "n": 849,
      "status": "PASS",
      "C1_slope": 1.019,
      "C1_ci": [
        0.797,
        1.241
      ],
      "C1": true,
      "C2_level": 0.0064,
      "C2_ci": [
        -0.024,
        0.0377
      ],
      "C2": true,
      "C3_min_z": -1.42,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0002,
      "logloss_vs_book_ci": [
        -0.0019,
        0.0014
      ],
      "mean_p": 0.4306,
      "actual": 0.437,
      "fair_odds": 2.4
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "away_win_either_half",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.044,
      "C1_ci": [
        0.89,
        1.198
      ],
      "C1": true,
      "C2_level": -0.0043,
      "C2_ci": [
        -0.0228,
        0.0158
      ],
      "C2": true,
      "C3_min_z": -1.9,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0004,
      "logloss_vs_book_ci": [
        -0.0016,
        0.0007
      ],
      "mean_p": 0.428,
      "actual": 0.4237,
      "fair_odds": 2.39
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "SERIEA",
    "market": "fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "fh_over_0.5",
      "n": 830,
      "status": "PASS",
      "C1_slope": 1.097,
      "C1_ci": [
        0.218,
        1.976
      ],
      "C1": true,
      "C2_level": -0.0089,
      "C2_ci": [
        -0.0419,
        0.0223
      ],
      "C2": true,
      "C3_min_z": -2.11,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0005,
        0.0008
      ],
      "mean_p": 0.6787,
      "actual": 0.6699,
      "fair_odds": 1.48
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "fh_over_0.5",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 1.04,
      "C1_ci": [
        0.448,
        1.632
      ],
      "C1": true,
      "C2_level": 0.0298,
      "C2_ci": [
        0.009,
        0.0498
      ],
      "C2": true,
      "C3_min_z": -0.52,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0016,
      "logloss_vs_book_ci": [
        0.0005,
        0.0027
      ],
      "mean_p": 0.6999,
      "actual": 0.7297,
      "fair_odds": 1.43
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "SERIEA",
    "market": "fh_over_1.5",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "fh_over_1.5",
      "n": 830,
      "status": "PASS",
      "C1_slope": 1.282,
      "C1_ci": [
        0.444,
        2.121
      ],
      "C1": true,
      "C2_level": -0.0102,
      "C2_ci": [
        -0.0393,
        0.021
      ],
      "C2": true,
      "C3_min_z": -2.03,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0003,
      "logloss_vs_book_ci": [
        -0.0006,
        0.0012
      ],
      "mean_p": 0.309,
      "actual": 0.2988,
      "fair_odds": 3.28
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "fh_over_1.5",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 0.966,
      "C1_ci": [
        0.429,
        1.503
      ],
      "C1": true,
      "C2_level": 0.0153,
      "C2_ci": [
        -0.0062,
        0.0371
      ],
      "C2": true,
      "C3_min_z": -0.78,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.001,
      "logloss_vs_book_ci": [
        -0.0004,
        0.0023
      ],
      "mean_p": 0.3393,
      "actual": 0.3546,
      "fair_odds": 2.96
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "SERIEA",
    "market": "sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "sh_over_0.5",
      "n": 830,
      "status": "PASS",
      "C1_slope": 0.652,
      "C1_ci": [
        -0.099,
        1.404
      ],
      "C1": true,
      "C2_level": 0.0002,
      "C2_ci": [
        -0.0278,
        0.0291
      ],
      "C2": true,
      "C3_min_z": -1.63,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0006,
      "logloss_vs_book_ci": [
        -0.0038,
        0.0024
      ],
      "mean_p": 0.7805,
      "actual": 0.7807,
      "fair_odds": 1.28
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "sh_over_0.5",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 0.915,
      "C1_ci": [
        0.478,
        1.351
      ],
      "C1": true,
      "C2_level": -0.0027,
      "C2_ci": [
        -0.0214,
        0.015
      ],
      "C2": true,
      "C3_min_z": -1.68,
      "C3": true,
      "C4_lifted_legs": 172,
      "C4_z": -1.06,
      "C4": true,
      "logloss_vs_book": -0.0011,
      "logloss_vs_book_ci": [
        -0.0038,
        0.0017
      ],
      "mean_p": 0.8156,
      "actual": 0.813,
      "fair_odds": 1.22
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "SERIEA",
    "market": "sh_over_1.5",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "sh_over_1.5",
      "n": 830,
      "status": "PASS",
      "C1_slope": 0.62,
      "C1_ci": [
        -0.019,
        1.259
      ],
      "C1": true,
      "C2_level": -0.0098,
      "C2_ci": [
        -0.0449,
        0.023
      ],
      "C2": true,
      "C3_min_z": -1.65,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0003,
      "logloss_vs_book_ci": [
        -0.0014,
        0.002
      ],
      "mean_p": 0.4351,
      "actual": 0.4253,
      "fair_odds": 2.32
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "sh_over_1.5",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 0.854,
      "C1_ci": [
        0.511,
        1.197
      ],
      "C1": true,
      "C2_level": -0.0158,
      "C2_ci": [
        -0.0376,
        0.0058
      ],
      "C2": true,
      "C3_min_z": -2.09,
      "C3": true,
      "C4_lifted_legs": 586,
      "C4_z": -1.16,
      "C4": true,
      "logloss_vs_book": 0.0005,
      "logloss_vs_book_ci": [
        -0.0019,
        0.0027
      ],
      "mean_p": 0.4942,
      "actual": 0.4784,
      "fair_odds": 2.03
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "SERIEA",
    "market": "home_win_either_half",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "home_win_either_half",
      "n": 830,
      "status": "PASS",
      "C1_slope": 1.087,
      "C1_ci": [
        0.889,
        1.286
      ],
      "C1": true,
      "C2_level": -0.0173,
      "C2_ci": [
        -0.0471,
        0.0128
      ],
      "C2": true,
      "C3_min_z": -1.66,
      "C3": true,
      "C4_lifted_legs": 205,
      "C4_z": -0.14,
      "C4": true,
      "logloss_vs_book": -0.003,
      "logloss_vs_book_ci": [
        -0.007,
        0.0008
      ],
      "mean_p": 0.5558,
      "actual": 0.5386,
      "fair_odds": 1.79
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "home_win_either_half",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 0.898,
      "C1_ci": [
        0.777,
        1.02
      ],
      "C1": true,
      "C2_level": -0.002,
      "C2_ci": [
        -0.0226,
        0.0188
      ],
      "C2": true,
      "C3_min_z": -2.04,
      "C3": true,
      "C4_lifted_legs": 549,
      "C4_z": -1.85,
      "C4": true,
      "logloss_vs_book": 0.0004,
      "logloss_vs_book_ci": [
        -0.0029,
        0.0038
      ],
      "mean_p": 0.5705,
      "actual": 0.5685,
      "fair_odds": 1.75
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "SERIEA",
    "market": "away_win_either_half",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "away_win_either_half",
      "n": 830,
      "status": "PASS",
      "C1_slope": 0.944,
      "C1_ci": [
        0.75,
        1.139
      ],
      "C1": true,
      "C2_level": 0.0231,
      "C2_ci": [
        -0.0103,
        0.0564
      ],
      "C2": true,
      "C3_min_z": -0.5,
      "C3": true,
      "C4_lifted_legs": 290,
      "C4_z": 0.81,
      "C4": true,
      "logloss_vs_book": -0.0028,
      "logloss_vs_book_ci": [
        -0.0065,
        0.0016
      ],
      "mean_p": 0.466,
      "actual": 0.4892,
      "fair_odds": 2.19
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "away_win_either_half",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 1.043,
      "C1_ci": [
        0.909,
        1.176
      ],
      "C1": true,
      "C2_level": 0.0154,
      "C2_ci": [
        -0.0073,
        0.0354
      ],
      "C2": true,
      "C3_min_z": -0.9,
      "C3": true,
      "C4_lifted_legs": 518,
      "C4_z": 1.27,
      "C4": true,
      "logloss_vs_book": -0.0022,
      "logloss_vs_book_ci": [
        -0.0046,
        0.0002
      ],
      "mean_p": 0.4788,
      "actual": 0.4942,
      "fair_odds": 2.1
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "BUNDES",
    "market": "fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "fh_over_0.5",
      "n": 665,
      "status": "PASS",
      "C1_slope": 0.95,
      "C1_ci": [
        0.358,
        1.542
      ],
      "C1": true,
      "C2_level": -0.0009,
      "C2_ci": [
        -0.0296,
        0.0264
      ],
      "C2": true,
      "C3_min_z": -1.23,
      "C3": true,
      "C4_lifted_legs": 260,
      "C4_z": -0.52,
      "C4": true,
      "logloss_vs_book": -0.0021,
      "logloss_vs_book_ci": [
        -0.0069,
        0.0026
      ],
      "mean_p": 0.7754,
      "actual": 0.7744,
      "fair_odds": 1.29
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "fh_over_0.5",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.416,
      "C1_ci": [
        0.953,
        1.878
      ],
      "C1": true,
      "C2_level": 0.0042,
      "C2_ci": [
        -0.0183,
        0.0256
      ],
      "C2": true,
      "C3_min_z": -2.03,
      "C3": true,
      "C4_lifted_legs": 130,
      "C4_z": -0.39,
      "C4": true,
      "logloss_vs_book": -0.0018,
      "logloss_vs_book_ci": [
        -0.004,
        0.0004
      ],
      "mean_p": 0.7559,
      "actual": 0.7601,
      "fair_odds": 1.33
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "BUNDES",
    "market": "fh_over_1.5",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "fh_over_1.5",
      "n": 665,
      "status": "PASS",
      "C1_slope": 1.113,
      "C1_ci": [
        0.62,
        1.606
      ],
      "C1": true,
      "C2_level": -0.0013,
      "C2_ci": [
        -0.0359,
        0.0332
      ],
      "C2": true,
      "C3_min_z": -1.55,
      "C3": true,
      "C4_lifted_legs": 301,
      "C4_z": 0.53,
      "C4": true,
      "logloss_vs_book": -0.0025,
      "logloss_vs_book_ci": [
        -0.0076,
        0.0026
      ],
      "mean_p": 0.4359,
      "actual": 0.4346,
      "fair_odds": 2.32
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "fh_over_1.5",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.142,
      "C1_ci": [
        0.787,
        1.497
      ],
      "C1": true,
      "C2_level": 0.0215,
      "C2_ci": [
        -0.0036,
        0.0467
      ],
      "C2": true,
      "C3_min_z": -0.61,
      "C3": true,
      "C4_lifted_legs": 132,
      "C4_z": 0.97,
      "C4": true,
      "logloss_vs_book": -0.0021,
      "logloss_vs_book_ci": [
        -0.0036,
        -0.0003
      ],
      "mean_p": 0.402,
      "actual": 0.4235,
      "fair_odds": 2.54
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "BUNDES",
    "market": "sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "sh_over_0.5",
      "n": 665,
      "status": "PASS",
      "C1_slope": 1.609,
      "C1_ci": [
        0.703,
        2.515
      ],
      "C1": true,
      "C2_level": 0.0146,
      "C2_ci": [
        -0.0127,
        0.0415
      ],
      "C2": true,
      "C3_min_z": -1.56,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0003,
      "logloss_vs_book_ci": [
        -0.0018,
        0.0013
      ],
      "mean_p": 0.829,
      "actual": 0.8436,
      "fair_odds": 1.21
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "sh_over_0.5",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.185,
      "C1_ci": [
        0.485,
        1.884
      ],
      "C1": true,
      "C2_level": 0.0092,
      "C2_ci": [
        -0.0097,
        0.0278
      ],
      "C2": true,
      "C3_min_z": -1.61,
      "C3": true,
      "C4_lifted_legs": 1,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0005,
      "logloss_vs_book_ci": [
        -0.0008,
        0.0019
      ],
      "mean_p": 0.8255,
      "actual": 0.8346,
      "fair_odds": 1.22
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "BUNDES",
    "market": "sh_over_1.5",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "sh_over_1.5",
      "n": 665,
      "status": "PASS",
      "C1_slope": 1.728,
      "C1_ci": [
        1.079,
        2.377
      ],
      "C1": true,
      "C2_level": 0.0036,
      "C2_ci": [
        -0.0335,
        0.0421
      ],
      "C2": true,
      "C3_min_z": -1.49,
      "C3": true,
      "C4_lifted_legs": 15,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0025,
        0.0029
      ],
      "mean_p": 0.5363,
      "actual": 0.5398,
      "fair_odds": 1.87
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "sh_over_1.5",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 0.955,
      "C1_ci": [
        0.542,
        1.369
      ],
      "C1": true,
      "C2_level": -0.014,
      "C2_ci": [
        -0.0383,
        0.0118
      ],
      "C2": true,
      "C3_min_z": -2.39,
      "C3": true,
      "C4_lifted_legs": 595,
      "C4_z": -1.09,
      "C4": true,
      "logloss_vs_book": 0.0001,
      "logloss_vs_book_ci": [
        -0.0029,
        0.0031
      ],
      "mean_p": 0.5493,
      "actual": 0.5353,
      "fair_odds": 1.84
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "BUNDES",
    "market": "home_win_either_half",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "home_win_either_half",
      "n": 665,
      "status": "PASS",
      "C1_slope": 1.215,
      "C1_ci": [
        0.941,
        1.489
      ],
      "C1": true,
      "C2_level": -0.0203,
      "C2_ci": [
        -0.0559,
        0.0164
      ],
      "C2": true,
      "C3_min_z": -1.48,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0005,
      "logloss_vs_book_ci": [
        -0.0001,
        0.0011
      ],
      "mean_p": 0.5917,
      "actual": 0.5714,
      "fair_odds": 1.71
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "home_win_either_half",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.037,
      "C1_ci": [
        0.872,
        1.201
      ],
      "C1": true,
      "C2_level": -0.002,
      "C2_ci": [
        -0.0252,
        0.0188
      ],
      "C2": true,
      "C3_min_z": -1.03,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.001,
      "logloss_vs_book_ci": [
        0.0002,
        0.0017
      ],
      "mean_p": 0.5824,
      "actual": 0.5804,
      "fair_odds": 1.72
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "BUNDES",
    "market": "away_win_either_half",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "away_win_either_half",
      "n": 665,
      "status": "PASS",
      "C1_slope": 1.164,
      "C1_ci": [
        0.887,
        1.442
      ],
      "C1": true,
      "C2_level": 0.0255,
      "C2_ci": [
        -0.0088,
        0.0569
      ],
      "C2": true,
      "C3_min_z": -1.07,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0022,
      "logloss_vs_book_ci": [
        0.0005,
        0.0038
      ],
      "mean_p": 0.4618,
      "actual": 0.4872,
      "fair_odds": 2.17
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "away_win_either_half",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.012,
      "C1_ci": [
        0.845,
        1.179
      ],
      "C1": true,
      "C2_level": 0.0151,
      "C2_ci": [
        -0.0107,
        0.038
      ],
      "C2": true,
      "C3_min_z": -2.32,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.001,
      "logloss_vs_book_ci": [
        -0.0012,
        0.0031
      ],
      "mean_p": 0.4574,
      "actual": 0.4725,
      "fair_odds": 2.23
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "LIGUE1",
    "market": "fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "fh_over_0.5",
      "n": 675,
      "status": "PASS",
      "C1_slope": 0.368,
      "C1_ci": [
        -0.291,
        1.027
      ],
      "C1": true,
      "C2_level": -0.0163,
      "C2_ci": [
        -0.0502,
        0.0176
      ],
      "C2": true,
      "C3_min_z": -2.13,
      "C3": true,
      "C4_lifted_legs": 219,
      "C4_z": -1.59,
      "C4": true,
      "logloss_vs_book": 0.002,
      "logloss_vs_book_ci": [
        -0.0031,
        0.007
      ],
      "mean_p": 0.7438,
      "actual": 0.7274,
      "fair_odds": 1.35
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "fh_over_0.5",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 0.803,
      "C1_ci": [
        0.452,
        1.154
      ],
      "C1": true,
      "C2_level": 0.0068,
      "C2_ci": [
        -0.0132,
        0.0266
      ],
      "C2": true,
      "C3_min_z": -1.54,
      "C3": true,
      "C4_lifted_legs": 520,
      "C4_z": -1.01,
      "C4": true,
      "logloss_vs_book": -0.0009,
      "logloss_vs_book_ci": [
        -0.0038,
        0.0019
      ],
      "mean_p": 0.7103,
      "actual": 0.7171,
      "fair_odds": 1.41
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "LIGUE1",
    "market": "fh_over_1.5",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "fh_over_1.5",
      "n": 675,
      "status": "PASS",
      "C1_slope": 0.452,
      "C1_ci": [
        -0.146,
        1.049
      ],
      "C1": true,
      "C2_level": -0.029,
      "C2_ci": [
        -0.0653,
        0.0099
      ],
      "C2": true,
      "C3_min_z": -2.27,
      "C3": true,
      "C4_lifted_legs": 91,
      "C4_z": -1.76,
      "C4": true,
      "logloss_vs_book": 0.0027,
      "logloss_vs_book_ci": [
        -0.0005,
        0.0059
      ],
      "mean_p": 0.3801,
      "actual": 0.3511,
      "fair_odds": 2.69
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "fh_over_1.5",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 0.812,
      "C1_ci": [
        0.507,
        1.116
      ],
      "C1": true,
      "C2_level": 0.0095,
      "C2_ci": [
        -0.0126,
        0.0304
      ],
      "C2": true,
      "C3_min_z": -2.4,
      "C3": true,
      "C4_lifted_legs": 227,
      "C4_z": -0.59,
      "C4": true,
      "logloss_vs_book": -0.0,
      "logloss_vs_book_ci": [
        -0.0019,
        0.0019
      ],
      "mean_p": 0.3401,
      "actual": 0.3496,
      "fair_odds": 3.01
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "LIGUE1",
    "market": "sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "sh_over_0.5",
      "n": 675,
      "status": "PASS",
      "C1_slope": 1.553,
      "C1_ci": [
        0.67,
        2.436
      ],
      "C1": true,
      "C2_level": 0.0009,
      "C2_ci": [
        -0.0298,
        0.0303
      ],
      "C2": true,
      "C3_min_z": -1.26,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0007,
      "logloss_vs_book_ci": [
        -0.0029,
        0.0019
      ],
      "mean_p": 0.8094,
      "actual": 0.8104,
      "fair_odds": 1.24
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "sh_over_0.5",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 0.856,
      "C1_ci": [
        0.408,
        1.304
      ],
      "C1": true,
      "C2_level": -0.0175,
      "C2_ci": [
        -0.0372,
        0.0022
      ],
      "C2": true,
      "C3_min_z": -1.64,
      "C3": true,
      "C4_lifted_legs": 28,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0012,
      "logloss_vs_book_ci": [
        -0.0008,
        0.0034
      ],
      "mean_p": 0.799,
      "actual": 0.7814,
      "fair_odds": 1.26
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "LIGUE1",
    "market": "sh_over_1.5",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "sh_over_1.5",
      "n": 675,
      "status": "PASS",
      "C1_slope": 1.375,
      "C1_ci": [
        0.662,
        2.089
      ],
      "C1": true,
      "C2_level": -0.0056,
      "C2_ci": [
        -0.0438,
        0.033
      ],
      "C2": true,
      "C3_min_z": -1.75,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0005,
      "logloss_vs_book_ci": [
        -0.0005,
        0.0014
      ],
      "mean_p": 0.4826,
      "actual": 0.477,
      "fair_odds": 2.1
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "sh_over_1.5",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 0.997,
      "C1_ci": [
        0.594,
        1.4
      ],
      "C1": true,
      "C2_level": -0.0163,
      "C2_ci": [
        -0.0389,
        0.0079
      ],
      "C2": true,
      "C3_min_z": -1.5,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0008,
      "logloss_vs_book_ci": [
        -0.0004,
        0.002
      ],
      "mean_p": 0.4655,
      "actual": 0.4493,
      "fair_odds": 2.19
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "LIGUE1",
    "market": "home_win_either_half",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "home_win_either_half",
      "n": 675,
      "status": "PASS",
      "C1_slope": 1.005,
      "C1_ci": [
        0.77,
        1.24
      ],
      "C1": true,
      "C2_level": 0.0063,
      "C2_ci": [
        -0.0303,
        0.0463
      ],
      "C2": true,
      "C3_min_z": -0.65,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0011,
      "logloss_vs_book_ci": [
        -0.0039,
        0.002
      ],
      "mean_p": 0.5804,
      "actual": 0.5867,
      "fair_odds": 1.71
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "home_win_either_half",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 1.053,
      "C1_ci": [
        0.893,
        1.212
      ],
      "C1": true,
      "C2_level": -0.0172,
      "C2_ci": [
        -0.0398,
        0.0057
      ],
      "C2": true,
      "C3_min_z": -1.56,
      "C3": true,
      "C4_lifted_legs": 160,
      "C4_z": -0.82,
      "C4": true,
      "logloss_vs_book": 0.0,
      "logloss_vs_book_ci": [
        -0.0022,
        0.0025
      ],
      "mean_p": 0.5824,
      "actual": 0.5652,
      "fair_odds": 1.71
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "LIGUE1",
    "market": "away_win_either_half",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "away_win_either_half",
      "n": 675,
      "status": "PASS",
      "C1_slope": 1.076,
      "C1_ci": [
        0.821,
        1.331
      ],
      "C1": true,
      "C2_level": -0.0202,
      "C2_ci": [
        -0.0583,
        0.0181
      ],
      "C2": true,
      "C3_min_z": -0.85,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0007,
      "logloss_vs_book_ci": [
        -0.0017,
        0.0032
      ],
      "mean_p": 0.478,
      "actual": 0.4578,
      "fair_odds": 2.12
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "away_win_either_half",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 0.877,
      "C1_ci": [
        0.724,
        1.031
      ],
      "C1": true,
      "C2_level": 0.0277,
      "C2_ci": [
        0.0058,
        0.0516
      ],
      "C2": true,
      "C3_min_z": -2.27,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0005,
      "logloss_vs_book_ci": [
        -0.0011,
        0.0021
      ],
      "mean_p": 0.4564,
      "actual": 0.4841,
      "fair_odds": 2.26
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "EREDIV",
    "market": "fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "EREDIV",
      "market": "fh_over_0.5",
      "n": 701,
      "status": "PASS",
      "C1_slope": 1.663,
      "C1_ci": [
        0.842,
        2.483
      ],
      "C1": true,
      "C2_level": 0.0241,
      "C2_ci": [
        -0.0047,
        0.0531
      ],
      "C2": true,
      "C3_min_z": -0.78,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0028,
      "logloss_vs_book_ci": [
        -0.005,
        -0.0005
      ],
      "mean_p": 0.7562,
      "actual": 0.7803,
      "fair_odds": 1.33
    },
    "replication_2019_20_to_2023_24": {
      "league": "EREDIV",
      "market": "fh_over_0.5",
      "n": 1456,
      "status": "PASS",
      "C1_slope": 1.317,
      "C1_ci": [
        0.701,
        1.933
      ],
      "C1": true,
      "C2_level": -0.0171,
      "C2_ci": [
        -0.043,
        0.0068
      ],
      "C2": true,
      "C3_min_z": -1.94,
      "C3": true,
      "C4_lifted_legs": 91,
      "C4_z": -1.21,
      "C4": true,
      "logloss_vs_book": 0.0015,
      "logloss_vs_book_ci": [
        -0.0009,
        0.004
      ],
      "mean_p": 0.7554,
      "actual": 0.7383,
      "fair_odds": 1.33
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "EREDIV",
    "market": "fh_over_1.5",
    "primary_2024_25_plus": {
      "league": "EREDIV",
      "market": "fh_over_1.5",
      "n": 701,
      "status": "PASS",
      "C1_slope": 1.774,
      "C1_ci": [
        1.086,
        2.462
      ],
      "C1": true,
      "C2_level": 0.0113,
      "C2_ci": [
        -0.0208,
        0.0411
      ],
      "C2": true,
      "C3_min_z": -1.67,
      "C3": true,
      "C4_lifted_legs": 10,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0012,
      "logloss_vs_book_ci": [
        -0.0037,
        0.0011
      ],
      "mean_p": 0.4138,
      "actual": 0.4251,
      "fair_odds": 2.48
    },
    "replication_2019_20_to_2023_24": {
      "league": "EREDIV",
      "market": "fh_over_1.5",
      "n": 1456,
      "status": "PASS",
      "C1_slope": 1.048,
      "C1_ci": [
        0.539,
        1.558
      ],
      "C1": true,
      "C2_level": -0.0138,
      "C2_ci": [
        -0.0404,
        0.01
      ],
      "C2": true,
      "C3_min_z": -2.12,
      "C3": true,
      "C4_lifted_legs": 134,
      "C4_z": -1.78,
      "C4": true,
      "logloss_vs_book": 0.0013,
      "logloss_vs_book_ci": [
        -0.0009,
        0.0035
      ],
      "mean_p": 0.408,
      "actual": 0.3942,
      "fair_odds": 2.48
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "EREDIV",
    "market": "sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "EREDIV",
      "market": "sh_over_0.5",
      "n": 701,
      "status": "PASS",
      "C1_slope": 0.796,
      "C1_ci": [
        0.082,
        1.509
      ],
      "C1": true,
      "C2_level": 0.0039,
      "C2_ci": [
        -0.0209,
        0.0278
      ],
      "C2": true,
      "C3_min_z": -1.61,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0013,
      "logloss_vs_book_ci": [
        -0.0046,
        0.0023
      ],
      "mean_p": 0.842,
      "actual": 0.8459,
      "fair_odds": 1.19
    },
    "replication_2019_20_to_2023_24": {
      "league": "EREDIV",
      "market": "sh_over_0.5",
      "n": 1456,
      "status": "PASS",
      "C1_slope": 1.056,
      "C1_ci": [
        0.548,
        1.564
      ],
      "C1": true,
      "C2_level": -0.0053,
      "C2_ci": [
        -0.0266,
        0.0132
      ],
      "C2": true,
      "C3_min_z": -2.09,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0003,
      "logloss_vs_book_ci": [
        -0.0023,
        0.0027
      ],
      "mean_p": 0.8363,
      "actual": 0.831,
      "fair_odds": 1.2
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "EREDIV",
    "market": "sh_over_1.5",
    "primary_2024_25_plus": {
      "league": "EREDIV",
      "market": "sh_over_1.5",
      "n": 701,
      "status": "FAIL",
      "C1_slope": 0.519,
      "C1_ci": [
        0.034,
        1.004
      ],
      "C1": true,
      "C2_level": -0.0072,
      "C2_ci": [
        -0.0406,
        0.0244
      ],
      "C2": true,
      "C3_min_z": -2.33,
      "C3": true,
      "C4_lifted_legs": 69,
      "C4_z": -2.53,
      "C4": false,
      "logloss_vs_book": 0.0023,
      "logloss_vs_book_ci": [
        -0.0009,
        0.0051
      ],
      "mean_p": 0.5336,
      "actual": 0.5264,
      "fair_odds": 1.9
    },
    "replication_2019_20_to_2023_24": {
      "league": "EREDIV",
      "market": "sh_over_1.5",
      "n": 1456,
      "status": "PASS",
      "C1_slope": 0.894,
      "C1_ci": [
        0.582,
        1.206
      ],
      "C1": true,
      "C2_level": -0.0008,
      "C2_ci": [
        -0.0288,
        0.0258
      ],
      "C2": true,
      "C3_min_z": -1.58,
      "C3": true,
      "C4_lifted_legs": 201,
      "C4_z": -0.18,
      "C4": true,
      "logloss_vs_book": 0.0011,
      "logloss_vs_book_ci": [
        -0.0013,
        0.0038
      ],
      "mean_p": 0.5227,
      "actual": 0.522,
      "fair_odds": 1.94
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "task": 16,
    "league": "EREDIV",
    "market": "home_win_either_half",
    "primary_2024_25_plus": {
      "league": "EREDIV",
      "market": "home_win_either_half",
      "n": 701,
      "status": "PASS",
      "C1_slope": 0.978,
      "C1_ci": [
        0.761,
        1.194
      ],
      "C1": true,
      "C2_level": -0.0085,
      "C2_ci": [
        -0.0436,
        0.0285
      ],
      "C2": true,
      "C3_min_z": -1.67,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0015,
        0.0018
      ],
      "mean_p": 0.5948,
      "actual": 0.5863,
      "fair_odds": 1.7
    },
    "replication_2019_20_to_2023_24": {
      "league": "EREDIV",
      "market": "home_win_either_half",
      "n": 1456,
      "status": "PASS",
      "C1_slope": 1.07,
      "C1_ci": [
        0.921,
        1.219
      ],
      "C1": true,
      "C2_level": -0.017,
      "C2_ci": [
        -0.0406,
        0.0071
      ],
      "C2": true,
      "C3_min_z": -1.41,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0004,
      "logloss_vs_book_ci": [
        -0.0014,
        0.0023
      ],
      "mean_p": 0.5953,
      "actual": 0.5783,
      "fair_odds": 1.67
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "EREDIV",
    "market": "away_win_either_half",
    "primary_2024_25_plus": {
      "league": "EREDIV",
      "market": "away_win_either_half",
      "n": 701,
      "status": "PASS",
      "C1_slope": 0.869,
      "C1_ci": [
        0.668,
        1.071
      ],
      "C1": true,
      "C2_level": 0.0034,
      "C2_ci": [
        -0.0294,
        0.0365
      ],
      "C2": true,
      "C3_min_z": -1.01,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0012,
      "logloss_vs_book_ci": [
        -0.0012,
        0.0036
      ],
      "mean_p": 0.4645,
      "actual": 0.4679,
      "fair_odds": 2.17
    },
    "replication_2019_20_to_2023_24": {
      "league": "EREDIV",
      "market": "away_win_either_half",
      "n": 1456,
      "status": "PASS",
      "C1_slope": 0.95,
      "C1_ci": [
        0.817,
        1.084
      ],
      "C1": true,
      "C2_level": 0.0106,
      "C2_ci": [
        -0.0142,
        0.0342
      ],
      "C2": true,
      "C3_min_z": -1.68,
      "C3": true,
      "C4_lifted_legs": 23,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.001,
      "logloss_vs_book_ci": [
        -0.0013,
        0.0032
      ],
      "mean_p": 0.4592,
      "actual": 0.4698,
      "fair_odds": 2.24
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "JUPILER",
    "market": "fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "JUPILER",
      "market": "fh_over_0.5",
      "n": 702,
      "status": "PASS",
      "C1_slope": 1.325,
      "C1_ci": [
        0.712,
        1.938
      ],
      "C1": true,
      "C2_level": 0.002,
      "C2_ci": [
        -0.0298,
        0.0318
      ],
      "C2": true,
      "C3_min_z": -1.93,
      "C3": true,
      "C4_lifted_legs": 197,
      "C4_z": 1.04,
      "C4": true,
      "logloss_vs_book": -0.0047,
      "logloss_vs_book_ci": [
        -0.0092,
        -0.0001
      ],
      "mean_p": 0.7259,
      "actual": 0.7279,
      "fair_odds": 1.37
    },
    "replication_2019_20_to_2023_24": {
      "league": "JUPILER",
      "market": "fh_over_0.5",
      "n": 1458,
      "status": "PASS",
      "C1_slope": 1.11,
      "C1_ci": [
        0.56,
        1.66
      ],
      "C1": true,
      "C2_level": 0.0186,
      "C2_ci": [
        -0.0021,
        0.0411
      ],
      "C2": true,
      "C3_min_z": -1.14,
      "C3": true,
      "C4_lifted_legs": 176,
      "C4_z": 0.43,
      "C4": true,
      "logloss_vs_book": -0.0021,
      "logloss_vs_book_ci": [
        -0.0039,
        0.0001
      ],
      "mean_p": 0.7228,
      "actual": 0.7414,
      "fair_odds": 1.39
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "JUPILER",
    "market": "fh_over_1.5",
    "primary_2024_25_plus": {
      "league": "JUPILER",
      "market": "fh_over_1.5",
      "n": 702,
      "status": "PASS",
      "C1_slope": 0.733,
      "C1_ci": [
        0.169,
        1.298
      ],
      "C1": true,
      "C2_level": -0.0012,
      "C2_ci": [
        -0.0369,
        0.0345
      ],
      "C2": true,
      "C3_min_z": -2.26,
      "C3": true,
      "C4_lifted_legs": 135,
      "C4_z": 0.36,
      "C4": true,
      "logloss_vs_book": 0.0004,
      "logloss_vs_book_ci": [
        -0.0035,
        0.0048
      ],
      "mean_p": 0.3645,
      "actual": 0.3632,
      "fair_odds": 2.77
    },
    "replication_2019_20_to_2023_24": {
      "league": "JUPILER",
      "market": "fh_over_1.5",
      "n": 1458,
      "status": "PASS",
      "C1_slope": 1.129,
      "C1_ci": [
        0.625,
        1.633
      ],
      "C1": true,
      "C2_level": -0.009,
      "C2_ci": [
        -0.0324,
        0.0136
      ],
      "C2": true,
      "C3_min_z": -1.47,
      "C3": true,
      "C4_lifted_legs": 215,
      "C4_z": -0.69,
      "C4": true,
      "logloss_vs_book": -0.0002,
      "logloss_vs_book_ci": [
        -0.0025,
        0.0022
      ],
      "mean_p": 0.3697,
      "actual": 0.3608,
      "fair_odds": 2.74
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "JUPILER",
    "market": "sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "JUPILER",
      "market": "sh_over_0.5",
      "n": 702,
      "status": "FAIL",
      "C1_slope": 1.214,
      "C1_ci": [
        0.0,
        2.428
      ],
      "C1": true,
      "C2_level": -0.0467,
      "C2_ci": [
        -0.08,
        -0.0168
      ],
      "C2": false,
      "C3_min_z": -2.81,
      "C3": true,
      "C4_lifted_legs": 41,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0055,
      "logloss_vs_book_ci": [
        0.0022,
        0.0085
      ],
      "mean_p": 0.8117,
      "actual": 0.765,
      "fair_odds": 1.23
    },
    "replication_2019_20_to_2023_24": {
      "league": "JUPILER",
      "market": "sh_over_0.5",
      "n": 1458,
      "status": "PASS",
      "C1_slope": 0.793,
      "C1_ci": [
        -0.379,
        1.966
      ],
      "C1": true,
      "C2_level": -0.0127,
      "C2_ci": [
        -0.033,
        0.0065
      ],
      "C2": true,
      "C3_min_z": -1.76,
      "C3": true,
      "C4_lifted_legs": 110,
      "C4_z": -0.19,
      "C4": true,
      "logloss_vs_book": 0.0003,
      "logloss_vs_book_ci": [
        -0.0024,
        0.0032
      ],
      "mean_p": 0.8324,
      "actual": 0.8196,
      "fair_odds": 1.2
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "task": 16,
    "league": "JUPILER",
    "market": "sh_over_1.5",
    "primary_2024_25_plus": {
      "league": "JUPILER",
      "market": "sh_over_1.5",
      "n": 702,
      "status": "PASS",
      "C1_slope": 1.238,
      "C1_ci": [
        0.409,
        2.066
      ],
      "C1": true,
      "C2_level": -0.0315,
      "C2_ci": [
        -0.0706,
        0.0045
      ],
      "C2": true,
      "C3_min_z": -1.74,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0015,
      "logloss_vs_book_ci": [
        0.0004,
        0.0026
      ],
      "mean_p": 0.4831,
      "actual": 0.4516,
      "fair_odds": 2.07
    },
    "replication_2019_20_to_2023_24": {
      "league": "JUPILER",
      "market": "sh_over_1.5",
      "n": 1458,
      "status": "PASS",
      "C1_slope": 1.068,
      "C1_ci": [
        0.234,
        1.901
      ],
      "C1": true,
      "C2_level": -0.0226,
      "C2_ci": [
        -0.0489,
        0.0026
      ],
      "C2": true,
      "C3_min_z": -2.57,
      "C3": true,
      "C4_lifted_legs": 156,
      "C4_z": -1.68,
      "C4": true,
      "logloss_vs_book": 0.0018,
      "logloss_vs_book_ci": [
        -0.0002,
        0.0038
      ],
      "mean_p": 0.5164,
      "actual": 0.4938,
      "fair_odds": 1.94
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "JUPILER",
    "market": "home_win_either_half",
    "primary_2024_25_plus": {
      "league": "JUPILER",
      "market": "home_win_either_half",
      "n": 702,
      "status": "PASS",
      "C1_slope": 1.104,
      "C1_ci": [
        0.823,
        1.385
      ],
      "C1": true,
      "C2_level": 0.002,
      "C2_ci": [
        -0.0333,
        0.0369
      ],
      "C2": true,
      "C3_min_z": -1.77,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0008,
      "logloss_vs_book_ci": [
        -0.0024,
        0.0009
      ],
      "mean_p": 0.575,
      "actual": 0.5769,
      "fair_odds": 1.74
    },
    "replication_2019_20_to_2023_24": {
      "league": "JUPILER",
      "market": "home_win_either_half",
      "n": 1458,
      "status": "PASS",
      "C1_slope": 1.203,
      "C1_ci": [
        1.01,
        1.395
      ],
      "C1": true,
      "C2_level": 0.0062,
      "C2_ci": [
        -0.0187,
        0.0293
      ],
      "C2": true,
      "C3_min_z": -1.58,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0009,
      "logloss_vs_book_ci": [
        0.0,
        0.0018
      ],
      "mean_p": 0.5761,
      "actual": 0.5823,
      "fair_odds": 1.73
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "JUPILER",
    "market": "away_win_either_half",
    "primary_2024_25_plus": {
      "league": "JUPILER",
      "market": "away_win_either_half",
      "n": 702,
      "status": "PASS",
      "C1_slope": 1.245,
      "C1_ci": [
        0.95,
        1.539
      ],
      "C1": true,
      "C2_level": -0.0173,
      "C2_ci": [
        -0.0566,
        0.0174
      ],
      "C2": true,
      "C3_min_z": -2.36,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0009,
      "logloss_vs_book_ci": [
        -0.0023,
        0.0006
      ],
      "mean_p": 0.4632,
      "actual": 0.4459,
      "fair_odds": 2.2
    },
    "replication_2019_20_to_2023_24": {
      "league": "JUPILER",
      "market": "away_win_either_half",
      "n": 1458,
      "status": "PASS",
      "C1_slope": 1.128,
      "C1_ci": [
        0.939,
        1.318
      ],
      "C1": true,
      "C2_level": 0.0189,
      "C2_ci": [
        -0.007,
        0.0425
      ],
      "C2": true,
      "C3_min_z": -1.68,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0014,
      "logloss_vs_book_ci": [
        0.0001,
        0.0028
      ],
      "mean_p": 0.4612,
      "actual": 0.4801,
      "fair_odds": 2.18
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "PRIMEIRA",
    "market": "fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "PRIMEIRA",
      "market": "fh_over_0.5",
      "n": 693,
      "status": "FAIL",
      "C1_slope": 1.975,
      "C1_ci": [
        1.016,
        2.934
      ],
      "C1": true,
      "C2_level": -0.012,
      "C2_ci": [
        -0.0452,
        0.0229
      ],
      "C2": true,
      "C3_min_z": -1.96,
      "C3": true,
      "C4_lifted_legs": 68,
      "C4_z": -2.07,
      "C4": false,
      "logloss_vs_book": 0.0023,
      "logloss_vs_book_ci": [
        -0.001,
        0.0057
      ],
      "mean_p": 0.7061,
      "actual": 0.6941,
      "fair_odds": 1.43
    },
    "replication_2019_20_to_2023_24": {
      "league": "PRIMEIRA",
      "market": "fh_over_0.5",
      "n": 1530,
      "status": "FAIL",
      "C1_slope": 1.116,
      "C1_ci": [
        0.424,
        1.807
      ],
      "C1": true,
      "C2_level": -0.027,
      "C2_ci": [
        -0.0497,
        -0.0054
      ],
      "C2": false,
      "C3_min_z": -3.3,
      "C3": false,
      "C4_lifted_legs": 739,
      "C4_z": -1.6,
      "C4": true,
      "logloss_vs_book": 0.0018,
      "logloss_vs_book_ci": [
        -0.0015,
        0.0054
      ],
      "mean_p": 0.7179,
      "actual": 0.6908,
      "fair_odds": 1.41
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "task": 16,
    "league": "PRIMEIRA",
    "market": "fh_over_1.5",
    "primary_2024_25_plus": {
      "league": "PRIMEIRA",
      "market": "fh_over_1.5",
      "n": 693,
      "status": "PASS",
      "C1_slope": 1.127,
      "C1_ci": [
        0.527,
        1.727
      ],
      "C1": true,
      "C2_level": -0.0066,
      "C2_ci": [
        -0.0394,
        0.0277
      ],
      "C2": true,
      "C3_min_z": -1.86,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0004,
      "logloss_vs_book_ci": [
        -0.0017,
        0.0024
      ],
      "mean_p": 0.3429,
      "actual": 0.3362,
      "fair_odds": 3.06
    },
    "replication_2019_20_to_2023_24": {
      "league": "PRIMEIRA",
      "market": "fh_over_1.5",
      "n": 1530,
      "status": "FAIL",
      "C1_slope": 1.038,
      "C1_ci": [
        0.559,
        1.517
      ],
      "C1": true,
      "C2_level": -0.0181,
      "C2_ci": [
        -0.04,
        0.0057
      ],
      "C2": true,
      "C3_min_z": -3.01,
      "C3": false,
      "C4_lifted_legs": 162,
      "C4_z": -2.04,
      "C4": false,
      "logloss_vs_book": 0.0015,
      "logloss_vs_book_ci": [
        -0.0007,
        0.0037
      ],
      "mean_p": 0.3501,
      "actual": 0.332,
      "fair_odds": 2.96
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "task": 16,
    "league": "PRIMEIRA",
    "market": "sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "PRIMEIRA",
      "market": "sh_over_0.5",
      "n": 693,
      "status": "PASS",
      "C1_slope": 1.009,
      "C1_ci": [
        0.392,
        1.627
      ],
      "C1": true,
      "C2_level": 0.0203,
      "C2_ci": [
        -0.011,
        0.0487
      ],
      "C2": true,
      "C3_min_z": -1.71,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.001,
      "logloss_vs_book_ci": [
        -0.0028,
        0.001
      ],
      "mean_p": 0.7676,
      "actual": 0.7879,
      "fair_odds": 1.32
    },
    "replication_2019_20_to_2023_24": {
      "league": "PRIMEIRA",
      "market": "sh_over_0.5",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.218,
      "C1_ci": [
        0.741,
        1.694
      ],
      "C1": true,
      "C2_level": 0.0032,
      "C2_ci": [
        -0.0177,
        0.0239
      ],
      "C2": true,
      "C3_min_z": -1.22,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0002,
      "logloss_vs_book_ci": [
        -0.001,
        0.0006
      ],
      "mean_p": 0.7628,
      "actual": 0.766,
      "fair_odds": 1.32
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "PRIMEIRA",
    "market": "sh_over_1.5",
    "primary_2024_25_plus": {
      "league": "PRIMEIRA",
      "market": "sh_over_1.5",
      "n": 693,
      "status": "PASS",
      "C1_slope": 0.989,
      "C1_ci": [
        0.506,
        1.473
      ],
      "C1": true,
      "C2_level": 0.0171,
      "C2_ci": [
        -0.0134,
        0.0529
      ],
      "C2": true,
      "C3_min_z": -1.02,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0004,
      "logloss_vs_book_ci": [
        -0.0018,
        0.0026
      ],
      "mean_p": 0.4143,
      "actual": 0.4315,
      "fair_odds": 2.52
    },
    "replication_2019_20_to_2023_24": {
      "league": "PRIMEIRA",
      "market": "sh_over_1.5",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.235,
      "C1_ci": [
        0.847,
        1.622
      ],
      "C1": true,
      "C2_level": 0.0171,
      "C2_ci": [
        -0.0089,
        0.0425
      ],
      "C2": true,
      "C3_min_z": -0.78,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0009,
      "logloss_vs_book_ci": [
        -0.0013,
        0.0031
      ],
      "mean_p": 0.4025,
      "actual": 0.4196,
      "fair_odds": 2.58
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "PRIMEIRA",
    "market": "home_win_either_half",
    "primary_2024_25_plus": {
      "league": "PRIMEIRA",
      "market": "home_win_either_half",
      "n": 693,
      "status": "PASS",
      "C1_slope": 0.884,
      "C1_ci": [
        0.704,
        1.065
      ],
      "C1": true,
      "C2_level": -0.0004,
      "C2_ci": [
        -0.0367,
        0.0352
      ],
      "C2": true,
      "C3_min_z": -2.04,
      "C3": true,
      "C4_lifted_legs": 280,
      "C4_z": -1.36,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0054,
        0.0064
      ],
      "mean_p": 0.5618,
      "actual": 0.5613,
      "fair_odds": 1.75
    },
    "replication_2019_20_to_2023_24": {
      "league": "PRIMEIRA",
      "market": "home_win_either_half",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 0.981,
      "C1_ci": [
        0.846,
        1.116
      ],
      "C1": true,
      "C2_level": -0.0158,
      "C2_ci": [
        -0.0384,
        0.0077
      ],
      "C2": true,
      "C3_min_z": -2.43,
      "C3": true,
      "C4_lifted_legs": 605,
      "C4_z": -1.73,
      "C4": true,
      "logloss_vs_book": -0.0005,
      "logloss_vs_book_ci": [
        -0.0047,
        0.0038
      ],
      "mean_p": 0.5721,
      "actual": 0.5562,
      "fair_odds": 1.75
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "PRIMEIRA",
    "market": "away_win_either_half",
    "primary_2024_25_plus": {
      "league": "PRIMEIRA",
      "market": "away_win_either_half",
      "n": 693,
      "status": "PASS",
      "C1_slope": 1.02,
      "C1_ci": [
        0.821,
        1.218
      ],
      "C1": true,
      "C2_level": -0.0041,
      "C2_ci": [
        -0.038,
        0.0297
      ],
      "C2": true,
      "C3_min_z": -1.76,
      "C3": true,
      "C4_lifted_legs": 199,
      "C4_z": 0.18,
      "C4": true,
      "logloss_vs_book": -0.0021,
      "logloss_vs_book_ci": [
        -0.0066,
        0.0026
      ],
      "mean_p": 0.4687,
      "actual": 0.4646,
      "fair_odds": 2.2
    },
    "replication_2019_20_to_2023_24": {
      "league": "PRIMEIRA",
      "market": "away_win_either_half",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.022,
      "C1_ci": [
        0.879,
        1.164
      ],
      "C1": true,
      "C2_level": 0.0034,
      "C2_ci": [
        -0.0195,
        0.0271
      ],
      "C2": true,
      "C3_min_z": -1.69,
      "C3": true,
      "C4_lifted_legs": 326,
      "C4_z": 1.47,
      "C4": true,
      "logloss_vs_book": -0.0016,
      "logloss_vs_book_ci": [
        -0.0042,
        0.001
      ],
      "mean_p": 0.4639,
      "actual": 0.4673,
      "fair_odds": 2.21
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "SUPERLIG",
    "market": "fh_over_0.5",
    "primary_2024_25_plus": {
      "league": "SUPERLIG",
      "market": "fh_over_0.5",
      "n": 728,
      "status": "PASS",
      "C1_slope": 1.445,
      "C1_ci": [
        0.782,
        2.108
      ],
      "C1": true,
      "C2_level": -0.0084,
      "C2_ci": [
        -0.0397,
        0.0233
      ],
      "C2": true,
      "C3_min_z": -1.95,
      "C3": true,
      "C4_lifted_legs": 180,
      "C4_z": 0.81,
      "C4": true,
      "logloss_vs_book": -0.002,
      "logloss_vs_book_ci": [
        -0.0058,
        0.0017
      ],
      "mean_p": 0.7295,
      "actual": 0.7212,
      "fair_odds": 1.38
    },
    "replication_2019_20_to_2023_24": {
      "league": "SUPERLIG",
      "market": "fh_over_0.5",
      "n": 1798,
      "status": "FAIL",
      "C1_slope": 1.04,
      "C1_ci": [
        0.542,
        1.538
      ],
      "C1": true,
      "C2_level": -0.0129,
      "C2_ci": [
        -0.0326,
        0.0075
      ],
      "C2": true,
      "C3_min_z": -1.83,
      "C3": true,
      "C4_lifted_legs": 450,
      "C4_z": -2.22,
      "C4": false,
      "logloss_vs_book": 0.0008,
      "logloss_vs_book_ci": [
        -0.0019,
        0.0036
      ],
      "mean_p": 0.7248,
      "actual": 0.7119,
      "fair_odds": 1.39
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "task": 16,
    "league": "SUPERLIG",
    "market": "fh_over_1.5",
    "primary_2024_25_plus": {
      "league": "SUPERLIG",
      "market": "fh_over_1.5",
      "n": 728,
      "status": "PASS",
      "C1_slope": 1.577,
      "C1_ci": [
        0.929,
        2.226
      ],
      "C1": true,
      "C2_level": -0.0156,
      "C2_ci": [
        -0.0506,
        0.0204
      ],
      "C2": true,
      "C3_min_z": -2.56,
      "C3": true,
      "C4_lifted_legs": 1,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0,
      "logloss_vs_book_ci": [
        -0.0023,
        0.0024
      ],
      "mean_p": 0.3658,
      "actual": 0.3503,
      "fair_odds": 2.81
    },
    "replication_2019_20_to_2023_24": {
      "league": "SUPERLIG",
      "market": "fh_over_1.5",
      "n": 1798,
      "status": "FAIL",
      "C1_slope": 0.688,
      "C1_ci": [
        0.235,
        1.14
      ],
      "C1": true,
      "C2_level": -0.0228,
      "C2_ci": [
        -0.046,
        -0.0006
      ],
      "C2": false,
      "C3_min_z": -3.0,
      "C3": false,
      "C4_lifted_legs": 405,
      "C4_z": -2.75,
      "C4": false,
      "logloss_vs_book": 0.0024,
      "logloss_vs_book_ci": [
        -0.0002,
        0.0049
      ],
      "mean_p": 0.3681,
      "actual": 0.3454,
      "fair_odds": 2.77
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "task": 16,
    "league": "SUPERLIG",
    "market": "sh_over_0.5",
    "primary_2024_25_plus": {
      "league": "SUPERLIG",
      "market": "sh_over_0.5",
      "n": 728,
      "status": "PASS",
      "C1_slope": 0.976,
      "C1_ci": [
        0.223,
        1.729
      ],
      "C1": true,
      "C2_level": -0.0155,
      "C2_ci": [
        -0.0434,
        0.0135
      ],
      "C2": true,
      "C3_min_z": -1.23,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0004,
      "logloss_vs_book_ci": [
        -0.0003,
        0.0012
      ],
      "mean_p": 0.7958,
      "actual": 0.7802,
      "fair_odds": 1.26
    },
    "replication_2019_20_to_2023_24": {
      "league": "SUPERLIG",
      "market": "sh_over_0.5",
      "n": 1798,
      "status": "PASS",
      "C1_slope": 0.531,
      "C1_ci": [
        0.033,
        1.029
      ],
      "C1": true,
      "C2_level": 0.0058,
      "C2_ci": [
        -0.0132,
        0.0241
      ],
      "C2": true,
      "C3_min_z": -1.35,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0012,
      "logloss_vs_book_ci": [
        -0.0,
        0.0023
      ],
      "mean_p": 0.7996,
      "actual": 0.8053,
      "fair_odds": 1.25
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "SUPERLIG",
    "market": "sh_over_1.5",
    "primary_2024_25_plus": {
      "league": "SUPERLIG",
      "market": "sh_over_1.5",
      "n": 728,
      "status": "PASS",
      "C1_slope": 1.174,
      "C1_ci": [
        0.638,
        1.71
      ],
      "C1": true,
      "C2_level": 0.0092,
      "C2_ci": [
        -0.0211,
        0.0427
      ],
      "C2": true,
      "C3_min_z": -1.51,
      "C3": true,
      "C4_lifted_legs": 1,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0005,
      "logloss_vs_book_ci": [
        -0.0024,
        0.0012
      ],
      "mean_p": 0.4702,
      "actual": 0.4794,
      "fair_odds": 2.18
    },
    "replication_2019_20_to_2023_24": {
      "league": "SUPERLIG",
      "market": "sh_over_1.5",
      "n": 1798,
      "status": "PASS",
      "C1_slope": 0.949,
      "C1_ci": [
        0.539,
        1.359
      ],
      "C1": true,
      "C2_level": 0.0159,
      "C2_ci": [
        -0.0072,
        0.0389
      ],
      "C2": true,
      "C3_min_z": -0.92,
      "C3": true,
      "C4_lifted_legs": 2,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0007,
      "logloss_vs_book_ci": [
        -0.0008,
        0.0022
      ],
      "mean_p": 0.4651,
      "actual": 0.4811,
      "fair_odds": 2.17
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "SUPERLIG",
    "market": "home_win_either_half",
    "primary_2024_25_plus": {
      "league": "SUPERLIG",
      "market": "home_win_either_half",
      "n": 728,
      "status": "PASS",
      "C1_slope": 1.009,
      "C1_ci": [
        0.78,
        1.239
      ],
      "C1": true,
      "C2_level": 0.0153,
      "C2_ci": [
        -0.0195,
        0.0477
      ],
      "C2": true,
      "C3_min_z": -1.89,
      "C3": true,
      "C4_lifted_legs": 335,
      "C4_z": 0.15,
      "C4": true,
      "logloss_vs_book": -0.0038,
      "logloss_vs_book_ci": [
        -0.0088,
        0.001
      ],
      "mean_p": 0.596,
      "actual": 0.6113,
      "fair_odds": 1.64
    },
    "replication_2019_20_to_2023_24": {
      "league": "SUPERLIG",
      "market": "home_win_either_half",
      "n": 1798,
      "status": "PASS",
      "C1_slope": 1.064,
      "C1_ci": [
        0.883,
        1.246
      ],
      "C1": true,
      "C2_level": -0.0049,
      "C2_ci": [
        -0.0249,
        0.0165
      ],
      "C2": true,
      "C3_min_z": -1.88,
      "C3": true,
      "C4_lifted_legs": 554,
      "C4_z": -0.6,
      "C4": true,
      "logloss_vs_book": -0.0012,
      "logloss_vs_book_ci": [
        -0.0038,
        0.0014
      ],
      "mean_p": 0.6,
      "actual": 0.5951,
      "fair_odds": 1.67
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 16,
    "league": "SUPERLIG",
    "market": "away_win_either_half",
    "primary_2024_25_plus": {
      "league": "SUPERLIG",
      "market": "away_win_either_half",
      "n": 728,
      "status": "PASS",
      "C1_slope": 1.146,
      "C1_ci": [
        0.908,
        1.384
      ],
      "C1": true,
      "C2_level": -0.0046,
      "C2_ci": [
        -0.0387,
        0.0287
      ],
      "C2": true,
      "C3_min_z": -1.06,
      "C3": true,
      "C4_lifted_legs": 66,
      "C4_z": 1.27,
      "C4": true,
      "logloss_vs_book": -0.0032,
      "logloss_vs_book_ci": [
        -0.0065,
        0.0001
      ],
      "mean_p": 0.4538,
      "actual": 0.4492,
      "fair_odds": 2.3
    },
    "replication_2019_20_to_2023_24": {
      "league": "SUPERLIG",
      "market": "away_win_either_half",
      "n": 1798,
      "status": "PASS",
      "C1_slope": 0.999,
      "C1_ci": [
        0.824,
        1.174
      ],
      "C1": true,
      "C2_level": 0.0014,
      "C2_ci": [
        -0.0208,
        0.0235
      ],
      "C2": true,
      "C3_min_z": -1.46,
      "C3": true,
      "C4_lifted_legs": 33,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0,
      "logloss_vs_book_ci": [
        -0.0015,
        0.0015
      ],
      "mean_p": 0.4536,
      "actual": 0.4549,
      "fair_odds": 2.22
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "EPL",
    "market": "dc1up_1x",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "dc1up_1x",
      "n": 830,
      "status": "PASS",
      "C1_slope": 1.05,
      "C1_ci": [
        0.825,
        1.275
      ],
      "C1": true,
      "C2_level": -0.0012,
      "C2_ci": [
        -0.0293,
        0.0258
      ],
      "C2": true,
      "C3_min_z": -1.56,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0008,
      "logloss_vs_book_ci": [
        -0.0033,
        0.0016
      ],
      "mean_p": 0.741,
      "actual": 0.7398,
      "fair_odds": 1.31
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "dc1up_1x",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.883,
      "C1_ci": [
        0.756,
        1.01
      ],
      "C1": true,
      "C2_level": 0.0011,
      "C2_ci": [
        -0.0179,
        0.0196
      ],
      "C2": true,
      "C3_min_z": -2.66,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0014,
      "logloss_vs_book_ci": [
        -0.0006,
        0.0037
      ],
      "mean_p": 0.7294,
      "actual": 0.7305,
      "fair_odds": 1.32
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "EPL",
    "market": "dc1up_x2",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "dc1up_x2",
      "n": 830,
      "status": "PASS",
      "C1_slope": 0.952,
      "C1_ci": [
        0.732,
        1.172
      ],
      "C1": true,
      "C2_level": 0.0321,
      "C2_ci": [
        -0.0016,
        0.0651
      ],
      "C2": true,
      "C3_min_z": -0.03,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0006,
      "logloss_vs_book_ci": [
        -0.0018,
        0.0007
      ],
      "mean_p": 0.6305,
      "actual": 0.6627,
      "fair_odds": 1.55
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "dc1up_x2",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.889,
      "C1_ci": [
        0.765,
        1.014
      ],
      "C1": true,
      "C2_level": 0.0122,
      "C2_ci": [
        -0.0071,
        0.0327
      ],
      "C2": true,
      "C3_min_z": -1.57,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0011,
      "logloss_vs_book_ci": [
        -0.0001,
        0.0023
      ],
      "mean_p": 0.6257,
      "actual": 0.6379,
      "fair_odds": 1.55
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "EPL",
    "market": "dc1up_12",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "dc1up_12",
      "n": 830,
      "status": "PASS",
      "C1_slope": 0.847,
      "C1_ci": [
        0.027,
        1.667
      ],
      "C1": true,
      "C2_level": -0.004,
      "C2_ci": [
        -0.0205,
        0.0127
      ],
      "C2": true,
      "C3_min_z": -1.7,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.001,
        0.0016
      ],
      "mean_p": 0.9462,
      "actual": 0.9422,
      "fair_odds": 1.06
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "dc1up_12",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.271,
      "C1_ci": [
        0.702,
        1.841
      ],
      "C1": true,
      "C2_level": 0.0086,
      "C2_ci": [
        -0.0022,
        0.0189
      ],
      "C2": true,
      "C3_min_z": -0.79,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0002,
        0.0006
      ],
      "mean_p": 0.9351,
      "actual": 0.9437,
      "fair_odds": 1.07
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "EPL",
    "market": "home_2up",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "home_2up",
      "n": 830,
      "status": "FAIL",
      "C1_slope": 1.048,
      "C1_ci": [
        0.844,
        1.251
      ],
      "C1": true,
      "C2_level": -0.0343,
      "C2_ci": [
        -0.0657,
        -0.0041
      ],
      "C2": false,
      "C3_min_z": -1.8,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0005,
      "logloss_vs_book_ci": [
        -0.0009,
        0.0018
      ],
      "mean_p": 0.468,
      "actual": 0.4337,
      "fair_odds": 2.19
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "home_2up",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.012,
      "C1_ci": [
        0.888,
        1.135
      ],
      "C1": true,
      "C2_level": -0.0032,
      "C2_ci": [
        -0.0232,
        0.0156
      ],
      "C2": true,
      "C3_min_z": -1.86,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0003,
      "logloss_vs_book_ci": [
        -0.0005,
        0.0012
      ],
      "mean_p": 0.4611,
      "actual": 0.4579,
      "fair_odds": 2.24
    },
    "strong_candidate": false,
    "verdict": "stays out"
  },
  {
    "task": 17,
    "league": "EPL",
    "market": "away_2up",
    "primary_2024_25_plus": {
      "league": "EPL",
      "market": "away_2up",
      "n": 830,
      "status": "PASS",
      "C1_slope": 0.986,
      "C1_ci": [
        0.782,
        1.191
      ],
      "C1": true,
      "C2_level": 0.0015,
      "C2_ci": [
        -0.0308,
        0.0321
      ],
      "C2": true,
      "C3_min_z": -0.88,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0001,
      "logloss_vs_book_ci": [
        -0.001,
        0.0013
      ],
      "mean_p": 0.3418,
      "actual": 0.3434,
      "fair_odds": 3.1
    },
    "replication_2019_20_to_2023_24": {
      "league": "EPL",
      "market": "away_2up",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.917,
      "C1_ci": [
        0.798,
        1.037
      ],
      "C1": true,
      "C2_level": 0.0058,
      "C2_ci": [
        -0.0137,
        0.0249
      ],
      "C2": true,
      "C3_min_z": -1.15,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0013,
      "logloss_vs_book_ci": [
        -0.0001,
        0.0027
      ],
      "mean_p": 0.3432,
      "actual": 0.3489,
      "fair_odds": 3.16
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "LALIGA",
    "market": "dc1up_1x",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "dc1up_1x",
      "n": 805,
      "status": "PASS",
      "C1_slope": 1.103,
      "C1_ci": [
        0.851,
        1.355
      ],
      "C1": true,
      "C2_level": 0.023,
      "C2_ci": [
        -0.0032,
        0.0517
      ],
      "C2": true,
      "C3_min_z": -0.43,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0039,
      "logloss_vs_book_ci": [
        -0.0069,
        -0.0009
      ],
      "mean_p": 0.7572,
      "actual": 0.7801,
      "fair_odds": 1.29
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "dc1up_1x",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.074,
      "C1_ci": [
        0.911,
        1.238
      ],
      "C1": true,
      "C2_level": 0.0129,
      "C2_ci": [
        -0.0035,
        0.0306
      ],
      "C2": true,
      "C3_min_z": -1.78,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0015,
      "logloss_vs_book_ci": [
        -0.003,
        0.0
      ],
      "mean_p": 0.7492,
      "actual": 0.7621,
      "fair_odds": 1.3
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "LALIGA",
    "market": "dc1up_x2",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "dc1up_x2",
      "n": 805,
      "status": "PASS",
      "C1_slope": 1.072,
      "C1_ci": [
        0.85,
        1.293
      ],
      "C1": true,
      "C2_level": -0.0155,
      "C2_ci": [
        -0.0432,
        0.0145
      ],
      "C2": true,
      "C3_min_z": -1.5,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0014,
      "logloss_vs_book_ci": [
        -0.0044,
        0.0018
      ],
      "mean_p": 0.6192,
      "actual": 0.6037,
      "fair_odds": 1.57
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "dc1up_x2",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.038,
      "C1_ci": [
        0.894,
        1.182
      ],
      "C1": true,
      "C2_level": -0.0067,
      "C2_ci": [
        -0.0254,
        0.0129
      ],
      "C2": true,
      "C3_min_z": -2.68,
      "C3": true,
      "C4_lifted_legs": 26,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0007,
      "logloss_vs_book_ci": [
        -0.0026,
        0.0012
      ],
      "mean_p": 0.6251,
      "actual": 0.6184,
      "fair_odds": 1.56
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "LALIGA",
    "market": "dc1up_12",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "dc1up_12",
      "n": 805,
      "status": "PASS",
      "C1_slope": 1.354,
      "C1_ci": [
        0.529,
        2.179
      ],
      "C1": true,
      "C2_level": 0.0245,
      "C2_ci": [
        0.0091,
        0.0402
      ],
      "C2": true,
      "C3_min_z": -1.7,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0002,
      "logloss_vs_book_ci": [
        -0.0009,
        0.0005
      ],
      "mean_p": 0.9209,
      "actual": 0.9453,
      "fair_odds": 1.09
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "dc1up_12",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 0.87,
      "C1_ci": [
        0.387,
        1.352
      ],
      "C1": true,
      "C2_level": -0.0007,
      "C2_ci": [
        -0.0134,
        0.0108
      ],
      "C2": true,
      "C3_min_z": -1.42,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0001,
        0.0005
      ],
      "mean_p": 0.9149,
      "actual": 0.9142,
      "fair_odds": 1.09
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "LALIGA",
    "market": "home_2up",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "home_2up",
      "n": 805,
      "status": "PASS",
      "C1_slope": 1.159,
      "C1_ci": [
        0.941,
        1.377
      ],
      "C1": true,
      "C2_level": 0.018,
      "C2_ci": [
        -0.0125,
        0.0472
      ],
      "C2": true,
      "C3_min_z": -1.5,
      "C3": true,
      "C4_lifted_legs": 79,
      "C4_z": 1.73,
      "C4": true,
      "logloss_vs_book": -0.0031,
      "logloss_vs_book_ci": [
        -0.0056,
        -0.0005
      ],
      "mean_p": 0.4628,
      "actual": 0.4807,
      "fair_odds": 2.27
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "home_2up",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.089,
      "C1_ci": [
        0.949,
        1.229
      ],
      "C1": true,
      "C2_level": 0.0003,
      "C2_ci": [
        -0.0197,
        0.0217
      ],
      "C2": true,
      "C3_min_z": -1.61,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0011,
      "logloss_vs_book_ci": [
        -0.0025,
        0.0003
      ],
      "mean_p": 0.4544,
      "actual": 0.4547,
      "fair_odds": 2.26
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "LALIGA",
    "market": "away_2up",
    "primary_2024_25_plus": {
      "league": "LALIGA",
      "market": "away_2up",
      "n": 805,
      "status": "PASS",
      "C1_slope": 1.049,
      "C1_ci": [
        0.83,
        1.268
      ],
      "C1": true,
      "C2_level": -0.002,
      "C2_ci": [
        -0.0318,
        0.0269
      ],
      "C2": true,
      "C3_min_z": -1.61,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0016,
      "logloss_vs_book_ci": [
        -0.0048,
        0.0015
      ],
      "mean_p": 0.3027,
      "actual": 0.3006,
      "fair_odds": 3.58
    },
    "replication_2019_20_to_2023_24": {
      "league": "LALIGA",
      "market": "away_2up",
      "n": 1900,
      "status": "PASS",
      "C1_slope": 1.059,
      "C1_ci": [
        0.911,
        1.207
      ],
      "C1": true,
      "C2_level": -0.0096,
      "C2_ci": [
        -0.0293,
        0.0082
      ],
      "C2": true,
      "C3_min_z": -2.18,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0016,
      "logloss_vs_book_ci": [
        -0.0034,
        0.0001
      ],
      "mean_p": 0.3049,
      "actual": 0.2953,
      "fair_odds": 3.52
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "SERIEA",
    "market": "dc1up_1x",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "dc1up_1x",
      "n": 803,
      "status": "PASS",
      "C1_slope": 1.119,
      "C1_ci": [
        0.908,
        1.33
      ],
      "C1": true,
      "C2_level": -0.0178,
      "C2_ci": [
        -0.0475,
        0.0134
      ],
      "C2": true,
      "C3_min_z": -1.29,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0029,
      "logloss_vs_book_ci": [
        -0.0063,
        0.0007
      ],
      "mean_p": 0.7351,
      "actual": 0.7173,
      "fair_odds": 1.3
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "dc1up_1x",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 0.989,
      "C1_ci": [
        0.854,
        1.123
      ],
      "C1": true,
      "C2_level": -0.0011,
      "C2_ci": [
        -0.0191,
        0.0168
      ],
      "C2": true,
      "C3_min_z": -1.56,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.001,
      "logloss_vs_book_ci": [
        -0.0034,
        0.0014
      ],
      "mean_p": 0.7335,
      "actual": 0.7323,
      "fair_odds": 1.32
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "SERIEA",
    "market": "dc1up_x2",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "dc1up_x2",
      "n": 803,
      "status": "PASS",
      "C1_slope": 0.945,
      "C1_ci": [
        0.75,
        1.14
      ],
      "C1": true,
      "C2_level": 0.0058,
      "C2_ci": [
        -0.0242,
        0.0354
      ],
      "C2": true,
      "C3_min_z": -1.82,
      "C3": true,
      "C4_lifted_legs": 407,
      "C4_z": 0.05,
      "C4": true,
      "logloss_vs_book": -0.0022,
      "logloss_vs_book_ci": [
        -0.0073,
        0.0027
      ],
      "mean_p": 0.653,
      "actual": 0.6588,
      "fair_odds": 1.49
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "dc1up_x2",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 1.091,
      "C1_ci": [
        0.956,
        1.226
      ],
      "C1": true,
      "C2_level": 0.0072,
      "C2_ci": [
        -0.0107,
        0.025
      ],
      "C2": true,
      "C3_min_z": -0.85,
      "C3": true,
      "C4_lifted_legs": 694,
      "C4_z": 0.31,
      "C4": true,
      "logloss_vs_book": -0.0037,
      "logloss_vs_book_ci": [
        -0.0064,
        -0.001
      ],
      "mean_p": 0.6524,
      "actual": 0.6596,
      "fair_odds": 1.48
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "SERIEA",
    "market": "dc1up_12",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "dc1up_12",
      "n": 803,
      "status": "PASS",
      "C1_slope": 1.364,
      "C1_ci": [
        0.39,
        2.339
      ],
      "C1": true,
      "C2_level": -0.0011,
      "C2_ci": [
        -0.0212,
        0.0175
      ],
      "C2": true,
      "C3_min_z": -2.11,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0001,
      "logloss_vs_book_ci": [
        -0.0013,
        0.0015
      ],
      "mean_p": 0.9202,
      "actual": 0.9191,
      "fair_odds": 1.09
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "dc1up_12",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 0.554,
      "C1_ci": [
        -0.008,
        1.116
      ],
      "C1": true,
      "C2_level": 0.0055,
      "C2_ci": [
        -0.0057,
        0.0157
      ],
      "C2": true,
      "C3_min_z": -1.13,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0006,
        0.0011
      ],
      "mean_p": 0.9355,
      "actual": 0.941,
      "fair_odds": 1.07
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "SERIEA",
    "market": "home_2up",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "home_2up",
      "n": 803,
      "status": "PASS",
      "C1_slope": 1.014,
      "C1_ci": [
        0.83,
        1.199
      ],
      "C1": true,
      "C2_level": -0.0074,
      "C2_ci": [
        -0.0359,
        0.0231
      ],
      "C2": true,
      "C3_min_z": -1.38,
      "C3": true,
      "C4_lifted_legs": 61,
      "C4_z": -0.49,
      "C4": true,
      "logloss_vs_book": -0.0032,
      "logloss_vs_book_ci": [
        -0.0077,
        0.0019
      ],
      "mean_p": 0.4234,
      "actual": 0.4159,
      "fair_odds": 2.45
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "home_2up",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 0.97,
      "C1_ci": [
        0.854,
        1.086
      ],
      "C1": true,
      "C2_level": -0.0064,
      "C2_ci": [
        -0.0264,
        0.0119
      ],
      "C2": true,
      "C3_min_z": -1.64,
      "C3": true,
      "C4_lifted_legs": 217,
      "C4_z": -1.6,
      "C4": true,
      "logloss_vs_book": -0.0018,
      "logloss_vs_book_ci": [
        -0.0047,
        0.0011
      ],
      "mean_p": 0.4363,
      "actual": 0.4299,
      "fair_odds": 2.41
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "SERIEA",
    "market": "away_2up",
    "primary_2024_25_plus": {
      "league": "SERIEA",
      "market": "away_2up",
      "n": 803,
      "status": "PASS",
      "C1_slope": 1.026,
      "C1_ci": [
        0.839,
        1.213
      ],
      "C1": true,
      "C2_level": 0.0243,
      "C2_ci": [
        -0.0091,
        0.0575
      ],
      "C2": true,
      "C3_min_z": -0.38,
      "C3": true,
      "C4_lifted_legs": 185,
      "C4_z": 1.74,
      "C4": true,
      "logloss_vs_book": -0.0034,
      "logloss_vs_book_ci": [
        -0.0076,
        0.0008
      ],
      "mean_p": 0.3381,
      "actual": 0.3624,
      "fair_odds": 3.25
    },
    "replication_2019_20_to_2023_24": {
      "league": "SERIEA",
      "market": "away_2up",
      "n": 1898,
      "status": "PASS",
      "C1_slope": 1.013,
      "C1_ci": [
        0.89,
        1.136
      ],
      "C1": true,
      "C2_level": 0.0058,
      "C2_ci": [
        -0.0124,
        0.0247
      ],
      "C2": true,
      "C3_min_z": -1.05,
      "C3": true,
      "C4_lifted_legs": 433,
      "C4_z": 1.12,
      "C4": true,
      "logloss_vs_book": -0.0015,
      "logloss_vs_book_ci": [
        -0.004,
        0.001
      ],
      "mean_p": 0.3509,
      "actual": 0.3567,
      "fair_odds": 3.04
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "BUNDES",
    "market": "dc1up_1x",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "dc1up_1x",
      "n": 638,
      "status": "PASS",
      "C1_slope": 1.135,
      "C1_ci": [
        0.863,
        1.406
      ],
      "C1": true,
      "C2_level": -0.0113,
      "C2_ci": [
        -0.0408,
        0.0192
      ],
      "C2": true,
      "C3_min_z": -1.63,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0001,
      "logloss_vs_book_ci": [
        -0.002,
        0.0019
      ],
      "mean_p": 0.7542,
      "actual": 0.7429,
      "fair_odds": 1.3
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "dc1up_1x",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.075,
      "C1_ci": [
        0.909,
        1.241
      ],
      "C1": true,
      "C2_level": -0.0091,
      "C2_ci": [
        -0.0309,
        0.0133
      ],
      "C2": true,
      "C3_min_z": -2.07,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.001,
      "logloss_vs_book_ci": [
        -0.0005,
        0.0026
      ],
      "mean_p": 0.7476,
      "actual": 0.7386,
      "fair_odds": 1.3
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "BUNDES",
    "market": "dc1up_x2",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "dc1up_x2",
      "n": 638,
      "status": "PASS",
      "C1_slope": 1.338,
      "C1_ci": [
        1.035,
        1.64
      ],
      "C1": true,
      "C2_level": 0.0238,
      "C2_ci": [
        -0.0136,
        0.0579
      ],
      "C2": true,
      "C3_min_z": -1.23,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.003,
      "logloss_vs_book_ci": [
        0.001,
        0.0051
      ],
      "mean_p": 0.622,
      "actual": 0.6458,
      "fair_odds": 1.57
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "dc1up_x2",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.103,
      "C1_ci": [
        0.924,
        1.281
      ],
      "C1": true,
      "C2_level": 0.0137,
      "C2_ci": [
        -0.0107,
        0.0371
      ],
      "C2": true,
      "C3_min_z": -1.73,
      "C3": true,
      "C4_lifted_legs": 9,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0013,
      "logloss_vs_book_ci": [
        -0.0015,
        0.0043
      ],
      "mean_p": 0.6209,
      "actual": 0.6346,
      "fair_odds": 1.58
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "BUNDES",
    "market": "dc1up_12",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "dc1up_12",
      "n": 638,
      "status": "PASS",
      "C1_slope": 1.174,
      "C1_ci": [
        0.384,
        1.965
      ],
      "C1": true,
      "C2_level": -0.0071,
      "C2_ci": [
        -0.0265,
        0.0102
      ],
      "C2": true,
      "C3_min_z": -1.25,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0001,
      "logloss_vs_book_ci": [
        -0.0024,
        0.0028
      ],
      "mean_p": 0.9475,
      "actual": 0.9404,
      "fair_odds": 1.05
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "dc1up_12",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.749,
      "C1_ci": [
        0.982,
        2.516
      ],
      "C1": true,
      "C2_level": 0.0096,
      "C2_ci": [
        -0.0014,
        0.0196
      ],
      "C2": true,
      "C3_min_z": -0.65,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0003,
      "logloss_vs_book_ci": [
        -0.0011,
        0.0006
      ],
      "mean_p": 0.942,
      "actual": 0.9516,
      "fair_odds": 1.06
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "BUNDES",
    "market": "home_2up",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "home_2up",
      "n": 638,
      "status": "PASS",
      "C1_slope": 1.398,
      "C1_ci": [
        1.111,
        1.684
      ],
      "C1": true,
      "C2_level": -0.0193,
      "C2_ci": [
        -0.0554,
        0.0169
      ],
      "C2": true,
      "C3_min_z": -2.19,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0029,
      "logloss_vs_book_ci": [
        0.001,
        0.0049
      ],
      "mean_p": 0.4754,
      "actual": 0.4561,
      "fair_odds": 2.17
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "home_2up",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.015,
      "C1_ci": [
        0.859,
        1.17
      ],
      "C1": true,
      "C2_level": -0.0124,
      "C2_ci": [
        -0.0363,
        0.0133
      ],
      "C2": true,
      "C3_min_z": -1.6,
      "C3": true,
      "C4_lifted_legs": 116,
      "C4_z": -0.02,
      "C4": true,
      "logloss_vs_book": 0.0005,
      "logloss_vs_book_ci": [
        -0.0017,
        0.0027
      ],
      "mean_p": 0.4718,
      "actual": 0.4595,
      "fair_odds": 2.16
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "BUNDES",
    "market": "away_2up",
    "primary_2024_25_plus": {
      "league": "BUNDES",
      "market": "away_2up",
      "n": 638,
      "status": "PASS",
      "C1_slope": 0.924,
      "C1_ci": [
        0.69,
        1.157
      ],
      "C1": true,
      "C2_level": 0.0339,
      "C2_ci": [
        -0.0034,
        0.0714
      ],
      "C2": true,
      "C3_min_z": -1.05,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0022,
      "logloss_vs_book_ci": [
        0.0002,
        0.0041
      ],
      "mean_p": 0.3251,
      "actual": 0.3589,
      "fair_odds": 3.23
    },
    "replication_2019_20_to_2023_24": {
      "league": "BUNDES",
      "market": "away_2up",
      "n": 1530,
      "status": "PASS",
      "C1_slope": 1.027,
      "C1_ci": [
        0.876,
        1.178
      ],
      "C1": true,
      "C2_level": 0.0062,
      "C2_ci": [
        -0.0149,
        0.0286
      ],
      "C2": true,
      "C3_min_z": -1.82,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0009,
      "logloss_vs_book_ci": [
        -0.0006,
        0.0024
      ],
      "mean_p": 0.3298,
      "actual": 0.3359,
      "fair_odds": 3.26
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "LIGUE1",
    "market": "dc1up_1x",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "dc1up_1x",
      "n": 638,
      "status": "PASS",
      "C1_slope": 0.922,
      "C1_ci": [
        0.686,
        1.158
      ],
      "C1": true,
      "C2_level": -0.0035,
      "C2_ci": [
        -0.0382,
        0.0311
      ],
      "C2": true,
      "C3_min_z": -1.2,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0002,
      "logloss_vs_book_ci": [
        -0.0031,
        0.0039
      ],
      "mean_p": 0.734,
      "actual": 0.7304,
      "fair_odds": 1.31
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "dc1up_1x",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 0.942,
      "C1_ci": [
        0.794,
        1.09
      ],
      "C1": true,
      "C2_level": -0.0123,
      "C2_ci": [
        -0.033,
        0.0076
      ],
      "C2": true,
      "C3_min_z": -2.12,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0004,
      "logloss_vs_book_ci": [
        -0.002,
        0.0031
      ],
      "mean_p": 0.7439,
      "actual": 0.7316,
      "fair_odds": 1.3
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "LIGUE1",
    "market": "dc1up_x2",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "dc1up_x2",
      "n": 638,
      "status": "PASS",
      "C1_slope": 0.893,
      "C1_ci": [
        0.662,
        1.124
      ],
      "C1": true,
      "C2_level": -0.0154,
      "C2_ci": [
        -0.0501,
        0.0207
      ],
      "C2": true,
      "C3_min_z": -1.9,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0012,
      "logloss_vs_book_ci": [
        -0.0018,
        0.0043
      ],
      "mean_p": 0.6408,
      "actual": 0.6254,
      "fair_odds": 1.53
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "dc1up_x2",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 1.052,
      "C1_ci": [
        0.893,
        1.211
      ],
      "C1": true,
      "C2_level": 0.0301,
      "C2_ci": [
        0.0086,
        0.0508
      ],
      "C2": true,
      "C3_min_z": -0.29,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": -0.0006,
      "logloss_vs_book_ci": [
        -0.002,
        0.0008
      ],
      "mean_p": 0.6285,
      "actual": 0.6586,
      "fair_odds": 1.57
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "LIGUE1",
    "market": "dc1up_12",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "dc1up_12",
      "n": 638,
      "status": "PASS",
      "C1_slope": 1.187,
      "C1_ci": [
        0.212,
        2.161
      ],
      "C1": true,
      "C2_level": -0.0089,
      "C2_ci": [
        -0.0314,
        0.0119
      ],
      "C2": true,
      "C3_min_z": -2.51,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0006,
      "logloss_vs_book_ci": [
        -0.0027,
        0.0044
      ],
      "mean_p": 0.943,
      "actual": 0.9342,
      "fair_odds": 1.06
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "dc1up_12",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 0.711,
      "C1_ci": [
        0.261,
        1.162
      ],
      "C1": true,
      "C2_level": -0.0073,
      "C2_ci": [
        -0.019,
        0.0046
      ],
      "C2": true,
      "C3_min_z": -2.82,
      "C3": true,
      "C4_lifted_legs": 0,
      "C4_z": null,
      "C4": true,
      "logloss_vs_book": 0.0007,
      "logloss_vs_book_ci": [
        -0.0019,
        0.0032
      ],
      "mean_p": 0.9354,
      "actual": 0.9281,
      "fair_odds": 1.07
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "LIGUE1",
    "market": "home_2up",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "home_2up",
      "n": 638,
      "status": "PASS",
      "C1_slope": 0.904,
      "C1_ci": [
        0.693,
        1.115
      ],
      "C1": true,
      "C2_level": 0.0159,
      "C2_ci": [
        -0.0213,
        0.0517
      ],
      "C2": true,
      "C3_min_z": -0.67,
      "C3": true,
      "C4_lifted_legs": 81,
      "C4_z": 0.27,
      "C4": true,
      "logloss_vs_book": 0.0004,
      "logloss_vs_book_ci": [
        -0.0029,
        0.0041
      ],
      "mean_p": 0.4559,
      "actual": 0.4718,
      "fair_odds": 2.21
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "home_2up",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 1.054,
      "C1_ci": [
        0.908,
        1.2
      ],
      "C1": true,
      "C2_level": -0.0206,
      "C2_ci": [
        -0.0438,
        0.0017
      ],
      "C2": true,
      "C3_min_z": -1.53,
      "C3": true,
      "C4_lifted_legs": 121,
      "C4_z": -1.52,
      "C4": true,
      "logloss_vs_book": -0.0003,
      "logloss_vs_book_ci": [
        -0.0023,
        0.0017
      ],
      "mean_p": 0.4577,
      "actual": 0.4371,
      "fair_odds": 2.22
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  },
  {
    "task": 17,
    "league": "LIGUE1",
    "market": "away_2up",
    "primary_2024_25_plus": {
      "league": "LIGUE1",
      "market": "away_2up",
      "n": 638,
      "status": "PASS",
      "C1_slope": 0.956,
      "C1_ci": [
        0.727,
        1.184
      ],
      "C1": true,
      "C2_level": -0.0067,
      "C2_ci": [
        -0.0388,
        0.0316
      ],
      "C2": true,
      "C3_min_z": -1.36,
      "C3": true,
      "C4_lifted_legs": 56,
      "C4_z": -0.71,
      "C4": true,
      "logloss_vs_book": 0.0001,
      "logloss_vs_book_ci": [
        -0.0024,
        0.0028
      ],
      "mean_p": 0.3452,
      "actual": 0.3386,
      "fair_odds": 3.1
    },
    "replication_2019_20_to_2023_24": {
      "league": "LIGUE1",
      "market": "away_2up",
      "n": 1725,
      "status": "PASS",
      "C1_slope": 0.907,
      "C1_ci": [
        0.769,
        1.046
      ],
      "C1": true,
      "C2_level": 0.0194,
      "C2_ci": [
        -0.0002,
        0.0398
      ],
      "C2": true,
      "C3_min_z": -1.06,
      "C3": true,
      "C4_lifted_legs": 121,
      "C4_z": -0.3,
      "C4": true,
      "logloss_vs_book": 0.0006,
      "logloss_vs_book_ci": [
        -0.0014,
        0.0025
      ],
      "mean_p": 0.3273,
      "actual": 0.3467,
      "fair_odds": 3.32
    },
    "strong_candidate": true,
    "verdict": "Strong candidate (pending real Betpawa prices)"
  }
]
```
