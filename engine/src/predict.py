"""Stage 5: live predictions for upcoming Premier League fixtures.

Runs the same pipeline as the backtests, fitted on everything known today:
  refresh data -> Dixon-Coles blend -> Platt calibration -> goal-timing markets
  -> logit blend with the bookmaker market -> accumulator slips per tier.
Writes web/public/data/predictions.json for the app and keeps a settled history
of every published slip in data/live/slip_history.json.

Usage:  python -m src.predict            (refresh current season, then predict)
        python -m src.predict --no-refresh
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from io import StringIO

import numpy as np
import pandas as pd
import requests

from .accumulators import (
    LEG_MARKETS, LEGS_PATH, RETAIL_MARGIN, SLIP_MARKETS, SLIPS_PATH, TIERS, best_slip, betting_round, blend,
    bookmaker_fair_probabilities, fit_model_weight,
)
from .backtest import _promoted_initialization
from .betpawa import fetch_premier_league_odds
from .build_dataset import build
from .calibration import (
    DC_PATH, ENGINE_DIR, MARKETS, MATCHES_PATH, add_actuals, enforce_probability_constraints, fit_calibrator,
)
from .dixon_coles import fit_dixon_coles, score_matrix, training_window
from .fetch_results import current_season_start, parse_match_dates, season_label
from .goal_timing import (
    GOALS_PATH, TIMING_MARKETS, TIMING_PATH, estimate_time_profile, fit_state_multipliers, simulate_match,
)
from .team_names import canonical_team

FIXTURES_URL = "https://football-data.co.uk/fixtures.csv"
TUNING_PATH = ENGINE_DIR / "reports" / "stage2_tuning.csv"
LIVE_DIR = ENGINE_DIR / "data" / "live"
HISTORY_PATH = LIVE_DIR / "slip_history.json"
WEB_DATA_PATH = ENGINE_DIR.parent / "web" / "public" / "data" / "predictions.json"
ARCHIVE_DIR = WEB_DATA_PATH.parent / "archive"
SIMULATIONS = 20_000
# A bet is "value" when probability x odds - 1 >= VALUE_EDGE. Keep in sync with web/src/lib.ts.
VALUE_EDGE = 0.03
# Long shots carry the most model error and variance; value singles need at least this probability.
VALUE_MIN_PROBABILITY = 0.25
# If Betpawa pays this much more than the (older) market-average price implies, the
# "edge" is more likely stale information (team news, line move) than a gift: warn and halve the stake.
PRICE_MOVE_WARNING = 0.08
# Bets are grouped by the user's calendar day (Tanzania, EAT), not by UK date.
LOCAL_TZ = "Africa/Dar_es_Salaam"

MARKET_LABELS = {
    "home_win": "Home win", "draw": "Draw", "away_win": "Away win",
    "over_0.5": "Over 0.5 goals", "over_1.5": "Over 1.5 goals", "over_2.5": "Over 2.5 goals",
    "over_3.5": "Over 3.5 goals", "under_2.5": "Under 2.5 goals", "under_3.5": "Under 3.5 goals",
    "btts_yes": "Both teams score", "btts_no": "Both teams score: No",
    "home_1up": "Home 1Up", "away_1up": "Away 1Up",
    "home_first": "Home scores first", "away_first": "Away scores first",
    "double_1x": "Home or draw", "double_x2": "Away or draw", "double_12": "Home or away",
}


def load_fixtures(today: pd.Timestamp, played: pd.DataFrame) -> pd.DataFrame:
    """Upcoming Premier League fixtures with average bookmaker odds."""
    response = requests.get(FIXTURES_URL, timeout=30)
    response.raise_for_status()
    raw = pd.read_csv(StringIO(response.content.decode("utf-8-sig")))
    raw = raw[raw.Div == "E0"].copy()
    fixtures = pd.DataFrame({
        "date": parse_match_dates(raw.Date),
        "time": raw.Time.astype(str),
        "home_team": raw.HomeTeam.map(canonical_team),
        "away_team": raw.AwayTeam.map(canonical_team),
        # Average market odds; fixtures.csv carries no Pinnacle columns.
        "odds_home": raw.get("AvgH", raw.get("B365H")), "odds_draw": raw.get("AvgD", raw.get("B365D")),
        "odds_away": raw.get("AvgA", raw.get("B365A")),
        "odds_over25": raw.get("Avg>2.5", raw.get("B365>2.5")),
        "odds_under25": raw.get("Avg<2.5", raw.get("B365<2.5")),
    })
    # fixtures.csv times are UK local time.
    local = pd.to_datetime(fixtures.date.dt.strftime("%Y-%m-%d") + " " + fixtures.time, errors="coerce")
    fixtures["kickoff_utc"] = (local.dt.tz_localize("Europe/London", ambiguous="NaT", nonexistent="shift_forward")
                               .dt.tz_convert("UTC").dt.tz_localize(None))
    fixtures["kickoff_utc"] = fixtures.kickoff_utc.fillna(fixtures.date)
    fixtures = fixtures[fixtures.kickoff_utc > today]
    season = season_label(current_season_start(today.date()))
    done = set(zip(played.loc[played.season == season, "home_team"], played.loc[played.season == season, "away_team"]))
    fixtures = fixtures[[(h, a) not in done for h, a in zip(fixtures.home_team, fixtures.away_team)]]
    fixtures["season"] = season
    return fixtures.sort_values(["date", "time"]).reset_index(drop=True)


def chosen_dc_settings() -> tuple[float, float]:
    tuning = pd.read_csv(TUNING_PATH)
    best = tuning[tuning.variant == "blend"].sort_values("validation_log_loss").iloc[0]
    return float(best.xi), float(best.blend_weight)


def fit_live_model(matches: pd.DataFrame, fixtures: pd.DataFrame, today: pd.Timestamp):
    xi, blend_weight = chosen_dc_settings()
    training = training_window(matches, today)
    teams = sorted(set(fixtures.home_team) | set(fixtures.away_team))
    base = fit_dixon_coles(training, today, xi=xi, variant="blend", blend_weight=blend_weight,
                           prediction_teams=teams)
    promoted = _promoted_initialization(matches, fixtures, training, base)
    model = fit_dixon_coles(training, today, xi=xi, variant="blend", blend_weight=blend_weight,
                            warm_start=base, prediction_teams=teams, promoted_values=promoted)
    return model, {"xi": xi, "blend_weight": blend_weight, "training_matches": len(training),
                   "training_last_date": training.date.max().date().isoformat()}


def fit_calibrators(matches: pd.DataFrame) -> tuple[dict, dict]:
    """Platt calibrators on every settled out-of-sample prediction we have."""
    dc = pd.read_parquet(DC_PATH)
    dc = add_actuals(dc[dc.variant == "blend"].merge(matches, on=["match_id", "date"]))
    main = {market: fit_calibrator(dc[raw], dc[actual], "platt") for market, (raw, actual) in MARKETS.items()}
    timing = pd.read_parquet(TIMING_PATH)
    path = {market: fit_calibrator(timing[raw], timing[actual], "platt")
            for market, (raw, actual) in TIMING_MARKETS.items()}
    return main, path


def predict_fixtures(fixtures, model, matches, goals, calibrators, model_weight) -> pd.DataFrame:
    main_cal, timing_cal = calibrators
    dc_history = pd.read_parquet(DC_PATH)
    dc_history = dc_history[dc_history.variant == "blend"]
    _, profile = estimate_time_profile(goals)
    history_matches = matches[matches.match_id.isin(dc_history.match_id)]
    multipliers = fit_state_multipliers(history_matches, goals[goals.match_id.isin(history_matches.match_id)],
                                        dc_history, profile)
    rows = []
    for index, fixture in fixtures.iterrows():
        matrix, raw = model.predict(fixture.home_team, fixture.away_team)
        cal = pd.DataFrame([{f"cal_{market}": main_cal[market].predict([raw[column]])[0]
                             for market, (column, _) in MARKETS.items()}])
        enforce_probability_constraints(cal, "cal")
        cal = cal.iloc[0]
        timing = simulate_match(raw["lambda_home"], raw["lambda_away"], profile, multipliers,
                                simulations=SIMULATIONS, seed=index + 1, matrix=matrix)
        model_probs = {
            "home_win": cal.cal_home, "draw": cal.cal_draw, "away_win": cal.cal_away,
            "over_0.5": cal.cal_over05, "over_1.5": cal.cal_over15, "over_2.5": cal.cal_over25,
            "over_3.5": cal.cal_over35, "under_2.5": 1 - cal.cal_over25, "under_3.5": 1 - cal.cal_over35,
            "btts_yes": cal.cal_btts, "btts_no": 1 - cal.cal_btts,
            "double_1x": cal.cal_home + cal.cal_draw, "double_x2": cal.cal_draw + cal.cal_away,
            "double_12": cal.cal_home + cal.cal_away,
            **{market: float(timing_cal[market].predict([timing[f"sim_{market}"]])[0])
               for market in ("home_1up", "away_1up", "home_first", "away_first")},
        }
        has_odds = fixture[["odds_home", "odds_draw", "odds_away", "odds_over25", "odds_under25"]].notna().all()
        market_probs = (bookmaker_fair_probabilities(fixture.odds_home, fixture.odds_draw, fixture.odds_away,
                                                     fixture.odds_over25, fixture.odds_under25, model.rho)
                        if has_odds else {})
        for market in LEG_MARKETS:
            model_p = float(model_probs[market])
            market_p = market_probs.get(market)
            final = float(blend(model_p, market_p, model_weight)) if market_p is not None else model_p
            rows.append({
                "fixture": index, "date": fixture.date, "time": fixture.time, "season": fixture.season,
                "kickoff_utc": fixture.kickoff_utc,
                "home_team": fixture.home_team, "away_team": fixture.away_team, "market": market,
                "model_probability": model_p, "bookmaker_probability": market_p, "probability": final,
                "odds": 1 / (market_p * (1 + RETAIL_MARGIN)) if market_p is not None else np.nan,
                "lambda_home": raw["lambda_home"], "lambda_away": raw["lambda_away"],
                "top_scorelines": raw["top_scorelines"],
            })
    legs = pd.DataFrame(rows)
    legs["round"] = betting_round(legs.date)
    legs["match_id"] = legs.fixture
    return legs


def attach_betpawa(legs: pd.DataFrame, betpawa: pd.DataFrame) -> pd.DataFrame:
    """Add real Betpawa odds per leg; slips then use real prices where available."""
    legs = legs.copy()
    if betpawa.empty:
        legs["betpawa_odds"] = np.nan
    else:
        merged = legs.merge(betpawa[["home_team", "away_team", "market", "kickoff_utc", "betpawa_odds"]]
                            .rename(columns={"kickoff_utc": "betpawa_kickoff"}),
                            on=["home_team", "away_team", "market"], how="left")
        # Guard against a same-teams fixture on another date (e.g. a cup tie).
        far = (merged.betpawa_kickoff - merged.kickoff_utc).abs() > pd.to_timedelta(1, unit="D")
        merged.loc[far, "betpawa_odds"] = np.nan
        legs = merged.drop(columns="betpawa_kickoff")
    legs["estimated_odds"] = legs.odds
    legs["odds"] = legs.betpawa_odds.fillna(legs.estimated_odds)
    legs["edge"] = legs.probability * legs.betpawa_odds - 1
    legs["price_warning"] = legs.bookmaker_probability * legs.betpawa_odds - 1 > PRICE_MOVE_WARNING
    return legs


def kelly_fraction(probability: float, odds: float) -> float:
    """Full-Kelly stake fraction; the app stakes a quarter of it, capped."""
    return max((probability * odds - 1) / (odds - 1), 0.0) if odds > 1 else 0.0


def value_picks(legs: pd.DataFrame) -> list[dict]:
    """Singles where Betpawa pays more than our fair odds, best edge first."""
    picks = legs[(legs.edge >= VALUE_EDGE) & (legs.probability >= VALUE_MIN_PROBABILITY)]
    picks = picks.sort_values("edge", ascending=False)
    return [_leg_json(row) | {"edge": round(float(row.edge), 4),
                              "kelly": round(kelly_fraction(row.probability, row.betpawa_odds), 4)}
            for row in picks.itertuples()]


def local_day(kickoff_utc: pd.Series) -> pd.Series:
    """Calendar day of each kickoff in the user's time zone, as YYYY-MM-DD."""
    return kickoff_utc.dt.tz_localize("UTC").dt.tz_convert(LOCAL_TZ).dt.strftime("%Y-%m-%d")


