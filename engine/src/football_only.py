"""Football-data history and completed ESPN scores, without any Understat dependency."""
from io import BytesIO
import time

import pandas as pd
import requests

from .fetch_results import current_season_start, parse_match_dates, season_code, season_label
from .leagues import ENGINE_DIR, get_league, paths
from .new_league_config import NEW_LEAGUES
from .team_names import canonical_team


def season_file(year, league, refresh=False, session=None):
    selected = get_league(league)
    target = paths(league).football_csv(season_code(year))
    study = ENGINE_DIR / "data" / "raw" / "new_leagues_study" / f"{selected.football_data_code}_{season_code(year)}.csv"
    if not target.exists() and study.exists() and not refresh:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(study.read_bytes())
    if refresh or not target.exists():
        response = (session or requests).get(
            f"https://www.football-data.co.uk/mmz4281/{season_code(year)}/{selected.football_data_code}.csv", timeout=30)
        response.raise_for_status()
        raw = pd.read_csv(BytesIO(response.content))
        if not {"Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"} <= set(raw):
            raise ValueError(f"{selected.code}: invalid results CSV")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(response.content)
        time.sleep(1)
    return pd.read_csv(target)


def load_history(league, start=2014, end=None, refresh_current=False):
    current = current_season_start()
    rows = []
    with requests.Session() as session:
        for year in range(start, (current if end is None else end) + 1):
            raw = season_file(year, league, refresh_current and year == current, session)
            dates = parse_match_dates(raw.Date)
            columns = ["AvgH", "AvgD", "AvgA", "Avg>2.5", "Avg<2.5"]
            if not set(columns) <= set(raw):
                columns = ["BbAvH", "BbAvD", "BbAvA", "BbAv>2.5", "BbAv<2.5"]
            for index, match in raw.dropna(subset=["HomeTeam", "AwayTeam", "FTHG", "FTAG"]).iterrows():
                try:
                    home, away = (canonical_team(match[c], league) for c in ("HomeTeam", "AwayTeam"))
                except ValueError as error:
                    print(f"{league}: results match skipped ({error})")
                    continue
                row = {"match_id": f"{league}:{year}:{index}", "league": league, "date": dates.loc[index],
                       "season": season_label(year), "home_team": home, "away_team": away,
                       "home_goals": int(match.FTHG), "away_goals": int(match.FTAG),
                       "first_scorer": None, "home_led_at_any_point": None, "away_led_at_any_point": None}
                for field, source in zip(("home", "draw", "away", "over25", "under25"), columns):
                    row[f"avg_odds_{field}"] = match.get(source, float("nan"))
                rows.append(row)
    return pd.DataFrame(rows, columns=["match_id", "league", "date", "season", "home_team", "away_team",
                                      "home_goals", "away_goals", "first_scorer", "home_led_at_any_point",
                                      "away_led_at_any_point", "avg_odds_home", "avg_odds_draw", "avg_odds_away",
                                      "avg_odds_over25", "avg_odds_under25"])


def parse_completed(response, league):
    rows = []
    for event in response.get("events", []):
        state = event.get("status", {}).get("type", {})
        if not state.get("completed") or state.get("state") != "post":
            continue
        try:
            competitors = {c["homeAway"]: c for c in event["competitions"][0]["competitors"]}
            home, away = competitors["home"], competitors["away"]
            date = pd.Timestamp(event["date"]).tz_convert("UTC").tz_localize(None)
            rows.append({"match_id": f"espn:{event['id']}", "league": league, "date": date,
                         "season": season_label(current_season_start(date.date())),
                         "home_team": canonical_team(home["team"]["displayName"], league),
                         "away_team": canonical_team(away["team"]["displayName"], league),
                         "home_goals": int(home["score"]), "away_goals": int(away["score"]),
                         "first_scorer": None, "home_led_at_any_point": None, "away_led_at_any_point": None})
        except (ValueError, KeyError, TypeError) as error:
            print(f"{league}: completed ESPN event {event.get('id')} skipped ({error})")
    return pd.DataFrame(rows, columns=["match_id", "league", "date", "season", "home_team", "away_team",
                                      "home_goals", "away_goals", "first_scorer", "home_led_at_any_point",
                                      "away_led_at_any_point"])


def espn_results(league, now, session=None):
    slug = NEW_LEAGUES[league][4]
    session = session or requests.Session()
    frames = []
    for offset in range(4):
        day = (now - pd.Timedelta(days=offset)).strftime("%Y%m%d")
        response = session.get(f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard",
                               params={"dates": day}, timeout=20)
        response.raise_for_status()
        frames.append(parse_completed(response.json(), league))
        time.sleep(1)
    return pd.concat(frames, ignore_index=True).drop_duplicates("match_id")


def score_actuals(frame):
    """Only outcomes determined by final scores. Goal timing remains unknown."""
    result = frame.copy()
    home, away = result.home_goals, result.away_goals
    total = home + away
    for name, values in {"home": home > away, "draw": home == away, "away": home < away,
                         "dc_1x": home >= away, "dc_x2": home <= away, "dc_12": home != away,
                         "btts": (home > 0) & (away > 0), "home_clean_sheet": away == 0,
                         "away_clean_sheet": home == 0, "no_goal": total == 0}.items():
        result[f"actual_{name}"] = values.astype(int)
    for line, suffix in ((.5, "05"), (1.5, "15"), (2.5, "25"), (3.5, "35")):
        result[f"actual_over{suffix}"] = (total > line).astype(int)
    for name in ("home_1up", "away_1up", "home_first", "away_first"):
        result[f"actual_{name}"] = None
    return result
