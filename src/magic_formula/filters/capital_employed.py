"""
capital_employed.py
-------------------
Filter for Tangible Capital Employed.

OOP Concept: Business Rule Encapsulation
- Joel Greenblatt defines Return on Capital as:
      ROC = EBIT / (Net Working Capital + Net Fixed Assets)
- The denominator is the Tangible Capital Employed.
- If a company operates with near-zero or negligible physical capital, its ROC mathematically
  explodes into thousands of percent, distorting the rankings.
- This filter ensures that only companies with real, measurable operating capital are qualified.
"""

from typing import Union
from magic_formula.models.company import Company
from magic_formula.filters.base import BaseFilter
from magic_formula.filters.helpers import parse_currency


class MinCapitalEmployedFilter(BaseFilter):
    """
    Filters out companies whose Tangible Capital Employed is below a required minimum threshold.
    """

    def __init__(self, min_capital: Union[float, str] = 10_000_000.0):
        """
        :param min_capital: Minimum tangible capital in USD (e.g. 10000000 or "10M"). Default: $10M.
        """
        self.min_capital: float = parse_currency(min_capital)

    @property
    def name(self) -> str:
        return f"Min Capital Employed Filter (${self._fmt(self.min_capital)})"

    def passes(self, company: Company) -> bool:
        if not company.financials:
            return False

        # Tangible capital employed = Net Fixed Assets + Net Working Capital
        cap_employed = company.financials.capital_employed
        return cap_employed >= self.min_capital

    def rejection_reason(self, company: Company) -> str:
        if not company.financials:
            return "No financial statement data available to compute capital employed"
        actual = company.financials.capital_employed
        return (
            f"Tangible Capital Employed (${self._fmt(actual)}) is below "
            f"minimum required ${self._fmt(self.min_capital)}"
        )

    @staticmethod
    def _fmt(val: float) -> str:
        if val >= 1e9:
            return f"{val / 1e9:,.1f}B"
        if val >= 1e6:
            return f"{val / 1e6:,.1f}M"
        return f"{val:,.0f}"
