"""Extra match factors on top of the Dixon-Coles goal model, tested walk-forward.

For every match, using only information from before kickoff:
  table    points-per-game difference (shrunk early season) and late-season
           pressure flags: relegation fight, title race, nothing to play for
  derby    a fixed list of English derbies
  home     team-specific home / away over- or under-performance against the model
           (residual goals in recent matches, shrunk toward zero)
  rest     days since each team's previous league match
  absences regular starters missing from the starting XI (Understat rosters):
           their share of the team's recent xG + xA, and missing regular defenders.
           Historical lineups include rotation, so this is an upper bound on what
           live injury news alone can add.

Each group adjusts the model's expected goals through a Poisson regression with
the model's lambda as offset, fitted only on seasons before the one predicted.
A group is worth using only if it lowers log loss on seasons it never saw.
Usage: python -m src.factors   (writes reports/factors_report.md)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm

from .calibration import DC_PATH, ENGINE_DIR, MATCHES_PATH
from .dixon_coles import market_probabilities, score_matrix

HISTORY_PATH = ENGINE_DIR / "data" / "processed" / "predictions_dc_history.parquet"
REPORT_PATH = ENGINE_DIR / "reports" / "factors_report.md"

DERBIES = {frozenset(pair) for pair in [
    ("Arsenal", "Tottenham"), ("Liverpool", "Everton"), ("Manchester City", "Manchester United"),
    ("Newcastle", "Sunderland"), ("Brighton", "Crystal Palace"), ("Liverpool", "Manchester United"),
    ("Arsenal", "Chelsea"), ("Chelsea", "Tottenham"), ("West Ham", "Tottenham"), ("West Ham", "Chelsea"),
    ("Aston Villa", "Birmingham"), ("Wolves", "West Brom"), ("Aston Villa", "West Brom"),
    ("Nottingham Forest", "Leicester"), ("Leeds", "Manchester United"), ("Fulham", "Chelsea"),
    ("Crystal Palace", "West Ham"), ("Southampton", "Bournemouth"), ("Burnley", "Blackburn"),
    ("Ipswich", "Norwich"), ("Sheffield United", "Sheffield Wednesday"), ("Coventry", "Aston Villa"),
]}

GROUPS = {
    "table": ["ppg_diff", "relegation", "title", "dead_rubber"],
    "derby": ["derby"],
    "home": ["att_resid", "def_resid"],
    "rest": ["rest_diff", "short_rest"],
    "absences": ["att_missing", "def_missing"],
}
RAW_UNDERSTAT = ENGINE_DIR / "data" / "raw" / "understat"
DEFENSIVE = {"GK", "DC", "DL", "DR"}
RECENT_MATCHES = 6


def load_rosters(years: range) -> dict[str, dict]:
    import json
    rosters = {}
    for year in years:
        path = RAW_UNDERSTAT / f"epl_{year}_rosters.json"
        if path.exists():
            rosters.update(json.loads(path.read_text(encoding="utf-8")))
    return rosters


def _absence_features(matches: pd.DataFrame, rosters: dict[str, dict]) -> pd.DataFrame:
    """Per match and side: attacking share and defenders missing among recent regular starters.

    A regular starter started at least half of the team's last RECENT_MATCHES matches.
    Contributions (xG + xA) come only from those earlier matches: no leakage.
    """
    team_history: dict[str, list[dict]] = {}
    rows = []
    for match in matches.sort_values("date").itertuples():
        roster = rosters.get(str(match.match_id))
        for side, key, team in (("home", "h", match.home_team), ("away", "a", match.away_team)):
            past = team_history.get(team, [])[-RECENT_MATCHES:]
            if roster is None or len(past) < 3:
                rows.append({"match_id": match.match_id, "side": side, "att_missing": np.nan, "def_missing": np.nan})
            else:
                starts: dict[str, int] = {}
                contribution: dict[str, float] = {}
                position: dict[str, str] = {}
                for game in past:
                    for pid, player in game.items():
                        contribution[pid] = contribution.get(pid, 0.0) + player["xg_xa"]
                        if player["started"]:
                            starts[pid] = starts.get(pid, 0) + 1
                            position[pid] = player["position"]
                total = sum(contribution.values()) or 1.0
                regulars = {pid for pid, n in starts.items() if n >= len(past) / 2}
                # Roster entries are keyed by a roster-row id; players are identified by player_id.
                started_now = {pl["player_id"] for pl in roster[key].values() if pl["position"] != "Sub"}
                missing = regulars - started_now
                rows.append({"match_id": match.match_id, "side": side,
                             "att_missing": sum(contribution.get(pid, 0.0) for pid in missing) / total,
                             "def_missing": float(min(sum(position[pid] in DEFENSIVE for pid in missing), 3))})
            if roster is not None:
                team_history.setdefault(team, []).append({
                    pl["player_id"]: {"started": pl["position"] != "Sub", "position": pl["position"],
                                      "xg_xa": float(pl["xG"]) + float(pl["xA"])}
                    for pl in roster[key].values()})
    return pd.DataFrame(rows)


def _table_features(matches: pd.DataFrame) -> pd.DataFrame:
    """Season-to-date table before each match, from that team's perspective."""
    rows = []
    for season, games in matches.sort_values("date").groupby("season", sort=False):
        table: dict[str, dict] = {}
        for day, today in games.groupby(games.date.dt.normalize(), sort=True):
            standings = sorted(table.items(), key=lambda kv: (-kv[1]["pts"], -kv[1]["gd"], -kv[1]["gf"]))
            position = {team: i + 1 for i, (team, _) in enumerate(standings)}
            leader = standings[0][1]["pts"] if standings else 0
            safety = standings[16][1]["pts"] if len(standings) >= 17 else 0   # 17th place: last safe spot
            for match in today.itertuples():
                for side, team in (("home", match.home_team), ("away", match.away_team)):
                    record = table.get(team, {"pts": 0, "gp": 0, "gd": 0, "gf": 0})
                    gp, pts = record["gp"], record["pts"]
                    late = gp >= 24
                    rows.append({
                        "match_id": match.match_id, "side": side,
                        "ppg": (pts / gp if gp else 1.37) * gp / (gp + 6) + 1.37 * 6 / (gp + 6),
                        "relegation": float(late and position.get(team, 20) >= 14 and pts - safety <= 4),
                        "title": float(late and leader - pts <= 4),
                        "dead_rubber": float(gp >= 30 and 8 <= position.get(team, 10) <= 14
                                             and leader - pts > 12 and pts - safety > 8),
                    })
            for match in today.itertuples():
                for team, scored, conceded in ((match.home_team, match.home_goals, match.away_goals),
                                               (match.away_team, match.away_goals, match.home_goals)):
                    record = table.setdefault(team, {"pts": 0, "gp": 0, "gd": 0, "gf": 0})
                    record["gp"] += 1
                    record["gf"] += scored
                    record["gd"] += scored - conceded
                    record["pts"] += 3 if scored > conceded else 1 if scored == conceded else 0
    return pd.DataFrame(rows)


