"""
strict.py
---------
Concrete implementation of Joel Greenblatt's original Magic Formula strategy.

OOP Concept: Concrete Subclasses & Inheritance
- Implements `BaseRankingStrategy` by fulfilling the abstract contract.
- Encapsulates Greenblatt's original formulas:
  1. Earnings Yield = EBIT / Enterprise Value
  2. Return on Capital = EBIT / (Net Working Capital + Net Fixed Assets)
"""

from magic_formula.models.company import Company
from magic_formula.models.metrics import MetricScores
from magic_formula.strategies.base import BaseRankingStrategy


class StrictMagicFormulaStrategy(BaseRankingStrategy):
    """
    Joel Greenblatt's exact Magic Formula ranking strategy.
    
    Value Metric: EBIT / Enterprise Value
    Quality Metric: EBIT / (Net Fixed Assets + Net Working Capital)
    """

    @property
    def name(self) -> str:
        return "Strict Magic Formula (Greenblatt Original)"

    def calculate_scores(self, company: Company) -> MetricScores:
        if not company.financials:
            raise ValueError(f"Company {company.ticker} has no financial data.")

        fin = company.financials
        return MetricScores(
            earnings_yield=fin.earnings_yield,
            return_on_capital=fin.return_on_capital,
            return_on_invested_capital=fin.return_on_assets,
            pe_ratio=fin.pe_ratio,
            ev_to_ebitda=fin.ev_to_ebitda,
        )
