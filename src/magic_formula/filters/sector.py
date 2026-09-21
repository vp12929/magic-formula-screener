"""
sector.py
---------
Sector exclusion filter (Excludes Financials and Utilities).

OOP Concept: Encapsulating Business Rules
- Magic Formula excludes Financials (different debt structure) and Utilities (regulated rates of return).
"""

from typing import Set
from magic_formula.models.company import Company
from magic_formula.filters.base import BaseFilter


class SectorFilter(BaseFilter):
    """Filters out companies from specified sectors (defaults: Financials and Utilities)."""

    DEFAULT_EXCLUDED_SECTORS = {
        "financial services",
        "financials",
        "banking",
        "insurance",
        "utilities",
    }

    def __init__(self, excluded_sectors: Set[str] = None):
        if excluded_sectors is None:
            self.excluded_sectors = {s.lower() for s in self.DEFAULT_EXCLUDED_SECTORS}
        else:
            self.excluded_sectors = {s.lower() for s in excluded_sectors}

    @property
    def name(self) -> str:
        return "Sector Exclusion Filter"

    def passes(self, company: Company) -> bool:
        company_sector = company.sector.lower()
        return not any(excluded in company_sector for excluded in self.excluded_sectors)

    def rejection_reason(self, company: Company) -> str:
        return f"Sector '{company.sector}' is excluded by Magic Formula rules"