def _rest_features(matches: pd.DataFrame) -> pd.DataFrame:
    long = pd.concat([matches[["match_id", "date", "home_team"]].rename(columns={"home_team": "team"}).assign(side="home"),
                      matches[["match_id", "date", "away_team"]].rename(columns={"away_team": "team"}).assign(side="away")])
    long = long.sort_values("date")
    long["rest"] = long.groupby("team").date.diff().dt.days.clip(2, 14).fillna(14)
    return long[["match_id", "side", "rest"]]


def _residual_features(matches: pd.DataFrame, predictions: pd.DataFrame, window: int = 38, shrink: float = 20.0) -> pd.DataFrame:
    """Team residuals vs the model in its recent home (or away) matches, before each match."""
    data = matches.merge(predictions[["match_id", "lambda_home", "lambda_away"]], on="match_id").sort_values("date")
    rows = []
    history: dict[tuple[str, str], list[tuple[float, float]]] = {}
    for day, today in data.groupby(data.date.dt.normalize(), sort=True):
        for match in today.itertuples():
            for side, team in (("home", match.home_team), ("away", match.away_team)):
                past = history.get((team, side), [])[-window:]
                n = len(past)
                weight = n / (n + shrink)
                att = np.mean([p[0] for p in past]) * weight if n else 0.0
                dfn = np.mean([p[1] for p in past]) * weight if n else 0.0
                rows.append({"match_id": match.match_id, "side": side, "att_resid": att, "def_resid": dfn})
        for match in today.itertuples():
            # Residual in log terms: log((goals + 0.5) / (lambda + 0.5)) is stable for small counts.
            home_att = np.log((match.home_goals + 0.5) / (match.lambda_home + 0.5))
            away_att = np.log((match.away_goals + 0.5) / (match.lambda_away + 0.5))
            history.setdefault((match.home_team, "home"), []).append((home_att, away_att))
            history.setdefault((match.away_team, "away"), []).append((away_att, home_att))
    return pd.DataFrame(rows)


