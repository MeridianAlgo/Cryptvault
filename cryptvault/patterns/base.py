"""
Base Pattern Detector

Abstract base class for all pattern detectors with common utilities.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import numpy as np

from ..data.models import PriceDataFrame


@dataclass
class DetectedPattern:
    """Detected pattern result."""
    pattern_type: str
    category: str
    confidence: float
    start_time: datetime
    end_time: datetime
    start_index: int
    end_index: int
    key_levels: Dict[str, float]
    description: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BasePatternDetector(ABC):
    """Abstract base for pattern detectors."""

    def __init__(self) -> None:
        self.min_pattern_length = 10
        self.max_pattern_length = 100

    @abstractmethod
    def detect(
        self,
        data: PriceDataFrame,
        sensitivity: float = 0.5
    ) -> List[DetectedPattern]:
        """Detect patterns in price data."""
        pass

    @abstractmethod
    def get_pattern_types(self) -> List[str]:
        """Get list of pattern types this detector can find."""
        pass

    def _calculate_confidence(
        self,
        factors: List[float],
        weights: List[float] = None
    ) -> float:
        """Calculate weighted confidence score."""
        if weights is None:
            weights = [1.0] * len(factors)

        if len(factors) != len(weights):
            raise ValueError("Factors and weights must have same length")

        weighted_sum = sum(f * w for f, w in zip(factors, weights))
        weight_sum = sum(weights)

        return max(0.0, min(1.0, weighted_sum / weight_sum))

    def _filter_overlapping(
        self,
        patterns: List[DetectedPattern]
    ) -> List[DetectedPattern]:
        """Filter overlapping patterns, keeping highest confidence."""
        if not patterns:
            return patterns

        sorted_patterns = sorted(patterns, key=lambda p: p.confidence, reverse=True)
        filtered = []

        for pattern in sorted_patterns:
            overlaps = False
            for accepted in filtered:
                overlap_start = max(pattern.start_index, accepted.start_index)
                overlap_end = min(pattern.end_index, accepted.end_index)

                if overlap_start < overlap_end:
                    overlap_length = overlap_end - overlap_start
                    pattern_length = pattern.end_index - pattern.start_index

                    if overlap_length > pattern_length * 0.5:
                        overlaps = True
                        break

            if not overlaps:
                filtered.append(pattern)

        return filtered
