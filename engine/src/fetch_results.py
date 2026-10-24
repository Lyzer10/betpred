"""Download and normalize football-data.co.uk Premier League CSV files."""
from __future__ import annotations

from datetime import date
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "football_data"
START_SEASON = 2014

SOURCE_COLUMNS = {
    "Date": "date", "HomeTeam": "home_team", "AwayTeam": "away_team",
    "FTHG": "fthg", "FTAG": "ftag", "HTHG": "hthg", "HTAG": "htag",
    "FTR": "ftr", "HS": "hs", "AS": "as", "HST": "hst", "AST": "ast",
    "B365H": "b365h", "B365D": "b365d", "B365A": "b365a",
    "PSH": "psh", "PSD": "psd", "PSA": "psa", "AvgH": "avgh",
    "AvgD": "avgd", "AvgA": "avga", "B365>2.5": "b365_over25",
    "B365<2.5": "b365_under25", "Avg>2.5": "avg_over25", "Avg<2.5": "avg_under25",
    # Older seasons (pre-2019/20) publish Betbrain averages instead of Avg.
    "P>2.5": "p_over25", "P<2.5": "p_under25",
    "BbAv>2.5": "bbav_over25", "BbAv<2.5": "bbav_under25",
    "BbAvH": "bbavh", "BbAvD": "bbavd", "BbAvA": "bbava",
    # Closing odds: evaluation only, never model inputs.
    "PSCH": "psch", "PSCD": "pscd", "PSCA": "psca",
    "AvgCH": "avgch", "AvgCD": "avgcd", "AvgCA": "avgca",
    "PC>2.5": "pc_over25", "PC<2.5": "pc_under25",
    "AvgC>2.5": "avgc_over25", "AvgC<2.5": "avgc_under25",
}


def current_season_start(today: date | None = None) -> int:
    today = today or date.today()
    return today.year if today.month >= 7 else today.year - 1


def season_code(year: int) -> str:
    return f"{year % 100:02d}{(year + 1) % 100:02d}"


def season_label(year: int) -> str:
    return f"{year}/{str(year + 1)[-2:]}"


def parse_match_dates(values: pd.Series) -> pd.Series:
    """Parse the two date formats used by football-data files."""
    text = values.astype("string").str.strip()
    parsed = pd.to_datetime(text, format="%d/%m/%Y", errors="coerce")
    short = parsed.isna()
    parsed.loc[short] = pd.to_datetime(text.loc[short], format="%d/%m/%y", errors="coerce")
    bad_mask = parsed.isna() & text.notna() & text.ne("")
    if bad_mask.any():
        bad = text[bad_mask].unique().tolist()
        raise ValueError(f"Unparseable match dates: {bad[:5]}")
    return parsed


def download_season(year: int, session: requests.Session | None = None, refresh: bool = False) -> Path:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    target = RAW_DIR / f"E0_{season_code(year)}.csv"
    if target.exists() and not refresh:
        return target
    url = f"https://www.football-data.co.uk/mmz4281/{season_code(year)}/E0.csv"
    response = (session or requests).get(url, timeout=30)
    response.raise_for_status()
    # Validate before caching an HTML error page.
    pd.read_csv(BytesIO(response.content), nrows=2)
    target.write_bytes(response.content)
    return target


def load_season(year: int, session: requests.Session | None = None, refresh: bool = False) -> pd.DataFrame:
    raw = pd.read_csv(download_season(year, session, refresh))
    # Only columns this season actually has; fetch_all adds the missing ones afterwards,
    # so concatenation never sees all-empty columns.
    selected = pd.DataFrame({destination: raw[source] for source, destination in SOURCE_COLUMNS.items() if source in raw},
                            index=raw.index)
    selected = selected[selected["home_team"].notna() & selected["away_team"].notna()].copy()
    selected = selected[selected["fthg"].notna() & selected["ftag"].notna()].copy()
    selected["date"] = parse_match_dates(selected["date"])
    selected.insert(1, "season", season_label(year))
    return selected


def fetch_all(start: int = START_SEASON, end: int | None = None, refresh_current: bool = False) -> pd.DataFrame:
    """Load all seasons; refresh_current re-downloads the in-progress season."""
    current = current_season_start()
    end = current if end is None else end
    with requests.Session() as session:
        frame = pd.concat([load_season(year, session, refresh_current and year == current)
                           for year in range(start, end + 1)], ignore_index=True)
    return frame.reindex(columns=["date", "season", *[c for c in SOURCE_COLUMNS.values() if c != "date"]])


def main() -> None:
    frame = fetch_all()
    print(f"Downloaded or loaded {len(frame):,} football-data matches.")


if __name__ == "__main__":
    main()
