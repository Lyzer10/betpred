# Goals by half and win either half study (PROJECT.md task 16, pre-registered 2026-11-07)

All nine live leagues (`EPL`, `LALIGA`, `SERIEA`, `BUNDES`, `LIGUE1`, `EREDIV`, `JUPILER`, `PRIMEIRA`, `SUPERLIG`), seasons 2014/15 onwards.
First-half goal share `s` per league = `mean(HTHG + HTAG) / mean(FTHG + FTAG)` over earlier seasons only; each team's goals per half are independent Poisson with means `s * lambda` (1H) and `(1 - s) * lambda` (2H).
Platt calibration (`LogisticRegression(C=1.0)` on `logit(raw)`) fitted per league x market on earlier seasons only; judged on 2024/25+ with `market_gates.evaluate` unchanged (`bookmaker_probability = raw`).
A `PASS` pair is **eligible pending real Betpawa prices** (>= 300 settled priced legs and one-sided level check passing, as in task 15); `FAIL` or `INSUFFICIENT` stays out.

| League | Market | n | Said | Won | Fair odds | Gates | Eligibility |
|---|---|---:|---:|---:|---:|---|---|
| EPL | fh_over_0.5 | 830 | 0.7357 | 0.7289 | 1.36 | **PASS** | eligible pending real Betpawa prices |
| EPL | fh_over_1.5 | 830 | 0.3843 | 0.3494 | 2.64 | **FAIL** | stays out |
| EPL | sh_over_0.5 | 830 | 0.8195 | 0.8133 | 1.22 | **FAIL** | stays out |
| EPL | sh_over_1.5 | 830 | 0.4965 | 0.4904 | 2.04 | **PASS** | eligible pending real Betpawa prices |
| EPL | home_win_either_half | 830 | 0.5881 | 0.5783 | 1.70 | **PASS** | eligible pending real Betpawa prices |
| EPL | away_win_either_half | 830 | 0.4707 | 0.4976 | 2.15 | **PASS** | eligible pending real Betpawa prices |
| LALIGA | fh_over_0.5 | 849 | 0.6707 | 0.6867 | 1.51 | **PASS** | eligible pending real Betpawa prices |
| LALIGA | fh_over_1.5 | 849 | 0.3175 | 0.3251 | 3.31 | **PASS** | eligible pending real Betpawa prices |
| LALIGA | sh_over_0.5 | 849 | 0.7785 | 0.8057 | 1.29 | **PASS** | eligible pending real Betpawa prices |
| LALIGA | sh_over_1.5 | 849 | 0.4387 | 0.4441 | 2.36 | **PASS** | eligible pending real Betpawa prices |
| LALIGA | home_win_either_half | 849 | 0.5831 | 0.6243 | 1.75 | **PASS** | eligible pending real Betpawa prices |
| LALIGA | away_win_either_half | 849 | 0.4306 | 0.4370 | 2.40 | **PASS** | eligible pending real Betpawa prices |
| SERIEA | fh_over_0.5 | 830 | 0.6787 | 0.6699 | 1.48 | **PASS** | eligible pending real Betpawa prices |
| SERIEA | fh_over_1.5 | 830 | 0.3090 | 0.2988 | 3.28 | **PASS** | eligible pending real Betpawa prices |
| SERIEA | sh_over_0.5 | 830 | 0.7805 | 0.7807 | 1.28 | **PASS** | eligible pending real Betpawa prices |
| SERIEA | sh_over_1.5 | 830 | 0.4351 | 0.4253 | 2.32 | **PASS** | eligible pending real Betpawa prices |
| SERIEA | home_win_either_half | 830 | 0.5558 | 0.5386 | 1.79 | **PASS** | eligible pending real Betpawa prices |
| SERIEA | away_win_either_half | 830 | 0.4660 | 0.4892 | 2.19 | **PASS** | eligible pending real Betpawa prices |
| BUNDES | fh_over_0.5 | 665 | 0.7754 | 0.7744 | 1.29 | **PASS** | eligible pending real Betpawa prices |
| BUNDES | fh_over_1.5 | 665 | 0.4359 | 0.4346 | 2.32 | **PASS** | eligible pending real Betpawa prices |
| BUNDES | sh_over_0.5 | 665 | 0.8290 | 0.8436 | 1.21 | **PASS** | eligible pending real Betpawa prices |
| BUNDES | sh_over_1.5 | 665 | 0.5363 | 0.5398 | 1.87 | **PASS** | eligible pending real Betpawa prices |
| BUNDES | home_win_either_half | 665 | 0.5917 | 0.5714 | 1.71 | **PASS** | eligible pending real Betpawa prices |
| BUNDES | away_win_either_half | 665 | 0.4618 | 0.4872 | 2.17 | **PASS** | eligible pending real Betpawa prices |
| LIGUE1 | fh_over_0.5 | 675 | 0.7438 | 0.7274 | 1.35 | **PASS** | eligible pending real Betpawa prices |
| LIGUE1 | fh_over_1.5 | 675 | 0.3801 | 0.3511 | 2.69 | **PASS** | eligible pending real Betpawa prices |
| LIGUE1 | sh_over_0.5 | 675 | 0.8094 | 0.8104 | 1.24 | **PASS** | eligible pending real Betpawa prices |
| LIGUE1 | sh_over_1.5 | 675 | 0.4826 | 0.4770 | 2.10 | **PASS** | eligible pending real Betpawa prices |
| LIGUE1 | home_win_either_half | 675 | 0.5804 | 0.5867 | 1.71 | **PASS** | eligible pending real Betpawa prices |
| LIGUE1 | away_win_either_half | 675 | 0.4780 | 0.4578 | 2.12 | **PASS** | eligible pending real Betpawa prices |
| EREDIV | fh_over_0.5 | 701 | 0.7562 | 0.7803 | 1.33 | **PASS** | eligible pending real Betpawa prices |
| EREDIV | fh_over_1.5 | 701 | 0.4138 | 0.4251 | 2.48 | **PASS** | eligible pending real Betpawa prices |
| EREDIV | sh_over_0.5 | 701 | 0.8420 | 0.8459 | 1.19 | **PASS** | eligible pending real Betpawa prices |
| EREDIV | sh_over_1.5 | 701 | 0.5336 | 0.5264 | 1.90 | **FAIL** | stays out |
| EREDIV | home_win_either_half | 701 | 0.5948 | 0.5863 | 1.70 | **PASS** | eligible pending real Betpawa prices |
| EREDIV | away_win_either_half | 701 | 0.4645 | 0.4679 | 2.17 | **PASS** | eligible pending real Betpawa prices |
| JUPILER | fh_over_0.5 | 702 | 0.7259 | 0.7279 | 1.37 | **PASS** | eligible pending real Betpawa prices |
| JUPILER | fh_over_1.5 | 702 | 0.3645 | 0.3632 | 2.77 | **PASS** | eligible pending real Betpawa prices |
| JUPILER | sh_over_0.5 | 702 | 0.8117 | 0.7650 | 1.23 | **FAIL** | stays out |
| JUPILER | sh_over_1.5 | 702 | 0.4831 | 0.4516 | 2.07 | **PASS** | eligible pending real Betpawa prices |
| JUPILER | home_win_either_half | 702 | 0.5750 | 0.5769 | 1.74 | **PASS** | eligible pending real Betpawa prices |
| JUPILER | away_win_either_half | 702 | 0.4632 | 0.4459 | 2.20 | **PASS** | eligible pending real Betpawa prices |
| PRIMEIRA | fh_over_0.5 | 693 | 0.7061 | 0.6941 | 1.43 | **FAIL** | stays out |
| PRIMEIRA | fh_over_1.5 | 693 | 0.3429 | 0.3362 | 3.06 | **PASS** | eligible pending real Betpawa prices |
| PRIMEIRA | sh_over_0.5 | 693 | 0.7676 | 0.7879 | 1.32 | **PASS** | eligible pending real Betpawa prices |
| PRIMEIRA | sh_over_1.5 | 693 | 0.4143 | 0.4315 | 2.52 | **PASS** | eligible pending real Betpawa prices |
| PRIMEIRA | home_win_either_half | 693 | 0.5618 | 0.5613 | 1.75 | **PASS** | eligible pending real Betpawa prices |
| PRIMEIRA | away_win_either_half | 693 | 0.4687 | 0.4646 | 2.20 | **PASS** | eligible pending real Betpawa prices |
| SUPERLIG | fh_over_0.5 | 728 | 0.7295 | 0.7212 | 1.38 | **PASS** | eligible pending real Betpawa prices |
| SUPERLIG | fh_over_1.5 | 728 | 0.3658 | 0.3503 | 2.81 | **PASS** | eligible pending real Betpawa prices |
| SUPERLIG | sh_over_0.5 | 728 | 0.7958 | 0.7802 | 1.26 | **PASS** | eligible pending real Betpawa prices |
| SUPERLIG | sh_over_1.5 | 728 | 0.4702 | 0.4794 | 2.18 | **PASS** | eligible pending real Betpawa prices |
| SUPERLIG | home_win_either_half | 728 | 0.5960 | 0.6113 | 1.64 | **PASS** | eligible pending real Betpawa prices |
| SUPERLIG | away_win_either_half | 728 | 0.4538 | 0.4492 | 2.30 | **PASS** | eligible pending real Betpawa prices |

