"""
base.py
-------
Defines the abstract interface for data providers.

OOP Concept: Dependency Inversion Principle (DIP)
- High-level modules (the Screener) should not depend on low-level modules
  (like a specific Yahoo Finance scraping library). Both should depend on abstractions (BaseDataProvider).
- This allows us to easily test our entire system offline with MockDataProvider,
  or swap to other financial data APIs (like AlphaVantage, Bloomberg, FMP) in the future.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from magic_formula.models.company import Company


class BaseDataProvider(ABC):
    """Abstract Base Class for financial market data providers."""

    @abstractmethod
    def fetch_company(self, ticker: str) -> Optional[Company]:
        """
        Fetches metadata and financial statement data for a single ticker.
        Returns None if data could not be retrieved.
        """
        pass

    def fetch_universe(self, tickers: List[str]) -> List[Company]:
        """
        Fetches financial data for a list of tickers.
        Default implementation iterates over fetch_company and ignores failed tickers.
        """
        companies: List[Company] = []
        for ticker in tickers:
            company = self.fetch_company(ticker)
            if company is not None and company.has_financials:
                companies.append(company)
        return companies
