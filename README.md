# Magic Formula Stock Screener & Historical Backtester

A Python application designed to find and backtest top investment opportunities using **Joel Greenblatt's Magic Formula Investing** methodology, built with clean **Object-Oriented Programming (OOP)** design patterns.

---

## 🎯 What is the Magic Formula?

Joel Greenblatt's Magic Formula ranks companies based on two fundamental metrics:
1. **Earnings Yield (EY)**: How cheap the company is relative to operating earnings:
   $$\text{Earnings Yield} = \frac{\text{EBIT}}{\text{Enterprise Value (EV)}}$$
2. **Return on Capital (ROC)**: How efficiently the company uses its operational capital to generate profits:
   $$\text{Return on Capital} = \frac{\text{EBIT}}{\text{Net Working Capital} + \text{Net Fixed Assets}}$$

### Screening & Portfolio Rules:
- **Excludes Financials & Utilities**: Due to distinct debt/capital structures.
- **Excludes Micro-caps**: Defaults to filtering for $\text{Market Cap} \ge \$50\text{M}$.
- **Ranking**: Companies are ranked on both EY and ROC. The two ranks are added to form the **Combined Rank**. Stocks with the lowest combined score are the top picks.
- **Annual Rebalancing**: Hold equal-weight positions for 12 months, sell non-qualifying stocks, and rotate into new top picks.

---

## 🧠 OOP Architecture & Design Patterns

| Pattern / Concept | Where it is Used | Explanation |
| :--- | :--- | :--- |
| **Encapsulation & State Invariants** | [`src/magic_formula/backtest/portfolio.py`](file:///src/magic_formula/backtest/portfolio.py) | `Portfolio` controls cash invariants and two-pass rebalancing. `Position` computes mark-to-market PnL and weighted-average cost basis. |
| **Single Responsibility Principle** | [`src/magic_formula/backtest/analyzer.py`](file:///src/magic_formula/backtest/analyzer.py) | `PerformanceAnalyzer` isolates mathematical risk/return analytics (CAGR, Sharpe, MDD, Alpha/Beta) from portfolio execution. |
| **Facade & Coordinator** | [`src/magic_formula/backtest/engine.py`](file:///src/magic_formula/backtest/engine.py) | `BacktestEngine` coordinates the Screener, Data Providers, Portfolio, and Analyzer over simulation timelines. |
| **Strategy Pattern** | [`src/magic_formula/strategies/`](file:///src/magic_formula/strategies/) | `BaseRankingStrategy` abstract class with `StrictMagicFormulaStrategy` and `ProxyRankingStrategy` implementations. |
| **Polymorphism & DIP** | [`src/magic_formula/providers/`](file:///src/magic_formula/providers/) | `BaseDataProvider` interface with `MockDataProvider` (offline) and `YahooFinanceProvider` (live market data). |
| **Composite & Open/Closed** | [`src/magic_formula/filters/`](file:///src/magic_formula/filters/) | `FilterChain` composing `SectorFilter`, `MarketCapFilter`, and `PositiveEarningsFilter`. |

---

## 🚀 Quickstart & Usage

### 1. Offline Screener Demo (Zero Network Delay)
```bash
python main.py --provider mock
```

### 2. Side-by-Side Strategy Comparison (Strict vs. Modern Proxy)
```bash
python main.py --provider mock --compare
```

### 3. Historical Backtesting Simulation
```bash
# Offline backtest (2023 - 2025 with mock universe)
python main.py --provider mock --backtest

# Live historical backtest against S&P 500 (SPY benchmark)
python main.py --provider yahoo --backtest --start-date 2023-01-01 --end-date 2024-01-01 --limit 10 --top 5 --export-csv
```

### 4. Running Unit Tests
```bash
pytest -v tests/
```
*(All 23 unit tests pass across models, filters, providers, portfolio, analyzer, and backtest engine).*
