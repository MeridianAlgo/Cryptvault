"""
System-Wide Constants

This module defines all constants used throughout CryptVault.
Constants are organized by category for easy reference.

Example:
    >>> from cryptvault.constants import SUPPORTED_INTERVALS, DEFAULT_ANALYSIS_DAYS
    >>> print(f"Default analysis period: {DEFAULT_ANALYSIS_DAYS} days")
    >>> print(f"Supported intervals: {SUPPORTED_INTERVALS}")
"""

from typing import List, Dict

# Version Information
VERSION = '4.0.0'
VERSION_INFO = (4, 0, 0)

# Application Metadata
APP_NAME = 'CryptVault'
APP_DESCRIPTION = 'Advanced AI-Powered Cryptocurrency Analysis Platform'
APP_AUTHOR = 'MeridianAlgo Algorithmic Research Team'
APP_LICENSE = 'MIT'
APP_URL = 'https://github.com/MeridianAlgo/Cryptvault'

# Analysis Constants
DEFAULT_ANALYSIS_DAYS = 60
DEFAULT_INTERVAL = '1d'
MIN_DATA_POINTS = 50
MAX_DATA_POINTS = 10000
DEFAULT_PATTERN_SENSITIVITY = 0.5

# Time Intervals
SUPPORTED_INTERVALS: List[str] = [
    '1m',   # 1 minute
    '5m',   # 5 minutes
    '15m',  # 15 minutes
    '30m',  # 30 minutes
    '1h',   # 1 hour
    '4h',   # 4 hours
    '1d',   # 1 day
    '1wk',  # 1 week
    '1mo',  # 1 month
]

# Interval to seconds mapping
INTERVAL_TO_SECONDS: Dict[str, int] = {
    '1m': 60,
    '5m': 300,
    '15m': 900,
    '30m': 1800,
    '1h': 3600,
    '4h': 14400,
    '1d': 86400,
    '1wk': 604800,
    '1mo': 2592000,  # Approximate (30 days)
}

# Pattern Types
PATTERN_TYPES: List[str] = [
    # Reversal Patterns
    'Double Top',
    'Double Bottom',
    'Triple Top',
    'Triple Bottom',
    'Head and Shoulders',
    'Inverse Head and Shoulders',
    'Rounding Top',
    'Rounding Bottom',
    'V-Top',
    'V-Bottom',

    # Continuation Patterns
    'Bull Flag',
    'Bear Flag',
    'Pennant',
    'Ascending Triangle',
    'Descending Triangle',
    'Symmetrical Triangle',
    'Rectangle',
    'Rising Wedge',
    'Falling Wedge',

    # Harmonic Patterns
    'Gartley',
    'Butterfly',
    'Bat',
    'Crab',
    'Shark',
    'Cypher',
    'ABCD',

    # Candlestick Patterns
    'Doji',
    'Hammer',
    'Shooting Star',
    'Engulfing Bull',
    'Engulfing Bear',
    'Morning Star',
    'Evening Star',
    'Harami',
]

# Pattern Categories
PATTERN_CATEGORIES: Dict[str, str] = {
    'Double Top': 'Bearish Reversal',
    'Double Bottom': 'Bullish Reversal',
    'Triple Top': 'Bearish Reversal',
    'Triple Bottom': 'Bullish Reversal',
    'Head and Shoulders': 'Bearish Reversal',
    'Inverse Head and Shoulders': 'Bullish Reversal',
    'Rounding Top': 'Bearish Reversal',
    'Rounding Bottom': 'Bullish Reversal',
    'V-Top': 'Bearish Reversal',
    'V-Bottom': 'Bullish Reversal',
    'Bull Flag': 'Bullish Continuation',
    'Bear Flag': 'Bearish Continuation',
    'Pennant': 'Continuation',
    'Ascending Triangle': 'Bullish Continuation',
    'Descending Triangle': 'Bearish Continuation',
    'Symmetrical Triangle': 'Continuation',
    'Rectangle': 'Continuation',
    'Rising Wedge': 'Bearish Reversal',
    'Falling Wedge': 'Bullish Reversal',
    'Gartley': 'Harmonic',
    'Butterfly': 'Harmonic',
    'Bat': 'Harmonic',
    'Crab': 'Harmonic',
    'Shark': 'Harmonic',
    'Cypher': 'Harmonic',
    'ABCD': 'Harmonic',
    'Doji': 'Indecision',
    'Hammer': 'Bullish Reversal',
    'Shooting Star': 'Bearish Reversal',
    'Engulfing Bull': 'Bullish Reversal',
    'Engulfing Bear': 'Bearish Reversal',
    'Morning Star': 'Bullish Reversal',
    'Evening Star': 'Bearish Reversal',
    'Harami': 'Reversal',
}

# Technical Indicators
INDICATOR_PERIODS: Dict[str, int] = {
    'RSI': 14,
    'MACD_FAST': 12,
    'MACD_SLOW': 26,
    'MACD_SIGNAL': 9,
    'SMA_SHORT': 20,
    'SMA_MEDIUM': 50,
    'SMA_LONG': 200,
    'EMA_SHORT': 12,
    'EMA_LONG': 26,
    'BOLLINGER_BANDS': 20,
    'ATR': 14,
    'STOCHASTIC': 14,
}

# Confidence Thresholds
CONFIDENCE_THRESHOLDS: Dict[str, float] = {
    'HIGH': 0.8,      # 80%+ confidence
    'MEDIUM': 0.6,    # 60-80% confidence
    'LOW': 0.4,       # 40-60% confidence
    'VERY_LOW': 0.0,  # <40% confidence
}

