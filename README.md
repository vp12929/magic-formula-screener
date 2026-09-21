# Magic Formula Stock Screener (Joel Greenblatt)

A Python application designed to find top investment opportunities using **Joel Greenblatt's Magic Formula Investing** methodology, built with clean **Object-Oriented Programming (OOP)** design patterns.

---

## 🎯 What is the Magic Formula?

Joel Greenblatt's Magic Formula ranks companies based on two fundamental metrics:
1. **Earnings Yield (EY)**: How cheap the company is relative to operating earnings:
   $$\text{Earnings Yield} = \frac{\text{EBIT}}{\text{Enterprise Value (EV)}}$$
2. **Return on Capital (ROC)**: How efficiently the company uses its operational capital to generate profits:
   $$\text{Return on Capital} = \frac{\text{EBIT}}{\text{Net Working Capital} + \text{Net Fixed Assets}}$$

### Screening Rules:
- **Excludes Financials & Utilities**: Due to distinct debt/capital structures.
- **Excludes Micro-caps**: Defaults to filtering for $\text{Market Cap} \ge \$50\text{M}$.
- **Ranking**: Companies are ranked on both EY and ROC. The two ranks are added to form the **Combined Rank**. Stocks with the lowest combined score are the top picks.

---

## 🧠 OOP Architecture & Design Patterns

| Pattern / Concept | Where it is Used | Explanation |
| :--- | :--- | :--- |
| **Encapsulation** | [`src/magic_formula/models/`](file:///src/magic_formula/models/) | Bundles financial attributes and computed `@property` getters inside `FinancialStatement` and `Company` objects. |
| **Strategy Pattern** | [`src/magic_formula/strategies/`](file:///src/magic_formula/strategies/) | `BaseRankingStrategy` abstract class with `StrictMagicFormulaStrategy` and `ProxyRankingStrategy` implementations. |
| **Polymorphism & DIP** | [`src/magic_formula/providers/`](file:///src/magic_formula/providers/) | `BaseDataProvider` interface with `MockDataProvider` (offline) and `YahooFinanceProvider` (live market data). |
| **Composite & Open/Closed** | [`src/magic_formula/filters/`](file:///src/magic_formula/filters/) | `FilterChain` composing `SectorFilter`, `MarketCapFilter`, and `PositiveEarningsFilter`. |
| **Presentation Separation** | [`src/magic_formula/reporters/`](file:///src/magic_formula/reporters/) | `ConsoleReporter` and `CsvReporter` isolate CLI and export formatting from domain logic. |

---

## 🚀 Quickstart & Usage

### 1. Offline Mock Demo (Zero Network Delay)
```bash
python main.py --provider mock
```

### 2. Side-by-Side Comparison (Strict vs. Modern Proxy)
```bash
python main.py --provider mock --compare
```

### 3. Live S&P Screening with Yahoo Finance
```bash
# Screen 30 companies from the curated universe
python main.py --provider yahoo --limit 30

# Screen S&P 500 universe, display top 20, and export to CSV
python main.py --provider yahoo --universe sp500 --limit 50 --export-csv
```

### 4. Running Unit Tests
```bash
pytest tests/
```

---

## 🐙 Connecting to GitHub

To publish this project to your GitHub account:

1. Create a new empty repository on [GitHub](https://github.com/new) (e.g. `magic-formula-screener`). Do not initialize with a README.
2. In your terminal inside this folder, run:
```bash
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<REPO_NAME>.git
git branch -M main
git push -u origin main
```
