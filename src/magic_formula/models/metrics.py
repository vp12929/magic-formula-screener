"""
metrics.py
----------
Defines data structures for calculated metrics and ranked stock outputs.

OOP Concept: Value Objects & Separation of Concerns
- We separate the static entity (Company & Financials) from dynamic calculation results
  (MetricScores, RankedCompany).
- This keeps the Company object clean and immutable while allowing different ranking
  strategies to produce independent result sets.
"""

from dataclasses import dataclass
from typing import Optional
from magic_formula.models.company import Company


@dataclass
class MetricScores:
    """Holds calculated valuation & efficiency scores for a company."""
    
    # Strict Greenblatt metrics
    earnings_yield: float           # EBIT / EV
    return_on_capital: float        # EBIT / Capital Employed
    
    # Modern Proxy metrics
    return_on_invested_capital: Optional[float] = None  # ROIC / ROA
    pe_ratio: Optional[float] = None                    # P/E
    ev_to_ebitda: Optional[float] = None                # EV/EBITDA


@dataclass
class RankedCompany:
    """Holds a company alongside its computed rankings."""
    
    company: Company
    scores: MetricScores
    ey_rank: int = 0
    roc_rank: int = 0
    combined_rank: int = 0

    @property
    def ticker(self) -> str:
        return self.company.ticker

    @property
    def name(self) -> str:
        return self.company.name

    @property
    def sector(self) -> str:
        return self.company.sector

    @property
    def market_cap(self) -> float:
        return self.company.market_cap

    def __lt__(self, other: "RankedCompany") -> bool:
        """
        Operator Overloading: __lt__ (Less Than).
        Allows Python's built-in `sorted()` or list.sort() to naturally order
        ranked companies by their combined rank (lower rank number is better).
        """
        if not isinstance(other, RankedCompany):
            return NotImplemented
        return self.combined_rank < other.combined_rank
