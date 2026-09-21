"""
csv_reporter.py
---------------
CSV file report generator.

OOP Concept: Polymorphic File Exporter
- Writes screening outputs to structured CSV files for Excel/analysis.
"""

import csv
from typing import List, Dict, Any, Optional
from pathlib import Path
from magic_formula.models.metrics import RankedCompany
from magic_formula.screener import ScreeningSummary
from magic_formula.reporters.base import BaseReporter


class CsvReporter(BaseReporter):
    """Exports screening results to CSV files."""

    def __init__(self, output_path: str = "magic_formula_results.csv"):
        self.output_path = Path(output_path)

    def report_ranked(self, results: List[RankedCompany], summary: Optional[ScreeningSummary] = None) -> None:
        with open(self.output_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Combined_Rank", "Ticker", "Company_Name", "Sector", "Industry",
                "Market_Cap", "Earnings_Yield_Pct", "EY_Rank", "Return_On_Capital_Pct", "ROC_Rank", "PE_Ratio"
            ])
            for r in results:
                writer.writerow([
                    r.combined_rank,
                    r.ticker,
                    r.name,
                    r.sector,
                    r.company.industry,
                    r.market_cap,
                    round(r.scores.earnings_yield * 100, 2),
                    r.ey_rank,
                    round(r.scores.return_on_capital * 100, 2),
                    r.roc_rank,
                    round(r.scores.pe_ratio, 2) if r.scores.pe_ratio else "N/A"
                ])
        print(f"Results exported successfully to: {self.output_path.resolve()}")

    def report_comparison(self, comparison_data: Dict[str, Any]) -> None:
        strict_top: List[RankedCompany] = comparison_data.get("strict_top_n", [])
        proxy_ranks = comparison_data.get("proxy_ranks", {})

        comp_path = self.output_path.with_name("magic_formula_comparison.csv")
        with open(comp_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Strict_Rank", "Ticker", "Company_Name", "Sector",
                "Greenblatt_EY_Pct", "Greenblatt_ROC_Pct", "Proxy_Rank"
            ])
            for strict_rank, r in enumerate(strict_top, 1):
                proxy_info = proxy_ranks.get(r.ticker)
                proxy_rank_num = proxy_info[0] if proxy_info else "N/A"
                writer.writerow([
                    strict_rank,
                    r.ticker,
                    r.name,
                    r.sector,
                    round(r.scores.earnings_yield * 100, 2),
                    round(r.scores.return_on_capital * 100, 2),
                    proxy_rank_num
                ])
        print(f"Comparison exported successfully to: {comp_path.resolve()}")
