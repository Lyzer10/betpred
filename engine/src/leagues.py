"""Supported research leagues and their isolated filesystem layout."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from .new_league_config import NEW_LEAGUES

ENGINE_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class League:
    code: str
    name: str
    country: str
    football_data_code: str
    understat_name: str | None
    betpawa_competition_id: int
    teams_per_season: int

    def teams(self, season_start: int) -> int:
        if self.code == "JUPILER":
            return 18 if season_start >= 2026 or 2020 <= season_start <= 2022 else 16
        if self.code == "SUPERLIG":
            return {2020: 21, 2021: 20, 2022: 19, 2023: 20, 2024: 19}.get(season_start, 18)
        if self.code == "LIGUE1" and season_start >= 2023:
            return 18
        return self.teams_per_season


LEAGUES = {
    "EPL": League("EPL", "Premier League", "England", "E0", "EPL", 11965, 20),
    "LALIGA": League("LALIGA", "La Liga", "Spain", "SP1", "La_liga", 12039, 20),
    "SERIEA": League("SERIEA", "Serie A", "Italy", "I1", "Serie_A", 12097, 20),
    "BUNDES": League("BUNDES", "Bundesliga", "Germany", "D1", "Bundesliga", 12110, 18),
    "LIGUE1": League("LIGUE1", "Ligue 1", "France", "F1", "Ligue_1", 12127, 20),
}
# Counts above and here come from distinct teams in the real season CSVs, not round assumptions.
LEAGUES.update({code: League(code, name, country, division, None, competition, 18)
                for code, (name, country, division, competition, _) in NEW_LEAGUES.items()})


def get_league(league: str | League = "EPL") -> League:
    if isinstance(league, League):
        return league
    try:
        return LEAGUES[str(league).upper()]
    except KeyError as exc:
        raise ValueError(f"Unknown league code: {league!r}. Choose from {', '.join(LEAGUES)}") from exc


@dataclass(frozen=True)
class LeaguePaths:
    league: League
    processed_dir: Path
    reports_dir: Path
    football_data_dir: Path
    understat_dir: Path

    @property
    def matches(self) -> Path: return self.processed_dir / "matches.parquet"
    @property
    def goals(self) -> Path: return self.processed_dir / "goals.parquet"
    @property
    def predictions_dc(self) -> Path: return self.processed_dir / "predictions_dc.parquet"
    @property
    def predictions_calibrated(self) -> Path: return self.processed_dir / "predictions_calibrated.parquet"
    @property
    def predictions_goal_timing(self) -> Path: return self.processed_dir / "predictions_goal_timing.parquet"
    @property
    def predictions_goal_timing_validation(self) -> Path: return self.processed_dir / "predictions_goal_timing_validation.parquet"
    @property
    def calibration_methods(self) -> Path: return self.processed_dir / "calibration_methods.json"
    @property
    def accumulator_legs(self) -> Path: return self.processed_dir / "accumulator_legs.parquet"
    @property
    def accumulator_slips(self) -> Path: return self.processed_dir / "accumulator_slips.parquet"
    @property
    def baseline_report(self) -> Path: return self.reports_dir / "baseline_report.md"
    @property
    def stage2_report(self) -> Path: return self.reports_dir / "stage2_report.md"
    @property
    def stage2_tuning(self) -> Path: return self.reports_dir / "stage2_tuning.csv"
    @property
    def stage3_report(self) -> Path: return self.reports_dir / "stage3_report.md"
    @property
    def stage4_report(self) -> Path: return self.reports_dir / "stage4_report.md"

    def football_csv(self, season_code: str) -> Path:
        return self.football_data_dir / f"{self.league.football_data_code}_{season_code}.csv"

    def understat_file(self, year: int, kind: str) -> Path:
        return self.understat_dir / f"{self.league.code.lower()}_{year}_{kind}.json"


def paths(league: str | League = "EPL") -> LeaguePaths:
    selected = get_league(league)
    processed = ENGINE_DIR / "data" / "processed"
    reports = ENGINE_DIR / "reports"
    if selected.code != "EPL":
        processed = processed / selected.code
        reports = reports / selected.code
    return LeaguePaths(selected, processed, reports, ENGINE_DIR / "data" / "raw" / "football_data",
                       ENGINE_DIR / "data" / "raw" / "understat")