def at_least(probabilities, k: int) -> float:
    """P(at least k of the independent legs win): Poisson-binomial tail."""
    distribution = np.array([1.0])
    for p in probabilities:
        distribution = np.convolve(distribution, [1 - p, p])
    return float(distribution[k:].sum())


def flexi_options(probabilities) -> list[dict]:
    """SportyBet Flexi: the ticket wins if at least k of n picks win (fixed, reduced payout)."""
    n = len(probabilities)
    return [{"min_correct": k, "probability": round(at_least(probabilities, k), 4)}
            for k in range(n - 1, max(n - 3, 1), -1)] if n >= 3 else []


def build_slips(legs: pd.DataFrame) -> dict:
    """Tier slips from one day's matches, using only the user's slip markets with a price."""
    pool = legs[legs.market.isin(SLIP_MARKETS) & legs.odds.notna() & (legs.odds >= 1.05)]
    slips = {}
    for tier in TIERS:
        picks = best_slip(pool, tier) if not pool.empty else None
        if picks is None:
            continue
        chosen = pool.loc[picks]
        total, win = float(chosen.odds.prod()), float(chosen.probability.prod())
        slips[tier.name] = {
            "total_odds": round(total, 2),
            "win_probability": round(win, 4),
            "odds_source": "betpawa" if chosen.betpawa_odds.notna().all() else "estimated",
            "expected_value": round(win * total - 1, 4),
            "kelly": round(kelly_fraction(win, total), 4),
            "price_warning": bool(chosen.price_warning.any()),
            "flexi": flexi_options(chosen.probability.tolist()),
            "legs": [_leg_json(row) for row in chosen.itertuples()],
        }
    return slips


