import numpy as np

from src.health import health_check

SLIP_MARKETS = ("home_1up", "over_1.5")


def _fixtures(n, ours, book, home_wins, rng):
    fixtures = []
    for i in range(n):
        home = bool(rng.random() < home_wins)
        outcomes = {"home_win": home, "draw": not home, "away_win": False,
                    "home_1up": bool(rng.random() < 0.7), "over_1.5": bool(rng.random() < 0.8)}
        fixtures.append({"markets": [
            {"market": "home_win", "probability": ours, "market_probability": book},
            {"market": "draw", "probability": 1 - ours - 0.05, "market_probability": 1 - book - 0.05},
            {"market": "away_win", "probability": 0.05, "market_probability": 0.05},
            {"market": "home_1up", "probability": 0.7, "market_probability": 0.7},
            {"market": "over_1.5", "probability": 0.8, "market_probability": 0.8},
        ], "result": {"outcomes": outcomes}})
    return fixtures


def test_insufficient_data_never_raises_alarm():
    result = health_check(_fixtures(10, 0.6, 0.6, 0.6, np.random.default_rng(0)), [], SLIP_MARKETS)
    assert result["status"] == "insufficient" and result["stake_factor"] == 1.0


def test_healthy_model_is_ok():
    rng = np.random.default_rng(1)
    slips = [{"status": "won" if rng.random() < 0.4 else "lost", "win_probability": 0.4} for _ in range(40)]
    result = health_check(_fixtures(60, 0.6, 0.6, 0.6, rng), slips, SLIP_MARKETS)
    assert result["status"] == "ok", result
    assert result["stake_factor"] == 1.0


def test_model_much_worse_than_bookmaker_halves_stakes():
    # We say 85% home win, the bookmaker says 55%, and the truth is 55%.
    result = health_check(_fixtures(60, 0.85, 0.55, 0.55, np.random.default_rng(2)), [], SLIP_MARKETS)
    accuracy = next(c for c in result["checks"] if c["name"] == "accuracy")
    assert accuracy["status"] == "warning"
    assert result["status"] == "warning" and result["stake_factor"] == 0.5


def test_slips_losing_far_more_than_predicted_is_flagged():
    slips = [{"status": "lost", "win_probability": 0.4} for _ in range(30)]
    result = health_check([], slips, SLIP_MARKETS)
    assert next(c for c in result["checks"] if c["name"] == "slips")["status"] == "warning"
