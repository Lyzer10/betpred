import pandas as pd
from src import overlap_study


def test_overlap_rule_known_answers(monkeypatch):
    # Abstract optimizer states (not claimed to be real matches or prices).
    pool = pd.DataFrame({"match_key": ["a", "b", "c"]})
    current = {"safe": pool.iloc[[0]], "medium": pool.iloc[[1]], "big": pool.iloc[[2]]}
    monkeypatch.setattr(overlap_study, "select_day_slips", lambda *args: current)
    monkeypatch.setattr(overlap_study, "_chosen", lambda eligible, tier: eligible.iloc[[-1]])
    a, m = overlap_study.select_variants(pool)
    assert all(a[t].equals(m[t]) for t in a)
    current["medium"] = pool.iloc[[0]]
    _, m = overlap_study.select_variants(pool)
    assert "a" not in set(m["big"].match_key)
    monkeypatch.setattr(overlap_study, "_chosen", lambda *args: None)
    _, m = overlap_study.select_variants(pool)
    assert "big" not in m
