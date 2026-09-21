"""
main.py
-------
CLI Entry Point for Magic Formula Stock Screener.

Usage Examples:
    # 1. Run instant offline demo with 25 mock companies (Strict Greenblatt):
    python main.py --provider mock

    # 2. Run side-by-side comparison of Strict vs Proxy formulas on mock data:
    python main.py --provider mock --compare

    # 3. Run live screening on top 30 S&P companies using Yahoo Finance:
    python main.py --provider yahoo --limit 30

    # 4. Run live full S&P 500 comparison and export to CSV:
    python main.py --provider yahoo --universe sp500 --limit 50 --compare --export-csv
"""

import sys
import argparse
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


def main():
    parser = argparse.ArgumentParser(
        description="Magic Formula Stock Screener (Joel Greenblatt) with OOP Architecture"
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
        help="Number of top ranked companies to display. Default: 20",
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

    args = parser.parse_args()

    print("=" * 80)
    print(" MAGIC FORMULA STOCK SCREENER (Joel Greenblatt)")
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

    print(f"Fetching financial statement data for {len(tickers)} companies...")

    # 2. Instantiate Filters & Screener
    filter_chain = FilterChain.default_magic_formula_chain(min_market_cap=args.min_mcap)
    strategy = StrictMagicFormulaStrategy() if args.strategy == "strict" else ProxyRankingStrategy()

    screener = MagicFormulaScreener(
        data_provider=data_provider,
        ranking_strategy=strategy,
        filter_chain=filter_chain,
    )

    console_reporter = ConsoleReporter()
    csv_reporter = CsvReporter() if args.export_csv else None

    # 3. Execute Screening / Comparison
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
