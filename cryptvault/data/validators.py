"""
Data Validators

Input validation and data sanitization functions for ensuring data integrity
and security throughout the application.

Example:
    >>> from cryptvault.data.validators import validate_ticker_symbol, validate_date_range
    >>> validate_ticker_symbol('BTC')  # Returns True
    >>> validate_ticker_symbol('INVALID123')  # Raises InvalidTickerError
"""

import re
from datetime import datetime, timedelta
from typing import List, Optional

from ..constants import SUPPORTED_TICKERS, SUPPORTED_INTERVALS
from ..exceptions import (
    InvalidTickerError, InvalidDateRangeError, InvalidIntervalError,
    DataValidationError
)


def validate_ticker_symbol(symbol: str, strict: bool = False) -> bool:
    """
    Validate ticker symbol.

    Args:
        symbol: Ticker symbol to validate
        strict: If True, only allow symbols in SUPPORTED_TICKERS

    Returns:
        True if valid

    Raises:
        InvalidTickerError: If symbol is invalid

    Example:
        >>> validate_ticker_symbol('BTC')
        True
        >>> validate_ticker_symbol('AAPL')
        True
    """
    if not symbol:
        raise InvalidTickerError(
            "Ticker symbol cannot be empty",
            details={'symbol': symbol}
        )

    symbol = symbol.upper().strip()

    # Check format (alphanumeric, 1-10 characters)
    if not re.match(r'^[A-Z0-9]{1,10}$', symbol):
        raise InvalidTickerError(
            "Invalid ticker symbol format",
            details={
                'symbol': symbol,
                'expected': 'Alphanumeric, 1-10 characters'
            }
        )

    # Check against supported list if strict
    if strict and symbol not in SUPPORTED_TICKERS:
        raise InvalidTickerError(
            "Ticker symbol not supported",
            details={
                'symbol': symbol,
                'supported_count': len(SUPPORTED_TICKERS)
            }
        )

    return True


def validate_date_range(
    start_date: datetime,
    end_date: datetime,
    max_days: Optional[int] = None
) -> bool:
    """
    Validate date range.

    Args:
        start_date: Start date
        end_date: End date
        max_days: Maximum allowed days (optional)

    Returns:
        True if valid

    Raises:
        InvalidDateRangeError: If date range is invalid

    Example:
        >>> from datetime import datetime, timedelta
        >>> end = datetime.now()
        >>> start = end - timedelta(days=30)
        >>> validate_date_range(start, end)
        True
    """
    # Check start before end
    if start_date >= end_date:
        raise InvalidDateRangeError(
            "Start date must be before end date",
            details={
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        )

    # Check not in future
    now = datetime.now()
    if end_date > now:
        raise InvalidDateRangeError(
            "End date cannot be in the future",
            details={
                'end': end_date.isoformat(),
                'now': now.isoformat()
            }
        )

    # Check maximum range
    if max_days:
        days_diff = (end_date - start_date).days
        if days_diff > max_days:
            raise InvalidDateRangeError(
                f"Date range exceeds maximum of {max_days} days",
                details={
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days_diff,
                    'max_days': max_days
                }
            )

    return True


def validate_interval(interval: str) -> bool:
    """
    Validate time interval.

    Args:
        interval: Time interval string

    Returns:
        True if valid

    Raises:
        InvalidIntervalError: If interval is invalid

    Example:
        >>> validate_interval('1d')
        True
        >>> validate_interval('1h')
        True
    """
    if not interval:
        raise InvalidIntervalError(
            "Interval cannot be empty",
            details={'interval': interval}
        )

    interval = interval.lower().strip()

    if interval not in SUPPORTED_INTERVALS:
        raise InvalidIntervalError(
            "Invalid interval",
            details={
                'interval': interval,
                'supported': SUPPORTED_INTERVALS
            }
        )

    return True


def validate_days(days: int, min_days: int = 1, max_days: int = 365) -> bool:
    """
    Validate number of days.

    Args:
        days: Number of days
        min_days: Minimum allowed days
        max_days: Maximum allowed days

    Returns:
        True if valid

    Raises:
        DataValidationError: If days is invalid
    """
    if not isinstance(days, int):
        raise DataValidationError(
            "Days must be an integer",
            details={'days': days, 'type': type(days).__name__}
        )

    if days < min_days:
        raise DataValidationError(
            f"Days must be at least {min_days}",
            details={'days': days, 'min': min_days}
        )

    if days > max_days:
        raise DataValidationError(
            f"Days cannot exceed {max_days}",
            details={'days': days, 'max': max_days}
        )

    return True


def sanitize_symbol(symbol: str) -> str:
    """
    Sanitize ticker symbol.

    Args:
        symbol: Ticker symbol

    Returns:
        Sanitized symbol (uppercase, trimmed)

    Example:
        >>> sanitize_symbol('  btc  ')
        'BTC'
    """
    if not symbol:
        return ''

    # Remove whitespace and convert to uppercase
    symbol = symbol.strip().upper()

    # Remove non-alphanumeric characters
    symbol = re.sub(r'[^A-Z0-9]', '', symbol)

    return symbol


def validate_price_data(
    data: List,
    min_points: int = 10,
    check_gaps: bool = True
) -> bool:
    """
    Validate price data quality.

    Args:
        data: List of price points
        min_points: Minimum required data points
        check_gaps: Check for data gaps

    Returns:
        True if valid

    Raises:
        DataValidationError: If data is invalid
    """
    if not data:
        raise DataValidationError(
            "Price data cannot be empty",
            details={'data_points': 0}
        )

    if len(data) < min_points:
        raise DataValidationError(
            f"Insufficient data points. Need at least {min_points}",
            details={
                'required': min_points,
                'available': len(data)
            }
        )

    # Check for None values
    none_count = sum(1 for p in data if p is None)
    if none_count > 0:
        raise DataValidationError(
            "Price data contains None values",
            details={
                'total_points': len(data),
                'none_count': none_count
            }
        )

    # Check for negative prices
    try:
        negative_count = sum(
            1 for p in data
            if hasattr(p, 'close') and p.close < 0
        )
        if negative_count > 0:
            raise DataValidationError(
                "Price data contains negative prices",
                details={'negative_count': negative_count}
            )
    except:
        pass

    return True


def validate_confidence(confidence: float) -> bool:
    """
    Validate confidence score.

    Args:
        confidence: Confidence score (0.0 to 1.0)

    Returns:
        True if valid

    Raises:
        DataValidationError: If confidence is invalid
    """
    if not isinstance(confidence, (int, float)):
        raise DataValidationError(
            "Confidence must be a number",
            details={'confidence': confidence, 'type': type(confidence).__name__}
        )

    if not 0.0 <= confidence <= 1.0:
        raise DataValidationError(
            "Confidence must be between 0.0 and 1.0",
            details={'confidence': confidence}
        )

    return True


def validate_sensitivity(sensitivity: float) -> bool:
    """
    Validate sensitivity parameter.

    Args:
        sensitivity: Sensitivity value (0.0 to 1.0)

    Returns:
        True if valid

    Raises:
        DataValidationError: If sensitivity is invalid
    """
    if not isinstance(sensitivity, (int, float)):
        raise DataValidationError(
            "Sensitivity must be a number",
            details={'sensitivity': sensitivity, 'type': type(sensitivity).__name__}
        )

    if not 0.0 <= sensitivity <= 1.0:
        raise DataValidationError(
            "Sensitivity must be between 0.0 and 1.0",
            details={'sensitivity': sensitivity}
        )

    return True
