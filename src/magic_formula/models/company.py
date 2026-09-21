"""
company.py
----------
Defines the Company class.

OOP Concept: Object Composition & Domain Modeling
- A Company *has-a* FinancialStatement (Composition).
- Instead of using loose tuples or dictionaries like `{"ticker": "AAPL", "ebit": ...}`,
  a Company object models the complete real-world entity with strong typing,
  readable representations, and self-contained behavior.
"""

from dataclasses import dataclass, field
from typing import Optional
from magic_formula.models.financials import FinancialStatement


@dataclass
class Company:
    """Represents a publicly traded company on a stock exchange."""
    
    ticker: str
    name: str
    sector: str
    industry: str = "Unknown"
    market_cap: float = 0.0
    financials: Optional[FinancialStatement] = None

    def __post_init__(self):
        """Clean and normalize attributes upon creation."""
        self.ticker = self.ticker.upper().strip()
        self.name = self.name.strip()
        self.sector = self.sector.strip()
        # If financials are present, synchronize market cap
        if self.financials and self.market_cap == 0.0:
            self.market_cap = self.financials.market_cap

    @property
    def has_financials(self) -> bool:
        """Returns True if financial statement data has been loaded."""
        return self.financials is not None

    def is_in_sector(self, *sectors: str) -> bool:
        """Convenience method to check if the company belongs to any given sector."""
        current_sector_lower = self.sector.lower()
        return any(s.lower() in current_sector_lower for s in sectors)

    def __repr__(self) -> str:
        return f"Company(ticker='{self.ticker}', name='{self.name}', sector='{self.sector}', market_cap=${self.market_cap:,.0f})"

    def __str__(self) -> str:
        return f"{self.ticker} ({self.name}) - {self.sector}"
