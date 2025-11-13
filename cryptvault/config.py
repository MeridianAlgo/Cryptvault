"""
Configuration Management System

This module provides centralized configuration management for CryptVault with
support for multiple environments, validation, and environment variable overrides.

Example:
    >>> from cryptvault.config import Config
    >>> config = Config.load('production')
    >>> api_key = config.get('api.yfinance.key')
    >>> timeout = config.get('network.timeout', default=30)
"""

import os
import yaml
import logging
from typing import Any, Dict, Optional
from pathlib import Path
from dataclasses import dataclass, field


logger = logging.getLogger(__name__)


@dataclass
class NetworkConfig:
    """Network and API configuration."""
    timeout: int = 30
    max_retries: int = 3
    retry_backoff: float = 2.0
    connection_pool_size: int = 10
    rate_limit_calls: int = 100
    rate_limit_period: int = 60  # seconds


@dataclass
class CacheConfig:
    """Caching configuration."""
    enabled: bool = True
    ttl: int = 300  # seconds (5 minutes)
    max_size_mb: int = 100
    backend: str = 'memory'  # 'memory' or 'disk'
    disk_path: Optional[str] = None


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = 'INFO'
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file_enabled: bool = True
    file_path: str = 'logs/cryptvault.log'
    file_max_bytes: int = 10485760  # 10 MB
    file_backup_count: int = 5
    console_enabled: bool = True


@dataclass
class AnalysisConfig:
    """Analysis configuration."""
    default_days: int = 60
    default_interval: str = '1d'
    min_data_points: int = 50
    pattern_sensitivity: float = 0.5
    ml_enabled: bool = True
    ml_confidence_threshold: float = 0.6


@dataclass
class DataSourceConfig:
    """Data source configuration."""
    primary: str = 'yfinance'
    fallback: list = field(default_factory=lambda: ['ccxt', 'cryptocompare'])
    yfinance_enabled: bool = True
    ccxt_enabled: bool = True
    cryptocompare_enabled: bool = True
    cryptocompare_api_key: Optional[str] = None


class ConfigValidator:
    """Validates configuration values."""

    @staticmethod
    def validate_network_config(config: NetworkConfig) -> bool:
        """
        Validate network configuration.

        Args:
            config: Network configuration to validate

        Returns:
            True if valid

        Raises:
            ValueError: If configuration is invalid
        """
        if config.timeout <= 0:
            raise ValueError("Network timeout must be positive")
        if config.max_retries < 0:
            raise ValueError("Max retries cannot be negative")
        if config.retry_backoff <= 0:
            raise ValueError("Retry backoff must be positive")
        if config.connection_pool_size <= 0:
            raise ValueError("Connection pool size must be positive")
        if config.rate_limit_calls <= 0:
            raise ValueError("Rate limit calls must be positive")
        if config.rate_limit_period <= 0:
            raise ValueError("Rate limit period must be positive")
        return True

    @staticmethod
    def validate_cache_config(config: CacheConfig) -> bool:
        """
        Validate cache configuration.

        Args:
            config: Cache configuration to validate

        Returns:
            True if valid

        Raises:
            ValueError: If configuration is invalid
        """
        if config.ttl <= 0:
            raise ValueError("Cache TTL must be positive")
        if config.max_size_mb <= 0:
            raise ValueError("Cache max size must be positive")
        if config.backend not in ['memory', 'disk']:
            raise ValueError("Cache backend must be 'memory' or 'disk'")
        if config.backend == 'disk' and not config.disk_path:
            raise ValueError("Disk cache requires disk_path")
        return True

    @staticmethod
    def validate_logging_config(config: LoggingConfig) -> bool:
        """
        Validate logging configuration.

        Args:
            config: Logging configuration to validate

        Returns:
            True if valid

        Raises:
            ValueError: If configuration is invalid
        """
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if config.level not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        if config.file_max_bytes <= 0:
            raise ValueError("File max bytes must be positive")
        if config.file_backup_count < 0:
            raise ValueError("File backup count cannot be negative")
        return True

    @staticmethod
    def validate_analysis_config(config: AnalysisConfig) -> bool:
        """
        Validate analysis configuration.

        Args:
            config: Analysis configuration to validate

        Returns:
            True if valid

        Raises:
            ValueError: If configuration is invalid
        """
        if config.default_days <= 0:
            raise ValueError("Default days must be positive")
        if config.min_data_points <= 0:
            raise ValueError("Min data points must be positive")
        if not 0 <= config.pattern_sensitivity <= 1:
            raise ValueError("Pattern sensitivity must be between 0 and 1")
        if not 0 <= config.ml_confidence_threshold <= 1:
            raise ValueError("ML confidence threshold must be between 0 and 1")
        valid_intervals = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1wk', '1mo']
        if config.default_interval not in valid_intervals:
            raise ValueError(f"Default interval must be one of {valid_intervals}")
        return True


