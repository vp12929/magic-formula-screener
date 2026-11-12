"""
main.py
-------
CLI Entry Point for Magic Formula Stock Screener and Historical Backtester.

Usage Examples:
    # 1. Run instant offline demo with 25 mock companies (Strict Greenblatt):
    python main.py --provider mock

    # 2. Run side-by-side comparison of Strict vs Proxy formulas on mock data:
    python main.py --provider mock --compare

    # 3. Run instant offline historical backtest (2023 - 2025, annual rebalance):
    python main.py --provider mock --backtest

    # 4. Run live historical backtest on curated S&P companies against SPY benchmark:
    python main.py --provider yahoo --backtest --start-date 2023-01-01 --end-date 2024-12-31 --limit 30 --export-csv
"""

import sys
import argparse
import csv
from pathlib import Path

# Add src/ to Python module search path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from magic_formula.providers.mock import MockDataProvider
from magic_formula.providers.yahoo import YahooFinanceProvider
from magic_formula.providers.universes import UniverseLoader
from magic_formula.strategies.strict import StrictMagicFormulaStrategy
from magic_formula.strategies.proxy import ProxyRankingStrategy
from magic_formula.filters.chain import FilterChain
from magic_formula.screener import MagicFormulaScreener
from magic_formula.reporters.console import ConsoleReporter
from magic_formula.reporters.csv_reporter import CsvReporter
from magic_formula.backtest.engine import BacktestEngine


def main():
    parser = argparse.ArgumentParser(
        description="Magic Formula Stock Screener & Backtester (Joel Greenblatt) with OOP Architecture"
    )
    parser.add_argument(
        "--provider",
        choices=["mock", "yahoo"],
        default="mock",
        help="Data provider to use: 'mock' (offline instant demo) or 'yahoo' (live market data via yfinance). Default: mock",
    )
    parser.add_argument(
        "--universe",
        choices=["curated", "sp500"],
        default="curated",
        help="Stock universe: 'curated' (50 diversified liquid stocks) or 'sp500' (S&P 500 index). Default: curated",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=25,
        help="Maximum number of tickers to analyze from the universe. Default: 25",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of top ranked companies to display / hold in portfolio. Default: 20",
    )
    parser.add_argument(
        "--strategy",
        choices=["strict", "proxy"],
        default="strict",
        help="Ranking strategy to use (ignored if --compare is set). Default: strict",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Run both Strict Greenblatt and Modern Proxy strategies side-by-side for comparison.",
    )
    parser.add_argument(
        "--min-mcap",
        type=float,
        default=50_000_000.0,
        help="Minimum market cap filter in USD (e.g. 50000000 = $50M). Default: 50,000,000",
    )
    parser.add_argument(
        "--export-csv",
        action="store_true",
        help="Export final results and comparison tables to CSV files.",
    )

    # Backtesting specific arguments
    parser.add_argument(
        "--backtest",
        action="store_true",
        help="Execute historical portfolio backtest simulation instead of static screener.",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default="2023-01-01",
        help="Backtest start date (YYYY-MM-DD). Default: 2023-01-01",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default="2025-01-01",
        help="Backtest end date (YYYY-MM-DD). Default: 2025-01-01",
    )
    parser.add_argument(
        "--rebalance-months",
        type=int,
        default=12,
        help="Rebalancing interval in months (e.g. 12 = annual rebalancing). Default: 12",
    )
    parser.add_argument(
        "--capital",
        type=float,
        default=100_000.0,
        help="Initial capital for backtesting. Default: $100,000",
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        default="SPY",
        help="Benchmark symbol for backtesting (e.g. SPY). Default: SPY",
    )

    args = parser.parse_args()

    mode_title = "HISTORICAL BACKTESTER" if args.backtest else "STOCK SCREENER"
    print("=" * 80)
    print(f" MAGIC FORMULA {mode_title} (Joel Greenblatt)")
    print(f" Provider: {args.provider.upper()} | Universe: {args.universe.upper()} | Top Results: {args.top}")
    print("=" * 80)

    # 1. Instantiate Data Provider (Polymorphism)
    if args.provider == "mock":
        data_provider = MockDataProvider()
        tickers = data_provider.get_all_tickers()[: args.limit]
    else:
        data_provider = YahooFinanceProvider(cache_data=True)
        if args.universe == "sp500":
            tickers = UniverseLoader.get_sp500_tickers()[: args.limit]
        else:
            tickers = UniverseLoader.get_curated_tickers(limit=args.limit)

    # 2. Instantiate Filters & Screener
    filter_chain = FilterChain.default_magic_formula_chain(min_market_cap=args.min_mcap)
    strategy = StrictMagicFormulaStrategy() if args.strategy == "strict" else ProxyRankingStrategy()

    screener = MagicFormulaScreener(
        data_provider=data_provider,
        ranking_strategy=strategy,
        filter_chain=filter_chain,
    )

    # 3. Execute Backtest or Screener
    if args.backtest:
        print(f"Initializing Backtest Engine with ${args.capital:,.2f} initial capital...")
        print(f"Simulation Period: {args.start_date} to {args.end_date} | Rebalancing Every {args.rebalance_months} Months")
        print(f"Benchmark: {args.benchmark} | Basket Size: Top {args.top} Stocks")

        engine = BacktestEngine(
            screener=screener,
            initial_capital=args.capital,
            risk_free_rate=0.03,
            fee_per_trade=5.0,
        )

        result = engine.run(
            tickers=tickers,
            start_date=args.start_date,
            end_date=args.end_date,
            top_n=args.top,
            rebalance_months=args.rebalance_months,
            benchmark_ticker=args.benchmark,
        )

        result.print_summary()

        if args.export_csv:
            csv_path = Path("backtest_equity_curve.csv")
            with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Cash", "Holdings_Value", "Strategy_Total_Equity", "Strategy_Return_Pct", "Benchmark_Equity", "Benchmark_Return_Pct"])
                for idx, snap in enumerate(result.portfolio.snapshots):
                    bm_snap = result.benchmark_snapshots[idx] if idx < len(result.benchmark_snapshots) else None
                    writer.writerow([
                        snap.date,
                        round(snap.cash, 2),
                        round(snap.holdings_value, 2),
                        round(snap.total_equity, 2),
                        round(snap.cumulative_return_pct * 100, 2),
                        round(bm_snap.total_equity, 2) if bm_snap else "N/A",
                        round(bm_snap.cumulative_return_pct * 100, 2) if bm_snap else "N/A",
                    ])
            print(f"Equity curve exported successfully to: {csv_path.resolve()}")

    else:
        # Standard Screener mode
        console_reporter = ConsoleReporter()
        csv_reporter = CsvReporter() if args.export_csv else None

        if args.compare:
            print("Running comparative analysis (Strict Magic Formula vs. Modern Proxy)...")
            comparison = screener.compare_strict_vs_proxy(tickers, top_n=args.top)
            console_reporter.report_comparison(comparison)
            if csv_reporter:
                csv_reporter.report_comparison(comparison)
        else:
            print(f"Executing screener using [{strategy.name}]...")
            top_stocks, summary = screener.run_screen(tickers, top_n=args.top)
            console_reporter.report_ranked(top_stocks, summary)
            if csv_reporter:
                csv_reporter.report_ranked(top_stocks, summary)


if __name__ == "__main__":
    main()