def _leg_json(row) -> dict:
    return {"date": row.date.date().isoformat(), "time": row.time, "kickoff_utc": row.kickoff_utc.isoformat() + "Z",
            "home": row.home_team, "away": row.away_team,
            "market": row.market, "label": MARKET_LABELS[row.market],
            "probability": round(float(row.probability), 4),
            "estimated_odds": round(float(row.estimated_odds), 2) if pd.notna(row.estimated_odds) else None,
            "betpawa_odds": None if pd.isna(row.betpawa_odds) else round(float(row.betpawa_odds), 2),
            "fair_odds": round(1 / float(row.probability), 2),
            "price_warning": bool(getattr(row, "price_warning", False))}


def outcome(match: pd.Series, market: str) -> bool:
    _, actual_column = LEG_MARKETS[market]
    if actual_column.startswith(("actual_under", "actual_btts_no")):
        base = actual_column.replace("under", "over").replace("btts_no", "btts")
        return not bool(match[base])
    return bool(match[actual_column])


def update_history(round_id: str | None, slips: dict, matches: pd.DataFrame, now: pd.Timestamp) -> list[dict]:
    """Store this round's slips (until its first kickoff) and settle finished legs."""
    LIVE_DIR.mkdir(parents=True, exist_ok=True)
    history = json.loads(HISTORY_PATH.read_text(encoding="utf-8")) if HISTORY_PATH.exists() else []
    if round_id and slips:
        # Each tier's slip is frozen once its first leg kicks off, so the history
        # only ever records slips that were published before any of their matches.
        for tier, slip in slips.items():
            first_kickoff = min(pd.Timestamp(leg["kickoff_utc"]).tz_localize(None) for leg in slip["legs"])
            stored = [entry for entry in history if entry["round"] == round_id and entry["tier"] == tier]
            if now < first_kickoff and (not stored or _not_started(stored[0], now)):
                history = [entry for entry in history if not (entry["round"] == round_id and entry["tier"] == tier)]
                history.append({"round": round_id, "tier": tier, "generated_at": now.isoformat() + "Z", **slip})
    settled = add_actuals(matches)
    lookup = {(row.home_team, row.away_team, row.season): row for _, row in settled.iterrows()}
    for entry in history:
        for leg in entry["legs"]:
            season = season_label(current_season_start(pd.Timestamp(leg["date"]).date()))
            match = lookup.get((leg["home"], leg["away"], season))
            leg["won"] = None if match is None else outcome(match, leg["market"])
        results = [leg["won"] for leg in entry["legs"]]
        entry["status"] = ("lost" if False in results else "pending" if None in results else "won")
    HISTORY_PATH.write_text(json.dumps(history, indent=2), encoding="utf-8")
    return history


