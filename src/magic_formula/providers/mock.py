"""
mock.py
-------
Mock data provider with a rich set of predefined companies for offline testing.

OOP Concept: Test Doubles & Mocking
- Provides immediate, deterministic responses for testing algorithms.
- Demonstrates how OOP polymorphism enables zero-network testing without changing
  a single line of core screening logic.
"""

from typing import Dict, List, Optional
from magic_formula.models.company import Company
from magic_formula.models.financials import FinancialStatement
from magic_formula.providers.base import BaseDataProvider


class MockDataProvider(BaseDataProvider):
    """Offline mock provider that returns a curated database of 25 companies."""

    def __init__(self):
        self._database: Dict[str, Company] = self._build_mock_database()

    def fetch_company(self, ticker: str) -> Optional[Company]:
        return self._database.get(ticker.upper().strip())

    def get_all_tickers(self) -> List[str]:
        return list(self._database.keys())

    def _build_mock_database(self) -> Dict[str, Company]:
        """Builds a diverse collection of companies across various industries."""
        raw_data = [
            # --- Top Tier Magic Formula Candidates ---
            ("AAPL", "Apple Inc.", "Technology", "Consumer Electronics", 3_000_000_000_000, 120_000_000_000, 3_050_000_000_000, 100_000_000_000, 130_000_000_000, 140_000_000_000, 145_000_000_000, 45_000_000_000, 350_000_000_000, 100_000_000_000, 60_000_000_000, 30_000_000_000),
            ("GOOGL", "Alphabet Inc.", "Communication Services", "Internet Content", 2_000_000_000_000, 95_000_000_000, 1_900_000_000_000, 80_000_000_000, 110_000_000_000, 160_000_000_000, 80_000_000_000, 115_000_000_000, 400_000_000_000, 30_000_000_000, 280_000_000_000, 110_000_000_000),
            ("MSFT", "Microsoft Corp.", "Technology", "Software", 3_100_000_000_000, 115_000_000_000, 3_050_000_000_000, 90_000_000_000, 130_000_000_000, 200_000_000_000, 110_000_000_000, 120_000_000_000, 480_000_000_000, 80_000_000_000, 250_000_000_000, 80_000_000_000),
            ("NVDA", "NVIDIA Corp.", "Technology", "Semiconductors", 2_800_000_000_000, 65_000_000_000, 2_750_000_000_000, 55_000_000_000, 70_000_000_000, 65_000_000_000, 20_000_000_000, 15_000_000_000, 90_000_000_000, 10_000_000_000, 60_000_000_000, 30_000_000_000),
            ("UNH", "UnitedHealth Group", "Healthcare", "Healthcare Plans", 450_000_000_000, 32_000_000_000, 500_000_000_000, 22_000_000_000, 36_000_000_000, 80_000_000_000, 70_000_000_000, 25_000_000_000, 280_000_000_000, 65_000_000_000, 90_000_000_000, 30_000_000_000),
            ("COST", "Costco Wholesale", "Consumer Defensive", "Discount Stores", 380_000_000_000, 9_500_000_000, 385_000_000_000, 7_000_000_000, 11_500_000_000, 35_000_000_000, 33_000_000_000, 26_000_000_000, 70_000_000_000, 9_000_000_000, 26_000_000_000, 13_000_000_000),
            ("PG", "Procter & Gamble", "Consumer Defensive", "Household Products", 390_000_000_000, 19_000_000_000, 420_000_000_000, 15_000_000_000, 22_000_000_000, 24_000_000_000, 33_000_000_000, 22_000_000_000, 120_000_000_000, 35_000_000_000, 48_000_000_000, 8_000_000_000),
            ("HD", "Home Depot", "Consumer Cyclical", "Home Improvement", 360_000_000_000, 21_000_000_000, 400_000_000_000, 15_000_000_000, 24_000_000_000, 28_000_000_000, 21_000_000_000, 26_000_000_000, 75_000_000_000, 45_000_000_000, 2_000_000_000, 3_000_000_000),
            ("ABBV", "AbbVie Inc.", "Healthcare", "Drug Manufacturers", 320_000_000_000, 16_000_000_000, 375_000_000_000, 6_000_000_000, 23_000_000_000, 23_000_000_000, 35_000_000_000, 7_000_000_000, 130_000_000_000, 65_000_000_000, 10_000_000_000, 12_000_000_000),
            ("NKE", "NIKE Inc.", "Consumer Cyclical", "Footwear & Accessories", 120_000_000_000, 6_500_000_000, 125_000_000_000, 5_500_000_000, 7_500_000_000, 16_000_000_000, 9_000_000_000, 5_000_000_000, 38_000_000_000, 12_000_000_000, 14_000_000_000, 7_000_000_000),
            ("TXN", "Texas Instruments", "Technology", "Semiconductors", 180_000_000_000, 7_000_000_000, 185_000_000_000, 6_500_000_000, 8_000_000_000, 10_000_000_000, 3_000_000_000, 12_000_000_000, 30_000_000_000, 13_000_000_000, 17_000_000_000, 8_000_000_000),
            ("LOW", "Lowe's Companies", "Consumer Cyclical", "Home Improvement", 140_000_000_000, 11_000_000_000, 175_000_000_000, 7_700_000_000, 13_000_000_000, 20_000_000_000, 16_000_000_000, 19_000_000_000, 48_000_000_000, 36_000_000_000, -14_000_000_000, 2_000_000_000),
            
            # --- High Value / Deep Value Candidates ---
            ("PFE", "Pfizer Inc.", "Healthcare", "Drug Manufacturers", 160_000_000_000, 10_000_000_000, 215_000_000_000, 6_000_000_000, 15_000_000_000, 50_000_000_000, 40_000_000_000, 35_000_000_000, 220_000_000_000, 62_000_000_000, 85_000_000_000, 7_000_000_000),
            ("BMY", "Bristol-Myers Squibb", "Healthcare", "Drug Manufacturers", 100_000_000_000, 8_000_000_000, 140_000_000_000, 4_000_000_000, 12_000_000_000, 25_000_000_000, 20_000_000_000, 10_000_000_000, 95_000_000_000, 45_000_000_000, 22_000_000_000, 7_000_000_000),
            ("VZ", "Verizon Communications", "Communication Services", "Telecom", 170_000_000_000, 30_000_000_000, 340_000_000_000, 12_000_000_000, 48_000_000_000, 40_000_000_000, 50_000_000_000, 110_000_000_000, 380_000_000_000, 170_000_000_000, 95_000_000_000, 4_000_000_000),

            # --- Financials (Should be excluded by Sector Filter) ---
            ("JPM", "JPMorgan Chase & Co.", "Financial Services", "Diversified Banks", 550_000_000_000, 60_000_000_000, 550_000_000_000, 50_000_000_000, 65_000_000_000, 4_000_000_000_000, 3_700_000_000_000, 15_000_000_000, 4_000_000_000_000, 300_000_000_000, 320_000_000_000, 500_000_000_000),
            ("BAC", "Bank of America", "Financial Services", "Diversified Banks", 300_000_000_000, 35_000_000_000, 300_000_000_000, 27_000_000_000, 38_000_000_000, 3_000_000_000_000, 2_700_000_000_000, 12_000_000_000, 3_000_000_000_000, 250_000_000_000, 280_000_000_000, 350_000_000_000),
            ("GS", "Goldman Sachs Group", "Financial Services", "Capital Markets", 150_000_000_000, 14_000_000_000, 150_000_000_000, 11_000_000_000, 16_000_000_000, 1_600_000_000_000, 1_450_000_000_000, 8_000_000_000, 1_600_000_000_000, 300_000_000_000, 115_000_000_000, 200_000_000_000),

            # --- Utilities (Should be excluded by Sector Filter) ---
            ("NEE", "NextEra Energy", "Utilities", "Regulated Electric", 160_000_000_000, 9_000_000_000, 235_000_000_000, 7_500_000_000, 13_000_000_000, 15_000_000_000, 22_000_000_000, 120_000_000_000, 175_000_000_000, 78_000_000_000, 50_000_000_000, 2_000_000_000),
            ("DUK", "Duke Energy", "Utilities", "Regulated Electric", 85_000_000_000, 5_500_000_000, 165_000_000_000, 4_200_000_000, 8_000_000_000, 10_000_000_000, 14_000_000_000, 95_000_000_000, 180_000_000_000, 80_000_000_000, 52_000_000_000, 1_000_000_000),

            # --- Microcaps (< $50M - Should be excluded by Market Cap Filter) ---
            ("TINY1", "Micro Innovation Inc.", "Technology", "Nanotech", 25_000_000, 5_000_000, 24_000_000, 4_000_000, 6_000_000, 8_000_000, 3_000_000, 2_000_000, 12_000_000, 1_000_000, 8_000_000, 3_000_000),
            ("TINY2", "Nano Solar Tech", "Technology", "Solar", 35_000_000, 7_000_000, 30_000_000, 5_500_000, 8_000_000, 12_000_000, 5_000_000, 4_000_000, 20_000_000, 2_000_000, 14_000_000, 7_000_000),
        ]

        db: Dict[str, Company] = {}
        for row in raw_data:
            (ticker, name, sector, industry, mcap, ebit, ev, net_inc, ebitda,
             curr_assets, curr_liab, fixed_assets, tot_assets, tot_debt, tot_equity, cash) = row

            fin = FinancialStatement(
                ebit=float(ebit),
                enterprise_value=float(ev),
                market_cap=float(mcap),
                net_income=float(net_inc),
                ebitda=float(ebitda),
                current_assets=float(curr_assets),
                current_liabilities=float(curr_liab),
                net_fixed_assets=float(fixed_assets),
                total_assets=float(tot_assets),
                total_debt=float(tot_debt),
                total_equity=float(tot_equity),
                cash_and_equivalents=float(cash),
            )

            db[ticker] = Company(
                ticker=ticker,
                name=name,
                sector=sector,
                industry=industry,
                market_cap=float(mcap),
                financials=fin,
            )

        return db
