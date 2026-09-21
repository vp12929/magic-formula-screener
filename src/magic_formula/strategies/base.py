"""
base.py
-------
Defines the abstract base strategy for metric calculations.

OOP Concept: Abstract Base Classes (ABC) & Strategy Pattern
- `abc.ABC` defines an "interface" or abstract contract in Python.
- Any subclass MUST implement `@abstractmethod` methods, otherwise Python will
  raise a TypeError when trying to instantiate it.
- This enforces consistency across all calculation formulas without hardcoding
  `if/else` logic throughout the application.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
from magic_formula.models.company import Company
from magic_formula.models.metrics import MetricScores, RankedCompany


class BaseRankingStrategy(ABC):
    """Abstract Base Class for stock scoring and ranking strategies."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the strategy."""
        pass

    @abstractmethod
    def calculate_scores(self, company: Company) -> MetricScores:
        """
        Calculates valuation and efficiency scores for a single company.
        Must be implemented by concrete strategy subclasses.
        """
        pass

    def rank_companies(self, companies: List[Company]) -> List[RankedCompany]:
        """
        Template Method Pattern:
        Common ranking algorithm shared across all strategies:
        1. Calculate raw scores for all companies.
        2. Rank by Value/Earnings Yield (descending: highest yield = rank 1).
        3. Rank by Quality/Return on Capital (descending: highest ROC = rank 1).
        4. Sum the ranks: Combined Rank = Rank(EY) + Rank(ROC).
        5. Sort by Combined Rank (ascending: lowest sum = best).
        """
        if not companies:
            return []

        # 1. Compute scores for each company
        company_scores: List[Tuple[Company, MetricScores]] = [
            (c, self.calculate_scores(c)) for c in companies if c.has_financials
        ]

        if not company_scores:
            return []

        # 2. Rank by Earnings Yield (highest EY gets rank 1)
        sorted_by_ey = sorted(company_scores, key=lambda item: item[1].earnings_yield, reverse=True)
        ey_ranks = {item[0].ticker: rank + 1 for rank, item in enumerate(sorted_by_ey)}

        # 3. Rank by Return on Capital (highest ROC gets rank 1)
        sorted_by_roc = sorted(company_scores, key=lambda item: item[1].return_on_capital, reverse=True)
        roc_ranks = {item[0].ticker: rank + 1 for rank, item in enumerate(sorted_by_roc)}

        # 4. Construct RankedCompany objects with combined ranks
        ranked_list: List[RankedCompany] = []
        for comp, score in company_scores:
            ey_r = ey_ranks[comp.ticker]
            roc_r = roc_ranks[comp.ticker]
            combined = ey_r + roc_r
            ranked_list.append(
                RankedCompany(
                    company=comp,
                    scores=score,
                    ey_rank=ey_r,
                    roc_rank=roc_r,
                    combined_rank=combined,
                )
            )

        # 5. Sort by combined rank ascending (e.g., rank 1 + rank 1 = 2 is best)
        ranked_list.sort()
        return ranked_list
