"""
proxy.py
--------
Concrete implementation of modern proxy/standard financial ratios for Magic Formula screening.

OOP Concept: Polymorphism in Action
- Swappable alternative to StrictMagicFormulaStrategy with the exact same interface.
- Uses conventional metrics:
  1. Value: 1 / (P/E Ratio) = Net Income / Market Cap
  2. Quality: Return on Assets (ROA) = Net Income / Total Assets
"""

from magic_formula.models.company import Company
from magic_formula.models.metrics import MetricScores
from magic_formula.strategies.base import BaseRankingStrategy


class ProxyRankingStrategy(BaseRankingStrategy):
    """
    Modern proxy ranking strategy using standard GAAP/IFRS ratios.
    
    Value Metric: Earnings Yield Proxy (Net Income / Market Cap = 1/PE)
    Quality Metric: Return on Assets (Net Income / Total Assets)
    """

    @property
    def name(self) -> str:
        return "Proxy Magic Formula (ROA & 1/PE Ratio)"

    def calculate_scores(self, company: Company) -> MetricScores:
        if not company.financials:
            raise ValueError(f"Company {company.ticker} has no financial data.")

        fin = company.financials
        # Earnings Yield proxy: Net Income / Market Cap
        ey_proxy = (fin.net_income / fin.market_cap) if fin.market_cap > 0 else 0.0
        # Quality proxy: Return on Assets
        roc_proxy = fin.return_on_assets

        return MetricScores(
            earnings_yield=ey_proxy,
            return_on_capital=roc_proxy,
            return_on_invested_capital=fin.return_on_assets,
            pe_ratio=fin.pe_ratio,
            ev_to_ebitda=fin.ev_to_ebitda,
        )
