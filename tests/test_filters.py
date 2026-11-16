"""
Unit tests for Filters (Sector, MarketCap, Profitability, CapitalEmployed, FilterChain).
"""

import pytest
from magic_formula.models.company import Company
from magic_formula.models.financials import FinancialStatement
from magic_formula.filters.sector import SectorFilter
from magic_formula.filters.market_cap import MarketCapFilter
from magic_formula.filters.profitability import PositiveEarningsFilter
from magic_formula.filters.capital_employed import MinCapitalEmployedFilter
from magic_formula.filters.chain import FilterChain
from magic_formula.filters.helpers import parse_currency


def test_parse_currency():
    assert parse_currency("50M") == 50_000_000.0
    assert parse_currency("50m") == 50_000_000.0
    assert parse_currency("2.5B") == 2_500_000_000.0
    assert parse_currency("500K") == 500_000.0
    assert parse_currency("$10B") == 10_000_000_000.0
    assert parse_currency("100,000,000") == 100_000_000.0
    assert parse_currency(25_000_000) == 25_000_000.0


def test_sector_filter():
    filter_rule = SectorFilter()

    tech = Company(ticker="AAPL", name="Apple", sector="Technology")
    bank = Company(ticker="JPM", name="JPMorgan", sector="Financial Services")
    utility = Company(ticker="NEE", name="NextEra", sector="Utilities")

    assert filter_rule.passes(tech) is True
    assert filter_rule.passes(bank) is False
    assert filter_rule.passes(utility) is False


def test_market_cap_filter_and_tiers():
    # String input parsing
    filter_rule = MarketCapFilter(min_market_cap="50M", max_market_cap="2B")
    comp_small = Company(ticker="SMALL", name="Small Inc", sector="Tech", market_cap=500_000_000.0)
    comp_mega = Company(ticker="MEGA", name="Mega Inc", sector="Tech", market_cap=50_000_000_000.0)

    assert filter_rule.passes(comp_small) is True
    assert filter_rule.passes(comp_mega) is False

    # Tier factory method
    mid_filter = MarketCapFilter.from_tier("mid")  # $2B - $10B
    assert mid_filter.passes(Company("A", "A", "Tech", market_cap=5_000_000_000.0)) is True
    assert mid_filter.passes(Company("B", "B", "Tech", market_cap=1_000_000_000.0)) is False
    assert mid_filter.passes(Company("C", "C", "Tech", market_cap=15_000_000_000.0)) is False


def test_min_capital_employed_filter():
    filter_rule = MinCapitalEmployedFilter(min_capital="10M")

    # High capital employed: 20M Fixed + (15M Curr Assets - 5M Curr Liab) = 30M
    good_capital = Company(
        ticker="GOOD_CAP", name="Good Capital", sector="Tech",
        financials=FinancialStatement(
            ebit=10.0, enterprise_value=100.0, market_cap=90.0, net_income=8.0,
            net_fixed_assets=20_000_000.0, current_assets=15_000_000.0, current_liabilities=5_000_000.0
        )
    )

    # Low capital employed: 1M Fixed + (2M Curr Assets - 1.5M Curr Liab) = 1.5M (< 10M)
    low_capital = Company(
        ticker="LOW_CAP", name="Low Capital", sector="Tech",
        financials=FinancialStatement(
            ebit=10.0, enterprise_value=100.0, market_cap=90.0, net_income=8.0,
            net_fixed_assets=1_000_000.0, current_assets=2_000_000.0, current_liabilities=1_500_000.0
        )
    )

    assert filter_rule.passes(good_capital) is True
    assert filter_rule.passes(low_capital) is False
    assert "below minimum required" in filter_rule.rejection_reason(low_capital)


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
    chain = FilterChain.default_magic_formula_chain(min_market_cap="50M", min_capital_employed="10M")

    valid_company = Company(
        ticker="GOOD", name="Good Corp", sector="Technology", market_cap=500_000_000.0,
        financials=FinancialStatement(
            ebit=50.0, enterprise_value=500.0, market_cap=500.0, net_income=40.0,
            net_fixed_assets=25_000_000.0, current_assets=20_000_000.0, current_liabilities=10_000_000.0
        )
    )
    bank_company = Company(
        ticker="BANK", name="Bank Corp", sector="Financial Services", market_cap=500_000_000.0,
        financials=FinancialStatement(
            ebit=50.0, enterprise_value=500.0, market_cap=500.0, net_income=40.0,
            net_fixed_assets=25_000_000.0, current_assets=20_000_000.0, current_liabilities=10_000_000.0
        )
    )

    assert chain.passes(valid_company) is True
    assert chain.passes(bank_company) is False
