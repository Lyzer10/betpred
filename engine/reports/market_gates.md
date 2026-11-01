# League x market gates

Rules pre-registered in PROJECT.md (task 1) before any result was computed. Test seasons 2024/25+
plus every settled live published prediction (monthly re-check).
FAIL = removed from that league's slip legs; INSUFFICIENT = fewer than 300 legs (kept, flagged).

| League | Market | n | Status | Slope (95% CI) | Level gap (95% CI) | lowest bin z | Lifted legs / z | Log loss vs bookmaker (95% CI) |
|---|---|---:|---|---|---|---:|---|---|
| Premier League | home_1up | 838 | **PASS** | 1.254 (0.995, 1.514) | +0.0032 (-0.0279, +0.0349) | -1.37 | 137 / 0.33 | -0.0004 (-0.0042, +0.0031) |
| Premier League | away_1up | 846 | **PASS** | 1.095 (0.84, 1.35) | +0.0044 (-0.0291, +0.0359) | -0.56 | 147 / -0.28 | -0.0008 (-0.0046, +0.0035) |
| Premier League | over_0.5 | 18 | INSUFFICIENT | | | | | |
| Premier League | over_1.5 | 832 | **PASS** | 0.695 (-0.007, 1.398) | -0.0045 (-0.0312, +0.0216) | -1.71 | 17 / - | +0.0003 (-0.0017, +0.0025) |
| Premier League | over_2.5 | 847 | **FAIL** | 0.673 (0.201, 1.145) | -0.0209 (-0.0523, +0.0102) | -1.77 | 85 / -2.76 ✗ | +0.0015 (-0.0013, +0.0044) |
| Premier League | under_2.5 | 847 | **PASS** | 0.673 (0.201, 1.145) | +0.0209 (-0.0106, +0.0517) | -1.97 | 30 / - | +0.0015 (-0.0011, +0.0044) |
| Premier League | under_3.5 | 847 | **PASS** | 0.524 (0.035, 1.014) | +0.0403 (+0.0085, +0.0715) | -1.96 | 21 / - | +0.0012 (-0.0012, +0.0036) |
| Premier League | home_win | 847 | **PASS** | 1.09 (0.877, 1.303) | -0.0217 (-0.0582, +0.0124) | -1.64 | 67 / -1.28 | -0.0003 (-0.0039, +0.0034) |
| Premier League | away_win | 847 | **PASS** | 1.042 (0.827, 1.257) | +0.0034 (-0.0266, +0.0327) | -1.02 | 87 / 0.02 | -0.0027 (-0.0069, +0.0012) |
| Premier League | double_1x | 788 | **PASS** | 1.026 (0.793, 1.259) | -0.0047 (-0.0356, +0.0288) | -1.71 | 89 / 0.86 | -0.0030 (-0.0072, +0.0007) |
| Premier League | double_x2 | 838 | **PASS** | 1.075 (0.86, 1.29) | +0.0210 (-0.0129, +0.0532) | -0.21 | 110 / -0.32 | -0.0002 (-0.0037, +0.0035) |
| Premier League | double_12 | 840 | **PASS** | 0.782 (0.013, 1.552) | -0.0204 (-0.0491, +0.0099) | -2.06 | 1 / - | -0.0013 (-0.0032, +0.0006) |
| La Liga | home_1up | 846 | **PASS** | 1.014 (0.79, 1.239) | +0.0085 (-0.0252, +0.0405) | -0.88 | 111 / 0.51 | -0.0012 (-0.0043, +0.0022) |
| La Liga | away_1up | 858 | **PASS** | 0.918 (0.696, 1.14) | -0.0144 (-0.0458, +0.0189) | -1.87 | 47 / - | +0.0010 (-0.0013, +0.0035) |
| La Liga | over_0.5 | 160 | INSUFFICIENT | | | | | |
| La Liga | over_1.5 | 836 | **PASS** | 1.546 (0.963, 2.13) | +0.0349 (+0.0073, +0.0640) | -1.8 | 23 / - | +0.0045 (+0.0007, +0.0079) |
| La Liga | over_2.5 | 859 | **PASS** | 0.903 (0.637, 1.168) | +0.0145 (-0.0170, +0.0451) | -0.72 | 67 / -0.45 | +0.0009 (-0.0023, +0.0039) |
| La Liga | under_2.5 | 859 | **PASS** | 0.903 (0.637, 1.168) | -0.0145 (-0.0437, +0.0161) | -1.12 | 74 / -0.31 | +0.0009 (-0.0022, +0.0040) |
| La Liga | under_3.5 | 858 | **PASS** | 0.965 (0.693, 1.238) | +0.0041 (-0.0246, +0.0284) | -0.98 | 0 / - | +0.0002 (-0.0021, +0.0030) |
| La Liga | home_win | 858 | **PASS** | 1.041 (0.854, 1.229) | +0.0113 (-0.0174, +0.0409) | -1.79 | 249 / 0.43 | -0.0037 (-0.0084, +0.0012) |
| La Liga | away_win | 859 | **PASS** | 0.93 (0.742, 1.119) | -0.0008 (-0.0298, +0.0272) | -1.92 | 78 / -1.21 | -0.0004 (-0.0054, +0.0050) |
| La Liga | double_1x | 776 | **PASS** | 0.924 (0.717, 1.131) | +0.0011 (-0.0303, +0.0331) | -1.21 | 225 / -1.9 | -0.0002 (-0.0054, +0.0053) |
| La Liga | double_x2 | 847 | **PASS** | 1.04 (0.85, 1.23) | -0.0116 (-0.0422, +0.0193) | -1.82 | 95 / -0.06 | -0.0039 (-0.0088, +0.0010) |
| La Liga | double_12 | 850 | **PASS** | 1.462 (0.935, 1.99) | +0.0095 (-0.0214, +0.0369) | -1.05 | 25 / - | -0.0021 (-0.0040, -0.0003) |
| Serie A | home_1up | 846 | **PASS** | 1.08 (0.87, 1.29) | -0.0324 (-0.0659, +0.0010) | -2.18 | 47 / - | -0.0006 (-0.0034, +0.0023) |
| Serie A | away_1up | 848 | **PASS** | 0.914 (0.719, 1.109) | +0.0095 (-0.0259, +0.0446) | -0.85 | 271 / -0.66 | -0.0005 (-0.0047, +0.0038) |
| Serie A | over_0.5 | 131 | INSUFFICIENT | | | | | |
| Serie A | over_1.5 | 847 | **PASS** | 1.3 (0.419, 2.18) | -0.0052 (-0.0352, +0.0235) | -2.07 | 86 / 0.93 | +0.0011 (-0.0020, +0.0041) |
| Serie A | over_2.5 | 848 | **PASS** | 0.966 (0.362, 1.571) | +0.0134 (-0.0181, +0.0463) | -1.44 | 0 / - | +0.0005 (-0.0015, +0.0027) |
| Serie A | under_2.5 | 848 | **PASS** | 0.966 (0.362, 1.571) | -0.0134 (-0.0480, +0.0221) | -2.74 | 24 / - | +0.0005 (-0.0015, +0.0026) |
| Serie A | under_3.5 | 848 | **PASS** | 1.405 (0.81, 2.0) | -0.0028 (-0.0324, +0.0247) | -2.41 | 62 / -1.03 | +0.0012 (-0.0014, +0.0040) |
| Serie A | home_win | 848 | **PASS** | 1.047 (0.865, 1.229) | +0.0012 (-0.0263, +0.0296) | -1.12 | 0 / - | -0.0029 (-0.0075, +0.0022) |
| Serie A | away_win | 848 | **PASS** | 1.035 (0.86, 1.211) | +0.0186 (-0.0087, +0.0477) | -0.32 | 204 / 1.31 | -0.0046 (-0.0097, +0.0007) |
| Serie A | double_1x | 770 | **PASS** | 0.976 (0.791, 1.161) | -0.0242 (-0.0587, +0.0079) | -2.58 | 187 / -1.48 | -0.0033 (-0.0087, +0.0028) |
| Serie A | double_x2 | 841 | **PASS** | 1.048 (0.863, 1.233) | -0.0012 (-0.0308, +0.0264) | -1.75 | 435 / -0.32 | -0.0025 (-0.0071, +0.0025) |
| Serie A | double_12 | 847 | **PASS** | 1.775 (0.876, 2.674) | +0.0187 (-0.0099, +0.0494) | -1.89 | 0 / - | +0.0024 (-0.0008, +0.0058) |
| Bundesliga | home_1up | 656 | **FAIL** | 0.994 (0.739, 1.249) | -0.0408 (-0.0787, -0.0026) ✗ | -2.04 | 125 / -1.85 | +0.0031 (-0.0011, +0.0078) |
| Bundesliga | away_1up | 671 | **PASS** | 0.911 (0.668, 1.154) | +0.0070 (-0.0319, +0.0440) | -2.05 | 1 / - | +0.0012 (-0.0020, +0.0044) |
| Bundesliga | over_0.5 | 13 | INSUFFICIENT | | | | | |
| Bundesliga | over_1.5 | 612 | **PASS** | 0.984 (0.28, 1.687) | -0.0196 (-0.0488, +0.0079) | -1.68 | 30 / - | +0.0028 (-0.0005, +0.0065) |
| Bundesliga | over_2.5 | 675 | **PASS** | 1.45 (0.926, 1.974) | +0.0120 (-0.0232, +0.0506) | -1.33 | 27 / - | +0.0004 (-0.0026, +0.0031) |
| Bundesliga | under_2.5 | 675 | **PASS** | 1.45 (0.926, 1.974) | -0.0120 (-0.0476, +0.0251) | -1.64 | 0 / - | +0.0004 (-0.0025, +0.0031) |
| Bundesliga | under_3.5 | 675 | **PASS** | 1.519 (1.034, 2.004) | -0.0262 (-0.0638, +0.0082) | -1.69 | 0 / - | -0.0027 (-0.0069, +0.0017) |
| Bundesliga | home_win | 673 | **PASS** | 1.25 (0.997, 1.504) | -0.0285 (-0.0647, +0.0080) | -2.22 | 0 / - | +0.0010 (-0.0004, +0.0025) |
| Bundesliga | away_win | 675 | **PASS** | 0.987 (0.759, 1.215) | +0.0321 (-0.0011, +0.0668) | -0.89 | 0 / - | +0.0035 (-0.0004, +0.0073) |
| Bundesliga | double_1x | 624 | **FAIL** | 0.982 (0.731, 1.234) | -0.0344 (-0.0745, -0.0001) ✗ | -2.02 | 60 / -1.7 | +0.0037 (+0.0003, +0.0071) |
| Bundesliga | double_x2 | 660 | **PASS** | 1.172 (0.927, 1.417) | +0.0253 (-0.0130, +0.0632) | -0.34 | 4 / - | -0.0002 (-0.0022, +0.0018) |
| Bundesliga | double_12 | 654 | **PASS** | 0.826 (-0.099, 1.752) | +0.0043 (-0.0267, +0.0365) | -0.95 | 0 / - | +0.0001 (-0.0028, +0.0030) |
| Ligue 1 | home_1up | 680 | **PASS** | 0.974 (0.743, 1.205) | -0.0233 (-0.0663, +0.0190) | -1.85 | 37 / - | -0.0026 (-0.0077, +0.0023) |
| Ligue 1 | away_1up | 685 | **FAIL** | 0.947 (0.681, 1.213) | -0.0552 (-0.0956, -0.0158) ✗ | -2.47 | 265 / -1.24 | +0.0050 (+0.0001, +0.0103) |
| Ligue 1 | over_0.5 | 12 | INSUFFICIENT | | | | | |
| Ligue 1 | over_1.5 | 674 | **PASS** | 0.789 (0.222, 1.355) | -0.0066 (-0.0430, +0.0267) | -0.94 | 0 / - | +0.0010 (-0.0007, +0.0028) |
| Ligue 1 | over_2.5 | 686 | **PASS** | 1.697 (1.04, 2.353) | -0.0047 (-0.0432, +0.0358) | -1.63 | 17 / - | +0.0024 (-0.0000, +0.0046) |
| Ligue 1 | under_2.5 | 686 | **PASS** | 1.697 (1.04, 2.353) | +0.0047 (-0.0315, +0.0441) | -1.86 | 10 / - | +0.0024 (+0.0001, +0.0045) |
| Ligue 1 | under_3.5 | 686 | **PASS** | 0.922 (0.448, 1.397) | -0.0154 (-0.0495, +0.0198) | -2.5 | 0 / - | +0.0009 (+0.0004, +0.0014) |
| Ligue 1 | home_win | 686 | **PASS** | 0.925 (0.723, 1.128) | +0.0347 (-0.0007, +0.0707) | -1.04 | 7 / - | +0.0022 (-0.0013, +0.0057) |
| Ligue 1 | away_win | 686 | **PASS** | 1.032 (0.801, 1.262) | -0.0191 (-0.0492, +0.0147) | -1.33 | 19 / - | +0.0008 (-0.0013, +0.0030) |
| Ligue 1 | double_1x | 646 | **PASS** | 1.076 (0.826, 1.326) | +0.0218 (-0.0142, +0.0549) | -1.56 | 0 / - | +0.0007 (-0.0015, +0.0031) |
| Ligue 1 | double_x2 | 676 | **PASS** | 0.913 (0.705, 1.122) | -0.0356 (-0.0727, +0.0010) | -1.94 | 44 / - | +0.0023 (-0.0009, +0.0056) |
| Ligue 1 | double_12 | 679 | **PASS** | 1.315 (0.408, 2.222) | +0.0160 (-0.0164, +0.0492) | -0.64 | 0 / - | +0.0009 (-0.0003, +0.0020) |

