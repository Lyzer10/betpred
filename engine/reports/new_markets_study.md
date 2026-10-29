# New markets study (PROJECT.md task 10, pre-registered 2026-10-29)

| League | Market | n | Said | Won | Fair odds | Gates | Raw matrix gates |
|---|---|---|---|---|---|---|---|
| EPL | home_over_0.5 | 830 | 0.789 | 0.763 | 1.25 | **PASS** | PASS |
| EPL | away_over_0.5 | 830 | 0.713 | 0.743 | 1.40 | **PASS** | PASS |
| EPL | home_over_1.5 | 830 | 0.477 | 0.469 | 2.12 | **PASS** | PASS |
| EPL | away_over_1.5 | 830 | 0.382 | 0.381 | 2.75 | **PASS** | PASS |
| EPL | dnb_home | 613 | 0.585 | 0.563 | 1.64 | **PASS** | PASS |
| EPL | dnb_away | 613 | 0.415 | 0.437 | 2.55 | **PASS** | PASS |
| LALIGA | home_over_0.5 | 849 | 0.762 | 0.806 | 1.32 | **PASS** | PASS |
| LALIGA | away_over_0.5 | 849 | 0.668 | 0.701 | 1.52 | **PASS** | PASS |
| LALIGA | home_over_1.5 | 849 | 0.427 | 0.424 | 2.56 | **PASS** | PASS |
| LALIGA | away_over_1.5 | 849 | 0.310 | 0.320 | 3.61 | **PASS** | PASS |
| LALIGA | dnb_home | 634 | 0.614 | 0.622 | 1.57 | **PASS** | PASS |
| LALIGA | dnb_away | 634 | 0.386 | 0.379 | 2.76 | **PASS** | PASS |
| SERIEA | home_over_0.5 | 830 | 0.747 | 0.717 | 1.33 | **FAIL** | PASS |
| SERIEA | away_over_0.5 | 830 | 0.686 | 0.696 | 1.46 | **PASS** | PASS |
| SERIEA | home_over_1.5 | 830 | 0.401 | 0.396 | 2.65 | **PASS** | PASS |
| SERIEA | away_over_1.5 | 830 | 0.325 | 0.349 | 3.43 | **PASS** | PASS |
| SERIEA | dnb_home | 611 | 0.558 | 0.543 | 1.72 | **PASS** | PASS |
| SERIEA | dnb_away | 611 | 0.442 | 0.457 | 2.40 | **PASS** | PASS |
| BUNDES | home_over_0.5 | 666 | 0.815 | 0.791 | 1.23 | **PASS** | PASS |
| BUNDES | away_over_0.5 | 666 | 0.732 | 0.745 | 1.36 | **PASS** | PASS |
| BUNDES | home_over_1.5 | 666 | 0.511 | 0.506 | 2.04 | **PASS** | PASS |
| BUNDES | away_over_1.5 | 666 | 0.386 | 0.429 | 2.72 | **PASS** | PASS |
| BUNDES | dnb_home | 503 | 0.609 | 0.557 | 1.60 | **FAIL** | PASS |
| BUNDES | dnb_away | 503 | 0.391 | 0.443 | 2.66 | **PASS** | PASS |
| LIGUE1 | home_over_0.5 | 675 | 0.784 | 0.782 | 1.27 | **PASS** | PASS |
| LIGUE1 | away_over_0.5 | 675 | 0.722 | 0.702 | 1.38 | **PASS** | PASS |
| LIGUE1 | home_over_1.5 | 675 | 0.466 | 0.465 | 2.24 | **PASS** | PASS |
| LIGUE1 | away_over_1.5 | 675 | 0.368 | 0.367 | 2.86 | **PASS** | PASS |
| LIGUE1 | dnb_home | 523 | 0.571 | 0.597 | 1.68 | **PASS** | PASS |
| LIGUE1 | dnb_away | 523 | 0.429 | 0.403 | 2.46 | **PASS** | PASS |

