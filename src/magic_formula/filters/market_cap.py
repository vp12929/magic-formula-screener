"""
market_cap.py
-------------
Market capitalization filter supporting min/max boundaries and market cap tier presets.

OOP Concepts:
- Configurable Rule Objects & Factory Method Pattern (`from_tier`)
- Input normalization: Handles numeric inputs or human-friendly strings like "50M", "2B".
"""

from typing import Optional, Union, Dict, Tuple
from magic_formula.models.company import Company
from magic_formula.filters.base import BaseFilter
from magic_formula.filters.helpers import parse_currency


class MarketCapFilter(BaseFilter):
    """Filters companies by market capitalization boundaries and tiers."""

    # Standard financial market cap definitions
    CAP_TIERS: Dict[str, Tuple[float, Optional[float]]] = {
        "all": (50_000_000.0, None),                # Greenblatt original threshold ($50M+)
        "micro": (50_000_000.0, 300_000_000.0),     # $50M - $300M
        "small": (300_000_000.0, 2_000_000_000.0),   # $300M - $2B
        "mid": (2_000_000_000.0, 10_000_000_000.0),  # $2B - $10B
        "large": (10_000_000_000.0, None),           # $10B+ (Large & Mega cap)
    }

    def __init__(
        self,
        min_market_cap: Union[float, str] = 50_000_000.0,
        max_market_cap: Optional[Union[float, str]] = None,
    ):
        self.min_market_cap = parse_currency(min_market_cap) if min_market_cap is not None else 0.0
        self.max_market_cap = parse_currency(max_market_cap) if max_market_cap is not None else None

        if self.max_market_cap is not None and self.min_market_cap > self.max_market_cap:
            raise ValueError(
                f"min_market_cap (${self.min_market_cap:,.0f}) cannot exceed max_market_cap (${self.max_market_cap:,.0f})"
            )

    @classmethod
    def from_tier(cls, tier: str) -> "MarketCapFilter":
        """
        Factory Method: Creates a MarketCapFilter for a predefined tier:
        - 'micro': $50M - $300M
        - 'small': $300M - $2B
        - 'mid': $2B - $10B
        - 'large': $10B+
        - 'all': $50M+
        """
        tier_clean = tier.lower().strip()
        if tier_clean not in cls.CAP_TIERS:
            valid_tiers = ", ".join(cls.CAP_TIERS.keys())
            raise ValueError(f"Unknown tier '{tier}'. Available tiers: {valid_tiers}")

        min_cap, max_cap = cls.CAP_TIERS[tier_clean]
        return cls(min_market_cap=min_cap, max_market_cap=max_cap)

    @property
    def name(self) -> str:
        if self.max_market_cap:
            return f"Market Cap Filter (${self._fmt(self.min_market_cap)} - ${self._fmt(self.max_market_cap)})"
        return f"Market Cap Filter (Min: ${self._fmt(self.min_market_cap)})"

    def passes(self, company: Company) -> bool:
        if company.market_cap < self.min_market_cap:
            return False
        if self.max_market_cap is not None and company.market_cap > self.max_market_cap:
            return False
        return True

    def rejection_reason(self, company: Company) -> str:
        if company.market_cap < self.min_market_cap:
            return f"Market Cap ${self._fmt(company.market_cap)} is below min required ${self._fmt(self.min_market_cap)}"
        return f"Market Cap ${self._fmt(company.market_cap)} exceeds max allowed ${self._fmt(self.max_market_cap)}"

    @staticmethod
    def _fmt(val: Optional[float]) -> str:
        if val is None:
            return "None"
        if val >= 1e9:
            return f"{val / 1e9:,.1f}B"
        if val >= 1e6:
            return f"{val / 1e6:,.1f}M"
        return f"{val:,.0f}"
