"""
console.py
----------
Console report generator with formatted ASCII tables.

OOP Concept: Robust cross-platform presentation
- Formats tabular results cleanly across all Windows / Linux / macOS terminals.
"""

from typing import List, Dict, Any, Optional
from tabulate import tabulate
from magic_formula.models.metrics import RankedCompany
from magic_formula.screener import ScreeningSummary
from magic_formula.reporters.base import BaseReporter


class ConsoleReporter(BaseReporter):
    """Prints formatted tables directly to the terminal."""

    def report_ranked(self, results: List[RankedCompany], summary: Optional[ScreeningSummary] = None) -> None:
        if summary:
            print("\n" + "=" * 85)
            print(" SCREENING SUMMARY")
            print(f" Total Analyzed: {summary.total_fetched} | Passed Filters: {summary.passed_filters} | Filtered Out: {summary.rejected_count}")
            print("=" * 85)

        if not results:
            print("No companies matched the screening criteria.")
            return

        table_data = []
        for r in results:
            mcap_str = f"${r.market_cap / 1e9:,.1f}B" if r.market_cap >= 1e9 else f"${r.market_cap / 1e6:,.1f}M"
            ey_pct = f"{r.scores.earnings_yield * 100:.1f}%"
            roc_pct = f"{r.scores.return_on_capital * 100:.1f}%"
            pe_str = f"{r.scores.pe_ratio:.1f}" if r.scores.pe_ratio else "N/A"

            table_data.append([
                r.combined_rank,
                r.ticker,
                r.name[:22],
                r.sector[:18],
                mcap_str,
                ey_pct,
                r.ey_rank,
                roc_pct,
                r.roc_rank,
                pe_str,
            ])

        headers = [
            "Comb. Rank", "Ticker", "Company Name", "Sector",
            "Mkt Cap", "EY (EBIT/EV)", "EY Rank", "ROC (Capital)", "ROC Rank", "P/E"
        ]

        # Use "grid" or "simple" for clean, universal cross-platform ASCII rendering
        print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))

    def report_comparison(self, comparison_data: Dict[str, Any]) -> None:
        strict_top: List[RankedCompany] = comparison_data.get("strict_top_n", [])
        proxy_ranks = comparison_data.get("proxy_ranks", {})

        print("\n" + "=" * 95)
        print(" COMPARISON ANALYSIS: Strict Magic Formula (Greenblatt) vs. Modern Proxy (ROA & 1/PE)")
        print(f" Total qualifying companies evaluated: {comparison_data.get('total_qualifying', 0)}")
        print("=" * 95)

        table_data = []
        for strict_rank, r in enumerate(strict_top, 1):
            ticker = r.ticker
            # Lookup where this company landed in the proxy ranking
            proxy_info = proxy_ranks.get(ticker)
            proxy_rank_num = proxy_info[0] if proxy_info else "N/A"
            
            diff_str = ""
            if isinstance(proxy_rank_num, int):
                diff = strict_rank - proxy_rank_num
                if diff > 0:
                    diff_str = f"+{diff} (Proxy higher)"
                elif diff < 0:
                    diff_str = f"{diff} (Strict higher)"
                else:
                    diff_str = "Identical (=)"

            ey_pct = f"{r.scores.earnings_yield * 100:.1f}%"
            roc_pct = f"{r.scores.return_on_capital * 100:.1f}%"

            table_data.append([
                strict_rank,
                ticker,
                r.name[:20],
                r.sector[:16],
                ey_pct,
                roc_pct,
                proxy_rank_num,
                diff_str
            ])

        headers = [
            "Strict Rank", "Ticker", "Company", "Sector",
            "Greenblatt EY", "Greenblatt ROC", "Proxy Rank", "Rank Difference"
        ]

        print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