Details:
```
[
 {
  "league": "EPL",
  "market": "home_over_0.5",
  "n": 830,
  "status": "PASS",
  "C1_slope": 1.12,
  "C1_ci": [
   0.824,
   1.415
  ],
  "C1": true,
  "C2_level": -0.0267,
  "C2_ci": [
   -0.0545,
   0.0017
  ],
  "C2": true,
  "C3_min_z": -2.2,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0009,
  "logloss_vs_book_ci": [
   -0.0006,
   0.0027
  ],
  "mean_p": 0.7894,
  "actual": 0.7627,
  "raw_status": "PASS"
 },
 {
  "league": "EPL",
  "market": "away_over_0.5",
  "n": 830,
  "status": "PASS",
  "C1_slope": 0.952,
  "C1_ci": [
   0.641,
   1.262
  ],
  "C1": true,
  "C2_level": 0.0305,
  "C2_ci": [
   0.0015,
   0.0629
  ],
  "C2": true,
  "C3_min_z": -0.82,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0001,
  "logloss_vs_book_ci": [
   -0.0003,
   0.0005
  ],
  "mean_p": 0.7129,
  "actual": 0.7434,
  "raw_status": "PASS"
 },
 {
  "league": "EPL",
  "market": "home_over_1.5",
  "n": 830,
  "status": "PASS",
  "C1_slope": 0.812,
  "C1_ci": [
   0.595,
   1.028
  ],
  "C1": true,
  "C2_level": -0.0087,
  "C2_ci": [
   -0.0426,
   0.0241
  ],
  "C2": true,
  "C3_min_z": -1.48,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0017,
  "logloss_vs_book_ci": [
   -0.0002,
   0.0038
  ],
  "mean_p": 0.4773,
  "actual": 0.4687,
  "raw_status": "PASS"
 },
 {
  "league": "EPL",
  "market": "away_over_1.5",
  "n": 830,
  "status": "PASS",
  "C1_slope": 0.834,
  "C1_ci": [
   0.591,
   1.077
  ],
  "C1": true,
  "C2_level": -0.0011,
  "C2_ci": [
   -0.037,
   0.0312
  ],
  "C2": true,
  "C3_min_z": -1.27,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0,
  "logloss_vs_book_ci": [
   -0.0013,
   0.0012
  ],
  "mean_p": 0.3818,
  "actual": 0.3807,
  "raw_status": "PASS"
 },
 {
  "league": "EPL",
  "market": "dnb_home",
  "n": 613,
  "status": "PASS",
  "C1_slope": 1.076,
  "C1_ci": [
   0.869,
   1.282
  ],
  "C1": true,
  "C2_level": -0.0224,
  "C2_ci": [
   -0.0605,
   0.0134
  ],
  "C2": true,
  "C3_min_z": -1.64,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0006,
  "logloss_vs_book_ci": [
   -0.0004,
   0.0017
  ],
  "mean_p": 0.5852,
  "actual": 0.5628,
  "raw_status": "PASS"
 },
 {
  "league": "EPL",
  "market": "dnb_away",
  "n": 613,
  "status": "PASS",
  "C1_slope": 1.076,
  "C1_ci": [
   0.869,
   1.282
  ],
  "C1": true,
  "C2_level": 0.0224,
  "C2_ci": [
   -0.0144,
   0.0564
  ],
  "C2": true,
  "C3_min_z": -0.76,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0006,
  "logloss_vs_book_ci": [
   -0.0004,
   0.0017
  ],
  "mean_p": 0.4148,
  "actual": 0.4372,
  "raw_status": "PASS"
 },
 {
  "league": "LALIGA",
  "market": "home_over_0.5",
  "n": 849,
  "status": "PASS",
  "C1_slope": 1.103,
  "C1_ci": [
   0.77,
   1.437
  ],
  "C1": true,
  "C2_level": 0.0437,
  "C2_ci": [
   0.0191,
   0.0689
  ],
  "C2": true,
  "C3_min_z": 0.04,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.0042,
  "logloss_vs_book_ci": [
   -0.0065,
   -0.0018
  ],
  "mean_p": 0.762,
  "actual": 0.8057,
  "raw_status": "PASS"
 },
 {
  "league": "LALIGA",
  "market": "away_over_0.5",
  "n": 849,
  "status": "PASS",
  "C1_slope": 1.066,
  "C1_ci": [
   0.762,
   1.369
  ],
  "C1": true,
  "C2_level": 0.0325,
  "C2_ci": [
   0.0025,
   0.062
  ],
  "C2": true,
  "C3_min_z": 0.26,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.002,
  "logloss_vs_book_ci": [
   -0.0035,
   -0.0002
  ],
  "mean_p": 0.6683,
  "actual": 0.7008,
  "raw_status": "PASS"
 },
 {
  "league": "LALIGA",
  "market": "home_over_1.5",
  "n": 849,
  "status": "PASS",
  "C1_slope": 1.197,
  "C1_ci": [
   0.956,
   1.438
  ],
  "C1": true,
  "C2_level": -0.0034,
  "C2_ci": [
   -0.0341,
   0.0239
  ],
  "C2": true,
  "C3_min_z": -1.1,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.0007,
  "logloss_vs_book_ci": [
   -0.0018,
   0.0005
  ],
  "mean_p": 0.4274,
  "actual": 0.424,
  "raw_status": "PASS"
 },
 {
  "league": "LALIGA",
  "market": "away_over_1.5",
  "n": 849,
  "status": "PASS",
  "C1_slope": 0.94,
  "C1_ci": [
   0.709,
   1.171
  ],
  "C1": true,
  "C2_level": 0.0105,
  "C2_ci": [
   -0.0179,
   0.0403
  ],
  "C2": true,
  "C3_min_z": -1.08,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0004,
  "logloss_vs_book_ci": [
   -0.0006,
   0.0016
  ],
  "mean_p": 0.3098,
  "actual": 0.3204,
  "raw_status": "PASS"
 },
 {
  "league": "LALIGA",
  "market": "dnb_home",
  "n": 634,
  "status": "PASS",
  "C1_slope": 1.022,
  "C1_ci": [
   0.825,
   1.218
  ],
  "C1": true,
  "C2_level": 0.0079,
  "C2_ci": [
   -0.0217,
   0.0397
  ],
  "C2": true,
  "C3_min_z": -1.46,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.002,
  "logloss_vs_book_ci": [
   -0.0056,
   0.0018
  ],
  "mean_p": 0.6136,
  "actual": 0.6215,
  "raw_status": "PASS"
 },
 {
  "league": "LALIGA",
  "market": "dnb_away",
  "n": 634,
  "status": "PASS",
  "C1_slope": 1.022,
  "C1_ci": [
   0.825,
   1.218
  ],
  "C1": true,
  "C2_level": -0.0079,
  "C2_ci": [
   -0.0413,
   0.024
  ],
  "C2": true,
  "C3_min_z": -1.67,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.002,
  "logloss_vs_book_ci": [
   -0.006,
   0.002
  ],
  "mean_p": 0.3864,
  "actual": 0.3785,
  "raw_status": "PASS"
 },
 {
  "league": "SERIEA",
  "market": "home_over_0.5",
  "n": 830,
  "status": "FAIL",
  "C1_slope": 1.313,
  "C1_ci": [
   1.031,
   1.595
  ],
  "C1": true,
  "C2_level": -0.0298,
  "C2_ci": [
   -0.0556,
   -0.0024
  ],
  "C2": false,
  "C3_min_z": -2.53,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.0009,
  "logloss_vs_book_ci": [
   -0.0035,
   0.002
  ],
  "mean_p": 0.7466,
  "actual": 0.7169,
  "raw_status": "PASS"
 },
 {
  "league": "SERIEA",
  "market": "away_over_0.5",
  "n": 830,
  "status": "PASS",
  "C1_slope": 1.045,
  "C1_ci": [
   0.769,
   1.32
  ],
  "C1": true,
  "C2_level": 0.0103,
  "C2_ci": [
   -0.0218,
   0.0405
  ],
  "C2": true,
  "C3_min_z": -1.76,
  "C3": true,
  "C4_lifted_legs": 161,
  "C4_z": 0.1,
  "C4": true,
  "logloss_vs_book": -0.0029,
  "logloss_vs_book_ci": [
   -0.0065,
   0.0008
  ],
  "mean_p": 0.6861,
  "actual": 0.6964,
  "raw_status": "PASS"
 },
 {
  "league": "SERIEA",
  "market": "home_over_1.5",
  "n": 830,
  "status": "PASS",
  "C1_slope": 1.17,
  "C1_ci": [
   0.933,
   1.407
  ],
  "C1": true,
  "C2_level": -0.0048,
  "C2_ci": [
   -0.0329,
   0.0287
  ],
  "C2": true,
  "C3_min_z": -1.45,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.0009,
  "logloss_vs_book_ci": [
   -0.0021,
   0.0002
  ],
  "mean_p": 0.4012,
  "actual": 0.3964,
  "raw_status": "PASS"
 },
 {
  "league": "SERIEA",
  "market": "away_over_1.5",
  "n": 830,
  "status": "PASS",
  "C1_slope": 0.775,
  "C1_ci": [
   0.568,
   0.982
  ],
  "C1": true,
  "C2_level": 0.0241,
  "C2_ci": [
   -0.007,
   0.0554
  ],
  "C2": true,
  "C3_min_z": -0.64,
  "C3": true,
  "C4_lifted_legs": 155,
  "C4_z": -0.53,
  "C4": true,
  "logloss_vs_book": 0.0012,
  "logloss_vs_book_ci": [
   -0.0018,
   0.0044
  ],
  "mean_p": 0.3253,
  "actual": 0.3494,
  "raw_status": "PASS"
 },
 {
  "league": "SERIEA",
  "market": "dnb_home",
  "n": 611,
  "status": "PASS",
  "C1_slope": 1.043,
  "C1_ci": [
   0.866,
   1.22
  ],
  "C1": true,
  "C2_level": -0.0142,
  "C2_ci": [
   -0.047,
   0.0193
  ],
  "C2": true,
  "C3_min_z": -2.08,
  "C3": true,
  "C4_lifted_legs": 23,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.0054,
  "logloss_vs_book_ci": [
   -0.011,
   0.0004
  ],
  "mean_p": 0.5576,
  "actual": 0.5434,
  "raw_status": "PASS"
 },
 {
  "league": "SERIEA",
  "market": "dnb_away",
  "n": 611,
  "status": "PASS",
  "C1_slope": 1.043,
  "C1_ci": [
   0.866,
   1.22
  ],
  "C1": true,
  "C2_level": 0.0142,
  "C2_ci": [
   -0.0186,
   0.0481
  ],
  "C2": true,
  "C3_min_z": -0.53,
  "C3": true,
  "C4_lifted_legs": 219,
  "C4_z": 0.62,
  "C4": true,
  "logloss_vs_book": -0.0054,
  "logloss_vs_book_ci": [
   -0.0113,
   0.0009
  ],
  "mean_p": 0.4424,
  "actual": 0.4566,
  "raw_status": "PASS"
 },
 {
  "league": "BUNDES",
  "market": "home_over_0.5",
  "n": 666,
  "status": "PASS",
  "C1_slope": 1.205,
  "C1_ci": [
   0.842,
   1.567
  ],
  "C1": true,
  "C2_level": -0.0234,
  "C2_ci": [
   -0.0541,
   0.0045
  ],
  "C2": true,
  "C3_min_z": -1.93,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0009,
  "logloss_vs_book_ci": [
   -0.0016,
   0.0037
  ],
  "mean_p": 0.8147,
  "actual": 0.7913,
  "raw_status": "PASS"
 },
 {
  "league": "BUNDES",
  "market": "away_over_0.5",
  "n": 666,
  "status": "PASS",
  "C1_slope": 1.024,
  "C1_ci": [
   0.683,
   1.366
  ],
  "C1": true,
  "C2_level": 0.0132,
  "C2_ci": [
   -0.0157,
   0.0441
  ],
  "C2": true,
  "C3_min_z": -1.41,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0,
  "logloss_vs_book_ci": [
   -0.0012,
   0.0014
  ],
  "mean_p": 0.7315,
  "actual": 0.7447,
  "raw_status": "PASS"
 },
 {
  "league": "BUNDES",
  "market": "home_over_1.5",
  "n": 666,
  "status": "PASS",
  "C1_slope": 1.179,
  "C1_ci": [
   0.882,
   1.475
  ],
  "C1": true,
  "C2_level": -0.0053,
  "C2_ci": [
   -0.0407,
   0.0305
  ],
  "C2": true,
  "C3_min_z": -2.16,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0008,
  "logloss_vs_book_ci": [
   -0.0007,
   0.0024
  ],
  "mean_p": 0.5113,
  "actual": 0.506,
  "raw_status": "PASS"
 },
 {
  "league": "BUNDES",
  "market": "away_over_1.5",
  "n": 666,
  "status": "PASS",
  "C1_slope": 1.018,
  "C1_ci": [
   0.716,
   1.319
  ],
  "C1": true,
  "C2_level": 0.0433,
  "C2_ci": [
   0.0069,
   0.0784
  ],
  "C2": true,
  "C3_min_z": -1.24,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.003,
  "logloss_vs_book_ci": [
   0.0001,
   0.0061
  ],
  "mean_p": 0.3862,
  "actual": 0.4294,
  "raw_status": "PASS"
 },
 {
  "league": "BUNDES",
  "market": "dnb_home",
  "n": 503,
  "status": "FAIL",
  "C1_slope": 1.301,
  "C1_ci": [
   1.03,
   1.571
  ],
  "C1": true,
  "C2_level": -0.0526,
  "C2_ci": [
   -0.0937,
   -0.0142
  ],
  "C2": false,
  "C3_min_z": -2.03,
  "C3": true,
  "C4_lifted_legs": 50,
  "C4_z": -2.7,
  "C4": false,
  "logloss_vs_book": 0.0055,
  "logloss_vs_book_ci": [
   0.0019,
   0.0095
  ],
  "mean_p": 0.6092,
  "actual": 0.5567,
  "raw_status": "PASS"
 },
 {
  "league": "BUNDES",
  "market": "dnb_away",
  "n": 503,
  "status": "PASS",
  "C1_slope": 1.301,
  "C1_ci": [
   1.03,
   1.571
  ],
  "C1": true,
  "C2_level": 0.0526,
  "C2_ci": [
   0.0097,
   0.0985
  ],
  "C2": true,
  "C3_min_z": -0.68,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0055,
  "logloss_vs_book_ci": [
   0.0017,
   0.0094
  ],
  "mean_p": 0.3908,
  "actual": 0.4433,
  "raw_status": "PASS"
 },
 {
  "league": "LIGUE1",
  "market": "home_over_0.5",
  "n": 675,
  "status": "PASS",
  "C1_slope": 1.022,
  "C1_ci": [
   0.698,
   1.346
  ],
  "C1": true,
  "C2_level": -0.0018,
  "C2_ci": [
   -0.0403,
   0.0346
  ],
  "C2": true,
  "C3_min_z": -0.9,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": -0.001,
  "logloss_vs_book_ci": [
   -0.0044,
   0.0025
  ],
  "mean_p": 0.784,
  "actual": 0.7822,
  "raw_status": "PASS"
 },
 {
  "league": "LIGUE1",
  "market": "away_over_0.5",
  "n": 675,
  "status": "PASS",
  "C1_slope": 0.792,
  "C1_ci": [
   0.48,
   1.103
  ],
  "C1": true,
  "C2_level": -0.0193,
  "C2_ci": [
   -0.0548,
   0.0147
  ],
  "C2": true,
  "C3_min_z": -1.85,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0018,
  "logloss_vs_book_ci": [
   -0.0014,
   0.005
  ],
  "mean_p": 0.7215,
  "actual": 0.7022,
  "raw_status": "PASS"
 },
 {
  "league": "LIGUE1",
  "market": "home_over_1.5",
  "n": 675,
  "status": "PASS",
  "C1_slope": 0.736,
  "C1_ci": [
   0.506,
   0.967
  ],
  "C1": true,
  "C2_level": -0.0005,
  "C2_ci": [
   -0.039,
   0.0381
  ],
  "C2": true,
  "C3_min_z": -1.49,
  "C3": true,
  "C4_lifted_legs": 118,
  "C4_z": -1.43,
  "C4": true,
  "logloss_vs_book": 0.0026,
  "logloss_vs_book_ci": [
   -0.0011,
   0.0065
  ],
  "mean_p": 0.4656,
  "actual": 0.4652,
  "raw_status": "PASS"
 },
 {
  "league": "LIGUE1",
  "market": "away_over_1.5",
  "n": 675,
  "status": "PASS",
  "C1_slope": 0.845,
  "C1_ci": [
   0.571,
   1.119
  ],
  "C1": true,
  "C2_level": -0.0005,
  "C2_ci": [
   -0.0348,
   0.0328
  ],
  "C2": true,
  "C3_min_z": -1.38,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0002,
  "logloss_vs_book_ci": [
   -0.0003,
   0.0008
  ],
  "mean_p": 0.3679,
  "actual": 0.3674,
  "raw_status": "PASS"
 },
 {
  "league": "LIGUE1",
  "market": "dnb_home",
  "n": 523,
  "status": "PASS",
  "C1_slope": 0.959,
  "C1_ci": [
   0.754,
   1.164
  ],
  "C1": true,
  "C2_level": 0.0261,
  "C2_ci": [
   -0.0136,
   0.0646
  ],
  "C2": true,
  "C3_min_z": -0.34,
  "C3": true,
  "C4_lifted_legs": 0,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0006,
  "logloss_vs_book_ci": [
   -0.0023,
   0.0037
  ],
  "mean_p": 0.5705,
  "actual": 0.5966,
  "raw_status": "PASS"
 },
 {
  "league": "LIGUE1",
  "market": "dnb_away",
  "n": 523,
  "status": "PASS",
  "C1_slope": 0.959,
  "C1_ci": [
   0.754,
   1.164
  ],
  "C1": true,
  "C2_level": -0.0261,
  "C2_ci": [
   -0.0631,
   0.0137
  ],
  "C2": true,
  "C3_min_z": -1.44,
  "C3": true,
  "C4_lifted_legs": 15,
  "C4_z": null,
  "C4": true,
  "logloss_vs_book": 0.0006,
  "logloss_vs_book_ci": [
   -0.0025,
   0.0037
  ],
  "mean_p": 0.4295,
  "actual": 0.4034,
  "raw_status": "PASS"
 }
]
```