def build_features(matches: pd.DataFrame, predictions: pd.DataFrame, rosters: dict | None = None) -> pd.DataFrame:
    """One row per predicted match: lambdas, outcome, and features for the home and away goal models."""
    table = _table_features(matches).pivot(index="match_id", columns="side")
    table.columns = [f"{name}_{side}" for name, side in table.columns]
    rest = _rest_features(matches).pivot(index="match_id", columns="side", values="rest")
    rest.columns = [f"rest_{c}" for c in rest.columns]
    resid = _residual_features(matches, predictions).pivot(index="match_id", columns="side")
    resid.columns = [f"{name}_{side}" for name, side in resid.columns]
    frame = (predictions[["match_id", "lambda_home", "lambda_away", "rho"]]
             .merge(matches[["match_id", "date", "season", "home_team", "away_team", "home_goals", "away_goals"]], on="match_id")
             .merge(table, on="match_id").merge(rest, on="match_id").merge(resid, on="match_id"))
    frame["derby"] = [float(frozenset((h, a)) in DERBIES) for h, a in zip(frame.home_team, frame.away_team)]
    if rosters:
        absences = _absence_features(matches, rosters).pivot(index="match_id", columns="side")
        absences.columns = [f"{name}_{side}" for name, side in absences.columns]
        frame = frame.merge(absences, on="match_id", how="left")
    return frame


def design(frame: pd.DataFrame, side: str, groups: list[str]) -> pd.DataFrame:
    """Features for one side's goal model; positive values should mean more goals for that side."""
    other = "away" if side == "home" else "home"
    columns = {}
    if "table" in groups:
        columns["ppg_diff"] = frame[f"ppg_{side}"] - frame[f"ppg_{other}"]
        for flag in ("relegation", "title", "dead_rubber"):
            columns[f"{flag}_self"] = frame[f"{flag}_{side}"]
            columns[f"{flag}_opp"] = frame[f"{flag}_{other}"]
    if "derby" in groups:
        columns["derby"] = frame["derby"]
    if "home" in groups:
        # This side's attacking residual in this venue role, and the opponent's defensive residual.
        columns["att_resid"] = frame[f"att_resid_{side}"]
        columns["opp_def_resid"] = frame[f"def_resid_{other}"]
    if "absences" in groups:
        columns["att_missing_self"] = frame[f"att_missing_{side}"]
        columns["def_missing_opp"] = frame[f"def_missing_{other}"]
        columns["att_missing_opp"] = frame[f"att_missing_{other}"]
        columns["def_missing_self"] = frame[f"def_missing_{side}"]
    if "rest" in groups:
        columns["rest_diff"] = frame[f"rest_{side}"] - frame[f"rest_{other}"]
        columns["short_rest"] = (frame[f"rest_{side}"] < 4).astype(float)
    return pd.DataFrame(columns, index=frame.index)


