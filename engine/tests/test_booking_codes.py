"""Betpawa booking codes: built only from Betpawa price ids and published only after a load-back check."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from src import booking_codes as bc
from src.betpawa import parse_market_prices, parse_markets

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "research_leagues" / "betpawa_E1_39240622.json"
NOW = pd.Timestamp("2026-11-08T10:00:00")


class FakeResponse:
    def __init__(self, payload: dict, status: int = 200):
        self.payload, self.status_code = payload, status

    def json(self) -> dict:
        return self.payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise bc.requests.HTTPError(f"HTTP {self.status_code}")


class FakeSession:
    """Betpawa stand-in: returns `code`, and on load-back the ids in `loaded` (default: the posted ids)."""
    def __init__(self, code: str = "ABC123", loaded: list[str] | None = None):
        self.code, self.loaded, self.posts, self.gets = code, loaded, [], []

    def post(self, url, json=None, headers=None, timeout=None):
        self.posts.append(json)
        return FakeResponse({"code": self.code})

    def get(self, url, headers=None, timeout=None):
        self.gets.append(url)
        posted = [str(s["selections"][0]) for s in self.posts[-1]["selections"]["selections"]]
        ids = self.loaded if self.loaded is not None else posted
        return FakeResponse({"items": [{"odds": {"selections": [i]}} for i in ids]})


def _slip(ids: list[str | None], kickoff: str = "2026-11-08T15:00:00Z") -> dict:
    return {"total_odds": 2.0, "legs": [{"kickoff_utc": kickoff, "betpawa_price_id": i} for i in ids]}


@pytest.fixture(autouse=True)
def _tmp_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(bc, "CACHE_PATH", tmp_path / "booking_codes.json")
    monkeypatch.setattr(bc, "PAUSE_SECONDS", 0)


def test_price_ids_come_from_the_same_prices_as_the_odds() -> None:
    markets = json.loads(FIXTURE.read_text(encoding="utf-8"))["markets"]
    odds, ids = parse_market_prices(markets)
    assert odds == parse_markets(markets)
    assert ids and set(ids) <= set(odds)
    by_id = {str(p["id"]): p for m in markets for r in m.get("row", []) for p in r.get("prices", [])}
    for key, price_id in ids.items():
        assert by_id[price_id]["odds"] == odds[key]      # the id is exactly the priced outcome


def test_code_published_only_after_load_back_matches() -> None:
    session = FakeSession()
    out = bc.add_booking_codes({"safe": _slip(["11", "22"])}, NOW, session=session)
    assert out["safe"]["booking_code"] == "ABC123"
    assert session.posts[0] == {"selections": {"selections": [{"type": "SINGLE", "selections": [11]},
                                                              {"type": "SINGLE", "selections": [22]}]}}


def test_wrong_load_back_means_no_code() -> None:
    out = bc.add_booking_codes({"safe": _slip(["11", "22"])}, NOW, session=FakeSession(loaded=["11", "99"]))
    assert "booking_code" not in out["safe"]
    out = bc.add_booking_codes({"safe": _slip(["11", "22"])}, NOW, session=FakeSession(loaded=["11"]))
    assert "booking_code" not in out["safe"]


def test_no_code_when_a_leg_has_no_betpawa_price_or_has_started() -> None:
    session = FakeSession()
    out = bc.add_booking_codes({"safe": _slip(["11", None]),
                                "big": _slip(["11", "22"], kickoff="2026-11-08T09:00:00Z")}, NOW, session=session)
    assert "booking_code" not in out["safe"] and "booking_code" not in out["big"]
    assert session.posts == []


def test_cache_reused_and_offline_uses_cache_only() -> None:
    first = FakeSession(code="FIRST1")
    bc.add_booking_codes({"safe": _slip(["22", "11"])}, NOW, session=first)
    second = FakeSession(code="OTHER2")
    out = bc.add_booking_codes({"medium": _slip(["11", "22"])}, NOW, session=second)
    assert out["medium"]["booking_code"] == "FIRST1" and second.posts == []    # same picks, any order
    offline = FakeSession()
    out = bc.add_booking_codes({"safe": _slip(["33"])}, NOW, online=False, session=offline)
    assert "booking_code" not in out["safe"] and offline.posts == []


def test_betpawa_error_means_no_code(capsys) -> None:
    class Down(FakeSession):
        def post(self, *a, **k):
            return FakeResponse({}, status=503)
    out = bc.add_booking_codes({"safe": _slip(["11"])}, NOW, session=Down())
    assert "booking_code" not in out["safe"]
    assert "Booking code for safe slip unavailable" in capsys.readouterr().out


def test_leg_json_carries_price_id_only_with_a_betpawa_price() -> None:
    from src.predict import _price_id
    row = type("Row", (), {"betpawa_price_id": 1579863214.0, "betpawa_odds": 5.49})
    assert _price_id(row) == "1579863214"
    row.betpawa_odds = float("nan")
    assert _price_id(row) is None
