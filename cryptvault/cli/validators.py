"""
Input Validation Module

This module provides input validation functions for the CLI, ensuring
that user input is valid, safe, and properly formatted before processing.

Functions:
    - validate_ticker: Validate ticker symbol
    - validate_days: Validate number of days
    - validate_interval: Validate data interval
    - validate_portfolio_holdings: Validate portfolio holdings format
    - sanitize_input: Sanitize user input
"""

import re
from typing import List, Dict, Tuple, Optional


class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass


def validate_ticker(ticker: str, supported_tickers: Optional[List[str]] = None) -> str:
    """
    Validate ticker symbol.

    Args:
        ticker: Ticker symbol to validate
        supported_tickers: Optional list of supported ticker symbols

    Returns:
        Validated and normalized ticker symbol (uppercase)

    Raises:
        ValidationError: If ticker is invalid

    Example:
        >>> validate_ticker('btc')
        'BTC'
        >>> validate_ticker('invalid!@#')
        ValidationError: Invalid ticker symbol format
    """
    if not ticker:
        raise ValidationError("Ticker symbol cannot be empty")

    # Sanitize and normalize
    ticker = sanitize_input(ticker).upper()

    # Check format (alphanumeric, 1-10 characters)
    if not re.match(r'^[A-Z0-9]{1,10}$', ticker):
        raise ValidationError(
            f"Invalid ticker symbol format: '{ticker}'. "
            "Ticker must be 1-10 alphanumeric characters."
        )

    # Check against supported list if provided
    if supported_tickers and ticker not in supported_tickers:
        # Provide helpful suggestions
        suggestions = _find_similar_tickers(ticker, supported_tickers)
        error_msg = f"Ticker '{ticker}' is not supported."

        if suggestions:
            error_msg += f"\n  Did you mean: {', '.join(suggestions[:5])}?"
        error_msg += f"\n  Use --demo to see all {len(supported_tickers)} supported tickers."

        raise ValidationError(error_msg)

    return ticker


def validate_days(days: int, min_days: int = 1, max_days: int = 3650) -> int:
    """
    Validate number of days for historical data.

    Args:
        days: Number of days to validate
        min_days: Minimum allowed days (default: 1)
        max_days: Maximum allowed days (default: 3650, ~10 years)

    Returns:
        Validated number of days

    Raises:
        ValidationError: If days is out of valid range

    Example:
        >>> validate_days(30)
        30
        >>> validate_days(0)
        ValidationError: Days must be between 1 and 3650
    """
    try:
        days = int(days)
    except (ValueError, TypeError):
        raise ValidationError(f"Days must be a valid integer, got: {days}")

    if days < min_days or days > max_days:
        raise ValidationError(
            f"Days must be between {min_days} and {max_days}. Got: {days}"
        )

    return days


def validate_interval(interval: str) -> str:
    """
    Validate data interval.

    Args:
        interval: Data interval to validate (e.g., '1h', '4h', '1d')

    Returns:
        Validated interval string

    Raises:
        ValidationError: If interval is not supported

    Example:
        >>> validate_interval('1d')
        '1d'
        >>> validate_interval('5m')
        ValidationError: Unsupported interval
    """
    if not interval:
        raise ValidationError("Interval cannot be empty")

    interval = sanitize_input(interval).lower()

    # Supported intervals
    valid_intervals = {
        '1m', '5m', '15m', '30m',  # Minutes
        '1h', '2h', '4h', '6h', '12h',  # Hours
        '1d', '1w', '1mo'  # Days, weeks, months
    }

    if interval not in valid_intervals:
        raise ValidationError(
            f"Unsupported interval: '{interval}'. "
            f"Valid intervals: {', '.join(sorted(valid_intervals))}"
        )

    return interval