class Config:
    """
    Main configuration class for CryptVault.

    Supports multiple environments (development, testing, production) and
    environment variable overrides.

    Attributes:
        environment: Current environment name
        network: Network configuration
        cache: Cache configuration
        logging: Logging configuration
        analysis: Analysis configuration
        data_sources: Data source configuration

    Example:
        >>> config = Config.load('production')
        >>> timeout = config.network.timeout
        >>> config.validate()
    """

    def __init__(self, environment: str = 'production'):
        """
        Initialize configuration.

        Args:
            environment: Environment name ('development', 'testing', 'production')
        """
        self.environment = environment
        self.network = NetworkConfig()
        self.cache = CacheConfig()
        self.logging = LoggingConfig()
        self.analysis = AnalysisConfig()
        self.data_sources = DataSourceConfig()
        self._custom_values: Dict[str, Any] = {}

    @classmethod
    def load(cls, environment: str = 'production') -> 'Config':
        """
        Load configuration for specified environment.

        Loads configuration from:
        1. Default values
        2. config/settings.yaml (if exists)
        3. Environment-specific config file (if exists)
        4. Environment variables (override)

        Args:
            environment: Environment name

        Returns:
            Configured Config instance

        Example:
            >>> config = Config.load('production')
            >>> config = Config.load('development')
        """
        config = cls(environment)

        # Load from YAML files
        config._load_from_yaml()

        # Override with environment variables
        config._load_from_env()

        # Validate configuration
        config.validate()

        logger.info(f"Configuration loaded for environment: {environment}")
        return config

    def _load_from_yaml(self) -> None:
        """Load configuration from YAML files."""
        config_dir = Path(__file__).parent.parent / 'config'

        # Load base settings
        base_config_path = config_dir / 'settings.yaml'
        if base_config_path.exists():
            with open(base_config_path, 'r') as f:
                base_config = yaml.safe_load(f) or {}
                self._apply_config_dict(base_config)

        # Load environment-specific settings
        env_config_path = config_dir / f'settings.{self.environment}.yaml'
        if env_config_path.exists():
            with open(env_config_path, 'r') as f:
                env_config = yaml.safe_load(f) or {}
                self._apply_config_dict(env_config)

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Network configuration
        if timeout := os.getenv('CRYPTVAULT_NETWORK_TIMEOUT'):
            self.network.timeout = int(timeout)
        if max_retries := os.getenv('CRYPTVAULT_NETWORK_MAX_RETRIES'):
            self.network.max_retries = int(max_retries)

        # Cache configuration
        if cache_enabled := os.getenv('CRYPTVAULT_CACHE_ENABLED'):
            self.cache.enabled = cache_enabled.lower() == 'true'
        if cache_ttl := os.getenv('CRYPTVAULT_CACHE_TTL'):
            self.cache.ttl = int(cache_ttl)

        # Logging configuration
        if log_level := os.getenv('CRYPTVAULT_LOG_LEVEL'):
            self.logging.level = log_level.upper()
        if log_file := os.getenv('CRYPTVAULT_LOG_FILE'):
            self.logging.file_path = log_file

        # Analysis configuration
        if default_days := os.getenv('CRYPTVAULT_DEFAULT_DAYS'):
            self.analysis.default_days = int(default_days)
        if ml_enabled := os.getenv('CRYPTVAULT_ML_ENABLED'):
            self.analysis.ml_enabled = ml_enabled.lower() == 'true'

        # Data source configuration
        if api_key := os.getenv('CRYPTOCOMPARE_API_KEY'):
            self.data_sources.cryptocompare_api_key = api_key

    def _apply_config_dict(self, config_dict: Dict[str, Any]) -> None:
        """Apply configuration from dictionary."""
        if 'network' in config_dict:
            for key, value in config_dict['network'].items():
                if hasattr(self.network, key):
                    setattr(self.network, key, value)

        if 'cache' in config_dict:
            for key, value in config_dict['cache'].items():
                if hasattr(self.cache, key):
                    setattr(self.cache, key, value)

        if 'logging' in config_dict:
            for key, value in config_dict['logging'].items():
                if hasattr(self.logging, key):
                    setattr(self.logging, key, value)

        if 'analysis' in config_dict:
            for key, value in config_dict['analysis'].items():
                if hasattr(self.analysis, key):
                    setattr(self.analysis, key, value)

        if 'data_sources' in config_dict:
            for key, value in config_dict['data_sources'].items():
                if hasattr(self.data_sources, key):
                    setattr(self.data_sources, key, value)

    def validate(self) -> bool:
        """
        Validate all configuration values.

        Returns:
            True if all configuration is valid

        Raises:
            ValueError: If any configuration is invalid

        Example:
            >>> config = Config.load()
            >>> config.validate()
            True
        """
        validator = ConfigValidator()
        validator.validate_network_config(self.network)
        validator.validate_cache_config(self.cache)
        validator.validate_logging_config(self.logging)
        validator.validate_analysis_config(self.analysis)
        return True

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.

        Args:
            key: Configuration key in dot notation (e.g., 'network.timeout')
            default: Default value if key not found

        Returns:
            Configuration value or default

        Example:
            >>> config = Config.load()
            >>> timeout = config.get('network.timeout')
            >>> custom = config.get('custom.value', default=42)
        """
        parts = key.split('.')

        # Check custom values first
        if key in self._custom_values:
            return self._custom_values[key]

        # Navigate through configuration objects
        obj = self
        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            else:
                return default

        return obj if obj != self else default

    def set(self, key: str, value: Any) -> None:
        """
        Set custom configuration value.

        Args:
            key: Configuration key in dot notation
            value: Value to set

        Example:
            >>> config = Config.load()
            >>> config.set('custom.api_key', 'secret123')
        """
        self._custom_values[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration

        Example:
            >>> config = Config.load()
            >>> config_dict = config.to_dict()
            >>> print(config_dict['network']['timeout'])
        """
        return {
            'environment': self.environment,
            'network': {
                'timeout': self.network.timeout,
                'max_retries': self.network.max_retries,
                'retry_backoff': self.network.retry_backoff,
                'connection_pool_size': self.network.connection_pool_size,
                'rate_limit_calls': self.network.rate_limit_calls,
                'rate_limit_period': self.network.rate_limit_period,
            },
            'cache': {
                'enabled': self.cache.enabled,
                'ttl': self.cache.ttl,
                'max_size_mb': self.cache.max_size_mb,
                'backend': self.cache.backend,
                'disk_path': self.cache.disk_path,
            },
            'logging': {
                'level': self.logging.level,
                'format': self.logging.format,
                'file_enabled': self.logging.file_enabled,
                'file_path': self.logging.file_path,
                'file_max_bytes': self.logging.file_max_bytes,
                'file_backup_count': self.logging.file_backup_count,
                'console_enabled': self.logging.console_enabled,
            },
            'analysis': {
                'default_days': self.analysis.default_days,
                'default_interval': self.analysis.default_interval,
                'min_data_points': self.analysis.min_data_points,
                'pattern_sensitivity': self.analysis.pattern_sensitivity,
                'ml_enabled': self.analysis.ml_enabled,
                'ml_confidence_threshold': self.analysis.ml_confidence_threshold,
            },
            'data_sources': {
                'primary': self.data_sources.primary,
                'fallback': self.data_sources.fallback,
                'yfinance_enabled': self.data_sources.yfinance_enabled,
                'ccxt_enabled': self.data_sources.ccxt_enabled,
                'cryptocompare_enabled': self.data_sources.cryptocompare_enabled,
            },
            'custom': self._custom_values,
        }


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get global configuration instance.

    Returns:
        Global Config instance

    Example:
        >>> from cryptvault.config import get_config
        >>> config = get_config()
        >>> timeout = config.network.timeout
    """
    global _config
    if _config is None:
        env = os.getenv('CRYPTVAULT_ENV', 'production')
        _config = Config.load(env)
    return _config


def reset_config() -> None:
    """
    Reset global configuration instance.

    Useful for testing or reloading configuration.

    Example:
        >>> from cryptvault.config import reset_config
        >>> reset_config()
        >>> config = get_config()  # Loads fresh configuration
    """
    global _config
    _config = None
