"""
yahoo.py
--------
Live data provider using yfinance.

OOP Concept: Encapsulating External I/O & API Mapping
- Wraps complex raw nested financial data from yfinance into clean domain objects.
- Isolates API changes or failures so the rest of the application remains untouched.
"""

from typing import Optional, Dict
import yfinance as yf
from magic_formula.models.company import Company
from magic_formula.models.financials import FinancialStatement
from magic_formula.providers.base import BaseDataProvider


class YahooFinanceProvider(BaseDataProvider):
    """Fetches real-time / latest annual fundamental data via Yahoo Finance."""

    def __init__(self, cache_data: bool = True):
        self.cache_data = cache_data
        self._cache: Dict[str, Optional[Company]] = {}

    def fetch_company(self, ticker: str) -> Optional[Company]:
        symbol = ticker.upper().strip()

        if self.cache_data and symbol in self._cache:
            return self._cache[symbol]

        try:
            ytick = yf.Ticker(symbol)
            info = ytick.info or {}

            # Basic metadata
            name = info.get("shortName") or info.get("longName") or symbol
            sector = info.get("sector") or "Unknown"
            industry = info.get("industry") or "Unknown"
            market_cap = float(info.get("marketCap") or ytick.fast_info.get("market_cap") or 0.0)
            enterprise_value = float(info.get("enterpriseValue") or market_cap)

            # Financials & Balance Sheet DataFrames
            income_stmt = ytick.financials
            balance_sheet = ytick.balance_sheet

            ebit = self._extract_field(income_stmt, ["Operating Income", "EBIT", "Total Operating Income As Reported"])
            net_income = self._extract_field(income_stmt, ["Net Income", "Net Income Common Stockholders"])
            ebitda = self._extract_field(income_stmt, ["EBITDA", "Normalized EBITDA"])

            curr_assets = self._extract_field(balance_sheet, ["Current Assets", "Total Current Assets"])
            curr_liab = self._extract_field(balance_sheet, ["Current Liabilities", "Total Current Liabilities"])
            net_ppe = self._extract_field(balance_sheet, ["Net PPE", "Properties", "Net Property Plant And Equipment"])
            tot_assets = self._extract_field(balance_sheet, ["Total Assets"])
            tot_debt = self._extract_field(balance_sheet, ["Total Debt", "Long Term Debt And Capital Lease Obligation"])
            tot_equity = self._extract_field(balance_sheet, ["Stockholders Equity", "Total Stockholder Equity"])
            cash = self._extract_field(balance_sheet, ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"])

            # Fallback if EBIT not explicitly in table
            if ebit == 0.0:
                ebit = float(info.get("operatingCashflow") or net_income or 0.0)

            fin = FinancialStatement(
                ebit=ebit,
                enterprise_value=enterprise_value,
                market_cap=market_cap,
                net_income=net_income,
                ebitda=ebitda if ebitda != 0.0 else None,
                current_assets=curr_assets,
                current_liabilities=curr_liab,
                net_fixed_assets=net_ppe,
                total_assets=tot_assets,
                total_debt=tot_debt,
                total_equity=tot_equity,
                cash_and_equivalents=cash,
            )

            company = Company(
                ticker=symbol,
                name=name,
                sector=sector,
                industry=industry,
                market_cap=market_cap,
                financials=fin,
            )

            if self.cache_data:
                self._cache[symbol] = company

            return company

        except Exception as err:
            # Silently handle unretrievable symbols
            if self.cache_data:
                self._cache[symbol] = None
            return None

    def _extract_field(self, df, field_names: list) -> float:
        """Extracts the most recent valid annual figure from a yfinance DataFrame."""
        if df is None or df.empty:
            return 0.0
        
        for name in field_names:
            if name in df.index:
                series = df.loc[name].dropna()
                if not series.empty:
                    val = float(series.iloc[0])
                    if val != 0.0:
                        return val
        return 0.0