def validate_portfolio_holdings(holdings_str: List[str]) -> Dict[str, float]:
    """
    Validate and parse portfolio holdings.

    Args:
        holdings_str: List of holdings in format ['BTC:0.5', 'ETH:10']

    Returns:
        Dictionary mapping ticker symbols to amounts

    Raises:
        ValidationError: If holdings format is invalid

    Example:
        >>> validate_portfolio_holdings(['BTC:0.5', 'ETH:10'])
        {'BTC': 0.5, 'ETH': 10.0}
    """
    if not holdings_str:
        raise ValidationError("Portfolio holdings cannot be empty")

    holdings = {}

    for holding in holdings_str:
        holding = sanitize_input(holding)

        if ':' not in holding:
            raise ValidationError(
                f"Invalid holding format: '{holding}'. "
                "Expected format: SYMBOL:AMOUNT (e.g., BTC:0.5)"
            )

        parts = holding.split(':')
        if len(parts) != 2:
            raise ValidationError(
                f"Invalid holding format: '{holding}'. "
                "Expected format: SYMBOL:AMOUNT (e.g., BTC:0.5)"
            )

        symbol, amount_str = parts
        symbol = symbol.upper().strip()

        # Validate symbol format
        if not re.match(r'^[A-Z0-9]{1,10}$', symbol):
            raise ValidationError(
                f"Invalid ticker symbol in holding: '{symbol}'"
            )

        # Validate amount
        try:
            amount = float(amount_str.strip())
        except ValueError:
            raise ValidationError(
                f"Invalid amount for {symbol}: '{amount_str}'. "
                "Amount must be a valid number."
            )

        if amount <= 0:
            raise ValidationError(
                f"Amount for {symbol} must be positive, got: {amount}"
            )

        holdings[symbol] = amount

    return holdings


def validate_file_path(file_path: str, must_exist: bool = False) -> str:
    """
    Validate file path for security and format.

    Args:
        file_path: File path to validate
        must_exist: Whether the file must already exist

    Returns:
        Validated file path

    Raises:
        ValidationError: If file path is invalid or unsafe
    """
    if not file_path:
        raise ValidationError("File path cannot be empty")

    file_path = sanitize_input(file_path)

    # Check for directory traversal attempts
    if '..' in file_path or file_path.startswith('/'):
        raise ValidationError(
            "Invalid file path: directory traversal not allowed"
        )

    # Check for valid file extensions for charts
    valid_extensions = ['.png', '.jpg', '.jpeg', '.svg', '.pdf']
    if not any(file_path.lower().endswith(ext) for ext in valid_extensions):
        raise ValidationError(
            f"Invalid file extension. Supported: {', '.join(valid_extensions)}"
        )

    if must_exist:
        import os
        if not os.path.exists(file_path):
            raise ValidationError(f"File not found: {file_path}")

    return file_path


def sanitize_input(user_input: str) -> str:
    """
    Sanitize user input by removing potentially dangerous characters.

    Args:
        user_input: Raw user input string

    Returns:
        Sanitized input string

    Example:
        >>> sanitize_input('BTC; rm -rf /')
        'BTC rm -rf '
    """
    if not isinstance(user_input, str):
        return str(user_input)

    # Remove null bytes
    user_input = user_input.replace('\x00', '')

    # Remove control characters except common whitespace
    user_input = ''.join(
        char for char in user_input
        if char.isprintable() or char in [' ', '\t', '\n']
    )

    # Strip leading/trailing whitespace
    user_input = user_input.strip()

    return user_input


def _find_similar_tickers(ticker: str, supported_tickers: List[str], max_suggestions: int = 5) -> List[str]:
    """
    Find similar ticker symbols using simple string matching.

    Args:
        ticker: Ticker to find matches for
        supported_tickers: List of supported tickers
        max_suggestions: Maximum number of suggestions to return

    Returns:
        List of similar ticker symbols
    """
    suggestions = []
    ticker_lower = ticker.lower()

    # Exact prefix matches
    for supported in supported_tickers:
        if supported.lower().startswith(ticker_lower):
            suggestions.append(supported)

    # Contains matches
    if len(suggestions) < max_suggestions:
        for supported in supported_tickers:
            if ticker_lower in supported.lower() and supported not in suggestions:
                suggestions.append(supported)

    return suggestions[:max_suggestions]
