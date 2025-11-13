"""
Logging Infrastructure

This module provides centralized logging configuration for CryptVault with
support for structured logging, log rotation, and context-aware logging.

Features:
    - Structured logging with JSON format option
    - Automatic log rotation
    - Context-aware logging (request ID, user ID, etc.)
    - Performance logging
    - Error tracking with stack traces
    - Multiple output handlers (console, file, syslog)

Example:
    >>> from cryptvault.utils.logging import setup_logging, get_logger
    >>> setup_logging()
    >>> logger = get_logger(__name__)
    >>> logger.info("Starting analysis", extra={'symbol': 'BTC', 'days': 60})
"""

import logging
import logging.handlers
import sys
import os
import json
import traceback
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from contextlib import contextmanager


# Global logger registry
_loggers: Dict[str, logging.Logger] = {}
_logging_configured = False


class StructuredFormatter(logging.Formatter):
    """
    Structured logging formatter that outputs JSON.

    Converts log records to JSON format for easy parsing and analysis.
    Includes timestamp, level, logger name, message, and any extra fields.

    Example output:
        {
            "timestamp": "2024-01-15T10:30:45.123Z",
            "level": "INFO",
            "logger": "cryptvault.analyzer",
            "message": "Analysis started",
            "symbol": "BTC",
            "days": 60
        }
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """
        log_data = {
            'timestamp': datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'levelno', 'lineno', 'module', 'msecs',
                          'message', 'pathname', 'process', 'processName',
                          'relativeCreated', 'thread', 'threadName', 'exc_info',
                          'exc_text', 'stack_info']:
                log_data[key] = value

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """
    Colored console formatter for better readability.

    Adds color coding based on log level:
    - DEBUG: Cyan
    - INFO: Green
    - WARNING: Yellow
    - ERROR: Red
    - CRITICAL: Red + Bold
    """

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[1;31m', # Bold Red
        'RESET': '\033[0m',       # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with colors.

        Args:
            record: Log record to format

        Returns:
            Colored log string
        """
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"

        # Format the message
        formatted = super().format(record)

        # Reset levelname for next use
        record.levelname = levelname

        return formatted


class ContextFilter(logging.Filter):
    """
    Add context information to log records.

    Automatically adds context like request ID, user ID, or session ID
    to all log records for better traceability.
    """

    def __init__(self):
        """Initialize context filter."""
        super().__init__()
        self.context: Dict[str, Any] = {}

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add context to log record.

        Args:
            record: Log record to filter

        Returns:
            True (always pass the record)
        """
        for key, value in self.context.items():
            setattr(record, key, value)
        return True

    def set_context(self, **kwargs: Any) -> None:
        """
        Set context values.

        Args:
            **kwargs: Context key-value pairs

        Example:
            >>> context_filter.set_context(request_id='abc123', user_id='user456')
        """
        self.context.update(kwargs)

    def clear_context(self) -> None:
        """Clear all context values."""
        self.context.clear()


# Global context filter
_context_filter = ContextFilter()


def setup_logging(
    level: str = 'INFO',
    log_file: Optional[str] = None,
    console: bool = True,
    structured: bool = False,
    rotation: bool = True,
    max_bytes: int = 10485760,  # 10 MB
    backup_count: int = 5
) -> None:
    """
    Set up logging configuration for CryptVault.

    Configures logging with console and/or file output, optional log rotation,
    and structured (JSON) or human-readable format.

    Args:
        level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_file: Path to log file (None to disable file logging)
        console: Enable console logging
        structured: Use structured (JSON) format
        rotation: Enable log file rotation
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup log files to keep

    Example:
        >>> setup_logging(level='DEBUG', log_file='logs/cryptvault.log')
        >>> setup_logging(level='INFO', console=True, structured=True)
    """
    global _logging_configured

    if _logging_configured:
        return

    # Create logs directory if needed
    if log_file:
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))

        if structured:
            console_formatter = StructuredFormatter()
        else:
            console_formatter = ColoredFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(_context_filter)
        root_logger.addHandler(console_handler)

    # File handler
    if log_file:
        if rotation:
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
        else:
            file_handler = logging.FileHandler(log_file)

        file_handler.setLevel(getattr(logging, level.upper()))

        if structured:
            file_formatter = StructuredFormatter()
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

        file_handler.setFormatter(file_formatter)
        file_handler.addFilter(_context_filter)
        root_logger.addHandler(file_handler)

    _logging_configured = True

    # Log configuration
    root_logger.info(
        "Logging configured",
        extra={
            'level': level,
            'console': console,
            'file': log_file,
            'structured': structured,
            'rotation': rotation
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the specified name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting analysis")
    """
    if name not in _loggers:
        _loggers[name] = logging.getLogger(name)
    return _loggers[name]


@contextmanager
def log_context(**kwargs: Any):
    """
    Context manager for adding context to logs.

    All log messages within the context will include the specified context values.

    Args:
        **kwargs: Context key-value pairs

    Example:
        >>> with log_context(request_id='abc123', user_id='user456'):
        ...     logger.info("Processing request")
        ...     # Log will include request_id and user_id
    """
    _context_filter.set_context(**kwargs)
    try:
        yield
    finally:
        _context_filter.clear_context()


def log_performance(
    logger: logging.Logger,
    operation: str,
    duration: float,
    **kwargs: Any
) -> None:
    """
    Log performance metrics.

    Args:
        logger: Logger instance
        operation: Operation name
        duration: Duration in seconds
        **kwargs: Additional metrics

    Example:
        >>> import time
        >>> start = time.time()
        >>> # ... do work ...
        >>> duration = time.time() - start
        >>> log_performance(logger, 'analysis', duration, symbol='BTC', patterns=5)
    """
    logger.info(
        f"Performance: {operation}",
        extra={
            'operation': operation,
            'duration_seconds': duration,
            'duration_ms': duration * 1000,
            **kwargs
        }
    )


def log_error_with_context(
    logger: logging.Logger,
    error: Exception,
    message: str,
    **kwargs: Any
) -> None:
    """
    Log error with full context and stack trace.

    Args:
        logger: Logger instance
        error: Exception that occurred
        message: Error message
        **kwargs: Additional context

    Example:
        >>> try:
        ...     # ... some operation ...
        ...     pass
        ... except Exception as e:
        ...     log_error_with_context(
        ...         logger, e, "Failed to fetch data",
        ...         symbol='BTC', source='yfinance'
        ...     )
    """
    logger.error(
        message,
        exc_info=True,
        extra={
            'error_type': type(error).__name__,
            'error_message': str(error),
            **kwargs
        }
    )


def configure_from_config(config: Any) -> None:
    """
    Configure logging from Config object.

    Args:
        config: Config instance with logging configuration

    Example:
        >>> from cryptvault.config import Config
        >>> config = Config.load()
        >>> configure_from_config(config)
    """
    setup_logging(
        level=config.logging.level,
        log_file=config.logging.file_path if config.logging.file_enabled else None,
        console=config.logging.console_enabled,
        structured=False,  # Can be added to config if needed
        rotation=True,
        max_bytes=config.logging.file_max_bytes,
        backup_count=config.logging.file_backup_count
    )


def reset_logging() -> None:
    """
    Reset logging configuration.

    Useful for testing or reconfiguring logging.

    Example:
        >>> reset_logging()
        >>> setup_logging(level='DEBUG')
    """
    global _logging_configured
    _logging_configured = False

    # Clear all handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Clear logger registry
    _loggers.clear()

    # Clear context
    _context_filter.clear_context()
