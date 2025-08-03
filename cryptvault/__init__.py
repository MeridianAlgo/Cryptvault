"""
Crypto Chart Pattern Analyzer

A terminal-based cryptocurrency chart pattern analyzer that identifies technical analysis patterns
without requiring external APIs.
"""

__version__ = "1.0.0"
__author__ = "Crypto Chart Analyzer"

from .data.models import PricePoint, PriceDataFrame
from .patterns.detector import PatternDetector
from .visualization.terminal_chart import TerminalChart

__all__ = [
    "PricePoint",
    "PriceDataFrame", 
    "PatternDetector",
    "TerminalChart"
]