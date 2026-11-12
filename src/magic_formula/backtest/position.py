"""
position.py
-----------
Defines Position and TradeRecord classes.

OOP Concepts:
- Encapsulation: A Position encapsulates the state of an asset holding (shares, cost basis, price).
  External code should not manually calculate market value or PnL; the Position object computes
  and provides those properties itself.
- State Invariants & Validation: Methods enforce rules like 'shares cannot be negative'
  and automatically update weighted average cost basis when more shares are bought.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TradeAction(Enum):
    """Enumeration of valid trading actions."""
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True)
class TradeRecord:
    """
    Immutable value object representing an executed transaction.
    
    OOP Concept: Immutability (frozen=True)
    - Once a trade occurs, historical trade details should never be modified.
    """
    date: str
    ticker: str
    action: TradeAction
    shares: float
    price: float
    total_amount: float
    fee: float = 0.0


class Position:
    """
    Represents an active stock holding in a portfolio.
    
    Tracks quantities, cost basis (weighted average purchase price),
    and current market valuation.
    """

    def __init__(self, ticker: str, shares: float, price: float, date: str):
        if shares <= 0:
            raise ValueError(f"Initial shares must be positive, got {shares}")
        if price <= 0:
            raise ValueError(f"Initial price must be positive, got {price}")

        self.ticker: str = ticker.upper().strip()
        self.shares: float = float(shares)
        self.entry_price: float = float(price)      # Weighted average cost basis per share
        self.entry_date: str = date
        self.current_price: float = float(price)

    # -------------------------------------------------------------
    # Computed Properties (Encapsulation)
    # -------------------------------------------------------------
    @property
    def cost_basis(self) -> float:
        """Total capital invested into this position."""
        return self.shares * self.entry_price

    @property
    def market_value(self) -> float:
        """Current total value of the holding at market price."""
        return self.shares * self.current_price

    @property
    def unrealized_pnl(self) -> float:
        """Profit or loss in dollar terms."""
        return self.market_value - self.cost_basis

    @property
    def unrealized_pnl_pct(self) -> float:
        """Profit or loss as a percentage return (e.g. 0.15 = +15%)."""
        if self.cost_basis == 0.0:
            return 0.0
        return (self.market_value - self.cost_basis) / self.cost_basis

    # -------------------------------------------------------------
    # State Modification Methods (Defensive Invariants)
    # -------------------------------------------------------------
    def update_price(self, new_price: float) -> None:
        """Updates the current mark-to-market price."""
        if new_price < 0:
            raise ValueError(f"Price cannot be negative: {new_price}")
        self.current_price = float(new_price)

    def add_shares(self, additional_shares: float, price: float) -> None:
        """
        Increases position size and recalculates weighted average cost basis.
        
        Formula:
            new_cost_basis = (old_shares * old_entry + added_shares * price) / total_shares
        """
        if additional_shares <= 0:
            raise ValueError(f"Shares to add must be positive, got {additional_shares}")
        if price <= 0:
            raise ValueError(f"Purchase price must be positive, got {price}")

        total_cost = self.cost_basis + (additional_shares * price)
        self.shares += additional_shares
        self.entry_price = total_cost / self.shares
        self.current_price = price

    def remove_shares(self, shares_to_remove: float) -> float:
        """
        Reduces position size (e.g. partial sale).
        Returns the remaining number of shares.
        Raises ValueError if attempting to sell more shares than currently held.
        """
        if shares_to_remove <= 0:
            raise ValueError(f"Shares to remove must be positive, got {shares_to_remove}")
        if shares_to_remove > self.shares:
            raise ValueError(
                f"Cannot sell {shares_to_remove} shares of {self.ticker}; only hold {self.shares}"
            )

        self.shares -= shares_to_remove
        return self.shares

    def __repr__(self) -> str:
        return (
            f"Position({self.ticker}, shares={self.shares:.2f}, "
            f"cost_basis=${self.cost_basis:,.2f}, mkt_val=${self.market_value:,.2f}, "
            f"pnl={self.unrealized_pnl_pct * 100:+.2f}%)"
        )
