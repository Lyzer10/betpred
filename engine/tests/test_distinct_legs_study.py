import pandas as pd

from src.distinct_legs_study import select


def _pool():
    # 6 matches x 2 markets; the best legs are over_1.5 on every match.
    rows = []
    for m in range(6):
        for market, p, o in (("over_1.5", .8, 1.3), ("double_1x", .7, 1.45)):
            rows.append(dict(match_id=f"M{m}", match_key=f"M{m}", market=market, probability=p, odds=o,
                             won=True))
    return pd.DataFrame(rows)


def test_a_repeats_identical_legs_d_never_does():
    pool = _pool()
    a, d = select(pool, "A"), select(pool, "D")
    keys = lambda s: [set(c.match_key + c.market) for c in s.values()]
    a_k, d_k = keys(a), keys(d)
    assert len(a) >= 2 and any(a_k[0] & k for k in a_k[1:])  # A shares identical legs
    for i, k in enumerate(d_k):
        for later in d_k[i + 1:]:
            assert not (k & later)  # D never repeats match+market
