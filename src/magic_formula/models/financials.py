"""
financials.py
-------------
Defines the FinancialStatement class.

OOP Concept: Encapsulation & Properties
- We encapsulate raw financial figures (EBIT, Assets, Liabilities, EV) inside one class.
- Instead of computing metrics across separate loose functions, we define @property
  getters directly on the object. This ensures data and the operations on that data
  live together in one cohesive unit.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class FinancialStatement:
    """Represents core financial figures and ratios for a company."""
    
    # Core Income Statement & Valuation figures
    ebit: float                     # Operating income (Earnings Before Interest & Taxes)
    enterprise_value: float         # Market Cap + Total Debt - Cash
    market_cap: float               # Total equity market value
    net_income: float               # Bottom-line profit
    ebitda: Optional[float] = None  # EBIT + Depreciation & Amortization
    
    # Balance Sheet figures for Greenblatt ROC calculation
    current_assets: float = 0.0
    current_liabilities: float = 0.0
    net_fixed_assets: float = 0.0   # Net Property, Plant & Equipment (PPE)
    total_assets: float = 0.0
    total_debt: float = 0.0
    total_equity: float = 0.0
    cash_and_equivalents: float = 0.0

    @property
    def net_working_capital(self) -> float:
        """
        Net Working Capital (NWC) = Current Assets - Current Liabilities.
        Represents the operational liquidity available in the short term.
        """
        return self.current_assets - self.current_liabilities

    @property
    def capital_employed(self) -> float:
        """
        Tangible Capital Employed = Net Fixed Assets + Net Working Capital.
        This is the denominator in Joel Greenblatt's Return on Capital (ROC) formula.
        We ensure it does not return zero or negative values to prevent division errors.
        """
        tangible_capital = self.net_fixed_assets + self.net_working_capital
        return tangible_capital if tangible_capital > 0 else 1.0

    # -------------------------------------------------------------
    # 1. Strict Greenblatt Magic Formula Metrics
    # -------------------------------------------------------------
    @property
    def earnings_yield(self) -> float:
        """
        Earnings Yield = EBIT / Enterprise Value (EV)
        Measures how cheap the company is relative to operating earnings.
        """
        if self.enterprise_value <= 0:
            return 0.0
        return self.ebit / self.enterprise_value

    @property
    def return_on_capital(self) -> float:
        """
        Return on Capital (ROC) = EBIT / Capital Employed
        Measures how efficiently the company generates profits from its operational assets.
        """
        return self.ebit / self.capital_employed

    # -------------------------------------------------------------
    # 2. Modern Proxy Metrics (For Comparison & Analysis)
    # -------------------------------------------------------------
    @property
    def return_on_assets(self) -> float:
        """ROA = Net Income / Total Assets"""
        if self.total_assets <= 0:
            return 0.0
        return self.net_income / self.total_assets

    @property
    def return_on_equity(self) -> float:
        """ROE = Net Income / Total Equity"""
        if self.total_equity <= 0:
            return 0.0
        return self.net_income / self.total_equity

    @property
    def pe_ratio(self) -> Optional[float]:
        """P/E = Market Cap / Net Income"""
        if self.net_income <= 0:
            return None
        return self.market_cap / self.net_income

    @property
    def ev_to_ebitda(self) -> Optional[float]:
        """EV / EBITDA"""
        if not self.ebitda or self.ebitda <= 0:
            return None
        return self.enterprise_value / self.ebitda
