"""
Unit tests for BacktestEngine.
"""

from magic_formula.providers.mock import MockDataProvider
from magic_formula.screener import MagicFormulaScreener
from magic_formula.strategies.strict import StrictMagicFormulaStrategy
from magic_formula.backtest.engine import BacktestEngine, BacktestResult


def test_backtest_engine_with_mock_provider():
    provider = MockDataProvider()
    screener = MagicFormulaScreener(
        data_provider=provider,
        ranking_strategy=StrictMagicFormulaStrategy(),
    )

    engine = BacktestEngine(
        screener=screener,
        initial_capital=100_000.0,
        fee_per_trade=5.0,
    )

    tickers = provider.get_all_tickers()
    result = engine.run(
        tickers=tickers,
        start_date="2023-01-01",
        end_date="2024-01-01",
        top_n=5,
        rebalance_months=12,
        benchmark_ticker="SPY",
    )

    assert isinstance(result, BacktestResult)
    assert len(result.portfolio.snapshots) > 200  # ~250 trading days in a year
    assert len(result.rebalance_dates) >= 1
    assert len(result.portfolio.trade_history) > 0

    # Ensure positions were opened
    assert len(result.holdings_by_period) >= 1
    first_rebalance = result.rebalance_dates[0]
    assert len(result.holdings_by_period[first_rebalance]) == 5

    # Check metrics
    metrics = result.metrics
    assert metrics.initial_capital == 100_000.0
    assert metrics.ending_equity > 0
    assert metrics.annualized_volatility > 0.0

    # Ensure summary prints cleanly
    result.print_summary()


def test_backtest_engine_multi_period_rebalance():
    provider = MockDataProvider()
    screener = MagicFormulaScreener(data_provider=provider)
    engine = BacktestEngine(screener=screener, initial_capital=50_000.0)

    # 2-year span from 2023 to 2025 with 12-month rebalance frequency
    result = engine.run(
        tickers=provider.get_all_tickers(),
        start_date="2023-01-01",
        end_date="2025-01-01",
        top_n=5,
        rebalance_months=12,
        benchmark_ticker="SPY",
    )

    # Should trigger initial buy + at least 1 annual rebalance
    assert len(result.rebalance_dates) >= 2
    assert len(result.portfolio.snapshots) > 400
    assert result.metrics.benchmark_total_return_pct is not None
