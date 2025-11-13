"""
Input Validation and Sanitization

Comprehensive input validation to prevent injection attacks and ensure
data integrity. Includes whitelisting for ticker symbols and strict
validation for all external input.

Example:
    >>> from cryptvault.security import InputValidator
    >>> validator = InputValidator()
    >>> validator.validate_ticker('BTC')  # OK
    >>> validator.validate_ticker('BTC; DROP TABLE')  # Raises ValidationError
"""

import re
import logging
from typing import List, Optional, Set
from pathlib import Path

from ..exceptions import ValidationError

logger = logging.getLogger(__name__)


# Whitelist of supported ticker symbols
# This prevents injection attacks and ensures only valid symbols are processed
TICKER_WHITELIST: Set[str] = {
    # Major Cryptocurrencies
    'BTC', 'ETH', 'USDT', 'BNB', 'XRP', 'ADA', 'DOGE', 'SOL', 'TRX', 'DOT',
    'MATIC', 'LTC', 'SHIB', 'AVAX', 'UNI', 'LINK', 'XMR', 'ETC', 'XLM', 'BCH',
    'ATOM', 'FIL', 'APT', 'ARB', 'OP', 'NEAR', 'VET', 'ALGO', 'ICP', 'QNT',
    'HBAR', 'GRT', 'AAVE', 'EOS', 'SAND', 'MANA', 'AXS', 'THETA', 'FTM', 'EGLD',
    
    # Major Stocks
    'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'BRK-A',
    'V', 'JNJ', 'WMT', 'JPM', 'MA', 'PG', 'UNH', 'HD', 'DIS', 'BAC',
    'ADBE', 'CRM', 'NFLX', 'CMCSA', 'XOM', 'PFE', 'CSCO', 'ABT', 'KO', 'PEP',
    'AVGO', 'TMO', 'COST', 'MRK', 'ABBV', 'ACN', 'NKE', 'LLY', 'DHR', 'TXN',
    'ORCL', 'NEE', 'WFC', 'CVX', 'MDT', 'UPS', 'PM', 'BMY', 'QCOM', 'HON',
    'RTX', 'UNP', 'INTU', 'LOW', 'AMD', 'AMGN', 'IBM', 'BA', 'GE', 'CAT',
    
    # Indices and ETFs
    'SPY', 'QQQ', 'DIA', 'IWM', 'VTI', 'VOO', 'VEA', 'VWO', 'AGG', 'BND',
    
    # Additional popular tickers
    'COIN', 'SQ', 'PYPL', 'SHOP', 'ROKU', 'SNAP', 'TWTR', 'UBER', 'LYFT', 'ABNB',
}


# Dangerous patterns that could indicate injection attempts
INJECTION_PATTERNS = [
    r';\s*\w+',  # Command injection (e.g., "; rm -rf")
    r'\|\s*\w+',  # Pipe injection
    r'&&\s*\w+',  # Command chaining
    r'\$\(',  # Command substitution
    r'`',  # Backtick command execution
    r'<script',  # XSS attempt
    r'javascript:',  # JavaScript injection
    r'on\w+\s*=',  # Event handler injection
    r'\.\./',  # Directory traversal
    r'\\x[0-9a-fA-F]{2}',  # Hex encoding
    r'%[0-9a-fA-F]{2}',  # URL encoding of special chars
    r'union\s+select',  # SQL injection
    r'drop\s+table',  # SQL injection
    r'exec\s*\(',  # Code execution
    r'eval\s*\(',  # Code execution
    r'__import__',  # Python import injection
]


