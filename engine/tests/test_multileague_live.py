import json

import numpy as np
import pandas as pd

from src import predict
from src.market_live import calibrate


def _csv():
    return pd.DataFrame({
        "Div": ["E0", "I1", "I1", "SP1"],
        "Date": ["25/10/2026"] * 4, "Time": ["15:00", "14:00", "17:00", "20:00"],
        "HomeTeam": ["Arsenal", "Inter", "Juventus", "Barcelona"],
        "AwayTeam": ["Everton", "Milan", "Roma", "Sevilla"],
        "AvgH": [1.5, 2.1, 1.9, np.nan], "AvgD": [4.5, 3.4, 3.4, np.nan], "AvgA": [7.0, 3.5, 4.2, np.nan],
        "Avg>2.5": [1.7, 1.9, 2.1, np.nan], "Avg<2.5": [2.2, 1.95, 1.8, np.nan],
    })


def test_load_fixtures_filters_one_league(monkeypatch):
    monkeypatch.setattr(predict, "_FIXTURES_CSV", _csv())
    empty = pd.DataFrame(columns=["season", "home_team", "away_team"])
    serie_a = predict.load_fixtures(pd.Timestamp("2026-10-24 12:00"), empty, "SERIEA")
    assert serie_a.home_team.tolist() == ["Inter", "Juventus"]
    assert set(serie_a.league) == {"SERIEA"}
    assert predict.load_fixtures(pd.Timestamp("2026-10-24 12:00"), empty, "EPL").home_team.tolist() == ["Arsenal"]


def test_market_mode_follows_the_bookmaker_and_skips_unpriced(monkeypatch):
    monkeypatch.setattr(predict, "_FIXTURES_CSV", _csv())
    monkeypatch.setattr(predict, "load_calibrators", lambda league: {})        # identity calibration
    monkeypatch.setattr(predict, "league_rho", lambda league: -0.05)
    empty = pd.DataFrame(columns=["season", "home_team", "away_team"])
    fixtures = predict.load_fixtures(pd.Timestamp("2026-10-24 12:00"), empty, "LALIGA")   # no odds
    assert predict.predict_market_fixtures(fixtures, "LALIGA").empty
    fixtures = predict.load_fixtures(pd.Timestamp("2026-10-24 12:00"), empty, "SERIEA")
    legs = predict.predict_market_fixtures(fixtures, "SERIEA").set_index(["home_team", "market"])
    inter = legs.loc["Inter"]
    implied = 1 / np.array([2.1, 3.4, 3.5])
    implied /= implied.sum()
    assert np.allclose(inter.loc[["home_win", "draw", "away_win"], "probability"], implied)
    assert inter.loc["home_1up", "probability"] >= inter.loc["home_win", "probability"]
    assert inter.loc["over_1.5", "probability"] >= inter.loc["over_2.5", "probability"]
    assert len(json.loads(inter.loc["home_win", "top_scorelines"])) == 3


def test_calibrate_applies_logistic_map():
    assert calibrate(0.6, None) == 0.6
    identity = {"coef": 1.0, "intercept": 0.0}
    assert abs(calibrate(0.6, identity) - 0.6) < 1e-12
    shrink = {"coef": 0.5, "intercept": 0.0}
    assert 0.5 < calibrate(0.8, shrink) < 0.8


def test_degenerate_calibrators_are_never_used():
    from src.market_live import usable
    good = {"coef": 1.1, "intercept": 0.1, "legs": 1500, "minority": 400}
    assert usable(good)
    assert not usable({**good, "legs": 36})            # Ligue 1 over 0.5: far too little evidence
    assert not usable({**good, "coef": -1.57})         # La Liga over 0.5: backwards slope
    assert not usable({**good, "minority": 3})         # almost no losses to learn from
    assert not usable(None)


