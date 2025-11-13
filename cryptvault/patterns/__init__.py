"""
Pattern Detection Module

Comprehensive chart pattern detection for technical analysis.
"""

from .base import BasePatternDetector, DetectedPattern
from .reversal import ReversalPatternDetector
from .continuation import ContinuationPatternDetector
from .harmonic import HarmonicPatternDetector

__all__ = [
    'BasePatternDetector',
    'DetectedPattern',
    'ReversalPatternDetector',
    'ContinuationPatternDetector',
    'HarmonicPatternDetector',
]
