import pytest
import pandas as pd

from src.leagues import ENGINE_DIR, LEAGUES, paths
from src.build_dataset import build
from src.fetch_results import current_season_start


def test_registry_fields_and_team_counts():
    assert set(LEAGUES) == {"EPL", "LALIGA", "SERIEA", "BUNDES", "LIGUE1"}
    for league in LEAGUES.values():
        assert all((league.code, league.name, league.country, league.football_data_code,
                    league.understat_name, league.betpawa_competition_id, league.teams_per_season))
    assert LEAGUES["LIGUE1"].teams(2022) == 20
    assert LEAGUES["LIGUE1"].teams(2023) == 18


def test_epl_paths_are_exactly_legacy_paths():
    value = paths("EPL")
    assert value.matches == ENGINE_DIR / "data" / "processed" / "matches.parquet"
    assert value.goals == ENGINE_DIR / "data" / "processed" / "goals.parquet"
    assert value.football_csv("2425") == ENGINE_DIR / "data" / "raw" / "football_data" / "E0_2425.csv"
    assert value.understat_file(2024, "results") == ENGINE_DIR / "data" / "raw" / "understat" / "epl_2024_results.json"
    assert value.stage2_report == ENGINE_DIR / "reports" / "stage2_report.md"


def test_unknown_league_is_strict():
    with pytest.raises(ValueError, match="Unknown league"):
        paths("UNKNOWN")


def test_epl_parameterized_rebuild_is_identical():
    league_paths = paths("EPL")
    current = current_season_start()
    if not league_paths.understat_file(current, "shots").exists():
        pytest.skip("Current EPL raw cache is not available")
    expected_matches = pd.read_parquet(league_paths.matches)
    expected_goals = pd.read_parquet(league_paths.goals)
    actual_matches, actual_goals = build(league="EPL", write=False)
    assert actual_matches.equals(expected_matches)
    assert actual_goals.equals(expected_goals)
