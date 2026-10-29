"""Source-verified configuration for PROJECT.md task 13's market-only leagues."""
NEW_LEAGUES = {
    "EREDIV": ("Eredivisie", "Netherlands", "N1", 12125, "ned.1"),
    "JUPILER": ("Belgian Pro League", "Belgium", "B1", 12128, "bel.1"),
    "PRIMEIRA": ("Primeira Liga", "Portugal", "P1", 12124, "por.1"),
    "SUPERLIG": ("Super Lig", "Turkey", "T1", 12182, "tur.1"),
}
VALIDATED_MARKETS = ("home_win", "away_win", "double_1x", "double_x2", "double_12",
                     "over_0.5", "over_1.5", "over_2.5")
FAILED_MARKETS = {"EREDIV": {"double_12"}, "JUPILER": set(), "PRIMEIRA": {"home_win"}, "SUPERLIG": set()}
FIXED_RHO = -0.054288
