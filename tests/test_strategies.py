"""
Unit tests for Ranking Strategies (Strict vs Proxy).
"""

import pytest
from magic_formula.models.financials import FinancialStatement
from magic_formula.models.company import Company
from magic_formula.strategies.strict import StrictMagicFormulaStrategy
from magic_formula.strategies.proxy import ProxyRankingStrategy


@pytest.fixture
def sample_companies():
    # Company A: Great ROC (High EBIT on low capital), moderate EY
    # EBIT = 100, EV = 1000 => EY = 10%
    # Fixed = 100, NWC = 100 => Capital = 200 => ROC = 100 / 200 = 50%
    comp_a = Company(
        ticker="COMP_A",
        name="Company A Quality",
        sector="Technology",
        financials=FinancialStatement(
            ebit=100.0,
            enterprise_value=1000.0,
            market_cap=900.0,
            net_income=70.0,
            current_assets=200.0,
            current_liabilities=100.0,
            net_fixed_assets=100.0,
            total_assets=400.0,
        )
    )

    # Company B: Very Cheap (High EY), moderate ROC
    # EBIT = 200, EV = 1000 => EY = 20%
    # Fixed = 500, NWC = 500 => Capital = 1000 => ROC = 200 / 1000 = 20%
    comp_b = Company(
        ticker="COMP_B",
        name="Company B Cheap",
        sector="Healthcare",
        financials=FinancialStatement(
            ebit=200.0,
            enterprise_value=1000.0,
            market_cap=800.0,
            net_income=140.0,
            current_assets=700.0,
            current_liabilities=200.0,
            net_fixed_assets=500.0,
            total_assets=1500.0,
        )
    )

    # Company C: Mediocre on both
    # EBIT = 30, EV = 1000 => EY = 3%
    # Fixed = 300, NWC = 300 => Capital = 600 => ROC = 30 / 600 = 5%
    comp_c = Company(
        ticker="COMP_C",
        name="Company C Mediocre",
        sector="Consumer Discretionary",
        financials=FinancialStatement(
            ebit=30.0,
            enterprise_value=1000.0,
            market_cap=950.0,
            net_income=20.0,
            current_assets=400.0,
            current_liabilities=100.0,
            net_fixed_assets=300.0,
            total_assets=800.0,
        )
    )

    return [comp_a, comp_b, comp_c]


def test_strict_magic_formula_ranking(sample_companies):
    strategy = StrictMagicFormulaStrategy()
    ranked = strategy.rank_companies(sample_companies)

    assert len(ranked) == 3
    # Both Comp A and Comp B will tie on combined rank (1+2=3), Comp C is worst (3+3=6)
    assert ranked[2].ticker == "COMP_C"
    assert ranked[2].combined_rank == 6


def test_polymorphism_strategy_swap(sample_companies):
    strict_strat = StrictMagicFormulaStrategy()
    proxy_strat = ProxyRankingStrategy()

    strict_ranked = strict_strat.rank_companies(sample_companies)
    proxy_ranked = proxy_strat.rank_companies(sample_companies)

    assert strict_strat.name.startswith("Strict")
    assert proxy_strat.name.startswith("Proxy")
    assert len(strict_ranked) == len(proxy_ranked) == 3
