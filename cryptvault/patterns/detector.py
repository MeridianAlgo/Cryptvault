"""Main pattern detector orchestrator - base implementation."""

from typing import List
from ..data.models import PriceDataFrame
from .types import DetectedPattern


class PatternDetector:
    """Main orchestrator for pattern detection - to be implemented."""
    
    def __init__(self):
        """Initialize pattern detector."""
        pass
    
    def detect_all_patterns(self, data: PriceDataFrame) -> List[DetectedPattern]:
        """Detect all patterns in the price data."""
        raise NotImplementedError("Pattern detection implementation pending")
    
    def detect_pattern_type(self, data: PriceDataFrame, pattern_type: str) -> List[DetectedPattern]:
        """Detect specific pattern type in the price data."""
        raise NotImplementedError("Specific pattern detection implementation pending")