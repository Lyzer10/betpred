import pandas as pd
import pytest
from src.fetch_results import parse_match_dates


def test_date_parsing_handles_short_and_long_years():
    result = parse_match_dates(pd.Series(["16/08/14", "16/08/2014"]))
    assert result.dt.strftime("%Y-%m-%d").tolist() == ["2014-08-16", "2014-08-16"]


def test_date_parsing_rejects_bad_values():
    with pytest.raises(ValueError, match="Unparseable"):
        parse_match_dates(pd.Series(["not a date"]))