## Football-data-only leagues

Task-13 validation is retained unchanged; untested markets stay NOT_VALIDATED (blocked).

EREDIV: home_win=PASS, draw=NOT_VALIDATED, away_win=PASS, over_0.5=PASS, over_1.5=PASS, over_2.5=PASS, over_3.5=NOT_VALIDATED, under_2.5=NOT_VALIDATED, under_3.5=NOT_VALIDATED, btts_yes=NOT_VALIDATED, btts_no=NOT_VALIDATED, home_1up=NOT_VALIDATED, away_1up=NOT_VALIDATED, home_first=NOT_VALIDATED, away_first=NOT_VALIDATED, double_1x=PASS, double_x2=PASS, double_12=FAIL
JUPILER: home_win=PASS, draw=NOT_VALIDATED, away_win=PASS, over_0.5=PASS, over_1.5=PASS, over_2.5=PASS, over_3.5=NOT_VALIDATED, under_2.5=NOT_VALIDATED, under_3.5=NOT_VALIDATED, btts_yes=NOT_VALIDATED, btts_no=NOT_VALIDATED, home_1up=NOT_VALIDATED, away_1up=NOT_VALIDATED, home_first=NOT_VALIDATED, away_first=NOT_VALIDATED, double_1x=PASS, double_x2=PASS, double_12=PASS
PRIMEIRA: home_win=FAIL, draw=NOT_VALIDATED, away_win=PASS, over_0.5=PASS, over_1.5=PASS, over_2.5=PASS, over_3.5=NOT_VALIDATED, under_2.5=NOT_VALIDATED, under_3.5=NOT_VALIDATED, btts_yes=NOT_VALIDATED, btts_no=NOT_VALIDATED, home_1up=NOT_VALIDATED, away_1up=NOT_VALIDATED, home_first=NOT_VALIDATED, away_first=NOT_VALIDATED, double_1x=PASS, double_x2=PASS, double_12=PASS
SUPERLIG: home_win=PASS, draw=NOT_VALIDATED, away_win=PASS, over_0.5=PASS, over_1.5=PASS, over_2.5=PASS, over_3.5=NOT_VALIDATED, under_2.5=NOT_VALIDATED, under_3.5=NOT_VALIDATED, btts_yes=NOT_VALIDATED, btts_no=NOT_VALIDATED, home_1up=NOT_VALIDATED, away_1up=NOT_VALIDATED, home_first=NOT_VALIDATED, away_first=NOT_VALIDATED, double_1x=PASS, double_x2=PASS, double_12=PASS
