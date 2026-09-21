"""
base.py
-------
Defines the abstract base filter interface.

OOP Concept: Open/Closed Principle (OCP)
- We define a clear filter contract. New screening rules can be created by subclassing
  `BaseFilter` without modifying any existing filtering or screener code.
"""

from abc import ABC, abstractmethod
from typing import Optional
from magic_formula.models.company import Company


class BaseFilter(ABC):
    """Abstract Base Class for universe filtering rules."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the filter rule."""
        pass

    @abstractmethod
    def passes(self, company: Company) -> bool:
        """
        Returns True if the company meets the filter criteria, False otherwise.
        """
        pass

    def rejection_reason(self, company: Company) -> Optional[str]:
        """Optional explanation if the company is rejected."""
        if not self.passes(company):
            return f"Failed {self.name}"
        return None
