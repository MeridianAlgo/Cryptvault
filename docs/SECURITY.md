# Security Documentation

## Overview

CryptVault implements comprehensive security measures to protect against common vulnerabilities and ensure safe operation. This document outlines the security features, best practices, and guidelines for secure usage.

## Security Features

### 1. Input Validation and Sanitization

**Location**: `cryptvault/security/input_validator.py`

All external input is validated and sanitized to prevent injection attacks:

- **Ticker Symbol Whitelist**: Only pre-approved ticker symbols are accepted
- **Injection Prevention**: Detects and blocks command injection, SQL injection, XSS attempts
- **Format Validation**: Strict format checking for all input types
- **Sanitization**: Removes dangerous characters and control codes

```python
from cryptvault.security import InputValidator

validator = InputValidator(strict_mode=True)
ticker = validator.validate_ticker('BTC')  # OK
ticker = validator.validate_ticker('BTC; rm -rf /')  # Raises ValidationError
```

#### Supported Ticker Whitelist

The system maintains a whitelist of ~150 supported tickers including:
- Major cryptocurrencies (BTC, ETH, etc.)
- Major stocks (AAPL, MSFT, etc.)
- Popular ETFs and indices

Custom tickers can be added programmatically:

```python
validator.add_to_whitelist(['CUSTOM1', 'CUSTOM2'])
```

### 2. Secure Credential Management

**Location**: `cryptvault/security/credential_manager.py`

Credentials are managed securely using environment variables:

- **Environment Variables**: All API keys stored in environment variables
- **No Hardcoding**: Credentials never hardcoded in source code
- **Secure Logging**: Automatic redaction of sensitive data in logs
- **Rotation Support**: Built-in credential rotation tracking

```python
from cryptvault.security import CredentialManager

creds = CredentialManager()
api_key = creds.get_credential('CRYPTOCOMPARE_API_KEY', required=True)
```

#### Setting Up Credentials

1. Create a `.env` file (never commit to repository):
```bash
CRYPTOCOMPARE_API_KEY=your_api_key_here
YFINANCE_API_KEY=your_api_key_here
```

2. Load credentials:
```python
creds = CredentialManager()
creds.load_from_env_file('.env')
```

3. Or set via environment:
```bash
export CRYPTOCOMPARE_API_KEY=your_api_key_here
```

#### Credential Rotation

The system tracks credential age and recommends rotation every 90 days:

```python
if creds.check_rotation_needed('API_KEY'):
    print("Consider rotating this credential")
```

### 3. Rate Limiting

**Location**: `cryptvault/security/rate_limiter.py`

Prevents API abuse and respects external API limits:

- **Token Bucket Algorithm**: Smooth rate limiting
- **Exponential Backoff**: Automatic backoff on repeated violations
- **Adaptive Limiting**: Adjusts rates based on API responses
- **Per-Resource Limits**: Different limits for different resources

```python
from cryptvault.security import RateLimiter, rate_limit

# Manual rate limiting
limiter = RateLimiter(max_calls=100, period=60)
limiter.acquire('api_call')

# Decorator-based rate limiting
@rate_limit(max_calls=10, period=60)
def fetch_data(symbol):
    return api.get(symbol)
```

#### Adaptive Rate Limiting

Automatically adjusts limits based on API responses:

```python
from cryptvault.security import AdaptiveRateLimiter

limiter = AdaptiveRateLimiter(max_calls=100, period=60, min_calls=10)
limiter.acquire('api_call')

# Report API response to adjust limits
response = make_api_call()
limiter.report_response('api_call', response.status_code)
```

### 4. Secure Logging

**Location**: `cryptvault/security/credential_manager.py` (SecureLogger)

Prevents accidental exposure of sensitive information:

- **Automatic Redaction**: API keys, passwords, tokens automatically redacted
- **Pattern Detection**: Detects and redacts long alphanumeric strings
- **Structured Logging**: Consistent log format with context

```python
from cryptvault.security import SecureLogger

SecureLogger.safe_log('info', 'API call successful', extra={
    'api_key': 'secret123',  # Will be redacted
    'symbol': 'BTC'
})
```

## Security Best Practices

### For Users

1. **Never Commit Credentials**
   - Add `.env` to `.gitignore`
   - Use `.env.example` for documentation
   - Store credentials in environment variables

2. **Use Strong API Keys**
   - Minimum 20 characters
   - Mix of letters, numbers, and symbols
   - Rotate regularly (every 90 days)

3. **Validate All Input**
   - Use provided validators for all external input
   - Enable strict mode for production
   - Never bypass validation

4. **Monitor Rate Limits**
   - Check remaining calls before making requests
   - Implement backoff strategies
   - Use adaptive rate limiting

5. **Keep Dependencies Updated**
   - Run `pip install --upgrade` regularly
   - Monitor security advisories
   - Use `safety check` to scan for vulnerabilities

### For Developers

1. **Input Validation**
   ```python
   # Always validate external input
   from cryptvault.security import InputValidator
   
   validator = InputValidator(strict_mode=True)
   ticker = validator.validate_ticker(user_input)
   ```

