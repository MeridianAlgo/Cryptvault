"""
Security Module

Provides security utilities including input validation, sanitization,
rate limiting, and credential management.

Example:
    >>> from cryptvault.security import InputValidator, sanitize_input
    >>> validator = InputValidator()
    >>> validator.validate_ticker('BTC')
    >>> safe_input = sanitize_input(user_input)
"""

from .input_validator import (
    InputValidator,
    sanitize_input,
    validate_no_injection,
    get_ticker_whitelist,
    is_ticker_whitelisted
)
from .rate_limiter import (
    RateLimiter,
    AdaptiveRateLimiter,
    rate_limit,
    get_api_rate_limiter,
    get_data_fetch_limiter
)
from .credential_manager import (
    CredentialManager,
    SecureLogger,
    get_credential_manager
)

__all__ = [
    'InputValidator',
    'sanitize_input',
    'validate_no_injection',
    'get_ticker_whitelist',
    'is_ticker_whitelisted',
    'RateLimiter',
    'AdaptiveRateLimiter',
    'rate_limit',
    'get_api_rate_limiter',
    'get_data_fetch_limiter',
    'CredentialManager',
    'SecureLogger',
    'get_credential_manager',
]
