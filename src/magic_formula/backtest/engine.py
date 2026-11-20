"""
engine.py
---------
Defines BacktestEngine and BacktestResult classes with Cash Dividend Tracking.

OOP Concepts:
- Facade Pattern: Coordinates Screener, Data Providers, Portfolio, and PerformanceAnalyzer.
- Event-driven Dividend Accounting: Automatically detects ex-dividend dates from price actions,
  credits cash payouts to the Portfolio, and includes total dividend income in final net benefits.
- Separation of Concerns: Keeps price downloading, portfolio accounting, and metric analysis isolated.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

from magic_formula.screener import MagicFormulaScreener
from magic_formula.backtest.portfolio import Portfolio, PortfolioSnapshot
from magic_formula.backtest.analyzer import PerformanceAnalyzer, PerformanceMetrics
from magic_formula.providers.mock import MockDataProvider


@dataclass
class BacktestResult:
    """Holds the complete output of a historical simulation run."""
    portfolio: Portfolio
    benchmark_snapshots: List[PortfolioSnapshot]
    metrics: PerformanceMetrics
    rebalance_dates: List[str]
    holdings_by_period: Dict[str, List[str]] = field(default_factory=dict)

    def print_summary(self) -> None:
        """Prints a comprehensive text summary of the backtest results."""
        print("\n" + "=" * 80)
        print(" HISTORICAL BACKTEST PERFORMANCE REPORT")
        print("=" * 80)
        print(self.metrics.summary())
        print("=" * 80)
        if self.portfolio.dividend_history:
            total_divs = len(self.portfolio.dividend_history)
            div_cash = self.portfolio.total_dividends_collected
            print(f"Dividends: Received {total_divs} payouts totaling ${div_cash:+,.2f} in cash income")
        print(f"Total Rebalance Events: {len(self.rebalance_dates)}")
        for d in self.rebalance_dates:
            stocks = self.holdings_by_period.get(d, [])
            stocks_str = ", ".join(stocks[:8]) + (f" ... (+{len(stocks)-8} more)" if len(stocks) > 8 else "")
            print(f"  • {d}: Selected {len(stocks)} stocks [{stocks_str}]")
        print("=" * 80)


class BacktestEngine:
    """
    Simulates historical trading of Magic Formula portfolios over time,
    accounting for stock price changes, trading commissions, and cash dividend income.
    """

    def __init__(
        self,
        screener: MagicFormulaScreener,
        initial_capital: float = 100_000.0,
        risk_free_rate: float = 0.03,
        fee_per_trade: float = 0.0,
    ):
        self.screener = screener
        self.initial_capital = float(initial_capital)
        self.risk_free_rate = float(risk_free_rate)
        self.fee_per_trade = float(fee_per_trade)
        self.analyzer = PerformanceAnalyzer(risk_free_rate=self.risk_free_rate)

    def run(
        self,
        tickers: List[str],
        start_date: str = "2023-01-01",
        end_date: str = "2025-01-01",
        top_n: int = 20,
        rebalance_months: int = 12,
        benchmark_ticker: str = "SPY",
        price_history_df: Optional[pd.DataFrame] = None,
        dividend_history_df: Optional[pd.DataFrame] = None,
    ) -> BacktestResult:
        """
        Executes the historical backtest simulation.
        
        :param tickers: Universe of tickers to screen from.
        :param start_date: Simulation start date (YYYY-MM-DD).
        :param end_date: Simulation end date (YYYY-MM-DD).
        :param top_n: Number of stocks to hold in the Magic Formula basket.
        :param rebalance_months: How often to re-screen and rebalance (default 12 months).
        :param benchmark_ticker: Benchmark symbol (default SPY).
        :param price_history_df: Optional pre-loaded DataFrame of closing prices.
        :param dividend_history_df: Optional pre-loaded DataFrame of cash dividend amounts per share.
        """
        # 1. Fetch or generate historical price and dividend matrices
        if price_history_df is None:
            price_history_df, dividend_history_df = self._fetch_price_and_dividend_history(
                tickers=tickers,
                benchmark=benchmark_ticker,
                start_date=start_date,
                end_date=end_date,
            )

        # Clean prices: forward-fill any missing weekend/holiday data
        price_history_df = price_history_df.ffill().bfill()
        available_dates = [d.strftime("%Y-%m-%d") for d in price_history_df.index]

        if len(available_dates) < 2:
            raise ValueError(f"Insufficient historical price data between {start_date} and {end_date}.")

        # 2. Compute periodic rebalance dates
        rebalance_dates = self._generate_rebalance_schedule(
            available_dates=available_dates,
            rebalance_months=rebalance_months,
        )

        # 3. Setup portfolios
        portfolio = Portfolio(initial_capital=self.initial_capital)
        benchmark_snapshots: List[PortfolioSnapshot] = []
        holdings_by_period: Dict[str, List[str]] = {}

        # Benchmark initial price
        has_benchmark = benchmark_ticker in price_history_df.columns
        bm_start_price = float(price_history_df[benchmark_ticker].iloc[0]) if has_benchmark else 1.0

        current_target_tickers: List[str] = []

        # 4. Step through each historical day
        for dt_idx, date_str in enumerate(available_dates):
            current_prices = price_history_df.iloc[dt_idx].to_dict()

            # --- A. CREDIT CASH DIVIDENDS ---
            if dividend_history_df is not None and dt_idx < len(dividend_history_df):
                div_series = dividend_history_df.iloc[dt_idx].to_dict()
                for held_sym in list(portfolio.positions.keys()):
                    div_amount = float(div_series.get(held_sym, 0.0) or 0.0)
                    if div_amount > 0:
                        portfolio.credit_dividend(
                            ticker=held_sym,
                            amount_per_share=div_amount,
                            date=date_str,
                        )

            # --- B. EXECUTE REBALANCING ---
            if date_str in rebalance_dates or dt_idx == 0:
                valid_tickers = [
                    t for t in tickers
                    if t in current_prices and not np.isnan(current_prices[t]) and current_prices[t] > 0
                ]
                top_ranked, _ = self.screener.run_screen(valid_tickers, top_n=top_n)
                current_target_tickers = [r.ticker for r in top_ranked]

                if current_target_tickers:
                    holdings_by_period[date_str] = list(current_target_tickers)
                    equal_weight = 1.0 / len(current_target_tickers)
                    target_weights = {t: equal_weight for t in current_target_tickers}

                    portfolio.rebalance(
                        target_weights=target_weights,
                        current_prices=current_prices,
                        date=date_str,
                        fee_per_trade=self.fee_per_trade,
                    )

            # --- C. RECORD MARK-TO-MARKET SNAPSHOT ---
            portfolio.take_snapshot(date=date_str, current_prices=current_prices)

            # --- D. RECORD BENCHMARK SNAPSHOT ---
            if has_benchmark:
                bm_price_today = float(current_prices.get(benchmark_ticker, bm_start_price))
                bm_equity = self.initial_capital * (bm_price_today / bm_start_price)
                bm_return = (bm_equity - self.initial_capital) / self.initial_capital
                benchmark_snapshots.append(
                    PortfolioSnapshot(
                        date=date_str,
                        cash=0.0,
                        holdings_value=bm_equity,
                        total_equity=bm_equity,
                        cumulative_return_pct=bm_return,
                    )
                )

        # 5. Evaluate final performance metrics
        metrics = self.analyzer.analyze(
            portfolio=portfolio,
            benchmark_snapshots=benchmark_snapshots if has_benchmark else None,
        )

        return BacktestResult(
            portfolio=portfolio,
            benchmark_snapshots=benchmark_snapshots,
            metrics=metrics,
            rebalance_dates=rebalance_dates,
            holdings_by_period=holdings_by_period,
        )

    # -------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------
    def _generate_rebalance_schedule(self, available_dates: List[str], rebalance_months: int) -> List[str]:
        """Calculates specific calendar dates where rebalancing must trigger."""
        if not available_dates:
            return []

        rebalance_dates = [available_dates[0]]
        last_dt = datetime.strptime(available_dates[0], "%Y-%m-%d")

        for d_str in available_dates[1:]:
            curr_dt = datetime.strptime(d_str, "%Y-%m-%d")
            months_diff = (curr_dt.year - last_dt.year) * 12 + (curr_dt.month - last_dt.month)
            if months_diff >= rebalance_months:
                rebalance_dates.append(d_str)
                last_dt = curr_dt

        return rebalance_dates

    def _fetch_price_and_dividend_history(
        self,
        tickers: List[str],
        benchmark: str,
        start_date: str,
        end_date: str,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Fetches live prices and dividends via yfinance or creates synthetic series for mock mode."""
        all_symbols = list(set(tickers + [benchmark]))

        if isinstance(self.screener.data_provider, MockDataProvider):
            return self._generate_synthetic_prices_and_dividends(all_symbols, start_date, end_date)

        # Fetch live data including dividend actions
        import yfinance as yf
        data = yf.download(all_symbols, start=start_date, end=end_date, progress=False, threads=False, actions=True)

        # Price DataFrame
        if "Close" in data:
            price_df = data["Close"]
        elif "Adj Close" in data:
            price_df = data["Adj Close"]
        else:
            price_df = data

        if isinstance(price_df, pd.Series):
            price_df = price_df.to_frame(name=all_symbols[0])

        # Dividend DataFrame
        if "Dividends" in data:
            div_df = data["Dividends"]
            if isinstance(div_df, pd.Series):
                div_df = div_df.to_frame(name=all_symbols[0])
        else:
            div_df = pd.DataFrame(0.0, index=price_df.index, columns=price_df.columns)

        return price_df, div_df

    def _generate_synthetic_prices_and_dividends(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Generates realistic daily price series and quarterly dividend distributions for offline testing."""
        dates = pd.date_range(start=start_date, end=end_date, freq="B")  # Business days
        np.random.seed(42)

        price_data = {}
        div_data = {ticker: np.zeros(len(dates)) for ticker in tickers}

        for ticker in tickers:
            daily_drift = 0.10 / 252
            daily_vol = 0.18 / np.sqrt(252)
            returns = np.random.normal(daily_drift, daily_vol, len(dates))
            price_curve = 100.0 * np.exp(np.cumsum(returns))
            price_data[ticker] = price_curve

            # Generate synthetic quarterly cash dividends (~0.6% per quarter = 2.4% yield)
            for idx in range(60, len(dates), 63):
                div_data[ticker][idx] = round(price_curve[idx] * 0.006, 2)

        price_df = pd.DataFrame(price_data, index=dates)
        div_df = pd.DataFrame(div_data, index=dates)
        return price_df, div_df