def _not_started(entry: dict, now: pd.Timestamp) -> bool:
    return all(pd.Timestamp(leg["kickoff_utc"]).tz_localize(None) > now for leg in entry["legs"])


def recent_results(matches: pd.DataFrame, now: pd.Timestamp, days: int = 120) -> list[dict]:
    """Settled outcomes of every leg market for recent matches (the app settles saved picks)."""
    recent = add_actuals(matches[matches.date >= now - pd.to_timedelta(days, unit="D")])
    return [{"date": row.date.date().isoformat(), "home": row.home_team, "away": row.away_team,
             "score": [int(row.home_goals), int(row.away_goals)],
             "outcomes": {market: outcome(row, market) for market in LEG_MARKETS}}
            for _, row in recent.sort_values("date", ascending=False).iterrows()]


def displayed_slips(round_id: str | None, slips: dict, history: list[dict], now: pd.Timestamp) -> dict:
    """Slips to show: once a tier's slip has a match under way, show that frozen slip.

    Later runs re-optimise over the matches not yet started, but those slips are
    never recorded, so showing them would let the app and the record disagree.
    """
    shown = {tier: {**slip, "locked": False} for tier, slip in slips.items()}
    for entry in history:
        if entry["round"] == round_id and not _not_started(entry, now):
            shown[entry["tier"]] = {key: entry[key] for key in ("total_odds", "win_probability", "legs", "status")}
            shown[entry["tier"]]["locked"] = True
    return shown


