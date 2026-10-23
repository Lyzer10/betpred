"""Strict team name normalization shared by every data source."""

CANONICAL_TEAM_NAMES = {
    # Canonical football-data names and common Understat variants.
    "Arsenal": "Arsenal", "Aston Villa": "Aston Villa", "Bournemouth": "Bournemouth",
    "Brighton": "Brighton", "Brighton & Hove Albion": "Brighton",
    "Burnley": "Burnley", "Cardiff": "Cardiff", "Cardiff City": "Cardiff",
    "Chelsea": "Chelsea", "Crystal Palace": "Crystal Palace", "Everton": "Everton",
    "Fulham": "Fulham", "Huddersfield": "Huddersfield", "Huddersfield Town": "Huddersfield",
    "Hull": "Hull", "Hull City": "Hull", "Ipswich": "Ipswich", "Ipswich Town": "Ipswich",
    "Leeds": "Leeds", "Leeds United": "Leeds", "Leicester": "Leicester",
    "Leicester City": "Leicester", "Liverpool": "Liverpool", "Luton": "Luton",
    "Luton Town": "Luton", "Man City": "Manchester City", "Manchester City": "Manchester City",
    "Man United": "Manchester United", "Manchester United": "Manchester United",
    "Middlesbrough": "Middlesbrough", "Newcastle": "Newcastle",
    "Newcastle United": "Newcastle", "Norwich": "Norwich", "Norwich City": "Norwich",
    "Nott'm Forest": "Nottingham Forest", "Nottingham Forest": "Nottingham Forest",
    "QPR": "Queens Park Rangers", "Queens Park Rangers": "Queens Park Rangers",
    "Sheffield United": "Sheffield United", "Sheffield Utd": "Sheffield United",
    "Southampton": "Southampton", "Stoke": "Stoke", "Stoke City": "Stoke",
    "Coventry": "Coventry", "Coventry City": "Coventry",
    "Sunderland": "Sunderland", "Swansea": "Swansea", "Swansea City": "Swansea",
    "Tottenham": "Tottenham", "Tottenham Hotspur": "Tottenham", "Watford": "Watford",
    "West Brom": "West Brom", "West Bromwich Albion": "West Brom",
    "West Ham": "West Ham", "West Ham United": "West Ham", "Wolves": "Wolves",
    "Wolverhampton Wanderers": "Wolves", "Brentford": "Brentford",
}


def canonical_team(name: str) -> str:
    """Return a canonical team name, raising for unexpected source values."""
    cleaned = str(name).strip()
    try:
        return CANONICAL_TEAM_NAMES[cleaned]
    except KeyError as exc:
        raise ValueError(f"Unmapped team name: {cleaned!r}") from exc
