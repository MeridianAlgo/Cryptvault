"""
Custom Exception Hierarchy

This module defines all custom exceptions used throughout CryptVault.
All exceptions inherit from CryptVaultError for easy catching and handling.

Exception Hierarchy:
    CryptVaultError
    ├── ConfigurationError
    ├── ValidationError
    │   ├── InvalidTickerError
    │   ├── InvalidDateRangeError
    │   └── InvalidIntervalError
    ├── DataError
    │   ├── DataFetchError
    │   │   ├── APIError
    │   │   ├── NetworkError
    │   │   └── RateLimitError
    │   ├── DataValidationError
    │   └── InsufficientDataError
    ├── AnalysisError
    │   ├── PatternDetectionError
    │   ├── MLPredictionError
    │   └── IndicatorCalculationError
    └── CacheError

Example:
    >>> from cryptvault.exceptions import DataFetchError
    >>> try:
    ...     data = fetch_data('INVALID')
    ... except DataFetchError as e:
    ...     logger.error(f"Failed to fetch data: {e}")
"""

from typing import Optional, Dict, Any


class CryptVaultError(Exception):
    """
    Base exception for all CryptVault errors.

    All custom exceptions in CryptVault inherit from this class,
    allowing for easy catching of all CryptVault-specific errors.

    Attributes:
        message: Error message
        details: Additional error details
        original_error: Original exception if this wraps another exception

    Example:
        >>> try:
        ...     # Some operation
        ...     pass
        ... except CryptVaultError as e:
        ...     print(f"CryptVault error: {e}")
        ...     if e.details:
        ...         print(f"Details: {e.details}")
    """

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ):
        """
        Initialize CryptVault error.

        Args:
            message: Human-readable error message
            details: Additional error details (optional)
            original_error: Original exception if wrapping (optional)
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.original_error = original_error

    def __str__(self) -> str:
        """Return string representation of error."""
        if self.details:
            details_str = ', '.join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message

    def __repr__(self) -> str:
        """Return detailed representation of error."""
        return f"{self.__class__.__name__}(message='{self.message}', details={self.details})"


# Configuration Errors

class ConfigurationError(CryptVaultError):
    """
    Raised when there is a configuration error.

    This includes invalid configuration values, missing required configuration,
    or configuration validation failures.

    Example:
        >>> raise ConfigurationError(
        ...     "Invalid timeout value",
        ...     details={'timeout': -1, 'expected': 'positive integer'}
        ... )
    """
    pass


# Validation Errors

class ValidationError(CryptVaultError):
    """
    Base class for input validation errors.

    Raised when user input or data fails validation checks.

    Example:
        >>> raise ValidationError(
        ...     "Invalid input",
        ...     details={'field': 'symbol', 'value': '123', 'reason': 'must be alphabetic'}
        ... )
    """
    pass


class InvalidTickerError(ValidationError):
    """
    Raised when a ticker symbol is invalid or unsupported.

    Example:
        >>> raise InvalidTickerError(
        ...     "Ticker symbol not supported",
        ...     details={'symbol': 'INVALID', 'supported': ['BTC', 'ETH', 'AAPL']}
        ... )
    """
    pass


class InvalidDateRangeError(ValidationError):
    """
    Raised when a date range is invalid.

    This includes cases where start date is after end date, dates are in the future,
    or the date range is too large or too small.

    Example:
        >>> raise InvalidDateRangeError(
        ...     "Start date must be before end date",
        ...     details={'start': '2024-01-01', 'end': '2023-01-01'}
        ... )
    """
    pass


class InvalidIntervalError(ValidationError):
    """
    Raised when a time interval is invalid.

    Example:
        >>> raise InvalidIntervalError(
        ...     "Invalid interval",
        ...     details={'interval': '2d', 'valid': ['1m', '5m', '1h', '1d', '1wk']}
        ... )
    """
    pass


# Data Errors

class DataError(CryptVaultError):
    """
    Base class for data-related errors.

    Includes errors related to data fetching, validation, and processing.
    """
    pass


class DataFetchError(DataError):
    """
    Raised when data cannot be fetched from external source.

    This is a general error for data fetching failures. More specific
    errors (APIError, NetworkError, RateLimitError) should be used when possible.

    Example:
        >>> raise DataFetchError(
        ...     "Failed to fetch data from API",
        ...     details={'source': 'yfinance', 'symbol': 'BTC', 'attempts': 3}
        ... )
    """
    pass


class APIError(DataFetchError):
    """
    Raised when an API returns an error response.

    Example:
        >>> raise APIError(
        ...     "API returned error",
        ...     details={'status_code': 404, 'message': 'Symbol not found'}
        ... )
    """
    pass


class NetworkError(DataFetchError):
    """
    Raised when a network error occurs during data fetching.

    This includes connection timeouts, DNS failures, and other network issues.

    Example:
        >>> raise NetworkError(
        ...     "Connection timeout",
        ...     details={'url': 'https://api.example.com', 'timeout': 30}
        ... )
    """
    pass


class RateLimitError(DataFetchError):
    """
    Raised when API rate limit is exceeded.

    Example:
        >>> raise RateLimitError(
        ...     "API rate limit exceeded",
        ...     details={'limit': 100, 'period': 60, 'retry_after': 45}
        ... )
    """
    pass


class DataValidationError(DataError):
    """
    Raised when data fails validation checks.

    This includes missing required fields, invalid data types, or data
    that doesn't meet quality requirements.

    Example:
        >>> raise DataValidationError(
        ...     "Missing required field",
        ...     details={'field': 'close', 'data_points': 100}
        ... )
    """
    pass


class InsufficientDataError(DataError):
    """
    Raised when there is insufficient data for analysis.

    Example:
        >>> raise InsufficientDataError(
        ...     "Insufficient data points for analysis",
        ...     details={'required': 50, 'available': 30, 'symbol': 'BTC'}
        ... )
    """
    pass


# Analysis Errors

class AnalysisError(CryptVaultError):
    """
    Base class for analysis-related errors.

    Includes errors during pattern detection, ML prediction, and indicator calculation.
    """
    pass


class PatternDetectionError(AnalysisError):
    """
    Raised when pattern detection fails.

    Example:
        >>> raise PatternDetectionError(
        ...     "Failed to detect patterns",
        ...     details={'pattern_type': 'double_top', 'reason': 'insufficient peaks'}
        ... )
    """
    pass


class MLPredictionError(AnalysisError):
    """
    Raised when ML prediction fails.

    Example:
        >>> raise MLPredictionError(
        ...     "ML model prediction failed",
        ...     details={'model': 'ensemble', 'reason': 'feature extraction failed'}
        ... )
    """
    pass


class IndicatorCalculationError(AnalysisError):
    """
    Raised when technical indicator calculation fails.

    Example:
        >>> raise IndicatorCalculationError(
        ...     "Failed to calculate RSI",
        ...     details={'indicator': 'RSI', 'period': 14, 'data_points': 10}
        ... )
    """
    pass


# Cache Errors

class CacheError(CryptVaultError):
    """
    Raised when cache operations fail.

    This includes cache read/write failures, cache corruption, or cache
    configuration errors.

    Example:
        >>> raise CacheError(
        ...     "Failed to write to cache",
        ...     details={'key': 'BTC_60d_1d', 'backend': 'disk'}
        ... )
    """
    pass


# Utility Functions

def wrap_exception(
    original_error: Exception,
    new_exception_class: type,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> CryptVaultError:
    """
    Wrap an exception in a CryptVault exception.

    This is useful for converting third-party exceptions into CryptVault
    exceptions while preserving the original error information.

    Args:
        original_error: Original exception to wrap
        new_exception_class: CryptVault exception class to use
        message: New error message
        details: Additional error details

    Returns:
        New CryptVault exception wrapping the original

    Example:
        >>> try:
        ...     # Some third-party library call
        ...     api.fetch_data()
        ... except requests.RequestException as e:
        ...     raise wrap_exception(
        ...         e,
        ...         NetworkError,
        ...         "Failed to fetch data from API",
        ...         details={'url': 'https://api.example.com'}
        ...     )
    """
    return new_exception_class(
        message=message,
        details=details,
        original_error=original_error
    )


def format_error_message(error: CryptVaultError, include_details: bool = True) -> str:
    """
    Format error message for display to user.

    Args:
        error: CryptVault exception
        include_details: Whether to include error details

    Returns:
        Formatted error message

    Example:
        >>> error = DataFetchError("API error", details={'status': 404})
        >>> message = format_error_message(error)
        >>> print(message)
        DataFetchError: API error (status=404)
    """
    message = f"{error.__class__.__name__}: {error.message}"

    if include_details and error.details:
        details_str = ', '.join(f"{k}={v}" for k, v in error.details.items())
        message += f" ({details_str})"

    if error.original_error:
        message += f"\nCaused by: {type(error.original_error).__name__}: {str(error.original_error)}"

    return message
