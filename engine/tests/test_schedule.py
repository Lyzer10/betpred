"""Run-mode decisions and the final-slips notification (scripts/run_mode.py, scripts/notify.py)."""
import importlib.util
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


run_mode, notify = _load("run_mode"), _load("notify")
SLIP = {"total_odds": 2.51, "win_probability": 0.48, "legs": [{}, {}, {}], "locked": False, "final": False}


def _published(generated="2026-10-25T04:05:00Z", final=False, first="2026-10-25T11:30:00Z", locked=False):
    slip = SLIP | {"final": final, "locked": locked}
    return {"generated_at": generated,
            "days": [{"date": "2026-10-25", "first_kickoff_utc": first, "final": final, "slips": {"safe": slip}}],
            "fixtures": [{"kickoff_utc": first}, {"kickoff_utc": "2026-10-25T19:45:00Z"}]}


def _at(hhmm_utc):
    return datetime.fromisoformat(f"2026-10-25T{hhmm_utc}:00").replace(tzinfo=timezone.utc)


def test_final_run_shortly_before_first_match():
    # First match 14:30 Tanzania (11:30 UTC): final from 13:35; not at 13:00.
    assert run_mode.decide(_published(), _at("10:00")) == "full"     # 13:00 run due, not final yet
    assert run_mode.decide(_published(generated="2026-10-25T10:05:00Z"), _at("10:30")) == "skip"
    assert run_mode.decide(_published(generated="2026-10-25T10:05:00Z"), _at("10:40")) == "final"


def test_final_happens_once_and_never_for_started_slips():
    after_final = _published(generated="2026-10-25T10:40:00Z", final=True)
    assert run_mode.decide(after_final, _at("11:00")) == "prices"   # 11:30 kick-off within 35 minutes
    started = _published(generated="2026-10-25T10:05:00Z", locked=True)
    assert run_mode.decide(started, _at("12:00")) == "skip"


def test_regular_full_runs_and_price_snapshots():
    assert run_mode.decide(_published(generated="2026-10-24T20:00:00Z"), _at("04:10")) == "full"   # 07:10
    assert run_mode.decide(_published(generated="2026-10-25T15:05:00Z", final=True), _at("19:20")) == "prices"
    assert run_mode.decide(_published(generated="2026-10-25T15:05:00Z", final=True), _at("18:00")) == "skip"


def test_notification_lists_only_final_slips():
    title, body = notify.message(_published(final=True), _at("10:40"))
    assert title == "Today's bets are final · first match 14:30"
    assert body == "Safe: odds 2.51 · 48% chance · 3 matches"
    assert notify.message(_published(final=False), _at("10:40")) is None
