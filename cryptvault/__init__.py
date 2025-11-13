"""
CryptVault - Advanced AI-Powered Cryptocurrency Analysis Platform

A comprehensive cryptocurrency and stock analysis platform with pattern detection,
machine learning predictions, and technical indicators.
"""

from cryptvault.__version__ import (
    __version__,
    __version_info__,
    __author__,
    __license__,
    __copyright__,
    __url__,
    __description__
)

from .data.models import PricePoint, PriceDataFrame
from .patterns.detector import PatternDetector
from .visualization.terminal_chart import TerminalChart
from .core.analyzer import PatternAnalyzer

# Optional dependency utilities
from .utils.optional_deps import (
    is_available,
    require_optional,
    get_available_features,
    print_feature_status,
    OptionalDependencyError
)

__all__ = [
    # Version info
    "__version__",
    "__version_info__",
    "__author__",
    "__license__",
    "__copyright__",
    "__url__",
    "__description__",
    # Core classes
    "PricePoint",
    "PriceDataFrame",
    "PatternDetector",
    "PatternAnalyzer",
    "TerminalChart",
    # Optional dependency utilities
    "is_available",
    "require_optional",
    "get_available_features",
    "print_feature_status",
    "OptionalDependencyError",
]
