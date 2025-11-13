# Security Module

The security module provides comprehensive security features for CryptVault including input validation, credential management, and rate limiting.

## Components

### Input Validator (`input_validator.py`)

Validates and sanitizes all external input to prevent injection attacks.

**Features:**
- Ticker symbol whitelist (~150 supported symbols)
- Injection pattern detection
- Input sanitization
- Format validation

**Usage:**
```python
from cryptvault.security import InputValidator

validator = InputValidator(strict_mode=True)
ticker = validator.validate_ticker('BTC')
days = validator.validate_days(60)
interval = validator.validate_interval('1d')
```

### Credential Manager (`credential_manager.py`)

Securely manages API keys and credentials using environment variables.

**Features:**
- Environment variable storage
- Secure logging (automatic redaction)
- Credential rotation tracking
- Validation

**Usage:**
```python
from cryptvault.security import CredentialManager

creds = CredentialManager()
api_key = creds.get_credential('CRYPTOCOMPARE_API_KEY', required=True)
creds.validate_credential('API_KEY', min_length=20)
```

### Rate Limiter (`rate_limiter.py`)

Implements rate limiting with exponential backoff.

**Features:**
- Token bucket algorithm
- Exponential backoff
- Adaptive rate limiting
- Per-resource limits

**Usage:**
```python
from cryptvault.security import RateLimiter, rate_limit

# Manual rate limiting
limiter = RateLimiter(max_calls=100, period=60)
limiter.acquire('api_call')

# Decorator-based
@rate_limit(max_calls=10, period=60)
def fetch_data(symbol):
    return api.get(symbol)
```

## Security Best Practices

1. **Always validate input** before processing
2. **Never hardcode credentials** in source code
3. **Use rate limiting** for all API calls
4. **Enable strict mode** in production
5. **Rotate credentials** every 90 days

## See Also

- [Security Documentation](../../docs/SECURITY.md)
- [Security Audit Script](../../scripts/security_audit.py)
