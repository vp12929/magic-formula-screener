"""
helpers.py
----------
Utility functions for financial filters and CLI inputs.
"""

from typing import Union


def parse_currency(val: Union[str, float, int]) -> float:
    """
    Parses human-friendly currency strings into float numbers.
    
    Examples:
        "50M" or "50m"   -> 50,000,000.0
        "2B" or "2b"     -> 2,000,000,000.0
        "1.5B"           -> 1,500,000,000.0
        "500K" or "500k" -> 500,000.0
        "50000000"       -> 50,000,000.0
        50000000         -> 50,000,000.0
    """
    if isinstance(val, (int, float)):
        return float(val)

    s = str(val).strip().upper().replace(",", "").replace("$", "")
    if not s:
        return 0.0

    multipliers = {
        "K": 1_000.0,
        "M": 1_000_000.0,
        "B": 1_000_000_000.0,
        "T": 1_000_000_000_000.0,
    }

    last_char = s[-1]
    if last_char in multipliers:
        multiplier = multipliers[last_char]
        num_part = s[:-1].strip()
        return float(num_part) * multiplier

    return float(s)
