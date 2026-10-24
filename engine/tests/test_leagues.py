import pytest
import pandas as pd

from src.leagues import ENGINE_DIR, LEAGUES, paths
from src.build_dataset import build
from src.fetch_results import current_season_start
from src.team_names import canonical_team


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


@pytest.mark.parametrize("league,source,canonical", [
    ("EPL", "Manchester United", "Manchester United"),
    ("LALIGA", "Athletic Club", "Ath Bilbao"),
    ("SERIEA", "Inter Milano", "Inter"),
    ("BUNDES", "Borussia M.Gladbach", "M'gladbach"),
    ("LIGUE1", "Paris Saint-Germain", "Paris SG"),
])
def test_team_mapping_is_strict_per_league(league, source, canonical):
    assert canonical_team(source, league) == canonical
    with pytest.raises(ValueError, match="Unmapped team"):
        canonical_team(f"Unknown {league}", league)


@pytest.mark.parametrize("league", LEAGUES)
def test_saved_walk_forward_has_no_leakage(league):
    prediction_path = paths(league).predictions_dc
    if not prediction_path.exists():
        pytest.skip(f"No saved backtest for {league}")
    predictions = pd.read_parquet(prediction_path)
    assert (predictions.training_max_date < predictions.prediction_date).all()


def test_epl_parameterized_rebuild_is_identical():
    league_paths = paths("EPL")
    current = current_season_start()
    if not league_paths.understat_file(current, "shots").exists():
        pytest.skip("Current EPL raw cache is not available")
    # Compare completed seasons only: the daily run refreshes the in-progress season's raw
    # files (new goals every matchday) without re-committing the parquet files.
    season = f"{current}/{str(current + 1)[-2:]}"

    def completed(matches: pd.DataFrame, goals: pd.DataFrame):
        past = matches[matches.season != season].reset_index(drop=True)
        return past, goals[goals.match_id.isin(past.match_id)].reset_index(drop=True)

    expected_matches, expected_goals = completed(pd.read_parquet(league_paths.matches), pd.read_parquet(league_paths.goals))
    actual_matches, actual_goals = completed(*build(league="EPL", write=False))
    assert actual_matches.equals(expected_matches)
    assert actual_goals.equals(expected_goals)
