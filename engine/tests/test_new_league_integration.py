import json
from pathlib import Path

import pandas as pd
import pytest

from src import predict
from src.accumulators import LEG_MARKETS
from src.football_only import load_history, parse_completed, score_actuals
from src.leagues import ENGINE_DIR, get_league, paths
from src.market_gates import new_league_gates
from src.market_live import league_rho, load_calibrators
from src.new_league_config import NEW_LEAGUES, VALIDATED_MARKETS, FAILED_MARKETS, FIXED_RHO
from src.team_names import canonical_team

FIXTURES = Path(__file__).parent / "fixtures" / "new_leagues"


@pytest.mark.parametrize("code", NEW_LEAGUES)
def test_current_names_counts_and_badges_are_verified(code):
    teams = json.loads((FIXTURES / f"{code}_teams.json").read_text(encoding="utf-8"))
    canonical = {canonical_team(t["team"]["displayName"], code) for t in teams["sports"][0]["leagues"][0]["teams"]}
    events = json.loads((FIXTURES / f"{code}_betpawa.json").read_text(encoding="utf-8"))["responses"][0]["responses"]
    prices = {canonical_team(p["name"], code) for e in events for p in e["participants"]}
    history = load_history(code, start=2026, end=2026)
    official = set(history.home_team) | set(history.away_team)
    assert canonical == official == prices
    assert len(canonical) == get_league(code).teams(2026)
    urls = json.loads((ENGINE_DIR.parent / "web" / "src" / "badgeUrls.json").read_text())
    assert all(urls[name].startswith("https://a.espncdn.com/") for name in canonical)
    assert get_league(code).understat_name is None


@pytest.mark.parametrize("code", NEW_LEAGUES)
def test_setup_excludes_current_season_and_uses_fixed_rho(code):
    metadata = json.loads((paths(code).processed_dir / "setup.json").read_text())
    assert all(int(season[:4]) < 2026 for season in metadata["training_seasons"])
    assert pd.Timestamp(metadata["training_max_date"]) < pd.Timestamp("2026-07-01")
    assert league_rho(code) == FIXED_RHO
    assert set(load_calibrators(code)) <= set(VALIDATED_MARKETS)


@pytest.mark.parametrize("code", NEW_LEAGUES)
def test_gate_blocking_and_real_fixture_prediction(code, monkeypatch):
    statuses = new_league_gates()[code]
    assert all(statuses[m] == "NOT_VALIDATED" for m in set(LEG_MARKETS) - set(VALIDATED_MARKETS))
    assert {m for m, s in statuses.items() if s == "FAIL"} == FAILED_MARKETS[code]
    history = load_history(code, start=2026, end=2026)
    # Use one real historical price row, without changing its teams, dates or odds.
    match = history.dropna(subset=[f"avg_odds_{m}" for m in ("home", "draw", "away", "over25", "under25")]).iloc[[0]].copy()
    match["kickoff_utc"] = match.date
    match["time"] = match.date.dt.strftime("%H:%M")
    for name in ("home", "draw", "away", "over25", "under25"):
        match[f"odds_{name}"] = match[f"avg_odds_{name}"]
    legs = predict.predict_market_fixtures(match, code).assign(league=code, betpawa_odds=float("nan"))
    blocked = {(code, market) for market, status in statuses.items() if status != "PASS"}
    seen = []
    monkeypatch.setattr(predict, "best_slip", lambda pool, tier: seen.append(set(pool.market)) or None)
    assert predict.build_slips(legs, blocked) == {}
    assert seen and all(markets <= set(VALIDATED_MARKETS) - FAILED_MARKETS[code] for markets in seen)
    pick = predict.best_pick(legs, blocked)
    assert pick is None or pick["market"] in set(VALIDATED_MARKETS) - FAILED_MARKETS[code]


@pytest.mark.parametrize("code", NEW_LEAGUES)
def test_real_completed_scores_settle_temp_archive(code, tmp_path, monkeypatch):
    payload = json.loads((FIXTURES / f"{code}_completed.json").read_text(encoding="utf-8"))
    completed = parse_completed(payload, code)
    assert not completed.empty
    find = predict.result_lookup(completed)
    row = completed.iloc[0]
    assert find(row.home_team, row.away_team, row.date) is not None
    assert find(row.away_team, row.home_team, row.date) is None
    assert find(row.home_team, row.away_team, row.date + pd.Timedelta(days=4)) is None
    snapshot = {"date": row.date.date().isoformat(), "fixtures": [{
        "date": row.date.date().isoformat(), "home": row.home_team, "away": row.away_team}], "slips": {}}
    target = tmp_path / f"{snapshot['date']}.json"
    target.write_text(json.dumps(snapshot))
    monkeypatch.setattr(predict, "ARCHIVE_DIR", tmp_path)
    predict.settle_archive(completed)
    settled = json.loads(target.read_text())["fixtures"][0]["result"]
    assert settled["score"] == [int(row.home_goals), int(row.away_goals)]
    assert settled["outcomes"]["home_win"] == (row.home_goals > row.away_goals)
    assert settled["outcomes"]["home_1up"] is None
    assert settled["outcomes"]["home_first"] is None
    assert predict.merge_results(completed, completed).equals(completed.reset_index(drop=True))


def test_monthly_new_gates_are_retained_without_leg_tables():
    gates = new_league_gates()
    assert set(gates) == set(NEW_LEAGUES)
    for code in NEW_LEAGUES:
        assert not paths(code).accumulator_legs.exists()
        assert set(gates[code]) == set(LEG_MARKETS)
