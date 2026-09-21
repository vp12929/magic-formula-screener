"""
Unit tests for the complete MagicFormulaScreener engine.
"""

from magic_formula.providers.mock import MockDataProvider
from magic_formula.screener import MagicFormulaScreener
from magic_formula.strategies.strict import StrictMagicFormulaStrategy
from magic_formula.strategies.proxy import ProxyRankingStrategy


def test_screener_with_mock_provider():
    provider = MockDataProvider()
    all_tickers = provider.get_all_tickers()
    
    screener = MagicFormulaScreener(
        data_provider=provider,
        ranking_strategy=StrictMagicFormulaStrategy()
    )

    top_stocks, summary = screener.run_screen(all_tickers, top_n=10)

    # 22 total mock companies, JPM/BAC/GS excluded (Financials), NEE/DUK excluded (Utilities), TINY1/TINY2 excluded (<$50M)
    assert summary.total_fetched == len(all_tickers)
    assert summary.passed_filters > 0
    assert len(top_stocks) <= 10

    # Ensure no excluded sectors leaked in
    for r in top_stocks:
        assert r.company.sector not in ["Financial Services", "Utilities"]
        assert r.company.market_cap >= 50_000_000


def test_screener_comparison_mode():
    provider = MockDataProvider()
    screener = MagicFormulaScreener(data_provider=provider)
    
    comparison = screener.compare_strict_vs_proxy(provider.get_all_tickers(), top_n=5)
    
    assert "strict_top_n" in comparison
    assert "proxy_top_n" in comparison
    assert len(comparison["strict_top_n"]) == 5
    assert len(comparison["proxy_top_n"]) == 5