Summary: **49 PASS / 5 FAIL** across 54 league x market pairs.

First-half goal shares by league:
```json
{
  "EPL": {
    "matches": 4630,
    "share_2024_25": 0.4471,
    "share_2026_27": 0.4474
  },
  "LALIGA": {
    "matches": 4649,
    "share_2024_25": 0.439,
    "share_2026_27": 0.4381
  },
  "SERIEA": {
    "matches": 4627,
    "share_2024_25": 0.4385,
    "share_2026_27": 0.4376
  },
  "BUNDES": {
    "matches": 3725,
    "share_2024_25": 0.4437,
    "share_2026_27": 0.4459
  },
  "LIGUE1": {
    "matches": 4299,
    "share_2024_25": 0.4415,
    "share_2026_27": 0.4406
  },
  "EREDIV": {
    "matches": 3687,
    "share_2024_25": 0.4364,
    "share_2026_27": 0.4386
  },
  "JUPILER": {
    "matches": 3360,
    "share_2024_25": 0.4329,
    "share_2026_27": 0.4385
  },
  "PRIMEIRA": {
    "matches": 3752,
    "share_2024_25": 0.4486,
    "share_2026_27": 0.4487
  },
  "SUPERLIG": {
    "matches": 4056,
    "share_2024_25": 0.4346,
    "share_2026_27": 0.4357
  }
}
```

