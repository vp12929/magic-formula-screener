"""
Unit tests for Data Providers.
"""

from magic_formula.providers.mock import MockDataProvider
from magic_formula.providers.base import BaseDataProvider


def test_mock_data_provider():
    provider = MockDataProvider()
    assert isinstance(provider, BaseDataProvider)

    # Test fetching valid ticker
    aapl = provider.fetch_company("AAPL")
    assert aapl is not None
    assert aapl.ticker == "AAPL"
    assert aapl.sector == "Technology"
    assert aapl.financials is not None
    assert aapl.financials.ebit > 0

    # Test fetching invalid ticker
    invalid = provider.fetch_company("NONEXISTENT_XYZ")
    assert invalid is None

    # Test fetch_universe
    universe = provider.fetch_universe(["AAPL", "GOOGL", "INVALID_TICKER"])
    assert len(universe) == 2
    tickers = [c.ticker for c in universe]
    assert "AAPL" in tickers
    assert "GOOGL" in tickers
