"""
chain.py
--------
Composite filter chain.

OOP Concept: Composite Pattern & Filter Pipeline
- `FilterChain` itself acts as a filter (`BaseFilter`), containing a list of sub-filters.
- Applies all filters in sequence, returning False as soon as any filter rejects the company.
"""

from typing import List, Tuple, Optional, Union
from magic_formula.models.company import Company
from magic_formula.filters.base import BaseFilter
from magic_formula.filters.sector import SectorFilter
from magic_formula.filters.market_cap import MarketCapFilter
from magic_formula.filters.profitability import PositiveEarningsFilter
from magic_formula.filters.capital_employed import MinCapitalEmployedFilter


class FilterChain(BaseFilter):
    """Executes a pipeline of filters sequentially on a company."""

    def __init__(self, filters: List[BaseFilter] = None):
        self.filters = filters if filters is not None else []

    @classmethod
    def default_magic_formula_chain(
        cls,
        min_market_cap: Union[float, str] = 50_000_000.0,
        max_market_cap: Optional[Union[float, str]] = None,
        min_capital_employed: Union[float, str] = 10_000_000.0,
        cap_tier: Optional[str] = None,
    ) -> "FilterChain":
        """
        Factory Method: Returns the standard Greenblatt filter pipeline
        with configurable market cap boundaries/tier and minimum operating capital.
        """
        if cap_tier:
            mcap_filter = MarketCapFilter.from_tier(cap_tier)
        else:
            mcap_filter = MarketCapFilter(min_market_cap=min_market_cap, max_market_cap=max_market_cap)

        filters = [
            SectorFilter(),
            mcap_filter,
            PositiveEarningsFilter(),
            MinCapitalEmployedFilter(min_capital=min_capital_employed),
        ]
        return cls(filters)

    @property
    def name(self) -> str:
        return f"FilterChain({len(self.filters)} active rules)"

    def add_filter(self, filter_rule: BaseFilter) -> None:
        """Adds a new filter to the pipeline dynamically."""
        self.filters.append(filter_rule)

    def passes(self, company: Company) -> bool:
        """Returns True only if the company satisfies every filter in the chain."""
        return all(f.passes(company) for f in self.filters)

    def evaluate(self, company: Company) -> Tuple[bool, List[str]]:
        """
        Evaluates a company against all filters, returning (passed, list_of_rejection_reasons).
        Useful for detailed debugging and reporting.
        """
        reasons = []
        for f in self.filters:
            if not f.passes(company):
                reasons.append(f.rejection_reason(company))
        return (len(reasons) == 0, reasons)
