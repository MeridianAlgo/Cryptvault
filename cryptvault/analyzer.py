"""
DEPRECATED: This module is deprecated and will be removed in a future version.

Please use cryptvault.core.analyzer instead:
    from cryptvault.core.analyzer import PatternAnalyzer

This file is kept for backward compatibility only.
"""

import warnings
from .core.analyzer import PatternAnalyzer, AnalysisResult, ResultValidator

warnings.warn(
    "cryptvault.analyzer is deprecated. Use cryptvault.core.analyzer instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['PatternAnalyzer', 'AnalysisResult', 'ResultValidator']