def test_league_context_table_and_form():
    rows = [("2026/27", "2026-08-16", "A", "B", 2, 0), ("2026/27", "2026-08-23", "B", "C", 1, 1),
            ("2026/27", "2026-08-30", "C", "A", 0, 1), ("2025/26", "2026-05-01", "A", "C", 0, 5)]
    matches = pd.DataFrame(rows, columns=["season", "date", "home_team", "away_team", "home_goals", "away_goals"])
    matches["date"] = pd.to_datetime(matches.date)
    ctx = predict.league_context(matches, "2026/27")
    assert ctx["A"] == {"position": 1, "teams": 3, "played": 2, "won": 2, "drawn": 0, "lost": 0, "points": 6,
                        "gd": 3, "gf": 3, "ga": 0, "form": ["W", "W"]}
    assert ctx["B"]["form"] == ["L", "D"] and ctx["B"]["points"] == 1   # last season's match ignored
    # B and C both have 1 point; C's goal difference (-1) beats B's (-2).
    assert ctx["C"]["position"] == 2 and ctx["B"]["position"] == 3


def test_failed_gates_never_enter_slips(monkeypatch):
    legs = pd.DataFrame({
        "league": ["SERIEA", "SERIEA", "EPL"], "market": ["home_1up", "home_win", "home_1up"],
        "odds": [1.6, 1.7, 1.5], "probability": [0.7, 0.65, 0.72],
    })
    blocked = {("SERIEA", "home_1up")}
    seen = []
    monkeypatch.setattr(predict, "best_slip", lambda pool, tier: seen.append(set(zip(pool.league, pool.market))) or None)
    assert predict.build_slips(legs, blocked) == {}
    assert seen and all(("SERIEA", "home_1up") not in s for s in seen)
    assert ("SERIEA", "home_win") in seen[0] and ("EPL", "home_1up") in seen[0]


def test_live_slip_pool_excludes_unders_and_btts_but_keeps_other_markets(monkeypatch):
    markets = ["under_2.5", "under_3.5", "btts_yes", "over_1.5", "double_1x", "home_1up", "home_win"]
    legs = pd.DataFrame({
        "league": "SERIEA", "market": markets, "odds": 1.6, "probability": 0.7,
    })
    seen = []
    monkeypatch.setattr(predict, "best_slip", lambda pool, tier: seen.append(set(pool.market)) or None)
    assert predict.build_slips(legs, set()) == {}
    assert seen
    assert all(markets == {"over_1.5", "double_1x", "home_1up", "home_win"} for markets in seen)


def test_failed_gates_reads_only_fail_status(tmp_path, monkeypatch):
    path = tmp_path / "gates.json"
    path.write_text(json.dumps({"gates": {"EPL": {"over_2.5": "FAIL", "over_0.5": "INSUFFICIENT", "home_1up": "PASS"}}}))
    monkeypatch.setattr(predict, "GATES_PATH", path)
    assert predict.failed_gates() == {("EPL", "over_2.5")}
    monkeypatch.setattr(predict, "GATES_PATH", tmp_path / "missing.json")
    assert predict.failed_gates() == set()


def test_understat_results_settle_scores_and_1up(monkeypatch):
    from src import build_dataset
    results = [{"id": "1", "isResult": True, "datetime": "2026-10-24 16:30:00", "h": {"title": "Chelsea"},
                "a": {"title": "Tottenham"}, "goals": {"h": "0", "a": "2"}, "xG": {"h": "1.1", "a": "1.4"}},
               {"id": "2", "isResult": False, "datetime": "2026-10-31 16:30:00", "h": {"title": "Arsenal"},
                "a": {"title": "Everton"}, "goals": {"h": None, "a": None}, "xG": {"h": None, "a": None}}]
    shots = {"1": {"h": [], "a": [{"result": "Goal", "minute": "30"}, {"result": "Goal", "minute": "80"}]}}
    monkeypatch.setattr(build_dataset, "fetch_season", lambda year, refresh, league: (results, shots))
    monkeypatch.setattr(build_dataset, "current_season_start", lambda: 2026)
    rows = build_dataset.understat_results("EPL")
    assert len(rows) == 1                                  # unplayed match ignored
    row = rows.iloc[0]
    assert (row.home_goals, row.away_goals, row.first_scorer) == (0, 2, "away")
    assert row.away_led_at_any_point and not row.home_led_at_any_point


