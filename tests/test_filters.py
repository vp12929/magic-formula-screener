"""
Unit tests for Filters (Sector, MarketCap, Profitability, FilterChain).
"""

from magic_formula.models.company import Company
from magic_formula.models.financials import FinancialStatement
from magic_formula.filters.sector import SectorFilter
from magic_formula.filters.market_cap import MarketCapFilter
from magic_formula.filters.profitability import PositiveEarningsFilter
from magic_formula.filters.chain import FilterChain


def test_sector_filter():
    filter_rule = SectorFilter()

    tech = Company(ticker="AAPL", name="Apple", sector="Technology")
    bank = Company(ticker="JPM", name="JPMorgan", sector="Financial Services")
    utility = Company(ticker="NEE", name="NextEra", sector="Utilities")

    assert filter_rule.passes(tech) is True
    assert filter_rule.passes(bank) is False
    assert filter_rule.passes(utility) is False


def test_market_cap_filter():
    filter_rule = MarketCapFilter(min_market_cap=50_000_000.0)

    large_cap = Company(ticker="LARGE", name="Large Inc", sector="Tech", market_cap=1_000_000_000.0)
    micro_cap = Company(ticker="MICRO", name="Micro Inc", sector="Tech", market_cap=10_000_000.0)

    assert filter_rule.passes(large_cap) is True
    assert filter_rule.passes(micro_cap) is False


def test_profitability_filter():
    filter_rule = PositiveEarningsFilter()

    profitable = Company(
        ticker="PROF", name="Profitable", sector="Tech",
        financials=FinancialStatement(ebit=100.0, enterprise_value=1000.0, market_cap=900.0, net_income=80.0)
    )
    loss_making = Company(
        ticker="LOSS", name="Loss Making", sector="Tech",
        financials=FinancialStatement(ebit=-10.0, enterprise_value=1000.0, market_cap=900.0, net_income=-20.0)
    )

    assert filter_rule.passes(profitable) is True
    assert filter_rule.passes(loss_making) is False


def test_filter_chain():
    chain = FilterChain.default_magic_formula_chain(min_market_cap=50_000_000.0)

    valid_company = Company(
        ticker="GOOD", name="Good Corp", sector="Technology", market_cap=500_000_000.0,
        financials=FinancialStatement(ebit=50.0, enterprise_value=500.0, market_cap=500.0, net_income=40.0)
    )
    bank_company = Company(
        ticker="BANK", name="Bank Corp", sector="Financial Services", market_cap=500_000_000.0,
        financials=FinancialStatement(ebit=50.0, enterprise_value=500.0, market_cap=500.0, net_income=40.0)
    )

    assert chain.passes(valid_company) is True
    assert chain.passes(bank_company) is False