class InputValidator:
    """
    Comprehensive input validator with whitelisting and injection prevention.
    
    This class provides strict validation for all external input to prevent
    injection attacks, ensure data integrity, and maintain security.
    
    Attributes:
        ticker_whitelist: Set of allowed ticker symbols
        strict_mode: If True, only whitelisted tickers are allowed
        
    Example:
        >>> validator = InputValidator(strict_mode=True)
        >>> validator.validate_ticker('BTC')  # OK
        >>> validator.validate_ticker('INVALID')  # Raises ValidationError
    """
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize input validator.
        
        Args:
            strict_mode: If True, only whitelisted tickers allowed
        """
        self.ticker_whitelist = TICKER_WHITELIST.copy()
        self.strict_mode = strict_mode
        logger.info(f"InputValidator initialized with {len(self.ticker_whitelist)} whitelisted tickers")
    
    def add_to_whitelist(self, tickers: List[str]) -> None:
        """
        Add tickers to whitelist.
        
        Args:
            tickers: List of ticker symbols to add
            
        Example:
            >>> validator = InputValidator()
            >>> validator.add_to_whitelist(['CUSTOM1', 'CUSTOM2'])
        """
        for ticker in tickers:
            ticker = ticker.upper().strip()
            if self._is_valid_ticker_format(ticker):
                self.ticker_whitelist.add(ticker)
                logger.debug(f"Added {ticker} to whitelist")
    
    def validate_ticker(self, ticker: str) -> str:
        """
        Validate ticker symbol with whitelist check.
        
        Args:
            ticker: Ticker symbol to validate
            
        Returns:
            Validated and normalized ticker symbol
            
        Raises:
            ValidationError: If ticker is invalid or not whitelisted
            
        Example:
            >>> validator = InputValidator()
            >>> validator.validate_ticker('btc')
            'BTC'
        """
        if not ticker:
            raise ValidationError(
                "Ticker symbol cannot be empty",
                details={'ticker': ticker}
            )
        
        # Sanitize input
        ticker = sanitize_input(ticker).upper()
        
        # Check for injection attempts
        validate_no_injection(ticker, 'ticker')
        
        # Validate format
        if not self._is_valid_ticker_format(ticker):
            raise ValidationError(
                f"Invalid ticker format: '{ticker}'",
                details={
                    'ticker': ticker,
                    'expected': 'Alphanumeric, 1-10 characters, optional hyphen'
                }
            )
        
        # Check whitelist in strict mode
        if self.strict_mode and ticker not in self.ticker_whitelist:
            suggestions = self._find_similar_tickers(ticker)
            error_msg = f"Ticker '{ticker}' is not in the whitelist"
            
            if suggestions:
                error_msg += f". Did you mean: {', '.join(suggestions[:3])}?"
            
            raise ValidationError(
                error_msg,
                details={
                    'ticker': ticker,
                    'whitelist_size': len(self.ticker_whitelist),
                    'suggestions': suggestions
                }
            )
        
        logger.debug(f"Validated ticker: {ticker}")
        return ticker
    
    def validate_days(self, days: int, min_days: int = 1, max_days: int = 3650) -> int:
        """
        Validate number of days.
        
        Args:
            days: Number of days to validate
            min_days: Minimum allowed days
            max_days: Maximum allowed days
            
        Returns:
            Validated number of days
            
        Raises:
            ValidationError: If days is invalid
        """
        try:
            days = int(days)
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"Days must be a valid integer",
                details={'days': days, 'error': str(e)}
            )
        
        if days < min_days or days > max_days:
            raise ValidationError(
                f"Days must be between {min_days} and {max_days}",
                details={'days': days, 'min': min_days, 'max': max_days}
            )
        
        return days
    
    def validate_interval(self, interval: str) -> str:
        """
        Validate time interval.
        
        Args:
            interval: Time interval to validate
            
        Returns:
            Validated interval
            
        Raises:
            ValidationError: If interval is invalid
        """
        if not interval:
            raise ValidationError("Interval cannot be empty")
        
        interval = sanitize_input(interval).lower()
        validate_no_injection(interval, 'interval')
        
        valid_intervals = {
            '1m', '5m', '15m', '30m',
            '1h', '2h', '4h', '6h', '12h',
            '1d', '1wk', '1mo'
        }
        
        if interval not in valid_intervals:
            raise ValidationError(
                f"Invalid interval: '{interval}'",
                details={
                    'interval': interval,
                    'valid_intervals': sorted(valid_intervals)
                }
            )
        
        return interval
    
    def validate_file_path(self, file_path: str, allowed_extensions: Optional[List[str]] = None) -> str:
        """
        Validate file path for security.
        
        Args:
            file_path: File path to validate
            allowed_extensions: List of allowed file extensions
            
        Returns:
            Validated file path
            
        Raises:
            ValidationError: If file path is unsafe
        """
        if not file_path:
            raise ValidationError("File path cannot be empty")
        
        file_path = sanitize_input(file_path)
        validate_no_injection(file_path, 'file_path')
        
        # Check for directory traversal
        if '..' in file_path:
            raise ValidationError(
                "Directory traversal not allowed",
                details={'file_path': file_path}
            )
        
        # Check for absolute paths (security risk)
        if Path(file_path).is_absolute():
            raise ValidationError(
                "Absolute paths not allowed",
                details={'file_path': file_path}
            )
        
        # Validate extension
        if allowed_extensions:
            if not any(file_path.lower().endswith(ext) for ext in allowed_extensions):
                raise ValidationError(
                    f"Invalid file extension",
                    details={
                        'file_path': file_path,
                        'allowed_extensions': allowed_extensions
                    }
                )
        
        return file_path
    
    def validate_amount(self, amount: float, min_amount: float = 0.0, max_amount: Optional[float] = None) -> float:
        """
        Validate numeric amount.
        
        Args:
            amount: Amount to validate
            min_amount: Minimum allowed amount
            max_amount: Maximum allowed amount (optional)
            
        Returns:
            Validated amount
            
        Raises:
            ValidationError: If amount is invalid
        """
        try:
            amount = float(amount)
        except (ValueError, TypeError) as e:
            raise ValidationError(
                "Amount must be a valid number",
                details={'amount': amount, 'error': str(e)}
            )
        
        if amount < min_amount:
            raise ValidationError(
                f"Amount must be at least {min_amount}",
                details={'amount': amount, 'min': min_amount}
            )
        
        if max_amount is not None and amount > max_amount:
            raise ValidationError(
                f"Amount cannot exceed {max_amount}",
                details={'amount': amount, 'max': max_amount}
            )
        
        return amount
    
    def _is_valid_ticker_format(self, ticker: str) -> bool:
        """Check if ticker matches valid format."""
        # Allow alphanumeric and hyphen, 1-10 characters
        return bool(re.match(r'^[A-Z0-9-]{1,10}$', ticker))
    
    def _find_similar_tickers(self, ticker: str, max_suggestions: int = 5) -> List[str]:
        """Find similar tickers in whitelist."""
        suggestions = []
        ticker_lower = ticker.lower()
        
        # Exact prefix matches
        for whitelisted in self.ticker_whitelist:
            if whitelisted.lower().startswith(ticker_lower):
                suggestions.append(whitelisted)
        
        # Contains matches
        if len(suggestions) < max_suggestions:
            for whitelisted in self.ticker_whitelist:
                if ticker_lower in whitelisted.lower() and whitelisted not in suggestions:
                    suggestions.append(whitelisted)
        
        return suggestions[:max_suggestions]


def sanitize_input(user_input: str) -> str:
    """
    Sanitize user input by removing dangerous characters.
    
    Removes null bytes, control characters, and normalizes whitespace
    to prevent injection attacks and ensure data integrity.
    
    Args:
        user_input: Raw user input
        
    Returns:
        Sanitized input string
        
    Example:
        >>> sanitize_input('BTC\\x00; rm -rf /')
        'BTC; rm -rf /'
        >>> sanitize_input('  AAPL  ')
        'AAPL'
    """
    if not isinstance(user_input, str):
        user_input = str(user_input)
    
    # Remove null bytes (common in injection attacks)
    user_input = user_input.replace('\x00', '')
    user_input = user_input.replace('\0', '')
    
    # Remove other control characters except common whitespace
    user_input = ''.join(
        char for char in user_input
        if char.isprintable() or char in [' ', '\t', '\n']
    )
    
    # Normalize whitespace
    user_input = ' '.join(user_input.split())
    
    # Strip leading/trailing whitespace
    user_input = user_input.strip()
    
    return user_input


def validate_no_injection(user_input: str, field_name: str = 'input') -> None:
    """
    Validate that input doesn't contain injection patterns.
    
    Checks for common injection attack patterns including command injection,
    SQL injection, XSS, and directory traversal attempts.
    
    Args:
        user_input: Input to validate
        field_name: Name of the field being validated (for error messages)
        
    Raises:
        ValidationError: If injection pattern detected
        
    Example:
        >>> validate_no_injection('BTC')  # OK
        >>> validate_no_injection('BTC; rm -rf /')  # Raises ValidationError
    """
    user_input_lower = user_input.lower()
    
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_input_lower, re.IGNORECASE):
            logger.warning(
                f"Injection attempt detected in {field_name}: {user_input}",
                extra={'field': field_name, 'input': user_input, 'pattern': pattern}
            )
            raise ValidationError(
                f"Invalid characters detected in {field_name}",
                details={
                    'field': field_name,
                    'reason': 'Potential injection attempt'
                }
            )
    
    # Check for suspicious character sequences
    suspicious_chars = ['<', '>', '|', '&', ';', '`', '$', '\\']
    found_suspicious = [char for char in suspicious_chars if char in user_input]
    
    if found_suspicious:
        logger.warning(
            f"Suspicious characters in {field_name}: {found_suspicious}",
            extra={'field': field_name, 'chars': found_suspicious}
        )
        raise ValidationError(
            f"Invalid characters in {field_name}: {', '.join(found_suspicious)}",
            details={
                'field': field_name,
                'suspicious_chars': found_suspicious
            }
        )


def get_ticker_whitelist() -> Set[str]:
    """
    Get the current ticker whitelist.
    
    Returns:
        Set of whitelisted ticker symbols
        
    Example:
        >>> whitelist = get_ticker_whitelist()
        >>> 'BTC' in whitelist
        True
    """
    return TICKER_WHITELIST.copy()


def is_ticker_whitelisted(ticker: str) -> bool:
    """
    Check if ticker is in whitelist.
    
    Args:
        ticker: Ticker symbol to check
        
    Returns:
        True if ticker is whitelisted
        
    Example:
        >>> is_ticker_whitelisted('BTC')
        True
        >>> is_ticker_whitelisted('INVALID')
        False
    """
    return ticker.upper() in TICKER_WHITELIST