def test_paused_pairs_are_kept_out_of_slips(tmp_path, monkeypatch):
    monkeypatch.setattr(predict, "PAUSED_PATH", tmp_path / "paused.json")
    predict.save_paused({("SERIEA", "home_1up")})
    assert predict.load_paused() == {("SERIEA", "home_1up")}
    legs = pd.DataFrame({"league": ["SERIEA", "SERIEA"], "market": ["home_1up", "home_win"],
                         "odds": [1.6, 1.7], "probability": [0.7, 0.65]})
    seen = []
    monkeypatch.setattr(predict, "best_slip", lambda pool, tier: seen.append(set(zip(pool.league, pool.market))) or None)
    predict.build_slips(legs, predict.load_paused())
    assert seen and all(("SERIEA", "home_1up") not in s for s in seen)


def test_realised_slips_profit_at_published_odds():
    history = [{"tier": "safe", "status": "won", "total_odds": 2.5, "win_probability": 0.4},
               {"tier": "safe", "status": "lost", "total_odds": 2.6, "win_probability": 0.38},
               {"tier": "safe", "status": "pending", "total_odds": 2.7, "win_probability": 0.37}]
    safe = predict.realised_slips(history)["safe"]
    assert safe == {"settled": 2, "won": 1, "predicted": 0.78, "profit": 0.5, "roi": 0.25}


def test_head_to_head_from_this_fixtures_point_of_view():
    rows = [("2024/25", "2024-09-01", "Arsenal", "Chelsea", 3, 1), ("2024/25", "2025-02-01", "Chelsea", "Arsenal", 2, 2),
            ("2025/26", "2025-10-01", "Chelsea", "Arsenal", 1, 0), ("2025/26", "2025-11-01", "Arsenal", "Spurs", 4, 0)]
    history = pd.DataFrame(rows, columns=["season", "date", "home_team", "away_team", "home_goals", "away_goals"])
    history["date"] = pd.to_datetime(history.date)
    h2h = predict.head_to_head(history, "Arsenal", "Chelsea")
    assert [m["date"] for m in h2h["meetings"]] == ["2025-10-01", "2025-02-01", "2024-09-01"]     # newest first
    assert (h2h["home_wins"], h2h["draws"], h2h["away_wins"]) == (1, 1, 1)                        # Arsenal's view
    assert h2h["avg_goals"] == round((4 + 4 + 1) / 3, 2) and h2h["over_2_5"] == 2 and h2h["btts"] == 2
    assert predict.head_to_head(history, "Arsenal", "Everton") is None


def test_load_fixtures_when_every_match_has_kicked_off(monkeypatch):
    # 25 Oct 2026: after the last EPL kick-off the filter list was empty and pandas dropped all columns.
    monkeypatch.setattr(predict, "_FIXTURES_CSV", _csv())
    empty = pd.DataFrame(columns=["season", "home_team", "away_team"])
    fixtures = predict.load_fixtures(pd.Timestamp("2026-10-26 12:00"), empty, "EPL")
    assert fixtures.empty and {"date", "time", "home_team", "kickoff_utc"} <= set(fixtures.columns)


def test_best_pick_is_the_most_likely_eligible_market_paying_enough():
    legs = pd.DataFrame({"league": "SERIEA",
                         "market": ["over_0.5", "home_1up", "over_1.5", "home_win", "btts_yes", "under_2.5"],
                         "probability": [0.95, 0.74, 0.74, 0.60, 0.80, 0.99],
                         "odds": [1.04, 1.30, 1.25, 1.60, 1.30, 1.40],
                         "betpawa_odds": [1.04, 1.30, np.nan, 1.60, 1.30, 1.40]})
    pick = predict.best_pick(legs, set())
    # Over 0.5 pays under 1.20; BTTS is not a slip market; unders are owner-excluded; over wins the tie by priority.
    assert (pick["market"], pick["probability"], pick["odds"], pick["odds_source"]) == ("over_1.5", 0.74, 1.25, "estimated")
    assert predict.best_pick(legs, {("SERIEA", "over_1.5")})["market"] == "home_1up"     # blocked pairs skipped
    assert predict.best_pick(legs[legs.market == "over_0.5"], set()) is None


