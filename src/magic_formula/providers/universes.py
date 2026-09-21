"""
universes.py
------------
Provides universe lists of stock tickers (S&P 500, Dow 30, S&P 1500 subset).

OOP Concept: Utility Modules & Fallback Resilience
- Encapsulates stock universe fetching with safe offline fallbacks.
"""

from typing import List
import requests
import pandas as pd


# Default curated universe of top liquid US stocks across major sectors
CURATED_UNIVERSE = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "UNH", "JNJ", "V",
    "PG", "HD", "COST", "ABBV", "MRK", "NKE", "TXN", "LOW", "PFE", "BMY",
    "VZ", "T", "INTC", "CSCO", "PEP", "KO", "MCD", "WMT", "DIS", "ADBE",
    "CRM", "QCOM", "AMD", "HON", "CAT", "GE", "BA", "MMM", "LMT", "DE",
    # Financials & Utilities (for testing filter exclusion)
    "JPM", "BAC", "WFC", "C", "GS", "MS", "NEE", "DUK", "SO", "D"
]


class UniverseLoader:
    """Loads ticker symbol lists for screening universes."""

    @staticmethod
    def get_sp500_tickers() -> List[str]:
        """
        Attempts to fetch the live S&P 500 list from Wikipedia.
        Falls back to curated list if network fails.
        """
        try:
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=5)
            tables = pd.read_html(response.text)
            sp500_df = tables[0]
            tickers = sp500_df["Symbol"].str.replace(".", "-", regex=False).tolist()
            return tickers
        except Exception:
            return CURATED_UNIVERSE

    @staticmethod
    def get_curated_tickers(limit: int = 50) -> List[str]:
        """Returns a stable, curated universe of diversified tickers."""
        return CURATED_UNIVERSE[:limit]
