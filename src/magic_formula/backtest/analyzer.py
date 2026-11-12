"""
analyzer.py
-----------
Defines PerformanceAnalyzer and PerformanceMetrics classes.

OOP Concept: Single Responsibility Principle (SRP)
- The Portfolio class manages positions and cash (operational domain).
- The PerformanceAnalyzer class is solely responsible for statistical risk and return analysis
  (analytical domain).
- Keeping these separate ensures that if we change financial formulas, add Sharpe/Sortino ratios,
  or alter benchmark calculations, we never touch or risk breaking portfolio execution logic.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple
import math
from magic_formula.backtest.portfolio import Portfolio, PortfolioSnapshot


@dataclass(frozen=True)
class PerformanceMetrics:
    """Immutable report holding all computed risk and return statistics."""
    initial_capital: float
    ending_equity: float
    total_return_pct: float
    cagr: float
    annualized_volatility: float
    sharpe_ratio: float
    max_drawdown_pct: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate_pct: float
    # Benchmark stats (e.g. vs SPY)
    benchmark_total_return_pct: Optional[float] = None
    benchmark_cagr: Optional[float] = None
    alpha: Optional[float] = None
    beta: Optional[float] = None

    def summary(self) -> str:
        """Returns a formatted summary text block."""
        lines = [
            f"Initial Capital:       ${self.initial_capital:,.2f}",
            f"Ending Equity:         ${self.ending_equity:,.2f}",
            f"Total Return:          {self.total_return_pct * 100:+.2f}%",
            f"CAGR (Annualized):     {self.cagr * 100:+.2f}%",
            f"Annual Volatility:     {self.annualized_volatility * 100:.2f}%",
            f"Sharpe Ratio:          {self.sharpe_ratio:.2f}",
            f"Max Drawdown:          {self.max_drawdown_pct * 100:.2f}%",
            f"Total Trades:          {self.total_trades} (Win rate: {self.win_rate_pct * 100:.1f}%)",
        ]
        if self.benchmark_total_return_pct is not None:
            lines.extend([
                f"Benchmark Return:      {self.benchmark_total_return_pct * 100:+.2f}%",
                f"Benchmark CAGR:        {self.benchmark_cagr * 100:+.2f}%",
                f"Beta vs Benchmark:     {self.beta:.2f}" if self.beta is not None else "Beta: N/A",
                f"Alpha (Annualized):    {self.alpha * 100:+.2f}%" if self.alpha is not None else "Alpha: N/A",
            ])
        return "\n".join(lines)


class PerformanceAnalyzer:
    """
    Computes financial metrics, risk ratios, drawdowns, and benchmark statistics.
    """

    def __init__(self, risk_free_rate: float = 0.03):
        """
        :param risk_free_rate: Annualized risk-free rate (e.g. 0.03 = 3% US 10-Yr Treasury yield).
        """
        self.risk_free_rate: float = float(risk_free_rate)

    def analyze(
        self,
        portfolio: Portfolio,
        benchmark_snapshots: Optional[List[PortfolioSnapshot]] = None,
    ) -> PerformanceMetrics:
        """
        Evaluates a completed portfolio backtest.
        """
        snapshots = portfolio.snapshots
        if not snapshots:
            # If no snapshots were recorded, record at least start and end
            snapshots = [
                PortfolioSnapshot("Start", portfolio.initial_capital, 0.0, portfolio.initial_capital, 0.0),
                PortfolioSnapshot("End", portfolio.cash, portfolio.holdings_value, portfolio.total_equity, portfolio.cumulative_return_pct),
            ]

        initial = portfolio.initial_capital
        ending = snapshots[-1].total_equity if snapshots else portfolio.total_equity
        total_return = (ending - initial) / initial if initial > 0 else 0.0

        # 1. CAGR
        cagr = self._calculate_cagr(snapshots, initial, ending)

        # 2. Daily/periodic returns & Volatility
        returns = self._calculate_period_returns(snapshots)
        ann_vol = self._calculate_annualized_volatility(returns)

        # 3. Sharpe Ratio: (CAGR - RiskFree) / AnnualizedVolatility
        if ann_vol > 1e-6:
            sharpe = (cagr - self.risk_free_rate) / ann_vol
        else:
            sharpe = 0.0

        # 4. Maximum Drawdown
        mdd = self._calculate_max_drawdown(snapshots)

        # 5. Trade stats
        win_count, loss_count, total_trades, win_rate = self._calculate_trade_stats(portfolio)

        # 6. Benchmark stats (if provided)
        bm_total_ret = None
        bm_cagr = None
        alpha = None
        beta = None

        if benchmark_snapshots and len(benchmark_snapshots) >= 2:
            bm_initial = benchmark_snapshots[0].total_equity
            bm_ending = benchmark_snapshots[-1].total_equity
            bm_total_ret = (bm_ending - bm_initial) / bm_initial
            bm_cagr = self._calculate_cagr(benchmark_snapshots, bm_initial, bm_ending)

            bm_returns = self._calculate_period_returns(benchmark_snapshots)
            alpha, beta = self._calculate_alpha_beta(returns, bm_returns, cagr, bm_cagr)

        return PerformanceMetrics(
            initial_capital=initial,
            ending_equity=ending,
            total_return_pct=total_return,
            cagr=cagr,
            annualized_volatility=ann_vol,
            sharpe_ratio=sharpe,
            max_drawdown_pct=mdd,
            total_trades=total_trades,
            winning_trades=win_count,
            losing_trades=loss_count,
            win_rate_pct=win_rate,
            benchmark_total_return_pct=bm_total_ret,
            benchmark_cagr=bm_cagr,
            alpha=alpha,
            beta=beta,
        )

    # -------------------------------------------------------------
    # Internal Calculation Methods
    # -------------------------------------------------------------
    def _calculate_cagr(
        self,
        snapshots: List[PortfolioSnapshot],
        initial: float,
        ending: float
    ) -> float:
        """Computes Compound Annual Growth Rate based on calendar days elapsed."""
        if len(snapshots) < 2 or initial <= 0 or ending <= 0:
            return 0.0

        start_date_str = snapshots[0].date
        end_date_str = snapshots[-1].date

        try:
            d_start = datetime.strptime(start_date_str[:10], "%Y-%m-%d")
            d_end = datetime.strptime(end_date_str[:10], "%Y-%m-%d")
            days = (d_end - d_start).days
        except (ValueError, TypeError):
            # Fallback assuming snapshots represent trading days (~252/year)
            days = max(1, int(len(snapshots) * (365.25 / 252)))

        if days <= 0:
            return 0.0

        years = days / 365.25
        return (ending / initial) ** (1.0 / years) - 1.0

    def _calculate_period_returns(self, snapshots: List[PortfolioSnapshot]) -> List[float]:
        """Calculates step-to-step percentage returns."""
        returns: List[float] = []
        for i in range(1, len(snapshots)):
            prev_eq = snapshots[i - 1].total_equity
            curr_eq = snapshots[i].total_equity
            if prev_eq > 0:
                returns.append((curr_eq - prev_eq) / prev_eq)
            else:
                returns.append(0.0)
        return returns

    def _calculate_annualized_volatility(self, returns: List[float], periods_per_year: int = 252) -> float:
        """Annualized standard deviation of returns."""
        if len(returns) < 2:
            return 0.0

        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
        stdev = math.sqrt(variance)
        return stdev * math.sqrt(periods_per_year)

    def _calculate_max_drawdown(self, snapshots: List[PortfolioSnapshot]) -> float:
        """
        Finds the maximum peak-to-trough decline.
        Returns a negative float (e.g. -0.25 = -25% drawdown).
        """
        if not snapshots:
            return 0.0

        peak = snapshots[0].total_equity
        max_dd = 0.0

        for s in snapshots:
            if s.total_equity > peak:
                peak = s.total_equity
            if peak > 0:
                dd = (s.total_equity - peak) / peak
                if dd < max_dd:
                    max_dd = dd

        return max_dd

    def _calculate_trade_stats(self, portfolio: Portfolio) -> Tuple[int, int, int, float]:
        """Calculates win/loss metrics from portfolio trade history."""
        # Simple matched trades estimate based on sells
        # Real trade evaluation checks sold positions vs their cost basis
        sells = [t for t in portfolio.trade_history if t.action.value == "SELL"]
        buys = [t for t in portfolio.trade_history if t.action.value == "BUY"]

        # Approximate winning trades by comparing exit price with average entry price
        # for that ticker
        buy_prices: dict = {}
        for b in buys:
            if b.ticker not in buy_prices:
                buy_prices[b.ticker] = []
            buy_prices[b.ticker].append(b.price)

        wins = 0
        losses = 0
        for s in sells:
            avg_entry = sum(buy_prices.get(s.ticker, [s.price])) / max(1, len(buy_prices.get(s.ticker, [s.price])))
            if s.price >= avg_entry:
                wins += 1
            else:
                losses += 1

        total = wins + losses
        win_rate = (wins / total) if total > 0 else 0.0
        return wins, losses, total, win_rate

    def _calculate_alpha_beta(
        self,
        strategy_returns: List[float],
        benchmark_returns: List[float],
        strategy_cagr: float,
        benchmark_cagr: float,
    ) -> Tuple[float, float]:
        """Calculates Beta and Jensen's Alpha relative to benchmark."""
        min_len = min(len(strategy_returns), len(benchmark_returns))
        if min_len < 3:
            return 0.0, 1.0

        s_ret = strategy_returns[:min_len]
        b_ret = benchmark_returns[:min_len]

        mean_s = sum(s_ret) / min_len
        mean_b = sum(b_ret) / min_len

        cov = sum((s_ret[i] - mean_s) * (b_ret[i] - mean_b) for i in range(min_len)) / (min_len - 1)
        var_b = sum((b_ret[i] - mean_b) ** 2 for i in range(min_len)) / (min_len - 1)

        if var_b > 1e-8:
            beta = cov / var_b
        else:
            beta = 1.0

        # Jensen's Alpha = CAGR_s - (r_f + Beta * (CAGR_b - r_f))
        alpha = strategy_cagr - (self.risk_free_rate + beta * (benchmark_cagr - self.risk_free_rate))
        return alpha, beta
