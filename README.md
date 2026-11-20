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
- **Market Capitalization Limits**: Filters micro-caps ($\ge \$50\text{M}$ default) or targets specific tiers (`small`, `mid`, `large`).
- **Tangible Capital Employed Limit**: Requires a minimum physical/working capital ($\ge \$10\text{M}$ default) to prevent distorted ROC calculations on asset-stripped firms.
- **Ranking**: Companies are ranked on both EY and ROC. The two ranks are added to form the **Combined Rank**. Stocks with the lowest combined score are the top picks.
- **Annual Rebalancing**: Hold equal-weight positions for 12 months, sell non-qualifying stocks, and rotate into new top picks.
- **Cash Dividend Accounting**: Automatically tracks cash dividend distributions on ex-dates, crediting cash balances and calculating Total Net Benefit ($\text{Capital Gains} + \text{Dividends} - \text{Fees}$).

---

## 🧠 OOP Architecture & Design Patterns

| Pattern / Concept | Where it is Used | Explanation |
| :--- | :--- | :--- |
| **Encapsulation & State Invariants** | [`src/magic_formula/backtest/portfolio.py`](file:///src/magic_formula/backtest/portfolio.py) | `Portfolio` controls cash invariants, two-pass rebalancing, and cash dividend crediting (`credit_dividend`). |
| **Single Responsibility Principle** | [`src/magic_formula/backtest/analyzer.py`](file:///src/magic_formula/backtest/analyzer.py) | `PerformanceAnalyzer` produces the Net Benefit breakdown ($\text{Capital Gains} + \text{Dividends} - \text{Fees}$) and risk analytics. |
| **Facade & Coordinator** | [`src/magic_formula/backtest/engine.py`](file:///src/magic_formula/backtest/engine.py) | `BacktestEngine` coordinates the Screener, Data Providers, Portfolio, Dividends, and Analyzer over simulation timelines. |
| **Configurable Rule Objects & Factory** | [`src/magic_formula/filters/market_cap.py`](file:///src/magic_formula/filters/market_cap.py) | `MarketCapFilter.from_tier()` constructs preset tier filters; accepts friendly strings like `50M` or `2B`. |
| **Domain Quality Filters** | [`src/magic_formula/filters/capital_employed.py`](file:///src/magic_formula/filters/capital_employed.py) | `MinCapitalEmployedFilter` ensures qualifying companies have tangible operational capital. |
| **Strategy Pattern** | [`src/magic_formula/strategies/`](file:///src/magic_formula/strategies/) | `BaseRankingStrategy` abstract class with `StrictMagicFormulaStrategy` and `ProxyRankingStrategy` implementations. |
| **Polymorphism & DIP** | [`src/magic_formula/providers/`](file:///src/magic_formula/providers/) | `BaseDataProvider` interface with `MockDataProvider` (offline) and `YahooFinanceProvider` (live market data). |
| **Composite & Open/Closed** | [`src/magic_formula/filters/`](file:///src/magic_formula/filters/) | `FilterChain` composing `SectorFilter`, `MarketCapFilter`, `PositiveEarningsFilter`, and `MinCapitalEmployedFilter`. |

---

## 🚀 Quickstart & Usage

### 1. Offline Screener Demo
```bash
python main.py --provider mock
```

### 2. Market Cap Filtering & Tiers
```bash
# Filter for Mid-Cap companies only ($2B - $10B)
python main.py --provider mock --cap-tier mid

# Custom market cap bounds ($500M to $5B) and minimum $25M operating capital
python main.py --provider mock --min-mcap 500M --max-mcap 5B --min-capital-employed 25M
```

### 3. Side-by-Side Strategy Comparison (Strict vs. Modern Proxy)
```bash
python main.py --provider mock --compare
```

### 4. Historical Backtesting Simulation
```bash
# Offline backtest (2023 - 2025 with mock universe)
python main.py --provider mock --backtest

# Live historical backtest against S&P 500 (SPY benchmark)
python main.py --provider yahoo --backtest --start-date 2023-01-01 --end-date 2024-01-01 --limit 10 --top 5 --export-csv
```

### 5. Running Unit Tests
```bash
pytest -v tests/
```
*(All 26 unit tests pass across models, filters, providers, portfolio, analyzer, and backtest engine).*
