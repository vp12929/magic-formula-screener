"""
screener.py
-----------
Defines the MagicFormulaScreener coordinator engine and comparison utilities.

OOP Concept: Orchestration, High Cohesion, Low Coupling
- The screener orchestrates the entire workflow:
  1. Fetch raw data from `BaseDataProvider`
  2. Filter out non-compliant companies using `FilterChain`
  3. Score and rank qualifying companies using `BaseRankingStrategy`
- Supports comparing multiple ranking strategies side-by-side on the exact same universe.
"""

from typing import List, Optional, Dict, Tuple
from magic_formula.models.company import Company
from magic_formula.models.metrics import RankedCompany
from magic_formula.providers.base import BaseDataProvider
from magic_formula.filters.chain import FilterChain
from magic_formula.strategies.base import BaseRankingStrategy
from magic_formula.strategies.strict import StrictMagicFormulaStrategy
from magic_formula.strategies.proxy import ProxyRankingStrategy


class ScreeningSummary:
    """Holds operational metrics about a screening run."""
    def __init__(self, total_fetched: int, passed_filters: int, ranked_count: int):
        self.total_fetched = total_fetched
        self.passed_filters = passed_filters
        self.ranked_count = ranked_count
        self.rejected_count = total_fetched - passed_filters


class MagicFormulaScreener:
    """Core screener orchestrator."""

    def __init__(
        self,
        data_provider: BaseDataProvider,
        ranking_strategy: Optional[BaseRankingStrategy] = None,
        filter_chain: Optional[FilterChain] = None,
    ):
        self.data_provider = data_provider
        self.strategy = ranking_strategy or StrictMagicFormulaStrategy()
        self.filter_chain = filter_chain or FilterChain.default_magic_formula_chain()

    def run_screen(
        self,
        tickers: List[str],
        top_n: int = 20
    ) -> Tuple[List[RankedCompany], ScreeningSummary]:
        """
        Executes the full screening pipeline:
        1. Fetches financial data for all given tickers.
        2. Filters out companies that fail sector, market cap, or profitability rules.
        3. Ranks remaining companies according to the chosen strategy.
        4. Returns top_n ranked companies and the run summary.
        """
        # 1. Fetch universe data
        all_companies = self.data_provider.fetch_universe(tickers)

        # 2. Filter companies
        filtered_companies: List[Company] = [
            comp for comp in all_companies if self.filter_chain.passes(comp)
        ]

        # 3. Score and rank
        ranked = self.strategy.rank_companies(filtered_companies)

        # 4. Limit to top N
        top_results = ranked[:top_n]
        summary = ScreeningSummary(
            total_fetched=len(all_companies),
            passed_filters=len(filtered_companies),
            ranked_count=len(top_results),
        )

        return top_results, summary

    def compare_strict_vs_proxy(
        self,
        tickers: List[str],
        top_n: int = 20
    ) -> Dict[str, any]:
        """
        Runs both the Strict Greenblatt strategy and the Proxy strategy
        on the exact same qualifying stock universe and generates comparison metrics.
        """
        # Fetch and filter once
        all_companies = self.data_provider.fetch_universe(tickers)
        qualifying = [c for c in all_companies if self.filter_chain.passes(c)]

        # Run both strategies
        strict_strategy = StrictMagicFormulaStrategy()
        proxy_strategy = ProxyRankingStrategy()

        strict_ranked = strict_strategy.rank_companies(qualifying)
        proxy_ranked = proxy_strategy.rank_companies(qualifying)

        # Build quick ticker -> rank lookup maps
        strict_ranks = {r.ticker: (idx + 1, r) for idx, r in enumerate(strict_ranked)}
        proxy_ranks = {r.ticker: (idx + 1, r) for idx, r in enumerate(proxy_ranked)}

        return {
            "total_qualifying": len(qualifying),
            "strict_top_n": strict_ranked[:top_n],
            "proxy_top_n": proxy_ranked[:top_n],
            "strict_ranks": strict_ranks,
            "proxy_ranks": proxy_ranks,
        }
