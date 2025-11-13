# CryptVault API Reference

## Overview

This document provides comprehensive API documentation for CryptVault's public interfaces. All public classes and methods are documented with usage examples, parameter descriptions, and return types.

## Table of Contents

1. [Core Analysis API](#core-analysis-api)
2. [Data Layer API](#data-layer-api)
3. [Pattern Detection API](#pattern-detection-api)
4. [Technical Indicators API](#technical-indicators-api)
5. [Machine Learning API](#machine-learning-api)
6. [Configuration API](#configuration-api)
7. [CLI API](#cli-api)
8. [Data Models](#data-models)
9. [Exceptions](#exceptions)

---

## Core Analysis API

### PatternAnalyzer

Main orchestrator for cryptocurrency and stock analysis.

**Module**: `cryptvault.core.analyzer`

#### Constructor

```python
PatternAnalyzer(config_manager: Optional[ConfigManager] = None)
```

**Parameters**:
- `config_manager` (ConfigManager, optional): Configuration manager instance. If not provided, default configuration is used.

**Example**:
```python
from cryptvault.core.analyzer import PatternAnalyzer

# Use default configuration
analyzer = PatternAnalyzer()

# Use custom configuration
from cryptvault.config.manager import ConfigManager
config = ConfigManager(env='production')
analyzer = PatternAnalyzer(config_manager=config)
```

#### Methods

##### analyze_ticker()

Analyze cryptocurrency or stock by ticker symbol with real-time data fetching.

```python
analyze_ticker(
    ticker: str,
    days: int = 60,
    interval: str = '1d',
    sensitivity: Optional[float] = None
) -> AnalysisResult
```

**Parameters**:
- `ticker` (str): Ticker symbol (e.g., 'BTC', 'ETH', 'AAPL')
- `days` (int, default=60): Number of days of historical data to fetch
- `interval` (str, default='1d'): Data interval - '1m', '5m', '1h', '4h', '1d', '1wk'
- `sensitivity` (float, optional): Pattern detection sensitivity 0.0-1.0

**Returns**:
- `AnalysisResult`: Comprehensive analysis results

**Raises**:
- `InvalidTickerError`: If ticker symbol is invalid
- `DataFetchError`: If data cannot be fetched
- `InsufficientDataError`: If insufficient data for analysis

**Example**:
```python
analyzer = PatternAnalyzer()

# Basic analysis
result = analyzer.analyze_ticker('BTC', days=60)

# Custom interval and sensitivity
result = analyzer.analyze_ticker(
    'ETH',
    days=30,
    interval='4h',
    sensitivity=0.7
)

if result.success:
    print(f"Found {len(result.patterns)} patterns")
    print(f"Analysis took {result.analysis_time:.2f}s")
```


##### analyze_from_csv()

Analyze patterns from CSV data.

```python
analyze_from_csv(
    csv_data: str,
    sensitivity: Optional[float] = None
) -> AnalysisResult
```

**Parameters**:
- `csv_data` (str): CSV formatted price data with columns: timestamp, open, high, low, close, volume
- `sensitivity` (float, optional): Pattern detection sensitivity 0.0-1.0

**Returns**:
- `AnalysisResult`: Analysis results

**Example**:
```python
csv_data = """timestamp,open,high,low,close,volume
2024-01-01,50000,51000,49500,50500,1000000
2024-01-02,50500,52000,50000,51500,1200000"""

result = analyzer.analyze_from_csv(csv_data)
```

##### analyze_from_json()

Analyze patterns from JSON data.

```python
analyze_from_json(
    json_data: str,
    sensitivity: Optional[float] = None
) -> AnalysisResult
```

**Parameters**:
- `json_data` (str): JSON formatted price data
- `sensitivity` (float, optional): Pattern detection sensitivity 0.0-1.0

**Returns**:
- `AnalysisResult`: Analysis results

**Example**:
```python
json_data = '''
{
    "symbol": "BTC",
    "data": [
        {"timestamp": "2024-01-01", "close": 50000, "volume": 1000000},
        {"timestamp": "2024-01-02", "close": 51000, "volume": 1200000}
    ]
}
'''

result = analyzer.analyze_from_json(json_data)
```

##### analyze_dataframe()

Analyze patterns from PriceDataFrame object.

```python
analyze_dataframe(
    data_frame: PriceDataFrame,
    sensitivity: Optional[float] = None
) -> AnalysisResult
```

**Parameters**:
- `data_frame` (PriceDataFrame): Price data frame to analyze
- `sensitivity` (float, optional): Pattern detection sensitivity 0.0-1.0

**Returns**:
- `AnalysisResult`: Analysis results

**Example**:
```python
from cryptvault.data.models import PriceDataFrame, PricePoint
from datetime import datetime

# Create price data
points = [
    PricePoint(datetime(2024, 1, 1), 50000, 51000, 49500, 50500, 1000000),
    PricePoint(datetime(2024, 1, 2), 50500, 52000, 50000, 51500, 1200000)
]
data_frame = PriceDataFrame(points, symbol='BTC', interval='1d')

result = analyzer.analyze_dataframe(data_frame)
```

---

## Data Layer API

### DataFetcher

Unified data fetcher with automatic fallback between data sources.

**Module**: `cryptvault.data.fetchers`

#### Constructor

```python
DataFetcher()
```

**Example**:
```python
from cryptvault.data.fetchers import DataFetcher

fetcher = DataFetcher()
```

#### Methods

##### fetch()

Fetch price data with automatic fallback between sources.

```python
fetch(
    symbol: str,
    days: int = 60,
    interval: str = '1d',
    source: Optional[str] = None
) -> PriceDataFrame
```

**Parameters**:
- `symbol` (str): Ticker symbol
- `days` (int, default=60): Number of days of data
- `interval` (str, default='1d'): Data interval
- `source` (str, optional): Specific source to use ('yfinance', 'ccxt')

**Returns**:
- `PriceDataFrame`: Fetched price data

**Raises**:
- `DataFetchError`: If all sources fail

**Example**:
```python
fetcher = DataFetcher()

# Fetch with automatic source selection
data = fetcher.fetch('BTC', days=60, interval='1d')

# Fetch from specific source
data = fetcher.fetch('BTC', days=30, source='yfinance')

print(f"Fetched {len(data)} data points")
```

##### fetch_market_data()

Fetch complete market data including ticker information.

```python
fetch_market_data(
    symbol: str,
    days: int = 60,
    interval: str = '1d'
) -> MarketData
```

**Parameters**:
- `symbol` (str): Ticker symbol
- `days` (int, default=60): Number of days
- `interval` (str, default='1d'): Data interval

**Returns**:
- `MarketData`: Complete market data with ticker info

**Example**:
```python
market_data = fetcher.fetch_market_data('AAPL', days=30)

print(f"Symbol: {market_data.ticker_info.name}")
print(f"Exchange: {market_data.ticker_info.exchange}")
print(f"Data points: {len(market_data.price_data)}")
```

##### get_available_sources()

Get status of available data sources.

```python
get_available_sources() -> Dict[str, bool]
```

**Returns**:
- `Dict[str, bool]`: Dictionary mapping source names to availability

**Example**:
```python
sources = fetcher.get_available_sources()
print(f"YFinance available: {sources.get('yfinance', False)}")
print(f"CCXT available: {sources.get('ccxt', False)}")
```

---

## Pattern Detection API

### BasePatternDetector

Abstract base class for all pattern detectors.

**Module**: `cryptvault.patterns.base`

#### Methods

##### detect()

Detect patterns in price data (must be implemented by subclasses).

```python
detect(
    data: PriceDataFrame,
    sensitivity: float = 0.5
) -> List[DetectedPattern]
```

**Parameters**:
- `data` (PriceDataFrame): Price data to analyze
- `sensitivity` (float, default=0.5): Detection sensitivity 0.0-1.0

**Returns**:
- `List[DetectedPattern]`: List of detected patterns

### ReversalPatternDetector

Detects reversal chart patterns.

**Module**: `cryptvault.patterns.reversal`

#### Constructor

```python
ReversalPatternDetector()
```

#### Methods

##### detect()

Detect reversal patterns in price data.

```python
detect(
    data: PriceDataFrame,
    sensitivity: float = 0.5
) -> List[DetectedPattern]
```

**Detected Patterns**:
- Head and Shoulders
- Inverse Head and Shoulders
- Double Top
- Double Bottom
- Triple Top
- Triple Bottom

**Example**:
```python
from cryptvault.patterns.reversal import ReversalPatternDetector
from cryptvault.data.fetchers import DataFetcher

# Fetch data
fetcher = DataFetcher()
data = fetcher.fetch('BTC', days=60)

# Detect reversal patterns
detector = ReversalPatternDetector()
patterns = detector.detect(data, sensitivity=0.6)

for pattern in patterns:
    print(f"{pattern.pattern_type}: {pattern.confidence:.2%} confidence")
```

### ContinuationPatternDetector

Detects continuation chart patterns.

**Module**: `cryptvault.patterns.continuation`

**Detected Patterns**:
- Bull Flag
- Bear Flag
- Pennant
- Ascending Triangle
- Descending Triangle
- Symmetrical Triangle

**Example**:
```python
from cryptvault.patterns.continuation import ContinuationPatternDetector

detector = ContinuationPatternDetector()
patterns = detector.detect(data, sensitivity=0.5)
```

### HarmonicPatternDetector

Detects harmonic patterns based on Fibonacci ratios.

**Module**: `cryptvault.patterns.harmonic`

**Detected Patterns**:
- Gartley
- Butterfly
- Bat
- Crab

**Example**:
```python
from cryptvault.patterns.harmonic import HarmonicPatternDetector

detector = HarmonicPatternDetector()
patterns = detector.detect(data, sensitivity=0.7)
```

---

## Technical Indicators API

### TechnicalIndicators

Calculate technical indicators efficiently using NumPy vectorization.

**Module**: `cryptvault.analysis.technical`

#### Trend Indicators

##### calculate_sma()

Calculate Simple Moving Average.

```python
calculate_sma(prices: List[float], period: int = 20) -> List[float]
```

**Parameters**:
- `prices` (List[float]): Price data
- `period` (int, default=20): Moving average period

**Returns**:
- `List[float]`: SMA values

**Time Complexity**: O(n)

**Example**:
```python
from cryptvault.indicators.trend import calculate_sma

closes = [50000, 51000, 50500, 52000, 51500]
sma = calculate_sma(closes, period=3)
print(f"SMA: {sma}")
```

##### calculate_ema()

Calculate Exponential Moving Average.

```python
calculate_ema(prices: List[float], period: int = 20) -> List[float]
```

**Parameters**:
- `prices` (List[float]): Price data
- `period` (int, default=20): EMA period

**Returns**:
- `List[float]`: EMA values

**Formula**: EMA = Price(t) × k + EMA(y) × (1 − k), where k = 2 / (period + 1)

**Example**:
```python
from cryptvault.indicators.trend import calculate_ema

ema = calculate_ema(closes, period=12)
```

#### Momentum Indicators

##### calculate_rsi()

Calculate Relative Strength Index.

```python
calculate_rsi(prices: List[float], period: int = 14) -> List[float]
```

**Parameters**:
- `prices` (List[float]): Price data
- `period` (int, default=14): RSI period

**Returns**:
- `List[float]`: RSI values (0-100)

**Formula**: RSI = 100 - (100 / (1 + RS)), where RS = Average Gain / Average Loss

**Interpretation**:
- RSI > 70: Overbought
- RSI < 30: Oversold

**Example**:
```python
from cryptvault.indicators.momentum import calculate_rsi

rsi = calculate_rsi(closes, period=14)
print(f"Current RSI: {rsi[-1]:.2f}")

if rsi[-1] > 70:
    print("Overbought condition")
elif rsi[-1] < 30:
    print("Oversold condition")
```

##### calculate_macd()

Calculate Moving Average Convergence Divergence.

```python
calculate_macd(
    prices: List[float],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> Dict[str, List[float]]
```

**Parameters**:
- `prices` (List[float]): Price data
- `fast_period` (int, default=12): Fast EMA period
- `slow_period` (int, default=26): Slow EMA period
- `signal_period` (int, default=9): Signal line period

**Returns**:
- `Dict[str, List[float]]`: Dictionary with 'macd', 'signal', 'histogram'

**Example**:
```python
from cryptvault.indicators.momentum import calculate_macd

macd_data = calculate_macd(closes)
print(f"MACD: {macd_data['macd'][-1]:.2f}")
print(f"Signal: {macd_data['signal'][-1]:.2f}")
print(f"Histogram: {macd_data['histogram'][-1]:.2f}")
```

#### Volatility Indicators

##### calculate_bollinger_bands()

Calculate Bollinger Bands.

```python
calculate_bollinger_bands(
    prices: List[float],
    period: int = 20,
    std_dev: float = 2.0
) -> Dict[str, List[float]]
```

**Parameters**:
- `prices` (List[float]): Price data
- `period` (int, default=20): Moving average period
- `std_dev` (float, default=2.0): Standard deviation multiplier

**Returns**:
- `Dict[str, List[float]]`: Dictionary with 'upper', 'middle', 'lower'

**Example**:
```python
from cryptvault.indicators.volatility import calculate_bollinger_bands

bb = calculate_bollinger_bands(closes, period=20, std_dev=2.0)
print(f"Upper Band: {bb['upper'][-1]:.2f}")
print(f"Middle Band: {bb['middle'][-1]:.2f}")
print(f"Lower Band: {bb['lower'][-1]:.2f}")
```

---

## Machine Learning API

### MLPredictor

Main ML prediction interface with ensemble models.

**Module**: `cryptvault.ml.predictor`

#### Constructor

```python
MLPredictor()
```

#### Methods

##### predict()

Generate comprehensive ML predictions.

```python
predict(
    data: PriceDataFrame,
    patterns: Optional[List] = None,
    horizon: int = 7
) -> Dict[str, Any]
```

**Parameters**:
- `data` (PriceDataFrame): Historical price data (minimum 30 points recommended)
- `patterns` (List, optional): List of detected chart patterns
- `horizon` (int, default=7): Prediction horizon in days

**Returns**:
- `Dict[str, Any]`: Prediction results containing:
  - `trend_forecast`: Predicted trend direction and strength
  - `ensemble_confidence`: Overall confidence score (0-1)
  - `price_predictions`: Optional list of predicted prices
  - `model_performance`: Model performance metrics

**Raises**:
- `ValidationError`: If input data is invalid
- `MLPredictionError`: If prediction generation fails

**Example**:
```python
from cryptvault.ml.predictor import MLPredictor
from cryptvault.data.fetchers import DataFetcher

# Fetch data
fetcher = DataFetcher()
data = fetcher.fetch('BTC', days=60)

# Generate predictions
predictor = MLPredictor()
result = predictor.predict(data, horizon=7)

print(f"Trend: {result['trend_forecast']['trend_7d']}")
print(f"Confidence: {result['ensemble_confidence']:.2%}")
print(f"Expected Change: {result['trend_forecast']['expected_change']}")

if 'price_predictions' in result:
    prices = result['price_predictions']['prices']
    print(f"7-day forecast: {prices}")
```

##### get_model_performance()

Get current model performance metrics.

```python
get_model_performance() -> Dict[str, float]
```

**Returns**:
- `Dict[str, float]`: Performance metrics including:
  - `ensemble_accuracy`: Overall accuracy (0-1)
  - `trained_models`: Number of trained models
  - `total_models`: Total models in ensemble
  - `training_samples`: Number of training samples
  - `is_trained`: Whether model has been trained

**Example**:
```python
performance = predictor.get_model_performance()
print(f"Accuracy: {performance['ensemble_accuracy']:.2%}")
print(f"Trained: {performance['is_trained']}")
```

---

## Configuration API

### ConfigManager

Centralized configuration management with environment support.

**Module**: `cryptvault.config.manager`

#### Constructor

```python
ConfigManager(env: str = 'production', config_path: Optional[str] = None)
```

**Parameters**:
- `env` (str, default='production'): Environment ('development', 'testing', 'production')
- `config_path` (str, optional): Path to custom config file

**Example**:
```python
from cryptvault.config.manager import ConfigManager

# Use default production config
config = ConfigManager()

# Use development config
config = ConfigManager(env='development')

# Use custom config file
config = ConfigManager(config_path='./my_config.yaml')
```

#### Methods

##### get()

Get configuration value.

```python
get(key: str, default: Any = None) -> Any
```

**Parameters**:
- `key` (str): Configuration key (dot notation supported)
- `default` (Any, optional): Default value if key not found

**Returns**:
- `Any`: Configuration value

**Example**:
```python
# Get simple value
min_points = config.get('analysis.min_data_points', 30)

# Get nested value
chart_width = config.get('display.chart_width', 120)
```

##### validate()

Validate all configuration values.

```python
validate() -> bool
```

**Returns**:
- `bool`: True if configuration is valid

**Raises**:
- `ConfigurationError`: If configuration is invalid

---

## CLI API

### Commands

Command-line interface functions.

**Module**: `cryptvault.cli.commands`

#### analyze_command()

Execute analysis command.

```python
analyze_command(
    ticker: str,
    days: int = 60,
    interval: str = '1d',
    sensitivity: Optional[float] = None,
    output_format: str = 'text'
) -> int
```

**Parameters**:
- `ticker` (str): Ticker symbol
- `days` (int, default=60): Number of days
- `interval` (str, default='1d'): Data interval
- `sensitivity` (float, optional): Detection sensitivity
- `output_format` (str, default='text'): Output format ('text', 'json')

**Returns**:
- `int`: Exit code (0 for success)

---

## Data Models

### PricePoint

Single price data point.

**Module**: `cryptvault.data.models`

```python
@dataclass
class PricePoint:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
```

### PriceDataFrame

Collection of price points.

```python
@dataclass
class PriceDataFrame:
    data: List[PricePoint]
    symbol: str
    interval: str
    
    def get_closes(self) -> List[float]
    def get_highs(self) -> List[float]
    def get_lows(self) -> List[float]
    def get_opens(self) -> List[float]
    def get_volumes(self) -> List[float]
    def get_timestamps(self) -> List[datetime]
```

### DetectedPattern

Detected pattern result.

```python
@dataclass
class DetectedPattern:
    pattern_type: str
    category: str
    confidence: float
    start_time: datetime
    end_time: datetime
    start_index: int
    end_index: int
    key_levels: Dict[str, float]
    description: str
    metadata: Dict[str, Any]
```

### AnalysisResult

Complete analysis result.

```python
@dataclass
class AnalysisResult:
    success: bool
    symbol: str
    patterns: List[Dict[str, Any]]
    pattern_summary: Dict[str, Any]
    technical_indicators: Dict[str, Any]
    ml_predictions: Optional[Dict[str, Any]]
    ticker_info: Dict[str, Any]
    chart: Optional[str]
    recommendations: List[str]
    analysis_time: float
    analysis_timestamp: datetime
    configuration_used: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    data_summary: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]
```

---

## Exceptions

### Exception Hierarchy

```
CryptVaultError (base)
├── DataFetchError
│   ├── APIError
│   ├── NetworkError
│   └── RateLimitError
├── ValidationError
│   ├── InvalidTickerError
│   └── InsufficientDataError
├── AnalysisError
│   ├── PatternDetectionError
│   ├── MLPredictionError
│   └── IndicatorCalculationError
└── ConfigurationError
```

### CryptVaultError

Base exception for all CryptVault errors.

**Module**: `cryptvault.exceptions`

```python
class CryptVaultError(Exception):
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    )
```

**Attributes**:
- `message` (str): Error message
- `details` (Dict, optional): Additional error context
- `original_error` (Exception, optional): Original exception if wrapped

**Example**:
```python
from cryptvault.exceptions import DataFetchError

try:
    data = fetcher.fetch('INVALID')
except DataFetchError as e:
    print(f"Error: {e.message}")
    print(f"Details: {e.details}")
```

---

## Complete Usage Example

```python
from cryptvault.core.analyzer import PatternAnalyzer
from cryptvault.config.manager import ConfigManager
from cryptvault.exceptions import CryptVaultError

# Initialize with custom configuration
config = ConfigManager(env='production')
analyzer = PatternAnalyzer(config_manager=config)

try:
    # Analyze ticker
    result = analyzer.analyze_ticker(
        ticker='BTC',
        days=60,
        interval='1d',
        sensitivity=0.6
    )
    
    if result.success:
        # Display patterns
        print(f"\nFound {len(result.patterns)} patterns:")
        for pattern in result.patterns:
            print(f"  - {pattern['pattern_type']}: {pattern['confidence']:.2%}")
        
        # Display technical indicators
        indicators = result.technical_indicators
        print(f"\nTechnical Indicators:")
        print(f"  RSI: {indicators.get('rsi', 'N/A')}")
        print(f"  MACD: {indicators.get('macd', 'N/A')}")
        
        # Display ML predictions
        if result.ml_predictions:
            ml = result.ml_predictions
            print(f"\nML Predictions:")
            print(f"  Trend: {ml['trend_forecast']['trend_7d']}")
            print(f"  Confidence: {ml['ensemble_confidence']:.2%}")
        
        # Display recommendations
        if result.recommendations:
            print(f"\nRecommendations:")
            for rec in result.recommendations:
                print(f"  - {rec}")
    
    else:
        print("Analysis failed:")
        for error in result.errors:
            print(f"  - {error}")

except CryptVaultError as e:
    print(f"Error: {e.message}")
    if e.details:
        print(f"Details: {e.details}")
```

---

## API Versioning

Current API Version: **4.0.0**

### Breaking Changes from 3.x

- `PatternAnalyzer` constructor now accepts `ConfigManager` instead of individual parameters
- `AnalysisResult` structure has been expanded with additional fields
- Pattern detection methods now return `DetectedPattern` objects instead of dictionaries
- Configuration management moved to `ConfigManager` class

### Deprecation Notices

None currently. All APIs are stable.

---

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/yourusername/cryptvault/issues
- Documentation: https://cryptvault.readthedocs.io
- Email: support@cryptvault.io
