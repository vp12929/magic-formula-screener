"""
Unit tests for PerformanceAnalyzer.
"""

import pytest
from magic_formula.backtest.portfolio import Portfolio, PortfolioSnapshot
from magic_formula.backtest.analyzer import PerformanceAnalyzer, PerformanceMetrics


def test_analyzer_cagr_and_total_return():
    port = Portfolio(initial_capital=10_000.0)
    # Simulate 1 full year from 2024-01-01 to 2025-01-01 (+20% gain)
    port.snapshots = [
        PortfolioSnapshot("2024-01-01", 10_000.0, 0.0, 10_000.0, 0.0),
        PortfolioSnapshot("2024-07-01", 5_000.0, 6_000.0, 11_000.0, 0.10),
        PortfolioSnapshot("2025-01-01", 0.0, 12_000.0, 12_000.0, 0.20),
    ]

    analyzer = PerformanceAnalyzer(risk_free_rate=0.03)
    metrics = analyzer.analyze(port)

    assert metrics.initial_capital == 10_000.0
    assert metrics.ending_equity == 12_000.0
    assert pytest.approx(metrics.total_return_pct, 0.001) == 0.20
    # ~1.0 year elapsed => CAGR ~ 20%
    assert pytest.approx(metrics.cagr, 0.02) == 0.20


def test_analyzer_max_drawdown():
    port = Portfolio(initial_capital=10_000.0)
    # Starts at 10,000 -> jumps to 15,000 (new peak) -> drops to 12,000 -> climbs to 18,000
    # Peak = 15,000. Drop to 12,000 is (12000 - 15000) / 15000 = -3000 / 15000 = -20% (-0.20)
    port.snapshots = [
        PortfolioSnapshot("2025-01-01", 10_000.0, 0.0, 10_000.0, 0.0),
        PortfolioSnapshot("2025-02-01", 0.0, 15_000.0, 15_000.0, 0.50),
        PortfolioSnapshot("2025-03-01", 0.0, 12_000.0, 12_000.0, 0.20),
        PortfolioSnapshot("2025-04-01", 0.0, 18_000.0, 18_000.0, 0.80),
    ]

    analyzer = PerformanceAnalyzer()
    metrics = analyzer.analyze(port)

    assert pytest.approx(metrics.max_drawdown_pct, 0.001) == -0.20


def test_analyzer_sharpe_ratio():
    port = Portfolio(initial_capital=10_000.0)
    port.snapshots = [
        PortfolioSnapshot("2024-01-01", 10_000.0, 0.0, 10_000.0, 0.0),
        PortfolioSnapshot("2024-06-01", 0.0, 11_000.0, 11_000.0, 0.10),
        PortfolioSnapshot("2025-01-01", 0.0, 12_500.0, 12_500.0, 0.25),
    ]

    # Risk-free = 3%
    analyzer = PerformanceAnalyzer(risk_free_rate=0.03)
    metrics = analyzer.analyze(port)

    assert metrics.annualized_volatility > 0.0
    # CAGR ~ 25%, risk_free = 3% => excess return > 0 => Sharpe > 0
    assert metrics.sharpe_ratio > 0.0


def test_analyzer_benchmark_comparison():
    strat_port = Portfolio(initial_capital=10_000.0)
    strat_port.snapshots = [
        PortfolioSnapshot("2024-01-01", 10_000.0, 0.0, 10_000.0, 0.0),
        PortfolioSnapshot("2024-07-01", 0.0, 12_000.0, 12_000.0, 0.20),
        PortfolioSnapshot("2025-01-01", 0.0, 14_000.0, 14_000.0, 0.40),
    ]

    # Benchmark: S&P 500 up only 10%
    bm_snapshots = [
        PortfolioSnapshot("2024-01-01", 10_000.0, 0.0, 10_000.0, 0.0),
        PortfolioSnapshot("2024-07-01", 0.0, 10_500.0, 10_500.0, 0.05),
        PortfolioSnapshot("2025-01-01", 0.0, 11_000.0, 11_000.0, 0.10),
    ]

    analyzer = PerformanceAnalyzer(risk_free_rate=0.02)
    metrics = analyzer.analyze(strat_port, benchmark_snapshots=bm_snapshots)

    assert pytest.approx(metrics.benchmark_total_return_pct, 0.001) == 0.10
    assert metrics.alpha is not None
    assert metrics.beta is not None
    assert "Benchmark Return:" in metrics.summary()