Gate details:
```json
[
 {
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
   -0.0386,
   0.0245
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
  "fair_odds": 1.36,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0694,
   -0.0
  ],
  "C2": false,
  "C3_min_z": -2.77,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0006,
  "logloss_vs_book_ci": [
   -0.0001,
   0.0012
  ],
  "mean_p": 0.3843,
  "actual": 0.3494,
  "fair_odds": 2.64,
  "eligibility": "stays out"
 },
 {
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
   -0.0319,
   0.0215
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
   0.0031
  ],
  "mean_p": 0.8195,
  "actual": 0.8133,
  "fair_odds": 1.22,
  "eligibility": "stays out"
 },
 {
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
   -0.0415,
   0.026
  ],
  "C2": true,
  "C3_min_z": -2.22,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.0001,
  "logloss_vs_book_ci": [
   -0.0018,
   0.0019
  ],
  "mean_p": 0.4965,
  "actual": 0.4904,
  "fair_odds": 2.04,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0438,
   0.0246
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
   0.0018
  ],
  "mean_p": 0.5881,
  "actual": 0.5783,
  "fair_odds": 1.7,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0107,
   0.0572
  ],
  "C2": true,
  "C3_min_z": -1.47,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.0004,
  "logloss_vs_book_ci": [
   -0.0015,
   0.0007
  ],
  "mean_p": 0.4707,
  "actual": 0.4976,
  "fair_odds": 2.15,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0138,
   0.0463
  ],
  "C2": true,
  "C3_min_z": -1.95,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0011,
  "logloss_vs_book_ci": [
   -0.0003,
   0.0025
  ],
  "mean_p": 0.6707,
  "actual": 0.6867,
  "fair_odds": 1.51,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0207,
   0.0389
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
  "fair_odds": 3.31,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0006,
   0.0542
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
   -0.0006
  ],
  "mean_p": 0.7785,
  "actual": 0.8057,
  "fair_odds": 1.29,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0317,
   0.0412
  ],
  "C2": true,
  "C3_min_z": -2.04,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.0,
  "logloss_vs_book_ci": [
   -0.001,
   0.001
  ],
  "mean_p": 0.4387,
  "actual": 0.4441,
  "fair_odds": 2.36,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   0.0111,
   0.0722
  ],
  "C2": true,
  "C3_min_z": -0.3,
  "C3": true,
  "C4_lifted_legs": 12,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.0033,
  "logloss_vs_book_ci": [
   -0.0058,
   -0.0006
  ],
  "mean_p": 0.5831,
  "actual": 0.6243,
  "fair_odds": 1.75,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0262,
   0.0366
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
   0.0016
  ],
  "mean_p": 0.4306,
  "actual": 0.437,
  "fair_odds": 2.4,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0394,
   0.0218
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
  "fair_odds": 1.48,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.041,
   0.02
  ],
  "C2": true,
  "C3_min_z": -2.03,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0003,
  "logloss_vs_book_ci": [
   -0.0007,
   0.0012
  ],
  "mean_p": 0.309,
  "actual": 0.2988,
  "fair_odds": 3.28,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0294,
   0.0272
  ],
  "C2": true,
  "C3_min_z": -1.63,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.0006,
  "logloss_vs_book_ci": [
   -0.0037,
   0.0025
  ],
  "mean_p": 0.7805,
  "actual": 0.7807,
  "fair_odds": 1.28,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0441,
   0.0234
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
   0.0021
  ],
  "mean_p": 0.4351,
  "actual": 0.4253,
  "fair_odds": 2.32,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.046,
   0.0134
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
  "fair_odds": 1.79,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0084,
   0.056
  ],
  "C2": true,
  "C3_min_z": -0.5,
  "C3": true,
  "C4_lifted_legs": 290,
  "C4_z": 0.81,
  "C4": true,
  "logloss_vs_book": -0.0028,
  "logloss_vs_book_ci": [
   -0.0067,
   0.0013
  ],
  "mean_p": 0.466,
  "actual": 0.4892,
  "fair_odds": 2.19,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0325,
   0.0282
  ],
  "C2": true,
  "C3_min_z": -1.23,
  "C3": true,
  "C4_lifted_legs": 260,
  "C4_z": -0.52,
  "C4": true,
  "logloss_vs_book": -0.0021,
  "logloss_vs_book_ci": [
   -0.0067,
   0.0029
  ],
  "mean_p": 0.7754,
  "actual": 0.7744,
  "fair_odds": 1.29,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0377,
   0.0327
  ],
  "C2": true,
  "C3_min_z": -1.55,
  "C3": true,
  "C4_lifted_legs": 301,
  "C4_z": 0.53,
  "C4": true,
  "logloss_vs_book": -0.0025,
  "logloss_vs_book_ci": [
   -0.0078,
   0.0023
  ],
  "mean_p": 0.4359,
  "actual": 0.4346,
  "fair_odds": 2.32,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.013,
   0.0422
  ],
  "C2": true,
  "C3_min_z": -1.56,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.0003,
  "logloss_vs_book_ci": [
   -0.0019,
   0.0013
  ],
  "mean_p": 0.829,
  "actual": 0.8436,
  "fair_odds": 1.21,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0361,
   0.0426
  ],
  "C2": true,
  "C3_min_z": -1.49,
  "C3": true,
  "C4_lifted_legs": 15,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0002,
  "logloss_vs_book_ci": [
   -0.0026,
   0.0031
  ],
  "mean_p": 0.5363,
  "actual": 0.5398,
  "fair_odds": 1.87,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0562,
   0.0128
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
  "fair_odds": 1.71,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.012,
   0.0617
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
   0.0037
  ],
  "mean_p": 0.4618,
  "actual": 0.4872,
  "fair_odds": 2.17,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0484,
   0.0177
  ],
  "C2": true,
  "C3_min_z": -2.13,
  "C3": true,
  "C4_lifted_legs": 219,
  "C4_z": -1.59,
  "C4": true,
  "logloss_vs_book": 0.002,
  "logloss_vs_book_ci": [
   -0.003,
   0.007
  ],
  "mean_p": 0.7438,
  "actual": 0.7274,
  "fair_odds": 1.35,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0666,
   0.0111
  ],
  "C2": true,
  "C3_min_z": -2.27,
  "C3": true,
  "C4_lifted_legs": 91,
  "C4_z": -1.76,
  "C4": true,
  "logloss_vs_book": 0.0027,
  "logloss_vs_book_ci": [
   -0.0008,
   0.0057
  ],
  "mean_p": 0.3801,
  "actual": 0.3511,
  "fair_odds": 2.69,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0285,
   0.0292
  ],
  "C2": true,
  "C3_min_z": -1.26,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.0007,
  "logloss_vs_book_ci": [
   -0.0031,
   0.0017
  ],
  "mean_p": 0.8094,
  "actual": 0.8104,
  "fair_odds": 1.24,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0414,
   0.0356
  ],
  "C2": true,
  "C3_min_z": -1.75,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0005,
  "logloss_vs_book_ci": [
   -0.0006,
   0.0015
  ],
  "mean_p": 0.4826,
  "actual": 0.477,
  "fair_odds": 2.1,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0322,
   0.041
  ],
  "C2": true,
  "C3_min_z": -0.65,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.0011,
  "logloss_vs_book_ci": [
   -0.004,
   0.0018
  ],
  "mean_p": 0.5804,
  "actual": 0.5867,
  "fair_odds": 1.71,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0558,
   0.019
  ],
  "C2": true,
  "C3_min_z": -0.85,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0007,
  "logloss_vs_book_ci": [
   -0.0019,
   0.0032
  ],
  "mean_p": 0.478,
  "actual": 0.4578,
  "fair_odds": 2.12,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0084,
   0.052
  ],
  "C2": true,
  "C3_min_z": -0.78,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.0028,
  "logloss_vs_book_ci": [
   -0.0048,
   -0.0006
  ],
  "mean_p": 0.7562,
  "actual": 0.7803,
  "fair_odds": 1.33,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0205,
   0.0431
  ],
  "C2": true,
  "C3_min_z": -1.67,
  "C3": true,
  "C4_lifted_legs": 10,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.0012,
  "logloss_vs_book_ci": [
   -0.0036,
   0.0013
  ],
  "mean_p": 0.4138,
  "actual": 0.4251,
  "fair_odds": 2.48,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0216,
   0.0296
  ],
  "C2": true,
  "C3_min_z": -1.61,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.0013,
  "logloss_vs_book_ci": [
   -0.0048,
   0.0022
  ],
  "mean_p": 0.842,
  "actual": 0.8459,
  "fair_odds": 1.19,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0391,
   0.0299
  ],
  "C2": true,
  "C3_min_z": -2.33,
  "C3": true,
  "C4_lifted_legs": 69,
  "C4_z": -2.53,
  "C4": false,
  "logloss_vs_book": 0.0023,
  "logloss_vs_book_ci": [
   -0.0006,
   0.0051
  ],
  "mean_p": 0.5336,
  "actual": 0.5264,
  "fair_odds": 1.9,
  "eligibility": "stays out"
 },
 {
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
   -0.042,
   0.0268
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
   0.0021
  ],
  "mean_p": 0.5948,
  "actual": 0.5863,
  "fair_odds": 1.7,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0306,
   0.0363
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
   0.0038
  ],
  "mean_p": 0.4645,
  "actual": 0.4679,
  "fair_odds": 2.17,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0301,
   0.0325
  ],
  "C2": true,
  "C3_min_z": -1.93,
  "C3": true,
  "C4_lifted_legs": 197,
  "C4_z": 1.04,
  "C4": true,
  "logloss_vs_book": -0.0047,
  "logloss_vs_book_ci": [
   -0.0088,
   -0.0002
  ],
  "mean_p": 0.7259,
  "actual": 0.7279,
  "fair_odds": 1.37,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0346,
   0.034
  ],
  "C2": true,
  "C3_min_z": -2.26,
  "C3": true,
  "C4_lifted_legs": 135,
  "C4_z": 0.36,
  "C4": true,
  "logloss_vs_book": 0.0004,
  "logloss_vs_book_ci": [
   -0.0036,
   0.0039
  ],
  "mean_p": 0.3645,
  "actual": 0.3632,
  "fair_odds": 2.77,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0789,
   -0.0159
  ],
  "C2": false,
  "C3_min_z": -2.81,
  "C3": true,
  "C4_lifted_legs": 41,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0055,
  "logloss_vs_book_ci": [
   0.0021,
   0.0086
  ],
  "mean_p": 0.8117,
  "actual": 0.765,
  "fair_odds": 1.23,
  "eligibility": "stays out"
 },
 {
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
   -0.069,
   0.0119
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
  "fair_odds": 2.07,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0332,
   0.0393
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
   0.0008
  ],
  "mean_p": 0.575,
  "actual": 0.5769,
  "fair_odds": 1.74,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0545,
   0.0171
  ],
  "C2": true,
  "C3_min_z": -2.36,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.0009,
  "logloss_vs_book_ci": [
   -0.0022,
   0.0005
  ],
  "mean_p": 0.4632,
  "actual": 0.4459,
  "fair_odds": 2.2,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.048,
   0.0217
  ],
  "C2": true,
  "C3_min_z": -1.96,
  "C3": true,
  "C4_lifted_legs": 68,
  "C4_z": -2.07,
  "C4": false,
  "logloss_vs_book": 0.0023,
  "logloss_vs_book_ci": [
   -0.0011,
   0.0055
  ],
  "mean_p": 0.7061,
  "actual": 0.6941,
  "fair_odds": 1.43,
  "eligibility": "stays out"
 },
 {
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
   -0.0429,
   0.0278
  ],
  "C2": true,
  "C3_min_z": -1.86,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0004,
  "logloss_vs_book_ci": [
   -0.0016,
   0.0024
  ],
  "mean_p": 0.3429,
  "actual": 0.3362,
  "fair_odds": 3.06,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0073,
   0.0469
  ],
  "C2": true,
  "C3_min_z": -1.71,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.001,
  "logloss_vs_book_ci": [
   -0.0029,
   0.0009
  ],
  "mean_p": 0.7676,
  "actual": 0.7879,
  "fair_odds": 1.32,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0174,
   0.0482
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
   0.0028
  ],
  "mean_p": 0.4143,
  "actual": 0.4315,
  "fair_odds": 2.52,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0371,
   0.0328
  ],
  "C2": true,
  "C3_min_z": -2.04,
  "C3": true,
  "C4_lifted_legs": 280,
  "C4_z": -1.36,
  "C4": true,
  "logloss_vs_book": 0.0002,
  "logloss_vs_book_ci": [
   -0.0057,
   0.0068
  ],
  "mean_p": 0.5618,
  "actual": 0.5613,
  "fair_odds": 1.75,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0359,
   0.03
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
   0.0025
  ],
  "mean_p": 0.4687,
  "actual": 0.4646,
  "fair_odds": 2.2,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0391,
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
   -0.0057,
   0.002
  ],
  "mean_p": 0.7295,
  "actual": 0.7212,
  "fair_odds": 1.38,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0514,
   0.0219
  ],
  "C2": true,
  "C3_min_z": -2.56,
  "C3": true,
  "C4_lifted_legs": 1,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.0,
  "logloss_vs_book_ci": [
   -0.0024,
   0.0021
  ],
  "mean_p": 0.3658,
  "actual": 0.3503,
  "fair_odds": 2.81,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0442,
   0.0133
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
   0.0011
  ],
  "mean_p": 0.7958,
  "actual": 0.7802,
  "fair_odds": 1.26,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0228,
   0.042
  ],
  "C2": true,
  "C3_min_z": -1.51,
  "C3": true,
  "C4_lifted_legs": 1,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.0005,
  "logloss_vs_book_ci": [
   -0.0022,
   0.0013
  ],
  "mean_p": 0.4702,
  "actual": 0.4794,
  "fair_odds": 2.18,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0206,
   0.0502
  ],
  "C2": true,
  "C3_min_z": -1.89,
  "C3": true,
  "C4_lifted_legs": 335,
  "C4_z": 0.15,
  "C4": true,
  "logloss_vs_book": -0.0038,
  "logloss_vs_book_ci": [
   -0.0089,
   0.0011
  ],
  "mean_p": 0.596,
  "actual": 0.6113,
  "fair_odds": 1.64,
  "eligibility": "eligible pending real Betpawa prices"
 },
 {
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
   -0.0385,
   0.0281
  ],
  "C2": true,
  "C3_min_z": -1.06,
  "C3": true,
  "C4_lifted_legs": 66,
  "C4_z": 1.27,
  "C4": true,
  "logloss_vs_book": -0.0032,
  "logloss_vs_book_ci": [
   -0.0067,
   0.0002
  ],
  "mean_p": 0.4538,
  "actual": 0.4492,
  "fair_odds": 2.3,
  "eligibility": "eligible pending real Betpawa prices"
 }
]
```
