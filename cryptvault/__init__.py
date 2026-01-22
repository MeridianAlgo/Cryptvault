"""
CryptVault - Advanced AI-Powered Cryptocurrency Analysis Platform

A comprehensive cryptocurrency and stock analysis platform with pattern detection,
machine learning predictions, and technical indicators.
"""

from cryptvault.__version__ import (
    __author__,
    __copyright__,
    __description__,
    __license__,
    __url__,
    __version__,
    __version_info__,
)

from .core.analyzer import PatternAnalyzer
from .data.models import PriceDataFrame, PricePoint
from .patterns.detector import PatternDetector

# Optional dependency utilities
from .utils.optional_deps import (
    OptionalDependencyError,
    get_available_features,
    is_available,
    print_feature_status,
    require_optional,
)
from .visualization.terminal_chart import TerminalChart

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
