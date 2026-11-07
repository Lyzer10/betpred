import json
from pathlib import Path
import pandas as pd

from src.accumulators import LEG_MARKETS, SLIP_MARKETS
from src.betpawa import RESEARCH_MARKETS, parse_markets


def test_real_event_research_markets():
    # Events 38781890 (2026-10-29), 38292840 (2026-11-07) and 38916500 (2026-11-07),
    # fetched with the identified client. Fields deleted only.
    markets = json.loads((Path(__file__).parent / "fixtures" / "betpawa_research.json").read_text())
    expected = (
        1.15, 1.7, 1.37, 2.71, 1.37, 2.84,
        1.37, 2.64, 1.24, 2.08,
        1.16, 1.66, 1.03, 1.77, 4.57,
        1.4, 2.46,
        6.53, 1.2, 12.08,
        2.74, 1.57,
        4.81, 2.41,
        14.52, 4.5,
        2.41, 1.62, 2.04, 1.46,
    )
    parsed = parse_markets(markets)
    research_only = {k: v for k, v in parsed.items() if k in RESEARCH_MARKETS}
    assert research_only == dict(zip(RESEARCH_MARKETS, expected))
    assert not set(RESEARCH_MARKETS).intersection(SLIP_MARKETS)
    assert not set(RESEARCH_MARKETS).intersection(LEG_MARKETS)


def test_research_prices_cannot_enter_live_selections_or_clv():
    from src.predict import best_pick, build_slips
    from src.prices import clv_report
    markets = json.loads((Path(__file__).parent / "fixtures" / "betpawa_research.json").read_text())
    odds = {k: v for k, v in parse_markets(markets).items() if k in RESEARCH_MARKETS}
    # Real quoted markets/prices, with no invented match, probability or outcome.
    legs = pd.DataFrame({"market": list(odds), "odds": list(odds.values())})
    assert best_pick(legs, set()) is None
    assert build_slips(legs, set()) == {}
    assert clv_report([], legs) == {"legs": 0}


def test_monitors_ignore_research_quotes_in_real_archive():
    from src.health import health_check, pair_monitor
    archive = Path(__file__).resolve().parents[2] / "web" / "e2e" / "fixtures" / "archive"
    fixtures = [fixture for path in archive.glob("20*.json")
                for fixture in json.loads(path.read_text())["fixtures"] if fixture.get("result")]
    quoted = json.loads((Path(__file__).parent / "fixtures" / "betpawa_research.json").read_text())
    research = [{"market": market, "odds": price} for market, price in parse_markets(quoted).items()
                if market in RESEARCH_MARKETS]
    augmented = [{**fixture, "markets": [*fixture["markets"], *research]} for fixture in fixtures]
    assert fixtures
    assert health_check(augmented, [], SLIP_MARKETS) == health_check(fixtures, [], SLIP_MARKETS)
    assert pair_monitor(augmented, SLIP_MARKETS, set()) == pair_monitor(fixtures, SLIP_MARKETS, set())
