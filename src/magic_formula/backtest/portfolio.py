"""
portfolio.py
------------
Defines Portfolio and PortfolioSnapshot classes.

OOP Concepts:
- Composition: A Portfolio owns and manages a collection of `Position` objects.
- Invariant Protection: Cash cannot fall below zero; sells cannot exceed owned shares.
- Transaction Logging: All operations generate immutable `TradeRecord` logs.
- Rebalancing Algorithm: Encapsulates the logic of rotating out of old stocks and into new
  Magic Formula picks with equal or custom weightings.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from magic_formula.backtest.position import Position, TradeAction, TradeRecord


@dataclass(frozen=True)
class PortfolioSnapshot:
    """
    Point-in-time snapshot of the portfolio's total state.
    Used to build the equity curve and calculate historical performance.
    """
    date: str
    cash: float
    holdings_value: float
    total_equity: float
    cumulative_return_pct: float


class Portfolio:
    """
    Manages cash, open positions, trade history, and periodic rebalancing.
    """

    def __init__(self, initial_capital: float = 100_000.0):
        if initial_capital <= 0:
            raise ValueError(f"Initial capital must be positive, got {initial_capital}")

        self.initial_capital: float = float(initial_capital)
        self.cash: float = float(initial_capital)
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[TradeRecord] = []
        self.snapshots: List[PortfolioSnapshot] = []

    # -------------------------------------------------------------
    # Valuation Properties
    # -------------------------------------------------------------
    @property
    def holdings_value(self) -> float:
        """Sum of market values for all open positions."""
        return sum(pos.market_value for pos in self.positions.values())

    @property
    def total_equity(self) -> float:
        """Total portfolio net worth (Cash + All Open Positions)."""
        return self.cash + self.holdings_value

    @property
    def cumulative_pnl(self) -> float:
        """Total dollar profit or loss since inception."""
        return self.total_equity - self.initial_capital

    @property
    def cumulative_return_pct(self) -> float:
        """Total return percentage since inception (e.g. 0.25 = +25%)."""
        return (self.total_equity - self.initial_capital) / self.initial_capital

    # -------------------------------------------------------------
    # Order Execution
    # -------------------------------------------------------------
    def buy(
        self,
        ticker: str,
        shares: float,
        price: float,
        date: str,
        fee: float = 0.0,
    ) -> TradeRecord:
        """
        Buys shares of a ticker.
        Deducts cash, adds to or creates a Position, and logs the trade.
        """
        symbol = ticker.upper().strip()
        total_cost = (shares * price) + fee

        if total_cost > self.cash + 1e-6:  # small epsilon for floating-point tolerance
            raise ValueError(
                f"Insufficient funds to buy {shares:.2f} of {symbol} at ${price:.2f} (Cost: ${total_cost:,.2f}, Cash: ${self.cash:,.2f})"
            )

        self.cash -= total_cost

        if symbol in self.positions:
            self.positions[symbol].add_shares(shares, price)
        else:
            self.positions[symbol] = Position(ticker=symbol, shares=shares, price=price, date=date)

        trade = TradeRecord(
            date=date,
            ticker=symbol,
            action=TradeAction.BUY,
            shares=shares,
            price=price,
            total_amount=total_cost,
            fee=fee,
        )
        self.trade_history.append(trade)
        return trade

    def sell(
        self,
        ticker: str,
        shares: float,
        price: float,
        date: str,
        fee: float = 0.0,
    ) -> TradeRecord:
        """
        Sells shares of a held position.
        Credits cash, reduces or closes the Position, and logs the trade.
        """
        symbol = ticker.upper().strip()
        if symbol not in self.positions:
            raise KeyError(f"Cannot sell {symbol}: position does not exist in portfolio.")

        position = self.positions[symbol]
        position.update_price(price)
        remaining_shares = position.remove_shares(shares)

        gross_proceeds = shares * price
        net_proceeds = gross_proceeds - fee
        self.cash += net_proceeds

        if remaining_shares == 0:
            del self.positions[symbol]

        trade = TradeRecord(
            date=date,
            ticker=symbol,
            action=TradeAction.SELL,
            shares=shares,
            price=price,
            total_amount=net_proceeds,
            fee=fee,
        )
        self.trade_history.append(trade)
        return trade

    def sell_all(self, ticker: str, price: float, date: str, fee: float = 0.0) -> Optional[TradeRecord]:
        """Liquidates the entire position in a given ticker."""
        symbol = ticker.upper().strip()
        if symbol not in self.positions:
            return None
        return self.sell(symbol, self.positions[symbol].shares, price, date, fee)

    # -------------------------------------------------------------
    # Mark to Market & Snapshots
    # -------------------------------------------------------------
    def update_prices(self, current_prices: Dict[str, float]) -> None:
        """Updates prices for all currently held positions."""
        for symbol, pos in self.positions.items():
            if symbol in current_prices:
                pos.update_price(current_prices[symbol])

    def take_snapshot(self, date: str, current_prices: Optional[Dict[str, float]] = None) -> PortfolioSnapshot:
        """
        Records the current portfolio state into the historical equity curve.
        """
        if current_prices:
            self.update_prices(current_prices)

        snapshot = PortfolioSnapshot(
            date=date,
            cash=self.cash,
            holdings_value=self.holdings_value,
            total_equity=self.total_equity,
            cumulative_return_pct=self.cumulative_return_pct,
        )
        self.snapshots.append(snapshot)
        return snapshot

    # -------------------------------------------------------------
    # Rebalancing (Magic Formula Rotation)
    # -------------------------------------------------------------
    def rebalance(
        self,
        target_weights: Dict[str, float],
        current_prices: Dict[str, float],
        date: str,
        fee_per_trade: float = 0.0,
    ) -> List[TradeRecord]:
        """
        Rebalances portfolio to match target percentage weights.
        
        Execution Order (Two-pass to prevent cash deficiency):
        1. Pass 1: Sell positions that are no longer in target, or trim overweight positions.
        2. Pass 2: Buy new positions and underweight positions with released cash.
        """
        # First update all prices
        self.update_prices(current_prices)
        trades: List[TradeRecord] = []

        total_value = self.total_equity
        target_shares: Dict[str, float] = {}

        for sym, weight in target_weights.items():
            sym_clean = sym.upper().strip()
            if sym_clean in current_prices and current_prices[sym_clean] > 0:
                target_allocation = total_value * weight
                target_shares[sym_clean] = target_allocation / current_prices[sym_clean]

        # --- PASS 1: SELLS & TRIMS ---
        for sym in list(self.positions.keys()):
            current_shares = self.positions[sym].shares
            desired_shares = target_shares.get(sym, 0.0)

            if desired_shares < current_shares:
                shares_to_sell = current_shares - desired_shares
                price = current_prices.get(sym, self.positions[sym].current_price)
                if shares_to_sell > 1e-4:
                    t = self.sell(sym, shares_to_sell, price, date, fee=fee_per_trade)
                    trades.append(t)

        # --- PASS 2: BUYS & ADDS ---
        for sym, desired_shares in target_shares.items():
            current_shares = self.positions[sym].shares if sym in self.positions else 0.0

            if desired_shares > current_shares:
                shares_to_buy = desired_shares - current_shares
                price = current_prices[sym]
                cost = (shares_to_buy * price) + fee_per_trade

                # Guard against cash round-off limits
                if cost > self.cash:
                    shares_to_buy = max(0.0, (self.cash - fee_per_trade) / price)

                if shares_to_buy > 1e-4:
                    t = self.buy(sym, shares_to_buy, price, date, fee=fee_per_trade)
                    trades.append(t)

        return trades

    def __repr__(self) -> str:
        return (
            f"Portfolio(equity=${self.total_equity:,.2f}, cash=${self.cash:,.2f}, "
            f"positions={len(self.positions)}, return={self.cumulative_return_pct * 100:+.2f}%)"
        )
