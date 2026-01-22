"""
Pattern Detection Module

Comprehensive chart pattern detection for technical analysis.
"""

from .base import BasePatternDetector, DetectedPattern
from .continuation import ContinuationPatternDetector
from .harmonic import HarmonicPatternDetector
from .reversal import ReversalPatternDetector

__all__ = [
    "BasePatternDetector",
    "DetectedPattern",
    "ReversalPatternDetector",
    "ContinuationPatternDetector",
    "HarmonicPatternDetector",
]
