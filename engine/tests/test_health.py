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


def _pair_fixtures(league, market, probability, wins, n):
    return [{"league": {"code": league}, "markets": [{"market": market, "probability": probability}],
             "result": {"outcomes": {market: i < wins}}} for i in range(n)]


def test_pair_monitor_pauses_only_over_confidence_and_recovers():
    from src.health import pair_monitor, pair_status
    # Said 70%, won 20 of 50 (40%): z far below -3, paused.
    rows = pair_monitor(_pair_fixtures("SERIEA", "home_1up", 0.7, 20, 50), ("home_1up",), set())
    assert rows[0]["status"] == "paused" and rows[0]["z"] < -3
    # Said 50%, won 45 of 50: wins MORE than predicted, never flagged.
    rows = pair_monitor(_pair_fixtures("EPL", "over_1.5", 0.5, 45, 50), ("over_1.5",), set())
    assert rows[0]["status"] == "ok"
    # Recovery band: z = -2.5 stays paused if it was paused, is only "watch" if it was not.
    assert pair_status(50, -2.5, was_paused=True) == "paused"
    assert pair_status(50, -2.5, was_paused=False) == "watch"
    assert pair_status(50, -1.9, was_paused=True) == "ok"
    assert pair_status(29, -5.0, was_paused=True) == "insufficient"


def test_slip_leg_monitor_counts_only_settled_legs():
    from src.health import slip_leg_monitor
    legs = [{"league": {"code": "EPL"}, "market": "home_win", "probability": 0.6, "won": i < 18} for i in range(30)]
    legs.append({"league": {"code": "EPL"}, "market": "home_win", "probability": 0.6, "won": None})
    rows = slip_leg_monitor([{"legs": legs}])
    assert rows[0]["n"] == 30 and rows[0]["actual"] == 0.6 and rows[0]["status"] == "ok"