def fit_adjustment(train: pd.DataFrame, groups: list[str]) -> dict:
    models = {}
    for side in ("home", "away"):
        x = sm.add_constant(design(train, side, groups), has_constant="add")
        y = train[f"{side}_goals"]
        offset = np.log(train[f"lambda_{side}"])
        models[side] = sm.GLM(y, x, family=sm.families.Poisson(), offset=offset).fit()
    return models


def adjusted_lambdas(frame: pd.DataFrame, models: dict, groups: list[str]) -> tuple[np.ndarray, np.ndarray]:
    out = []
    for side in ("home", "away"):
        x = sm.add_constant(design(frame, side, groups), has_constant="add")
        out.append(np.asarray(models[side].predict(x, offset=np.log(frame[f"lambda_{side}"]))))
    return out[0], out[1]


def market_log_loss(frame: pd.DataFrame, lam: np.ndarray, mu: np.ndarray) -> dict:
    """Log loss of the markets the slips use, from the full score matrix."""
    losses = {"1x2": [], "over_1.5": [], "over_2.5": [], "under_3.5": [], "home_1up_proxy": []}
    for (l, m, rho), hg, ag in zip(zip(lam, mu, frame.rho), frame.home_goals, frame.away_goals):
        markets = market_probabilities(score_matrix(l, m, rho))
        result = markets["prob_home"] if hg > ag else markets["prob_draw"] if hg == ag else markets["prob_away"]
        losses["1x2"].append(-np.log(max(result, 1e-9)))
        for key, prob, hit in (("over_1.5", markets["prob_over15"], hg + ag > 1.5),
                               ("over_2.5", markets["prob_over25"], hg + ag > 2.5),
                               ("under_3.5", 1 - markets["prob_over35"], hg + ag < 3.5),
                               ("home_1up_proxy", markets["prob_home"], hg > ag)):
            losses[key].append(-np.log(max(prob if hit else 1 - prob, 1e-9)))
    return {k: float(np.mean(v)) for k, v in losses.items()}


def walk_forward_study(frame: pd.DataFrame, eval_seasons: list[str], variants: dict[str, list[str]]) -> pd.DataFrame:
    rows = []
    for season in eval_seasons:
        train, test = frame[frame.season < season], frame[frame.season == season]
        if train.empty or test.empty:      # e.g. lineup data not available for this season
            continue
        base = market_log_loss(test, test.lambda_home.to_numpy(), test.lambda_away.to_numpy())
        rows.append({"season": season, "variant": "baseline", "n": len(test), **base})
        for name, groups in variants.items():
            models = fit_adjustment(train, groups)
            lam, mu = adjusted_lambdas(test, models, groups)
            rows.append({"season": season, "variant": name, "n": len(test), **market_log_loss(test, lam, mu)})
    return pd.DataFrame(rows)


