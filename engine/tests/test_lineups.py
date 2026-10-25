from src.lineups import parse_summary


def _roster(side, team, starters):
    players = [{"athlete": {"displayName": f"{team} {i}"}, "jersey": str(i), "starter": i <= starters,
                "position": {"abbreviation": "G" if i == 1 else "M"}, "formationPlace": i} for i in range(1, 19)]
    return {"homeAway": side, "team": {"displayName": team}, "formation": "4-3-3", "roster": players}


def test_lineups_only_when_both_elevens_are_announced():
    summary = {"rosters": [_roster("home", "Internazionale", 11), _roster("away", "Milan", 11)]}
    lineup = parse_summary(summary, "SERIEA")
    assert (lineup["home"], lineup["away"]) == ("Inter", "Milan")           # ESPN names mapped to ours
    assert len(lineup["home_lineup"]["starters"]) == 11 and len(lineup["home_lineup"]["subs"]) == 7
    assert lineup["home_lineup"]["starters"][0] == {
        "name": "Internazionale 1", "number": "1", "position": "G", "formation_place": 1,
    }
    assert parse_summary({"rosters": [_roster("home", "Inter", 11), _roster("away", "Milan", 0)]}, "SERIEA") is None
    assert parse_summary({"rosters": []}, "SERIEA") is None


def test_event_teams_maps_espn_names_to_ours():
    from src.lineups import event_teams
    event = {"competitions": [{"competitors": [
        {"homeAway": "away", "team": {"displayName": "Tottenham Hotspur"}},
        {"homeAway": "home", "team": {"displayName": "Chelsea"}}]}]}
    assert event_teams(event, "EPL") == ("Chelsea", "Tottenham")


def test_last_xi_picks_the_right_team_and_needs_eleven():
    from src.schedule import last_xi
    summary = {"rosters": [_roster("home", "Real Betis", 11), _roster("away", "Barcelona", 11)]}
    xi = last_xi(summary, "LALIGA", "Barcelona")
    assert xi["formation"] == "4-3-3" and xi["starters"][0]["name"] == "Barcelona 1" and len(xi["starters"]) == 11
    assert last_xi({"rosters": [_roster("away", "Barcelona", 10)]}, "LALIGA", "Barcelona") is None
    assert last_xi(summary, "LALIGA", "Sevilla") is None