def _fixture_key(fixture: dict) -> tuple:
    return fixture["date"], fixture["home"], fixture["away"]


def archive_snapshot(fixtures: list[dict], slips: dict, day: str, now: pd.Timestamp) -> None:
    """Save a match day's predictions and bets; matches already kicked off keep their earlier prediction."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    path = ARCHIVE_DIR / f"{day}.json"
    previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"fixtures": []}
    current = {_fixture_key(f): f for f in previous["fixtures"]}
    for fixture in fixtures:
        current[_fixture_key(fixture)] = {
            key: fixture[key] for key in ("date", "time", "kickoff_utc", "home", "away", "expected_goals", "top_scorelines")
        } | {"markets": [{k: m.get(k) for k in ("market", "label", "probability", "market_probability", "betpawa_odds")}
                         for m in fixture["markets"]]}
    snapshot = {"date": day, "generated_at": now.isoformat() + "Z",
                "fixtures": sorted(current.values(), key=lambda f: f["kickoff_utc"]),
                # Locked slips are already frozen; unlocked ones are the latest pre-kickoff version.
                "slips": {tier: {k: v for k, v in slip.items() if k != "status"} for tier, slip in slips.items()}}
    path.write_text(json.dumps(snapshot, indent=1), encoding="utf-8")


def settle_archive(matches: pd.DataFrame) -> list[dict]:
    """Attach final scores and per-market outcomes to archived predictions; return the index."""
    if not ARCHIVE_DIR.exists():
        return []
    settled = add_actuals(matches)
    lookup = {(row.home_team, row.away_team, row.season): row for _, row in settled.iterrows()}
    index = []
    for path in sorted(ARCHIVE_DIR.glob("20*.json"), reverse=True):
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for fixture in snapshot["fixtures"]:
            if "result" in fixture:
                continue
            season = season_label(current_season_start(pd.Timestamp(fixture["date"]).date()))
            match = lookup.get((fixture["home"], fixture["away"], season))
            if match is not None:
                fixture["result"] = {"score": [int(match.home_goals), int(match.away_goals)],
                                     "outcomes": {m: outcome(match, m) for m in LEG_MARKETS}}
                changed = True
        for slip in snapshot.get("slips", {}).values():
            for leg in slip["legs"]:
                if leg.get("won") is None:
                    season = season_label(current_season_start(pd.Timestamp(leg["date"]).date()))
                    match = lookup.get((leg["home"], leg["away"], season))
                    if match is not None:
                        leg["won"] = outcome(match, leg["market"])
                        changed = True
            results = [leg.get("won") for leg in slip["legs"]]
            slip["status"] = "lost" if False in results else "pending" if None in results else "won"
        if changed:
            path.write_text(json.dumps(snapshot, indent=1), encoding="utf-8")
        done = sum("result" in f for f in snapshot["fixtures"])
        index.append({"date": snapshot["date"], "fixtures": len(snapshot["fixtures"]), "settled": done})
    (ARCHIVE_DIR / "index.json").write_text(json.dumps(index, indent=1), encoding="utf-8")
    return index


def live_record() -> dict:
    """Accuracy of published predictions: last pre-kickoff prediction per settled match."""
    latest = {}
    for path in sorted(ARCHIVE_DIR.glob("20*.json")) if ARCHIVE_DIR.exists() else []:
        for fixture in json.loads(path.read_text(encoding="utf-8"))["fixtures"]:
            latest[_fixture_key(fixture)] = fixture
    settled = [f for f in latest.values() if "result" in f]
    if not settled:
        return {"matches": 0}
    keys = ("home_win", "draw", "away_win")
    ours, market, actual, confident, value_returns = [], [], [], [], []
    for fixture in settled:
        markets = {m["market"]: m for m in fixture["markets"]}
        for m in fixture["markets"]:
            price = m.get("betpawa_odds")
            if price and m["probability"] >= VALUE_MIN_PROBABILITY and m["probability"] * price - 1 >= VALUE_EDGE:
                value_returns.append(price - 1 if fixture["result"]["outcomes"][m["market"]] else -1.0)
        ours.append([markets[k]["probability"] for k in keys])
        market.append([markets[k]["market_probability"] or np.nan for k in keys])
        actual.append([fixture["result"]["outcomes"][k] for k in keys])
        confident += [fixture["result"]["outcomes"][m["market"]] for m in fixture["markets"] if m["probability"] >= 0.7]
    ours, market, actual = np.array(ours), np.array(market, float), np.array(actual, float)
    has_market = ~np.isnan(market).any(axis=1)

    def log_loss(p, rows):
        return float(-np.mean(np.log(np.clip((p[rows] * actual[rows]).sum(axis=1), 1e-9, 1))))

    return {
        "matches": len(settled),
        "result_hit_rate": round(float(np.mean(ours.argmax(axis=1) == actual.argmax(axis=1))), 4),
        "log_loss": round(log_loss(ours, has_market), 4) if has_market.any() else None,
        "market_log_loss": round(log_loss(market, has_market), 4) if has_market.any() else None,
        "confident_picks": len(confident),
        "confident_hit_rate": round(float(np.mean(confident)), 4) if confident else None,
        "value_bets": len(value_returns),
        "value_bets_won": int(sum(r > 0 for r in value_returns)),
        "value_roi": round(float(np.mean(value_returns)), 4) if value_returns else None,
    }


def backtest_summary() -> dict:
    slips = pd.read_parquet(SLIPS_PATH)
    accuracy = slips[slips["mode"] == "accuracy"]
    return {tier: {"slips": int(len(group)), "win_rate": round(float(group.won.mean()), 4),
                   "predicted_win_rate": round(float(group.predicted_win.mean()), 4),
                   "average_odds": round(float(group.total_odds.mean()), 2)}
            for tier, group in accuracy.groupby("tier")}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-refresh", action="store_true", help="use cached data, skip downloads")
    args = parser.parse_args()
    now = pd.Timestamp(datetime.now(timezone.utc)).tz_localize(None)

    if args.no_refresh:
        matches, goals = pd.read_parquet(MATCHES_PATH), pd.read_parquet(GOALS_PATH)
    else:
        matches, goals = build(refresh_current=True)
    fixtures = load_fixtures(now, matches)
    if fixtures.empty:
        raise SystemExit("No upcoming Premier League fixtures in fixtures.csv")

    model, model_info = fit_live_model(matches, fixtures, now)
    model_weight = fit_model_weight(pd.read_parquet(LEGS_PATH))
    legs = predict_fixtures(fixtures, model, matches, goals, fit_calibrators(matches), model_weight)
    try:
        betpawa = fetch_premier_league_odds()
        print(f"Betpawa: {betpawa.home_team.nunique()} home teams, {len(betpawa)} prices")
    except Exception as error:  # Betpawa down or changed: predictions still publish.
        print(f"Betpawa odds unavailable ({error}); using estimated odds")
        betpawa = pd.DataFrame(columns=["home_team", "away_team", "market", "kickoff_utc", "betpawa_odds"])
    legs = attach_betpawa(legs, betpawa)
    legs["day"] = local_day(legs.kickoff_utc)
    days = []
    for day, day_legs in legs.groupby("day", sort=True):
        slips = build_slips(day_legs)
        history = update_history(day, slips, matches, now)
        days.append({"date": day, "fixtures": sorted(int(f) for f in day_legs.fixture.unique()),
                     "value_picks": value_picks(day_legs),
                     "slips": displayed_slips(day, slips, history, now)})
    if not days:
        history = update_history(None, {}, matches, now)

    output = {
        "generated_at": now.isoformat() + "Z",
        "model": {**model_info, "market_blend_model_weight": model_weight, "retail_margin": RETAIL_MARGIN},
        "backtest": backtest_summary(),
        "time_zone": LOCAL_TZ,
        "fixtures": [
            {
                "id": int(fixture_id), "date": group.date.iloc[0].date().isoformat(), "time": group.time.iloc[0],
                "kickoff_utc": group.kickoff_utc.iloc[0].isoformat() + "Z",
                "home": group.home_team.iloc[0], "away": group.away_team.iloc[0],
                "day": group["day"].iloc[0],
                "expected_goals": [round(float(group.lambda_home.iloc[0]), 2), round(float(group.lambda_away.iloc[0]), 2)],
                "top_scorelines": json.loads(group.top_scorelines.iloc[0]),
                "has_market_odds": bool(group.bookmaker_probability.notna().all()),
                "markets": [
                    {"market": row.market, "label": MARKET_LABELS[row.market],
                     "probability": round(float(row.probability), 4),
                     "model_probability": round(float(row.model_probability), 4),
                     "market_probability": None if pd.isna(row.bookmaker_probability) else round(float(row.bookmaker_probability), 4),
                     "fair_odds": round(1 / float(row.probability), 2),
                     "betpawa_odds": None if pd.isna(row.betpawa_odds) else round(float(row.betpawa_odds), 2)}
                    for row in group.itertuples()
                ],
            }
            for fixture_id, group in legs.groupby("fixture", sort=True)
        ],
        "days": days,
        "value_rules": {"min_edge": VALUE_EDGE, "min_probability": VALUE_MIN_PROBABILITY},
        "history": history,
        "results": recent_results(matches, now),
    }
    for day in days:
        archive_snapshot([f for f in output["fixtures"] if f["day"] == day["date"]], day["slips"], day["date"], now)
    output["archive"] = settle_archive(matches)
    output["live_record"] = live_record()
    WEB_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    WEB_DATA_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"{len(output['fixtures'])} fixtures over {len(days)} days: "
          + "; ".join(f"{d['date']} {len(d['value_picks'])} value picks, slips {'/'.join(d['slips']) or '-'}" for d in days))
    print(f"Wrote {WEB_DATA_PATH}")


if __name__ == "__main__":
    main()
