"""
market_cap.py
-------------
Market capitalization filter (Filters out illiquid micro-caps).

OOP Concept: Configurable Rule Objects
- Parameterized with `min_market_cap` and optional `max_market_cap`.
"""

from typing import Optional
from magic_formula.models.company import Company
from magic_formula.filters.base import BaseFilter


class MarketCapFilter(BaseFilter):
    """Filters companies by market capitalization boundaries."""

    def __init__(self, min_market_cap: float = 50_000_000.0, max_market_cap: Optional[float] = None):
        self.min_market_cap = min_market_cap
        self.max_market_cap = max_market_cap

    @property
    def name(self) -> str:
        return f"Market Cap Filter (Min: ${self.min_market_cap:,.0f})"

    def passes(self, company: Company) -> bool:
        if company.market_cap < self.min_market_cap:
            return False
        if self.max_market_cap is not None and company.market_cap > self.max_market_cap:
            return False
        return True

    def rejection_reason(self, company: Company) -> str:
        return f"Market Cap ${company.market_cap:,.0f} is outside required bounds (${self.min_market_cap:,.0f})"