2. **Credential Management**
   ```python
   # Never hardcode credentials
   # BAD:
   api_key = "hardcoded_key_123"
   
   # GOOD:
   from cryptvault.security import get_credential_manager
   creds = get_credential_manager()
   api_key = creds.get_credential('API_KEY', required=True)
   ```

3. **Rate Limiting**
   ```python
   # Apply rate limiting to all API calls
   from cryptvault.security import rate_limit
   
   @rate_limit(max_calls=100, period=60)
   def fetch_market_data(symbol):
       return api.get(symbol)
   ```

4. **Secure Logging**
   ```python
   # Use secure logging for sensitive operations
   from cryptvault.security import SecureLogger
   
   SecureLogger.safe_log('info', 'Operation completed', extra={
       'user_data': sensitive_data  # Will be redacted
   })
   ```

## OWASP Top 10 Compliance

CryptVault addresses the OWASP Top 10 security risks:

### A01:2021 – Broken Access Control
- **Status**: N/A (No authentication system)
- **Mitigation**: Input validation prevents unauthorized operations

### A02:2021 – Cryptographic Failures
- **Status**: ✅ Addressed
- **Mitigation**: Credentials stored in environment variables, never in code

### A03:2021 – Injection
- **Status**: ✅ Addressed
- **Mitigation**: Comprehensive input validation and sanitization
- **Implementation**: `validate_no_injection()` checks for injection patterns

### A04:2021 – Insecure Design
- **Status**: ✅ Addressed
- **Mitigation**: Security controls implemented at design level

### A05:2021 – Security Misconfiguration
- **Status**: ✅ Addressed
- **Mitigation**: Centralized configuration management with validation

### A06:2021 – Vulnerable and Outdated Components
- **Status**: ✅ Monitored
- **Mitigation**: Regular dependency scanning with `safety` and `bandit`

### A07:2021 – Identification and Authentication Failures
- **Status**: N/A (No authentication system)

### A08:2021 – Software and Data Integrity Failures
- **Status**: ✅ Addressed
- **Mitigation**: Input validation and data integrity checks

### A09:2021 – Security Logging and Monitoring Failures
- **Status**: ✅ Addressed
- **Mitigation**: Structured logging with automatic sensitive data redaction

### A10:2021 – Server-Side Request Forgery (SSRF)
- **Status**: ✅ Addressed
- **Mitigation**: Ticker whitelist prevents arbitrary URL requests

## Security Audit

### Running Security Audit

Run the comprehensive security audit:

```bash
python scripts/security_audit.py
```

Generate a report:

```bash
python scripts/security_audit.py --report security_report.json
```

### Audit Checks

The security audit performs the following checks:

1. **Dependency Vulnerability Scanning**
   - Uses `safety` to check for known vulnerabilities
   - Scans all dependencies in requirements files

2. **Code Security Analysis**
   - Uses `bandit` for static code analysis
   - Identifies security issues in Python code

3. **Credential Exposure Detection**
   - Scans for hardcoded credentials
   - Checks for API keys, passwords, tokens in code

4. **Input Validation Verification**
   - Verifies input validation is implemented
   - Checks for whitelist and injection prevention

5. **OWASP Top 10 Checks**
   - Validates compliance with OWASP guidelines
   - Identifies potential vulnerabilities

6. **Configuration Security**
   - Checks for exposed .env files
   - Verifies .gitignore configuration

### Installing Security Tools

```bash
pip install safety bandit
```

## Vulnerability Reporting

If you discover a security vulnerability, please report it to:

**Email**: security@cryptvault.example.com

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

**Do not** publicly disclose vulnerabilities until they have been addressed.

## Security Updates

Security updates are released as soon as possible after vulnerabilities are discovered. To stay updated:

1. Watch the repository for security advisories
2. Subscribe to release notifications
3. Run `pip install --upgrade cryptvault` regularly
4. Monitor the CHANGELOG for security fixes

## Compliance and Standards

CryptVault follows these security standards:

- **OWASP Top 10**: Addresses all applicable risks
- **PCI DSS**: Not applicable (no payment processing)
- **GDPR**: No personal data collected
- **CWE Top 25**: Mitigates common weaknesses

## Security Checklist

### Before Deployment

- [ ] All credentials stored in environment variables
- [ ] `.env` file not committed to repository
- [ ] `.env` added to `.gitignore`
- [ ] Input validation enabled in strict mode
- [ ] Rate limiting configured appropriately
- [ ] Security audit passed with no critical issues
- [ ] Dependencies scanned for vulnerabilities
- [ ] Logging configured with sensitive data redaction
- [ ] API keys rotated within last 90 days

### Regular Maintenance

- [ ] Run security audit monthly
- [ ] Update dependencies quarterly
- [ ] Rotate credentials every 90 days
- [ ] Review logs for suspicious activity
- [ ] Monitor rate limit violations
- [ ] Check for security advisories

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [API Security Best Practices](https://owasp.org/www-project-api-security/)
- [Secure Coding Guidelines](https://www.securecoding.cert.org/)

## Contact

For security questions or concerns:
- Email: security@cryptvault.example.com
- GitHub Issues: Use the security label
- Documentation: See docs/SECURITY.md

---

**Last Updated**: 2024
**Version**: 4.0.0
