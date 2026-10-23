import pytest
from src.team_names import canonical_team


def test_known_aliases_are_canonical():
    assert canonical_team("Man United") == "Manchester United"
    assert canonical_team("Wolverhampton Wanderers") == "Wolves"


def test_unknown_team_fails_loudly():
    with pytest.raises(ValueError, match="Unmapped team"):
        canonical_team("Made Up FC")

