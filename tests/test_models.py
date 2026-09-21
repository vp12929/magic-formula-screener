"""
Unit tests for data models (FinancialStatement, Company, RankedCompany).
"""

import pytest
from magic_formula.models.financials import FinancialStatement
from magic_formula.models.company import Company
from magic_formula.models.metrics import MetricScores, RankedCompany


def test_financial_statement_properties():
    # Setup test financial data:
    # EBIT = 100, EV = 1000 => EY = 10% (0.10)
    # Fixed Assets = 300, Current Assets = 200, Current Liab = 100 => Working Capital = 100
    # Tangible Capital Employed = 300 + 100 = 400 => ROC = 100 / 400 = 25% (0.25)
    fin = FinancialStatement(
        ebit=100.0,
        enterprise_value=1000.0,
        market_cap=900.0,
        net_income=70.0,
        current_assets=200.0,
        current_liabilities=100.0,
        net_fixed_assets=300.0,
        total_assets=600.0,
        total_equity=500.0,
    )
    
    assert fin.net_working_capital == 100.0
    assert fin.capital_employed == 400.0
    assert pytest.approx(fin.earnings_yield, 0.001) == 0.10
    assert pytest.approx(fin.return_on_capital, 0.001) == 0.25
    assert pytest.approx(fin.return_on_assets, 0.001) == 70.0 / 600.0
    assert pytest.approx(fin.pe_ratio, 0.001) == 900.0 / 70.0


def test_company_creation_and_methods():
    fin = FinancialStatement(
        ebit=50.0,
        enterprise_value=500.0,
        market_cap=450.0,
        net_income=35.0
    )
    company = Company(
        ticker="msft ",
        name="Microsoft Corp",
        sector="Technology",
        financials=fin
    )
    
    # Check post-init normalization
    assert company.ticker == "MSFT"
    assert company.has_financials is True
    assert company.market_cap == 450.0
    assert company.is_in_sector("Technology") is True
    assert company.is_in_sector("Financials", "Utilities") is False


def test_ranked_company_comparison():
    c1 = Company(ticker="AAA", name="Alpha Inc", sector="Tech", market_cap=100)
    c2 = Company(ticker="BBB", name="Beta Inc", sector="Healthcare", market_cap=200)
    
    s1 = MetricScores(earnings_yield=0.15, return_on_capital=0.30)
    s2 = MetricScores(earnings_yield=0.10, return_on_capital=0.20)
    
    # Combined rank: lower is better (Rank 1 + Rank 2 = 3 vs Rank 5 + Rank 5 = 10)
    r1 = RankedCompany(company=c1, scores=s1, combined_rank=3)
    r2 = RankedCompany(company=c2, scores=s2, combined_rank=10)
    
    # Test operator overloading (__lt__)
    assert r1 < r2
    sorted_list = sorted([r2, r1])
    assert sorted_list[0].ticker == "AAA"
