import pandas as pd

from src import prices


def _prices(rows):
    frame = pd.DataFrame(rows, columns=["snapshot_utc", "home", "away", "kickoff_utc", "market", "betpawa_odds"])
    for column in ("snapshot_utc", "kickoff_utc"):
        frame[column] = pd.to_datetime(frame[column])
    return frame


def _history(odds):
    return [{"tier": "safe", "final": True, "legs": [
        {"league": {"code": "EPL"}, "home": "Arsenal", "away": "Everton", "market": "home_win",
         "kickoff_utc": "2026-10-24T14:00:00Z", "betpawa_odds": odds, "won": True}]}]


def test_clv_uses_last_price_before_kickoff():
    log = _prices([
        ("2026-10-24 04:00", "Arsenal", "Everton", "2026-10-24 14:00", "home_win", 1.60),
        ("2026-10-24 13:20", "Arsenal", "Everton", "2026-10-24 14:00", "home_win", 1.50),
        ("2026-10-24 14:30", "Arsenal", "Everton", "2026-10-24 14:00", "home_win", 1.20),   # in play: ignored
    ])
    report = prices.clv_report(_history(1.60), log)
    assert report["legs"] == 1
    assert abs(report["mean_clv"] - (1.60 / 1.50 - 1)) < 1e-4
    assert report["beat_close"] == 1.0 and report["league"]["EPL"]["legs"] == 1


def test_no_closing_price_without_a_snapshot_near_kickoff():
    # Only a morning price: not a closing price, so no CLV is claimed.
    log = _prices([("2026-10-24 04:00", "Arsenal", "Everton", "2026-10-24 14:00", "home_win", 1.60)])
    assert prices.clv_report(_history(1.60), log) == {"legs": 0}


def test_log_prices_appends_only_priced_slip_markets(tmp_path, monkeypatch):
    monkeypatch.setattr(prices, "PRICES_DIR", tmp_path)
    now = pd.Timestamp("2026-10-24 04:00")
    legs = pd.DataFrame({
        "league": "EPL", "home_team": "Arsenal", "away_team": "Everton", "day": "2026-10-24",
        "kickoff_utc": pd.Timestamp("2026-10-24 14:00"), "market": ["home_win", "btts_yes", "away_win"],
        "betpawa_odds": [1.6, 1.9, None], "probability": [0.6, 0.5, 0.2], "bookmaker_probability": [0.6, 0.5, 0.2]})
    assert prices.log_prices(legs, now) == 1
    assert prices.log_prices(legs, now + pd.Timedelta(hours=1)) == 1
    logged = pd.read_csv(tmp_path / "2026-10-24.csv")
    assert logged.market.tolist() == ["home_win", "home_win"] and len(logged.columns) == len(prices.COLUMNS)