def main() -> None:
    matches = pd.read_parquet(MATCHES_PATH)
    dc = pd.read_parquet(DC_PATH)
    predictions = pd.concat([pd.read_parquet(HISTORY_PATH), dc[dc.variant == "blend"]], ignore_index=True)
    frame = build_features(matches, predictions, load_rosters(range(2021, 2027)))
    frame = frame[frame.season >= "2017/18"]           # residual features need a season of history
    base_groups = [g for g in GROUPS if g != "absences"]
    variants = {**{g: [g] for g in base_groups}, "all": base_groups}
    eval_seasons = ["2021/22", "2022/23", "2023/24", "2024/25", "2025/26", "2026/27"]
    study = walk_forward_study(frame, eval_seasons, variants)
    weighted = study.groupby("variant").apply(
        lambda g: pd.Series({c: np.average(g[c], weights=g.n) for c in ["1x2", "over_1.5", "over_2.5", "under_3.5", "home_1up_proxy"]}),
        include_groups=False)
    gain = (weighted.loc["baseline"] - weighted).drop(index="baseline")
    final = fit_adjustment(frame[frame.season < "2026/27"], base_groups)

    # Absences: rosters start in 2021/22, so train from there and evaluate 2022/23 onwards.
    absent = frame.dropna(subset=["att_missing_home", "att_missing_away"])
    absence_study = walk_forward_study(absent, eval_seasons[1:], {"absences": ["absences"]})
    absence_weighted = absence_study.groupby("variant").apply(
        lambda g: pd.Series({c: np.average(g[c], weights=g.n) for c in ["1x2", "over_1.5", "over_2.5", "under_3.5", "home_1up_proxy"]}),
        include_groups=False)
    absence_final = fit_adjustment(absent[absent.season < "2026/27"], ["absences"])

    lines = ["# Factor study", "",
             "Walk-forward: each season's adjustment is fitted only on earlier seasons (from 2017/18).",
             f"Evaluated on {', '.join(eval_seasons)} ({int(study[study.variant == 'baseline'].n.sum())} matches).", "",
             "## Log loss (lower is better), match-weighted", "",
             "| Variant | 1X2 | Over 1.5 | Over 2.5 | Under 3.5 | Home win (1Up proxy) |", "|---|---:|---:|---:|---:|---:|"]
    for variant, row in weighted.iterrows():
        lines.append(f"| {variant} | {row['1x2']:.4f} | {row['over_1.5']:.4f} | {row['over_2.5']:.4f} | {row['under_3.5']:.4f} | {row['home_1up_proxy']:.4f} |")
    lines += ["", "## Improvement vs baseline (positive = better)", "",
              "| Variant | 1X2 | Over 1.5 | Over 2.5 | Under 3.5 | Home win |", "|---|---:|---:|---:|---:|---:|"]
    for variant, row in gain.iterrows():
        lines.append(f"| {variant} | {row['1x2']:+.4f} | {row['over_1.5']:+.4f} | {row['over_2.5']:+.4f} | {row['under_3.5']:+.4f} | {row['home_1up_proxy']:+.4f} |")
    lines += ["", "## By season: 1X2 log loss", "", "| Season | " + " | ".join(weighted.index) + " |",
              "|---|" + "---:|" * len(weighted.index)]
    for season, g in study.groupby("season"):
        values = g.set_index("variant")["1x2"]
        lines.append(f"| {season} | " + " | ".join(f"{values[v]:.4f}" for v in weighted.index) + " |")
    for side in ("home", "away"):
        lines += ["", f"## Fitted effects, {side} goals (all factors, trained to 2025/26)", "",
                  "| Feature | Coefficient | Std. error | Goals multiplier |", "|---|---:|---:|---:|"]
        model = final[side]
        for name in model.params.index:
            lines.append(f"| {name} | {model.params[name]:+.3f} | {model.bse[name]:.3f} | x{np.exp(model.params[name]):.3f} |")
    lines += ["", "## Absences (missing regular starters), evaluated 2022/23 onwards", "",
              f"{int(absence_study[absence_study.variant == 'baseline'].n.sum())} matches with lineup data. "
              "Uses actual starting XIs, so it is an upper bound for live injury news.", "",
              "| Variant | 1X2 | Over 1.5 | Over 2.5 | Under 3.5 | Home win |", "|---|---:|---:|---:|---:|---:|"]
    for variant, row in absence_weighted.iterrows():
        lines.append(f"| {variant} | {row['1x2']:.4f} | {row['over_1.5']:.4f} | {row['over_2.5']:.4f} | {row['under_3.5']:.4f} | {row['home_1up_proxy']:.4f} |")
    for side in ("home", "away"):
        lines += ["", f"### Absence effects, {side} goals", "", "| Feature | Coefficient | Std. error | Goals multiplier |", "|---|---:|---:|---:|"]
        model = absence_final[side]
        for name in model.params.index:
            lines.append(f"| {name} | {model.params[name]:+.3f} | {model.bse[name]:.3f} | x{np.exp(model.params[name]):.3f} |")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(gain.round(4).to_string())
    print((absence_weighted.loc["baseline"] - absence_weighted).round(4).to_string())
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()
