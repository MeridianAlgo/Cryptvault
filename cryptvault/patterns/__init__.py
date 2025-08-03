"""Pattern detection module for identifying chart patterns."""

from .detector import PatternDetector
from .types import PatternType, DetectedPattern
from .geometric import GeometricPatternAnalyzer
# from .technical import TechnicalIndicatorAnalyzer  # Moved to indicators module
# from .confidence import ConfidenceCalculator  # Integrated into pattern analyzers

__all__ = [
    "PatternDetector",
    "PatternType",
    "DetectedPattern",
    "GeometricPatternAnalyzer", 
    # "TechnicalIndicatorAnalyzer",  # Moved to indicators module
    # "ConfidenceCalculator"  # Integrated into pattern analyzers
]