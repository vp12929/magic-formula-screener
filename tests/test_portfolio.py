"""
Unit tests for Position and Portfolio classes.
"""

import pytest
from magic_formula.backtest.position import Position, TradeAction, TradeRecord
from magic_formula.backtest.portfolio import Portfolio, PortfolioSnapshot


def test_position_calculations():
    # Buy 10 shares at $100
    pos = Position(ticker="AAPL", shares=10.0, price=100.0, date="2025-01-01")

    assert pos.ticker == "AAPL"
    assert pos.shares == 10.0
    assert pos.entry_price == 100.0
    assert pos.cost_basis == 1000.0
    assert pos.market_value == 1000.0
    assert pos.unrealized_pnl == 0.0
    assert pos.unrealized_pnl_pct == 0.0

    # Price goes up to $150 (+50%)
    pos.update_price(150.0)
    assert pos.market_value == 1500.0
    assert pos.unrealized_pnl == 500.0
    assert pytest.approx(pos.unrealized_pnl_pct, 0.001) == 0.50

    # Buy 10 more shares at $200
    # New cost basis: (10*100 + 10*200) / 20 = 3000 / 20 = $150/share
    pos.add_shares(additional_shares=10.0, price=200.0)
    assert pos.shares == 20.0
    assert pytest.approx(pos.entry_price, 0.001) == 150.0
    assert pytest.approx(pos.cost_basis, 0.001) == 3000.0


def test_position_validation():
    with pytest.raises(ValueError, match="Initial shares must be positive"):
        Position("AAPL", shares=0, price=100, date="2025-01-01")

    pos = Position("AAPL", shares=5.0, price=100.0, date="2025-01-01")
    with pytest.raises(ValueError, match="Cannot sell 10"):
        pos.remove_shares(10.0)


def test_portfolio_buy_and_sell():
    port = Portfolio(initial_capital=10_000.0)
    assert port.cash == 10_000.0
    assert port.total_equity == 10_000.0

    # Buy 20 shares of MSFT at $200 (Total $4,000)
    trade_buy = port.buy("MSFT", shares=20.0, price=200.0, date="2025-01-02", fee=10.0)
    assert trade_buy.action == TradeAction.BUY
    assert port.cash == 10_000.0 - 4_010.0  # 5,990.0
    assert "MSFT" in port.positions
    assert port.positions["MSFT"].shares == 20.0

    # Selling 10 shares of MSFT at $250
    trade_sell = port.sell("MSFT", shares=10.0, price=250.0, date="2025-06-01", fee=5.0)
    assert trade_sell.action == TradeAction.SELL
    # Proceeds = 2500 - 5 = 2495. New cash = 5990 + 2495 = 8485
    assert port.cash == 8485.0
    assert port.positions["MSFT"].shares == 10.0

    # Insufficient funds check
    with pytest.raises(ValueError, match="Insufficient funds"):
        port.buy("GOOGL", shares=1000.0, price=200.0, date="2025-06-02")


def test_portfolio_snapshots():
    port = Portfolio(initial_capital=10_000.0)
    port.buy("AAPL", shares=50.0, price=100.0, date="2025-01-01")  # $5,000 cash left

    # Stock price goes to $120
    snapshot = port.take_snapshot(date="2025-03-01", current_prices={"AAPL": 120.0})
    # Equity = 5,000 cash + 50 * 120 ($6,000) = $11,000
    assert snapshot.total_equity == 11_000.0
    assert pytest.approx(snapshot.cumulative_return_pct, 0.001) == 0.10
    assert len(port.snapshots) == 1


def test_portfolio_rebalance():
    # Start with 2 stocks (50/50)
    port = Portfolio(initial_capital=10_000.0)
    port.buy("STOCK_A", shares=50.0, price=100.0, date="2025-01-01") # $5,000
    port.buy("STOCK_B", shares=50.0, price=100.0, date="2025-01-01") # $5,000
    assert port.cash == 0.0

    # Prices stay at 100. Now we rebalance: drop STOCK_B, introduce STOCK_C (50% A, 50% C)
    target_weights = {"STOCK_A": 0.50, "STOCK_C": 0.50}
    current_prices = {"STOCK_A": 100.0, "STOCK_B": 100.0, "STOCK_C": 100.0}

    trades = port.rebalance(target_weights, current_prices, date="2025-06-01")

    # Should have sold all STOCK_B, and bought 50 shares of STOCK_C
    assert "STOCK_B" not in port.positions
    assert "STOCK_A" in port.positions
    assert "STOCK_C" in port.positions
    assert port.positions["STOCK_C"].shares == 50.0
    assert pytest.approx(port.total_equity, 0.01) == 10_000.0
