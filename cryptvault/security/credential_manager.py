"""
Secure Credential Management

Provides secure storage and retrieval of API keys and credentials using
environment variables, with support for credential rotation and secure logging.

Example:
    >>> from cryptvault.security import CredentialManager
    >>> creds = CredentialManager()
    >>> api_key = creds.get_credential('CRYPTOCOMPARE_API_KEY')
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
from pathlib import Path

from ..exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class SecureLogger:
    """
    Logger wrapper that prevents logging of sensitive information.
    
    Automatically redacts API keys, passwords, and other credentials
    from log messages to prevent accidental exposure.
    """
    
    # Patterns to redact in logs
    SENSITIVE_KEYS = [
        'api_key', 'apikey', 'api-key',
        'password', 'passwd', 'pwd',
        'secret', 'token', 'auth',
        'credential', 'key'
    ]
    
    @staticmethod
    def redact_sensitive_data(data: Any) -> Any:
        """
        Redact sensitive information from data.
        
        Args:
            data: Data to redact (dict, str, or other)
            
        Returns:
            Data with sensitive information redacted
        """
        if isinstance(data, dict):
            return {
                key: '***REDACTED***' if any(sensitive in key.lower() for sensitive in SecureLogger.SENSITIVE_KEYS)
                else SecureLogger.redact_sensitive_data(value)
                for key, value in data.items()
            }
        elif isinstance(data, str):
            # Redact anything that looks like an API key (long alphanumeric strings)
            if len(data) > 20 and data.isalnum():
                return '***REDACTED***'
            return data
        elif isinstance(data, (list, tuple)):
            return type(data)(SecureLogger.redact_sensitive_data(item) for item in data)
        else:
            return data
    
    @staticmethod
    def safe_log(level: str, message: str, extra: Optional[Dict] = None) -> None:
        """
        Log message with automatic redaction of sensitive data.
        
        Args:
            level: Log level ('debug', 'info', 'warning', 'error')
            message: Log message
            extra: Extra data to log (will be redacted)
        """
        if extra:
            extra = SecureLogger.redact_sensitive_data(extra)
        
        log_func = getattr(logger, level.lower(), logger.info)
        if extra:
            log_func(message, extra=extra)
        else:
            log_func(message)


class CredentialManager:
    """
    Secure credential manager using environment variables.
    
    Provides secure storage and retrieval of API keys and credentials
    with support for credential rotation, validation, and secure logging.
    
    Credentials are stored in environment variables and never logged or
    exposed in error messages.
    
    Example:
        >>> creds = CredentialManager()
        >>> api_key = creds.get_credential('CRYPTOCOMPARE_API_KEY')
        >>> creds.set_credential('MY_API_KEY', 'secret123')
        >>> creds.validate_credential('CRYPTOCOMPARE_API_KEY')
    """
    
    def __init__(self):
        """Initialize credential manager."""
        self._credentials_cache: Dict[str, str] = {}
        self._last_rotation: Dict[str, datetime] = {}
        self._rotation_interval = timedelta(days=90)  # Recommend rotation every 90 days
        SecureLogger.safe_log('info', "CredentialManager initialized")
    
    def get_credential(self, key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
        """
        Get credential from environment variables.
        
        Args:
            key: Credential key name
            default: Default value if not found
            required: If True, raise error if not found
            
        Returns:
            Credential value or default
            
        Raises:
            ConfigurationError: If required credential not found
            
        Example:
            >>> creds = CredentialManager()
            >>> api_key = creds.get_credential('CRYPTOCOMPARE_API_KEY')
            >>> optional_key = creds.get_credential('OPTIONAL_KEY', default='default_value')
        """
        # Check cache first
        if key in self._credentials_cache:
            SecureLogger.safe_log('debug', f"Retrieved credential from cache: {key}")
            return self._credentials_cache[key]
        
        # Get from environment
        value = os.getenv(key, default)
        
        if value is None and required:
            SecureLogger.safe_log('error', f"Required credential not found: {key}")
            raise ConfigurationError(
                f"Required credential '{key}' not found in environment variables",
                details={'key': key, 'required': True}
            )
        
        if value:
            # Cache the credential
            self._credentials_cache[key] = value
            SecureLogger.safe_log('debug', f"Retrieved credential from environment: {key}")
        else:
            SecureLogger.safe_log('debug', f"Credential not found, using default: {key}")
        
        return value
    
    def set_credential(self, key: str, value: str, persist: bool = False) -> None:
        """
        Set credential in environment and cache.
        
        Args:
            key: Credential key name
            value: Credential value
            persist: If True, attempt to persist to .env file (not recommended for production)
            
        Example:
            >>> creds = CredentialManager()
            >>> creds.set_credential('MY_API_KEY', 'secret123')
        """
        # Set in environment
        os.environ[key] = value
        
        # Cache the credential
        self._credentials_cache[key] = value
        
        # Record rotation time
        self._last_rotation[key] = datetime.now()
        
        SecureLogger.safe_log('info', f"Credential set: {key}")
        
        if persist:
            self._persist_to_env_file(key, value)
    
    def remove_credential(self, key: str) -> None:
        """
        Remove credential from environment and cache.
        
        Args:
            key: Credential key name
            
        Example:
            >>> creds = CredentialManager()
            >>> creds.remove_credential('OLD_API_KEY')
        """
        # Remove from environment
        if key in os.environ:
            del os.environ[key]
        
        # Remove from cache
        if key in self._credentials_cache:
            del self._credentials_cache[key]
        
        # Remove rotation record
        if key in self._last_rotation:
            del self._last_rotation[key]
        
        SecureLogger.safe_log('info', f"Credential removed: {key}")
    
    def validate_credential(self, key: str, min_length: int = 10) -> bool:
        """
        Validate that credential exists and meets minimum requirements.
        
        Args:
            key: Credential key name
            min_length: Minimum required length
            
        Returns:
            True if credential is valid
            
        Raises:
            ConfigurationError: If credential is invalid
            
        Example:
            >>> creds = CredentialManager()
            >>> creds.validate_credential('CRYPTOCOMPARE_API_KEY')
        """
        value = self.get_credential(key)
        
        if not value:
            raise ConfigurationError(
                f"Credential '{key}' is not set",
                details={'key': key}
            )
        
        if len(value) < min_length:
            raise ConfigurationError(
                f"Credential '{key}' is too short (minimum {min_length} characters)",
                details={'key': key, 'min_length': min_length}
            )
        
        SecureLogger.safe_log('debug', f"Credential validated: {key}")
        return True
    
    def check_rotation_needed(self, key: str) -> bool:
        """
        Check if credential rotation is recommended.
        
        Args:
            key: Credential key name
            
        Returns:
            True if rotation is recommended
            
        Example:
            >>> creds = CredentialManager()
            >>> if creds.check_rotation_needed('API_KEY'):
            ...     print("Consider rotating this credential")
        """
        if key not in self._last_rotation:
            # No rotation record, recommend rotation
            return True
        
        last_rotation = self._last_rotation[key]
        time_since_rotation = datetime.now() - last_rotation
        
        if time_since_rotation > self._rotation_interval:
            SecureLogger.safe_log(
                'warning',
                f"Credential rotation recommended: {key}",
                extra={'days_since_rotation': time_since_rotation.days}
            )
            return True
        
        return False
    
    def get_all_credential_keys(self) -> list:
        """
        Get list of all credential keys (not values).
        
        Returns:
            List of credential key names
            
        Example:
            >>> creds = CredentialManager()
            >>> keys = creds.get_all_credential_keys()
            >>> print(keys)
            ['CRYPTOCOMPARE_API_KEY', 'YFINANCE_API_KEY']
        """
        # Get all environment variables that look like credentials
        credential_keys = []
        
        for key in os.environ.keys():
            if any(sensitive in key.upper() for sensitive in ['API', 'KEY', 'SECRET', 'TOKEN', 'PASSWORD']):
                credential_keys.append(key)
        
        return sorted(credential_keys)
    
    def _persist_to_env_file(self, key: str, value: str) -> None:
        """
        Persist credential to .env file (development only).
        
        WARNING: This should only be used in development environments.
        Production credentials should be managed through secure systems.
        
        Args:
            key: Credential key name
            value: Credential value
        """
        env_file = Path('.env')
        
        try:
            # Read existing .env file
            existing_lines = []
            if env_file.exists():
                with open(env_file, 'r') as f:
                    existing_lines = f.readlines()
            
            # Update or add the credential
            key_found = False
            updated_lines = []
            
            for line in existing_lines:
                if line.startswith(f"{key}="):
                    updated_lines.append(f"{key}={value}\n")
                    key_found = True
                else:
                    updated_lines.append(line)
            
            if not key_found:
                updated_lines.append(f"{key}={value}\n")
            
            # Write back to file
            with open(env_file, 'w') as f:
                f.writelines(updated_lines)
            
            SecureLogger.safe_log('info', f"Credential persisted to .env file: {key}")
            
        except Exception as e:
            SecureLogger.safe_log(
                'error',
                f"Failed to persist credential to .env file: {key}",
                extra={'error': str(e)}
            )
    
    def load_from_env_file(self, env_file: str = '.env') -> int:
        """
        Load credentials from .env file.
        
        Args:
            env_file: Path to .env file
            
        Returns:
            Number of credentials loaded
            
        Example:
            >>> creds = CredentialManager()
            >>> count = creds.load_from_env_file('.env')
            >>> print(f"Loaded {count} credentials")
        """
        env_path = Path(env_file)
        
        if not env_path.exists():
            SecureLogger.safe_log('warning', f".env file not found: {env_file}")
            return 0
        
        count = 0
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse key=value
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        self.set_credential(key, value)
                        count += 1
            
            SecureLogger.safe_log('info', f"Loaded {count} credentials from {env_file}")
            
        except Exception as e:
            SecureLogger.safe_log(
                'error',
                f"Failed to load credentials from {env_file}",
                extra={'error': str(e)}
            )
        
        return count
    
    def get_credential_status(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all managed credentials.
        
        Returns:
            Dictionary with credential status information
            
        Example:
            >>> creds = CredentialManager()
            >>> status = creds.get_credential_status()
            >>> for key, info in status.items():
            ...     print(f"{key}: {info['status']}")
        """
        status = {}
        
        for key in self.get_all_credential_keys():
            value = self.get_credential(key)
            
            status[key] = {
                'exists': value is not None,
                'length': len(value) if value else 0,
                'rotation_needed': self.check_rotation_needed(key),
                'last_rotation': self._last_rotation.get(key),
            }
        
        return status


# Global credential manager instance
_credential_manager: Optional[CredentialManager] = None


def get_credential_manager() -> CredentialManager:
    """
    Get global credential manager instance.
    
    Returns:
        Global CredentialManager instance
        
    Example:
        >>> from cryptvault.security import get_credential_manager
        >>> creds = get_credential_manager()
        >>> api_key = creds.get_credential('API_KEY')
    """
    global _credential_manager
    if _credential_manager is None:
        _credential_manager = CredentialManager()
    return _credential_manager
