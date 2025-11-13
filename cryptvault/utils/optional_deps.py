"""
Optional Dependency Management

This module provides graceful handling for optional dependencies that enable
additional features but are not required for core functionality.

Features:
    - Lazy loading of optional packages
    - Clear error messages when optional features are unavailable
    - Feature availability checking
    - Dependency installation instructions

Example:
    >>> from cryptvault.utils.optional_deps import require_optional
    >>> torch = require_optional('torch', feature='LSTM predictions')
    >>> # If torch is not installed, raises ImportError with helpful message
"""

import importlib
import sys
from typing import Any, Dict, Optional, List


# Mapping of optional dependencies to their features and installation instructions
OPTIONAL_DEPENDENCIES: Dict[str, Dict[str, Any]] = {
    'torch': {
        'feature': 'LSTM neural network predictions',
        'install': 'pip install cryptvault[ml]',
        'alternative': 'Use scikit-learn models (included in base installation)',
        'package_name': 'torch',
    },
    'tensorflow': {
        'feature': 'TensorFlow-based LSTM predictions',
        'install': 'pip install tensorflow>=2.8.0',
        'alternative': 'Use PyTorch or scikit-learn models',
        'package_name': 'tensorflow',
    },
    'plotly': {
        'feature': 'Interactive web-based charts',
        'install': 'pip install cryptvault[viz]',
        'alternative': 'Use matplotlib charts (included in base installation)',
        'package_name': 'plotly',
    },
    'dash': {
        'feature': 'Interactive web dashboards',
        'install': 'pip install cryptvault[viz]',
        'alternative': 'Use command-line interface or matplotlib charts',
        'package_name': 'dash',
    },
    'websockets': {
        'feature': 'Real-time data streaming',
        'install': 'pip install cryptvault[streaming]',
        'alternative': 'Use polling with yfinance/ccxt (included in base)',
        'package_name': 'websockets',
    },
    'numba': {
        'feature': 'Accelerated numerical computations',
        'install': 'pip install cryptvault[fast]',
        'alternative': 'Use standard NumPy operations (slightly slower)',
        'package_name': 'numba',
    },
    'sqlalchemy': {
        'feature': 'Database persistence for analysis results',
        'install': 'pip install cryptvault[db]',
        'alternative': 'Use in-memory cache (included in base)',
        'package_name': 'sqlalchemy',
    },
    'redis': {
        'feature': 'High-performance caching with Redis',
        'install': 'pip install cryptvault[db]',
        'alternative': 'Use in-memory cache (included in base)',
        'package_name': 'redis',
    },
    'openpyxl': {
        'feature': 'Excel export functionality',
        'install': 'pip install cryptvault[export]',
        'alternative': 'Use JSON or CSV export (built-in)',
        'package_name': 'openpyxl',
    },
    'jinja2': {
        'feature': 'HTML report generation',
        'install': 'pip install cryptvault[export]',
        'alternative': 'Use console output or JSON export',
        'package_name': 'jinja2',
    },
    'requests': {
        'feature': 'Webhook notifications',
        'install': 'pip install cryptvault[notify]',
        'alternative': 'Use console output',
        'package_name': 'requests',
    },
}


class OptionalDependencyError(ImportError):
    """
    Exception raised when an optional dependency is not available.

    This exception provides helpful information about:
    - What feature requires the dependency
    - How to install the dependency
    - What alternatives are available
    """

    def __init__(
        self,
        package: str,
        feature: str,
        install_cmd: str,
        alternative: Optional[str] = None
    ):
        """
        Initialize OptionalDependencyError.

        Args:
            package: Name of the missing package
            feature: Feature that requires this package
            install_cmd: Command to install the package
            alternative: Alternative approach if package not installed
        """
        message = (
            f"\n{'='*70}\n"
            f"Optional Dependency Not Available: {package}\n"
            f"{'='*70}\n\n"
            f"Feature: {feature}\n\n"
            f"To enable this feature, install the required package:\n"
            f"  {install_cmd}\n"
        )

        if alternative:
            message += f"\nAlternative: {alternative}\n"

        message += f"\n{'='*70}\n"

        super().__init__(message)
        self.package = package
        self.feature = feature
        self.install_cmd = install_cmd
        self.alternative = alternative


def is_available(package: str) -> bool:
    """
    Check if an optional package is available.

    Args:
        package: Name of the package to check

    Returns:
        True if package is installed and importable, False otherwise

    Example:
        >>> if is_available('torch'):
        ...     print("LSTM predictions available")
        ... else:
        ...     print("Using scikit-learn models")
    """
    try:
        importlib.import_module(package)
        return True
    except ImportError:
        return False


