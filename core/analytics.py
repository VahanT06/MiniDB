"""
Database Analytics and Statistical Computation Module

This module provides the `Analytics` class, which serves as the data metrics engine.
It extracts multi-type record attributes from a primary database
store to compute statistical descriptors and value distribution profiles.

Key Capabilities:
    - Basic descriptive statistics (Minimum, Maximum, Average, Median).
    - Frequency analysis and distribution counts for categorical attributes.
    - Custom slice-ranking (Top K) of records based on target numeric attributes.
"""


from collections import Counter
from statistics import median
from typing import Any, List, Optional


class Analytics:
    """
    Performs analytical operations on the database.
    """

    def __init__(self, database):
        self._db = database

    def _numeric_values(self, attribute: str) -> List[float]:
        """Helper to extract all numeric values for a given attribute."""
        vals = []
        for rec in self._db._data.values():
            if rec is None:
                continue
            v = rec.get(attribute)
            if isinstance(v, (int, float)):
                vals.append(float(v))
        return vals

    def _all_values(self, attribute: str) -> List[Any]:
        """Helper to extract all values (including strings) for a given attribute."""
        vals = []
        for rec in self._db._data.values():
            if rec is None:
                continue
            if attribute in rec:
                v = rec[attribute]
                if v is not None:
                    vals.append(v)
        return vals

    def min_value(self, attribute: str) -> Optional[float]:
        values = self._numeric_values(attribute)
        if not values:
            return None
        return min(values)

    def max_value(self, attribute: str) -> Optional[float]:
        values = self._numeric_values(attribute)
        if not values:
            return None
        return max(values)

    def average_value(self, attribute: str) -> Optional[float]:
        values = self._numeric_values(attribute)
        if not values:
            return None
        return sum(values) / len(values)

    def median_value(self, attribute: str) -> Optional[float]:
        values = self._numeric_values(attribute)
        if not values:
            return None
        return float(median(values))

    def top_k_by_count(self, attribute: str, k: int = 10):
        """Returns the top K most frequent values for a categorical attribute."""
        values = self._all_values(attribute)
        counter = Counter(values)
        return counter.most_common(k)

    def top_k_by_numeric(self, attribute: str, k: int = 10, largest: bool = True):
        """Returns the top K records based on a numeric attribute value."""
        pairs = []
        for rec in self._db._data.values():
            if rec is None:
                continue
            v = rec.get(attribute)
            if isinstance(v, (int, float)):
                pairs.append((v, rec))

        if not pairs:
            return []

        pairs.sort(key=lambda x: x[0], reverse=largest)
        return pairs[:k]
