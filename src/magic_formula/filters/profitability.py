"""
profitability.py
----------------
Profitability filter (Excludes companies with negative operating income / EBIT).

OOP Concept: Single Responsibility Filter
- Ensures only economically viable, profitable operating businesses are ranked.
"""

from magic_formula.models.company import Company
from magic_formula.filters.base import BaseFilter


class PositiveEarningsFilter(BaseFilter):
    """Filters out companies with negative or zero operating earnings (EBIT <= 0)."""

    @property
    def name(self) -> str:
        return "Positive Operating Earnings Filter (EBIT > 0)"

    def passes(self, company: Company) -> bool:
        if not company.financials:
            return False
        return company.financials.ebit > 0.0

    def rejection_reason(self, company: Company) -> str:
        return "Operating income (EBIT) is negative or zero"