def require_optional(
    package: str,
    feature: Optional[str] = None,
    install_cmd: Optional[str] = None,
    alternative: Optional[str] = None
) -> Any:
    """
    Import an optional package or raise a helpful error.

    This function attempts to import an optional package. If the package
    is not available, it raises an OptionalDependencyError with helpful
    information about how to install it and what alternatives exist.

    Args:
        package: Name of the package to import
        feature: Description of the feature requiring this package
        install_cmd: Command to install the package
        alternative: Alternative approach if package not available

    Returns:
        The imported module

    Raises:
        OptionalDependencyError: If package is not available

    Example:
        >>> torch = require_optional('torch', feature='LSTM predictions')
        >>> model = torch.nn.LSTM(input_size=10, hidden_size=20)
    """
    # Get package info from registry if available
    if package in OPTIONAL_DEPENDENCIES:
        info = OPTIONAL_DEPENDENCIES[package]
        feature = feature or info['feature']
        install_cmd = install_cmd or info['install']
        alternative = alternative or info.get('alternative')
        package_name = info['package_name']
    else:
        package_name = package
        feature = feature or f"Feature requiring {package}"
        install_cmd = install_cmd or f"pip install {package}"

    try:
        return importlib.import_module(package_name)
    except ImportError as e:
        raise OptionalDependencyError(
            package=package,
            feature=feature,
            install_cmd=install_cmd,
            alternative=alternative
        ) from e


def get_available_features() -> Dict[str, bool]:
    """
    Get a dictionary of all optional features and their availability.

    Returns:
        Dictionary mapping feature names to availability status

    Example:
        >>> features = get_available_features()
        >>> for feature, available in features.items():
        ...     status = "✓" if available else "✗"
        ...     print(f"{status} {feature}")
    """
    features = {}
    for package, info in OPTIONAL_DEPENDENCIES.items():
        feature_name = info['feature']
        features[feature_name] = is_available(info['package_name'])
    return features


def print_feature_status() -> None:
    """
    Print a formatted table of optional features and their availability.

    This is useful for diagnostics and helping users understand what
    features are available in their installation.

    Example:
        >>> print_feature_status()
        CryptVault Optional Features
        ============================
        ✓ LSTM neural network predictions
        ✗ Interactive web-based charts
        ✓ Accelerated numerical computations
    """
    print("\nCryptVault Optional Features")
    print("=" * 70)

    features = get_available_features()
    for feature, available in sorted(features.items()):
        status = "✓" if available else "✗"
        print(f"{status} {feature}")

    print("=" * 70)
    print("\nTo install optional features:")
    print("  pip install cryptvault[ml]        # Machine learning features")
    print("  pip install cryptvault[viz]       # Visualization features")
    print("  pip install cryptvault[streaming] # Real-time data")
    print("  pip install cryptvault[fast]      # Performance optimizations")
    print("  pip install cryptvault[db]        # Database support")
    print("  pip install cryptvault[export]    # Export formats")
    print("  pip install cryptvault[notify]    # Notifications")
    print("  pip install cryptvault[full]      # All optional features")
    print()


def get_missing_dependencies(feature_group: str) -> List[str]:
    """
    Get list of missing dependencies for a feature group.

    Args:
        feature_group: Feature group name (e.g., 'ml', 'viz', 'streaming')

    Returns:
        List of missing package names

    Example:
        >>> missing = get_missing_dependencies('ml')
        >>> if missing:
        ...     print(f"Missing packages: {', '.join(missing)}")
    """
    feature_groups = {
        'ml': ['torch'],
        'viz': ['plotly', 'dash'],
        'streaming': ['websockets'],
        'fast': ['numba'],
        'db': ['sqlalchemy', 'redis'],
        'export': ['openpyxl', 'jinja2'],
        'notify': ['requests'],
    }

    packages = feature_groups.get(feature_group, [])
    return [pkg for pkg in packages if not is_available(pkg)]


# Cache for imported optional modules to avoid repeated imports
_optional_module_cache: Dict[str, Any] = {}


def try_import(package: str, default: Any = None) -> Any:
    """
    Try to import a package, returning default if not available.

    This is useful when you want to gracefully degrade functionality
    without raising an exception.

    Args:
        package: Name of the package to import
        default: Value to return if import fails (default: None)

    Returns:
        The imported module or the default value

    Example:
        >>> torch = try_import('torch')
        >>> if torch is not None:
        ...     # Use PyTorch
        ...     model = torch.nn.LSTM(10, 20)
        ... else:
        ...     # Use alternative
        ...     model = SklearnModel()
    """
    if package in _optional_module_cache:
        return _optional_module_cache[package]

    try:
        module = importlib.import_module(package)
        _optional_module_cache[package] = module
        return module
    except ImportError:
        return default


def check_feature_requirements(feature: str) -> bool:
    """
    Check if all requirements for a feature are met.

    Args:
        feature: Feature name to check

    Returns:
        True if all requirements are met, False otherwise

    Example:
        >>> if check_feature_requirements('LSTM neural network predictions'):
        ...     print("LSTM predictions available")
        ... else:
        ...     print("Install torch for LSTM predictions")
    """
    for package, info in OPTIONAL_DEPENDENCIES.items():
        if info['feature'] == feature:
            return is_available(info['package_name'])
    return False
