"""
base.py
-------
Defines abstract reporting interface.

OOP Concept: Single Responsibility & Presentation Layer Separation
- Decouples domain calculations from output formatting (Console, CSV, JSON).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from magic_formula.models.metrics import RankedCompany
from magic_formula.screener import ScreeningSummary


class BaseReporter(ABC):
    """Abstract Base Class for screening report generators."""

    @abstractmethod
    def report_ranked(self, results: List[RankedCompany], summary: Optional[ScreeningSummary] = None) -> None:
        """Outputs a list of ranked companies."""
        pass

    @abstractmethod
    def report_comparison(self, comparison_data: Dict[str, Any]) -> None:
        """Outputs a side-by-side strategy comparison."""
        pass
