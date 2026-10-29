"""Research only: PROJECT.md task 13, pre-registered before results."""
from io import StringIO
import json
import time

import numpy as np
import pandas as pd
import requests
from scipy.special import expit, logit
from sklearn.linear_model import LogisticRegression

from .accumulators import bookmaker_implied
from .betpawa import BASE_URL, HEADERS
from .leagues import ENGINE_DIR, LEAGUES
from .market_live import league_rho
from .market_gates import evaluate

CANDIDATES = {"N1": ("Eredivisie", "ned.1"), "B1": ("Belgian Pro League", "bel.1"),
              "P1": ("Primeira Liga", "por.1"), "T1": ("Super Lig", "tur.1")}
MARKETS = ("home_win", "away_win", "double_1x", "double_x2", "double_12", "over_0.5", "over_1.5", "over_2.5")
CACHE = ENGINE_DIR / "data" / "raw" / "new_leagues_study"


def download(url, name, session):
    path = CACHE / name
    if not path.exists():
        response = session.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(response.content)
        time.sleep(1)
    return path.read_bytes()


def odds_columns(frame):
    modern = ["AvgH", "AvgD", "AvgA", "Avg>2.5", "Avg<2.5"]
    older = ["BbAvH", "BbAvD", "BbAvA", "BbAv>2.5", "BbAv<2.5"]
    return modern if set(modern) <= set(frame) else older if set(older) <= set(frame) else None


def outcomes(home, away):
    return dict(home_win=int(home > away), away_win=int(away > home), double_1x=int(home >= away),
                double_x2=int(home <= away), double_12=int(home != away),
                **{f"over_{line}": int(home + away > line) for line in (.5, 1.5, 2.5)})


def calibrate_seasons(legs):
    result = legs.copy()
    result["probability"] = np.nan
    for season in sorted(result.season.unique())[1:]:
        for market in MARKETS:
            past = result[(result.season < season) & (result.market == market)]
            current = (result.season == season) & (result.market == market)
            if past.won.nunique() < 2:
                raise ValueError(f"Insufficient calibration outcomes before {season} {market}")
            model = LogisticRegression(C=1.0)
            model.fit(logit(past.bookmaker_probability.clip(1e-6, 1-1e-6)).to_numpy().reshape(-1, 1), past.won)
            raw = logit(result.loc[current, "bookmaker_probability"].clip(1e-6, 1-1e-6))
            result.loc[current, "probability"] = expit(model.intercept_[0] + model.coef_[0, 0] * raw)
    return result


def main():
    session = requests.Session()
    rho = float(np.median([league_rho(code) for code in LEAGUES]))
    lines = ["# New leagues study", "", f"Fixed median live-league rho: {rho:.6f}.", ""]
    categories = json.loads(download(BASE_URL + "/categories/list/2", "betpawa_categories.json", session))
    for div, (name, slug) in CANDIDATES.items():
        rows, coverage = [], []
        for year in range(2014, 2027):
            code = f"{year % 100:02d}{(year+1) % 100:02d}"
            data = download(f"https://www.football-data.co.uk/mmz4281/{code}/{div}.csv", f"{div}_{code}.csv", session)
            frame = pd.read_csv(StringIO(data.decode("utf-8-sig", errors="replace")))
            columns = odds_columns(frame)
            played = frame.dropna(subset=["FTHG", "FTAG", "Date"])
            valid = played.iloc[:0] if columns is None else played[(played[columns].notna() & played[columns].gt(0)).all(axis=1)]
            coverage.append(f"| {year}/{str(year+1)[2:]} | {len(played)} | {len(valid)} | {', '.join(columns or [])} |")
            for match in valid.to_dict("records"):
                raw = bookmaker_implied(*(float(match[c]) for c in columns), rho)[0]
                actual = outcomes(match["FTHG"], match["FTAG"])
                for market in MARKETS:
                    rows.append(dict(date=pd.to_datetime(match["Date"], dayfirst=True), season=year,
                                     market=market, bookmaker_probability=raw[market], won=actual[market]))
            print(f"{name} {year}: {len(valid)} complete odds", flush=True)
        legs = calibrate_seasons(pd.DataFrame(rows))
        test = legs[legs.season >= 2024]
        rng = np.random.default_rng(20261029)
        gates = [evaluate(div, market, test, "probability", rng) for market in MARKETS]
        # Match competition names explicitly; country disambiguates generic names such as Pro League.
        country = {"N1": "Netherlands", "B1": "Belgium", "P1": "Portugal", "T1": "Turkey"}[div]
        regions = categories["withRegions"][0]["regions"]
        competition_name = {"N1": "Eredivisie", "B1": "Pro League", "P1": "Liga Portugal", "T1": "Super Lig"}[div]
        matches = [c["competition"] for r in regions if r["region"]["name"] == country
                   for c in r["competitions"] if c["competition"]["name"] == competition_name]
        espn_url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard"
        espn = json.loads(download(espn_url, f"espn_{slug}.json", session))
        events = espn.get("events", [])
        covered = bool(events)
        passed = sum(g["status"] == "PASS" for g in gates)
        ready = passed >= 6 and bool(matches) and covered
        lines += [f"## {name}: {'READY' if ready else 'NOT READY'}", "",
                  f"Markets passing: {passed}/8. Betpawa {country} competitions: {json.dumps(matches)}.",
                  f"ESPN: {espn_url}; {len(events)} events. Example: " + (events[0].get("name", "") if events else "none; coverage unconfirmed"), "",
                  "| Season | Played | Complete odds | Source columns |", "|---|---:|---:|---|", *coverage, "",
                  "| Market | N | Status | Predicted | Actual |", "|---|---:|---|---:|---:|"]
        for gate in gates:
            lines.append(f"| {gate['market']} | {gate['n']} | {gate['status']} | {gate.get('mean_p', 'unknown')} | {gate.get('actual', 'unknown')} |")
        lines += ["", "Gate details: " + json.dumps(gates, default=lambda x: bool(x)), ""]
        print(f"{name}: {passed}/8 PASS; {'READY' if ready else 'NOT READY'}", flush=True)
    lines += ["## ESPN settlement evidence", "", "Real completed events on 2026-10-25:", ""]
    for name, slug in CANDIDATES.values():
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard?dates=20261025"
        results = json.loads(download(url, f"espn_results_{slug}.json", session))
        completed = [event for event in results.get("events", []) if event["status"]["type"].get("completed")]
        if not completed:
            lines.append(f"- {name}: no completed example in this response; settlement unconfirmed.")
            continue
        event = completed[0]
        score = ", ".join(f"{team['team']['displayName']} {team.get('score', 'unknown')}"
                          for team in event["competitions"][0]["competitors"])
        lines.append(f"- {name}: {url}; event {event['id']}, {event['status']['type']['name']}: {score}.")
    (ENGINE_DIR / "reports" / "new_leagues_study.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