# ML Model Constants
ML_PREDICTION_HORIZON = 7  # Days
ML_FEATURE_COUNT = 80      # Total number of features
ML_MIN_TRAINING_SAMPLES = 100
ML_ENSEMBLE_WEIGHTS: Dict[str, float] = {
    'linear': 0.30,
    'random_forest': 0.25,
    'gradient_boosting': 0.25,
    'lstm': 0.20,
}

# Cache Constants
CACHE_TTL_SECONDS = 300  # 5 minutes
CACHE_MAX_SIZE_MB = 100
CACHE_KEY_PREFIX = 'cryptvault'

# Network Constants
DEFAULT_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_BACKOFF = 2.0  # Exponential backoff multiplier
CONNECTION_POOL_SIZE = 10
RATE_LIMIT_CALLS = 100
RATE_LIMIT_PERIOD = 60  # seconds

# Data Source Constants
DATA_SOURCES: List[str] = [
    'yfinance',
    'ccxt',
    'cryptocompare',
]

PRIMARY_DATA_SOURCE = 'yfinance'
FALLBACK_DATA_SOURCES = ['ccxt', 'cryptocompare']

# Supported Assets
# Major Cryptocurrencies
MAJOR_CRYPTOCURRENCIES: List[str] = [
    'BTC', 'ETH', 'USDT', 'BNB', 'SOL', 'XRP', 'USDC', 'ADA', 'AVAX', 'DOGE',
    'TRX', 'DOT', 'MATIC', 'LINK', 'TON', 'SHIB', 'LTC', 'BCH', 'UNI', 'ATOM',
    'XLM', 'XMR', 'ETC', 'HBAR', 'FIL', 'APT', 'ARB', 'VET', 'NEAR', 'ALGO',
    'ICP', 'GRT', 'AAVE', 'MKR', 'SNX', 'SAND', 'MANA', 'AXS', 'FTM', 'THETA',
    'EOS', 'XTZ', 'FLOW', 'EGLD', 'ZEC', 'CAKE', 'KLAY', 'RUNE', 'NEO', 'DASH',
]

# Major Stocks
MAJOR_STOCKS: List[str] = [
    # Technology
    'AAPL', 'TSLA', 'GOOGL', 'GOOG', 'MSFT', 'NVDA', 'AMZN', 'META', 'NFLX',
    'AMD', 'INTC', 'CRM', 'ORCL', 'ADBE', 'CSCO', 'AVGO', 'QCOM', 'TXN',
    'INTU', 'IBM',
    # Finance
    'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'SCHW', 'AXP', 'USB',
    'V', 'MA', 'PYPL', 'SQ', 'COIN',
    # Consumer
    'WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'COST', 'LOW', 'DIS', 'CMCSA',
    # Healthcare
    'JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'MRK', 'ABT', 'DHR', 'LLY', 'BMY',
    # Energy & Industrial
    'XOM', 'CVX', 'COP', 'SLB', 'BA', 'CAT', 'GE', 'MMM', 'HON', 'UPS',
    # Transportation
    'UBER', 'LYFT', 'ABNB', 'DAL', 'UAL', 'AAL',
]

# ETFs
MAJOR_ETFS: List[str] = [
    'SPY', 'QQQ', 'IWM', 'DIA', 'VOO', 'VTI', 'GLD', 'SLV',
]

# All supported tickers
SUPPORTED_TICKERS = MAJOR_CRYPTOCURRENCIES + MAJOR_STOCKS + MAJOR_ETFS

# Logging Constants
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FILE_MAX_BYTES = 10485760  # 10 MB
LOG_FILE_BACKUP_COUNT = 5

# File Paths
DEFAULT_LOG_DIR = 'logs'
DEFAULT_CACHE_DIR = 'cache'
DEFAULT_DATA_DIR = 'data'
DEFAULT_CONFIG_DIR = 'config'

# Color Codes (for terminal output)
COLORS: Dict[str, str] = {
    'RESET': '\033[0m',
    'BOLD': '\033[1m',
    'RED': '\033[91m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'MAGENTA': '\033[95m',
    'CYAN': '\033[96m',
    'WHITE': '\033[97m',
}

# Trend Classifications
TREND_BULLISH = 'bullish'
TREND_BEARISH = 'bearish'
TREND_SIDEWAYS = 'sideways'
TREND_NEUTRAL = 'neutral'

# Volume Profile Types
VOLUME_INCREASING = 'increasing'
VOLUME_DECREASING = 'decreasing'
VOLUME_STABLE = 'stable'
VOLUME_UNKNOWN = 'unknown'

# Error Messages
ERROR_MESSAGES: Dict[str, str] = {
    'INSUFFICIENT_DATA': 'Insufficient data points. Need at least {min_points}, got {actual_points}',
    'INVALID_TICKER': 'Invalid ticker symbol: {symbol}',
    'INVALID_INTERVAL': 'Invalid interval: {interval}. Supported: {supported}',
    'INVALID_DATE_RANGE': 'Invalid date range: start={start}, end={end}',
    'API_ERROR': 'API error: {message}',
    'NETWORK_ERROR': 'Network error: {message}',
    'RATE_LIMIT': 'Rate limit exceeded. Retry after {retry_after} seconds',
    'CONFIGURATION_ERROR': 'Configuration error: {message}',
    'ANALYSIS_ERROR': 'Analysis error: {message}',
}

# Success Messages
SUCCESS_MESSAGES: Dict[str, str] = {
    'ANALYSIS_COMPLETE': 'Analysis completed in {time:.2f}s | {patterns} patterns found',
    'DATA_FETCHED': 'Fetched {points} data points for {symbol}',
    'CACHE_HIT': 'Cache hit for {key}',
    'CACHE_MISS': 'Cache miss for {key}',
}