def test_league_tables_list_full_rows_in_position_order():
    rows = [("2026/27", "2026-08-16", "A", "B", 2, 0), ("2026/27", "2026-08-23", "B", "C", 1, 1)]
    matches = pd.DataFrame(rows, columns=["season", "date", "home_team", "away_team", "home_goals", "away_goals"])
    matches["date"] = pd.to_datetime(matches.date)
    ctx = predict.league_context(matches, "2026/27")
    table = predict.league_tables(ctx, {"A": "EPL", "B": "EPL", "C": "EPL"})["EPL"]
    assert [r["team"] for r in table] == ["A", "C", "B"]
    assert (table[0]["won"], table[0]["gf"], table[0]["ga"], table[0]["points"]) == (1, 2, 0, 3)


def _results(rows):
    frame = pd.DataFrame(rows, columns=["season", "date", "home_team", "away_team", "home_goals", "away_goals"])
    frame["date"] = pd.to_datetime(frame.date)
    return frame.assign(first_scorer="none", home_led_at_any_point=False, away_led_at_any_point=False)


def test_a_home_away_swap_in_the_fast_source_is_not_counted_twice():
    # Real case: football-data had Rennes v Paris SG on 23 Aug 2026 (correct, ESPN agrees); Understat swapped it.
    official = _results([("2026/27", "2026-08-23", "Rennes", "Paris SG", 2, 2)])
    fast = _results([("2026/27", "2026-08-23 18:45", "Paris SG", "Rennes", 2, 2),
                     ("2026/27", "2026-10-25 16:00", "Paris SG", "Lyon", 1, 0)])          # genuinely new
    merged = predict.merge_results(official, fast)
    assert list(zip(merged.home_team, merged.away_team)) == [("Rennes", "Paris SG"), ("Paris SG", "Lyon")]


def test_settlement_never_uses_a_result_from_another_date():
    find = predict.result_lookup(_results([("2026/27", "2026-08-23", "Paris SG", "Rennes", 2, 2)]))
    assert find("Paris SG", "Rennes", "2026-08-24") is not None
    assert find("Paris SG", "Rennes", "2027-02-14") is None       # the real reverse fixture months later


def test_betpawa_fallback_adds_only_matches_football_data_lacks():
    now = pd.Timestamp("2026-10-27 08:00")
    prices = pd.DataFrame([
        {"home_team": h, "away_team": a, "kickoff_utc": pd.Timestamp(k), "market": m, "betpawa_odds": o}
        for h, a, k in (("Roma", "Cagliari", "2026-10-27 19:45"), ("Inter", "Milan", "2026-10-27 19:45"),
                        ("Lazio", "Como", "2026-11-05 19:45"), ("Genoa", "Lecce", "2026-10-27 17:30"))
        for m, o in (("home_win", 1.34), ("draw", 5.95), ("away_win", 9.04), ("over_2.5", 1.7), ("under_2.5", 2.1))
        if not (h == "Genoa" and m == "draw")])                       # Genoa: incomplete prices
    have = pd.DataFrame({"home_team": ["Inter"], "away_team": ["Milan"], "date": [pd.Timestamp("2026-10-27")], "time": ["19:45"]})
    played = pd.DataFrame(columns=["season", "home_team", "away_team"])
    out = predict.add_betpawa_fixtures(have, prices, now, played, "SERIEA")
    added = out[out.odds_source == "betpawa"]
    assert added[["home_team", "away_team"]].values.tolist() == [["Roma", "Cagliari"]]  # not Inter (has data), Lazio (too far), Genoa
    row = added.iloc[0]
    assert (row.odds_home, row.odds_draw, row.odds_away, row.odds_over25, row.odds_under25) == (1.34, 5.95, 9.04, 1.7, 2.1)
    assert row.time == "19:45" and row.season == "2026/27"                                 # 19:45 UTC = 19:45 London (GMT)
    assert out[out.home_team == "Inter"].odds_source.iloc[0] == "average"
