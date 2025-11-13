# CryptVault Architecture Documentation

## Overview

CryptVault is designed as a modular, production-ready cryptocurrency and stock analysis platform. The architecture follows clean architecture principles with clear separation of concerns, dependency injection, and comprehensive error handling.

The system is built around a layered architecture that separates concerns into distinct modules:
- **CLI Layer**: User interaction and command processing
- **Core Layer**: Business logic orchestration
- **Service Layer**: Specialized analysis services (patterns, indicators, ML)
- **Data Layer**: Data fetching, caching, and validation
- **Infrastructure Layer**: Configuration, logging, and error handling

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Interface Layer                      │
│         (User Interaction & Command Processing)              │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Commands   │  │  Formatters  │  │  Validators  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Core Analysis Layer                        │
│         (Orchestration & Business Logic)                     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Pattern    │  │      ML      │  │  Portfolio   │     │
│  │   Analyzer   │  │  Predictor   │  │   Manager    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Service Layer                              │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Indicators  │  │   Patterns   │  │      ML      │     │
│  │  (RSI, MACD) │  │  (Reversal,  │  │  (Features,  │     │
│  │              │  │ Continuation)│  │   Models)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Data Layer                                 │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │     Data     │  │     Cache    │  │  Validators  │     │
│  │   Fetchers   │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              Infrastructure Layer                            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │    Config    │  │   Logging    │  │  Exceptions  │     │
│  │   Manager    │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Input (CLI)
      │
      ▼
Input Validation
      │
      ▼
Core Analyzer (Orchestrator)
      │
      ├──────────────┬──────────────┬──────────────┐
      ▼              ▼              ▼              ▼
Data Fetcher   Pattern Detector  Indicators   ML Predictor
      │              │              │              │
      ▼              ▼              ▼              ▼
   Cache         Base Pattern    NumPy Calc    Features
      │              │              │              │
      └──────────────┴──────────────┴──────────────┘
                     │
                     ▼
              Result Aggregation
                     │
                     ▼
              Output Formatting
                     │
                     ▼
              User Display 
```


## Component Interactions

### Analysis Workflow

The typical analysis workflow follows these steps:

1. **User Request**: User invokes CLI command with ticker symbol
2. **Input Validation**: CLI validators check ticker format and parameters
3. **Data Fetching**: Data fetcher retrieves historical price data
4. **Data Validation**: Validator ensures data quality and completeness
5. **Pattern Detection**: Multiple pattern detectors analyze price data
6. **Technical Indicators**: Indicators module calculates RSI, MACD, etc.
7. **ML Prediction**: ML predictor generates trend forecasts
8. **Result Aggregation**: Core analyzer combines all results
9. **Output Formatting**: Formatters prepare user-friendly output
10. **Display**: Results displayed to user via CLI

### Error Handling Flow

```
Component Error
      │
      ▼
Exception Raised
      │
      ▼
Caught by Orchestrator
      │
      ├─────────────┬─────────────┐
      ▼             ▼             ▼
  Log Error   Add to Errors   Continue with
                  List        Other Components
      │             │             │
      └─────────────┴─────────────┘
                    │
                    ▼
            Partial Results
                    │
                    ▼
            User Notification
```

## Detailed Component Design

### 1. CLI Layer (`cryptvault/cli/`)

**Purpose**: Provide user interface for interacting with the system.

**Components**:

- **commands.py**: Command implementations
  - `analyze_command()`: Main analysis command
  - `list_tickers_command()`: List supported tickers
  - `portfolio_command()`: Portfolio analysis
  
- **formatters.py**: Output formatting
  - `format_analysis_result()`: Format analysis output
  - `format_pattern_table()`: Format pattern detection results
  - `format_indicators()`: Format technical indicators
  
- **validators.py**: Input validation
  - `validate_ticker()`: Validate ticker symbols
  - `validate_date_range()`: Validate date parameters
  - `validate_interval()`: Validate time intervals

**Design Decisions**:
- Separated validation from command logic for reusability
- Formatters support both colored and plain text output
- Commands are thin wrappers that delegate to core layer

### 2. Core Layer (`cryptvault/core/`)

**Purpose**: Orchestrate analysis workflow and business logic.

**Components**:

- **analyzer.py**: Main orchestrator (`PatternAnalyzer`)
  - Coordinates all analysis components
  - Implements graceful degradation
  - Manages error handling and logging
  - Returns structured `AnalysisResult` objects
  
**Key Methods**:
```python
analyze_ticker(ticker, days, interval, sensitivity) -> AnalysisResult
analyze_from_csv(csv_data, sensitivity) -> AnalysisResult
analyze_from_json(json_data, sensitivity) -> AnalysisResult
analyze_dataframe(data_frame, sensitivity) -> AnalysisResult
```

**Design Decisions**:
- Single responsibility: orchestration only, no business logic
- Graceful degradation: continues even if components fail
- Multiple input formats supported (ticker, CSV, JSON, DataFrame)
- Comprehensive error tracking with partial results

**AnalysisResult Structure**:
```python
@dataclass
class AnalysisResult:
    success: bool
    symbol: str
    patterns: List[Dict]
    pattern_summary: Dict
    technical_indicators: Dict
    ml_predictions: Optional[Dict]
    ticker_info: Dict
    chart: Optional[str]
    recommendations: List[str]
    analysis_time: float
    analysis_timestamp: datetime
    configuration_used: Dict
    errors: List[str]
    warnings: List[str]
    data_summary: Dict
```

### 3. Data Layer (`cryptvault/data/`)

**Purpose**: Handle data fetching, caching, and validation.

**Components**:

- **fetchers.py**: Data source abstraction
  - `BaseDataFetcher`: Abstract base class
  - `YFinanceFetcher`: Yahoo Finance integration
  - `CCXTFetcher`: Cryptocurrency exchange integration
  - `DataFetcher`: Unified interface with fallback
  
- **models.py**: Data structures
  - `PricePoint`: Single price data point
  - `PriceDataFrame`: Collection of price points
  - `TickerInfo`: Ticker metadata
  - `MarketData`: Complete market data
  
- **cache.py**: Caching layer
  - 5-minute TTL for API responses
  - LRU eviction policy
  - Thread-safe operations
  
- **validators.py**: Data validation
  - Validates data completeness
  - Checks for anomalies
  - Ensures data quality

**Design Decisions**:
- Abstraction allows easy addition of new data sources
- Automatic fallback between sources for reliability
- Rate limiting prevents API abuse
- Caching reduces API calls and improves performance

**Data Fetcher Flow**:
```
User Request
      │
      ▼
Check Cache
      │
   Hit? ──Yes──> Return Cached Data
      │
     No
      │
      ▼
Try Primary Source (YFinance)
      │
   Success? ──Yes──> Cache & Return
      │
     No
      │
      ▼
Try Fallback Source (CCXT)
      │
   Success? ──Yes──> Cache & Return
      │
     No
      │
      ▼
Raise DataFetchError
```

### 4. Pattern Detection Layer (`cryptvault/patterns/`)

**Purpose**: Detect various chart patterns in price data.

**Components**:

- **base.py**: Abstract base class
  - `BasePatternDetector`: Common interface
  - `DetectedPattern`: Pattern result structure
  - Utility methods for confidence calculation
  
- **reversal.py**: Reversal patterns
  - Head and Shoulders
  - Double Top/Bottom
  - Triple Top/Bottom
  
- **continuation.py**: Continuation patterns
  - Flags (Bull/Bear)
  - Pennants
  - Triangles (Ascending/Descending/Symmetrical)
  
- **harmonic.py**: Harmonic patterns
  - Gartley
  - Butterfly
  - Bat
  - Crab
  
- **candlestick.py**: Candlestick patterns
  - Doji
  - Hammer
  - Engulfing
  - Morning/Evening Star

**Design Decisions**:
- Base class enforces consistent interface
- Each detector is independent (single responsibility)
- Confidence scores normalized to 0-1 range
- Overlapping patterns filtered by confidence

**Pattern Detection Algorithm**:
```
1. Identify potential pattern regions
2. Calculate pattern-specific metrics
3. Compute confidence factors:
   - Shape similarity
   - Volume confirmation
   - Trend context
   - Historical accuracy
4. Combine factors into confidence score
5. Filter by minimum confidence threshold
6. Remove overlapping patterns
7. Return sorted by confidence
```

### 5. Technical Indicators Layer (`cryptvault/indicators/`)

**Purpose**: Calculate technical indicators efficiently.

**Components**:

- **trend.py**: Trend indicators
  - SMA (Simple Moving Average)
  - EMA (Exponential Moving Average)
  - WMA (Weighted Moving Average)
  
- **momentum.py**: Momentum indicators
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Stochastic Oscillator
  
- **volatility.py**: Volatility indicators
  - Bollinger Bands
  - ATR (Average True Range)
  - Standard Deviation

**Design Decisions**:
- NumPy vectorization for performance
- Comprehensive docstrings with formulas
- Edge case handling (insufficient data)
- Time complexity documented

**Performance Optimization**:
- Vectorized operations (10-100x faster than loops)
- Minimal memory allocation
- Efficient algorithms (O(n) where possible)
- Cached intermediate results

### 6. Machine Learning Layer (`cryptvault/ml/`)

**Purpose**: Generate price predictions using machine learning.

**Components**:

- **predictor.py**: Main prediction interface
  - Orchestrates ML pipeline
  - Handles training and prediction
  - Validates results
  
- **features.py**: Feature extraction
  - `TechnicalFeatureExtractor`: Technical indicators as features
  - `PatternFeatureExtractor`: Pattern-based features
  - `TimeFeatureExtractor`: Time-based features
  
- **models.py**: ML models
  - `LinearPredictor`: Linear regression baseline
  - `LSTMPredictor`: LSTM neural network
  - `EnsembleModel`: Combines multiple models
  
- **cache.py**: Prediction caching
  - Caches predictions with timestamps
  - Tracks accuracy over time
  - Invalidates stale predictions

**Design Decisions**:
- Ensemble approach for robustness
- Feature engineering from domain knowledge
- Graceful degradation if ML fails
- Confidence scores reflect prediction quality

**ML Pipeline**:
```
Price Data + Patterns
      │
      ▼
Feature Extraction
      │
      ├─────────────┬─────────────┐
      ▼             ▼             ▼
  Technical     Pattern        Time
  Features      Features     Features
      │             │             │
      └─────────────┴─────────────┘
                    │
                    ▼
            Feature Vector
                    │
                    ▼
            Ensemble Model
                    │
      ├─────────────┼─────────────┐
      ▼             ▼             ▼
   Linear        LSTM         Other
   Model         Model        Models
      │             │             │
      └─────────────┴─────────────┘
                    │
                    ▼
         Weighted Combination
                    │
                    ▼
            Predictions
```

### 7. Configuration Layer (`cryptvault/config/`)

**Purpose**: Centralized configuration management.

**Components**:

- **manager.py**: Configuration manager
  - Loads from YAML files
  - Environment variable overrides
  - Validation on load
  - Environment-specific configs (dev/test/prod)

**Configuration Structure**:
```yaml
analysis:
  min_data_points: 30
  max_data_points: 1000
  default_interval: "1d"

patterns:
  enabled_geometric: true
  enabled_reversal: true
  enabled_harmonic: true
  enabled_candlestick: true
  enabled_divergence: true

sensitivity:
  level: "medium"  # low, medium, high
  geometric_patterns: 0.5
  reversal_patterns: 0.6
  harmonic_patterns: 0.7

display:
  chart_width: 120
  chart_height: 30
  enable_colors: true

data_sources:
  primary: "yfinance"
  fallback: ["ccxt"]
  yfinance_enabled: true
  ccxt_enabled: true
```

**Design Decisions**:
- YAML for human-readable configuration
- Environment variables for sensitive data
- Validation prevents invalid configurations
- Defaults for all settings

### 8. Exception Hierarchy (`cryptvault/exceptions.py`)

**Purpose**: Structured error handling with context.

**Exception Hierarchy**:
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

**Design Decisions**:
- Hierarchical structure for catch flexibility
- Context information in exception objects
- Original error preserved for debugging
- User-friendly messages separate from technical details

## Design Patterns Used

### 1. Strategy Pattern
- **Where**: Pattern detectors, data fetchers
- **Why**: Allows swapping detection/fetching algorithms
- **Benefit**: Easy to add new patterns or data sources

### 2. Template Method Pattern
- **Where**: `BasePatternDetector`, `BaseDataFetcher`
- **Why**: Defines algorithm skeleton, subclasses fill details
- **Benefit**: Consistent interface, reduced code duplication

### 3. Facade Pattern
- **Where**: `PatternAnalyzer`, `DataFetcher`
- **Why**: Simplifies complex subsystem interactions
- **Benefit**: Easy-to-use API for clients

### 4. Factory Pattern
- **Where**: Configuration loading, model creation
- **Why**: Encapsulates object creation logic
- **Benefit**: Flexible object instantiation

### 5. Observer Pattern
- **Where**: Logging system
- **Why**: Decouples logging from business logic
- **Benefit**: Flexible logging configuration

### 6. Decorator Pattern
- **Where**: Caching, rate limiting
- **Why**: Adds functionality without modifying core code
- **Benefit**: Clean separation of concerns

## Performance Considerations

### Optimization Strategies

1. **Vectorization**
   - NumPy operations for indicator calculations
   - 10-100x faster than Python loops
   - Minimal memory allocation

2. **Caching**
   - API response caching (5-minute TTL)
   - Prediction caching (5-minute TTL)
   - Computation result caching
   - LRU eviction policy

3. **Lazy Loading**
   - Modules loaded only when needed
   - Reduces startup time
   - Lower memory footprint

4. **Connection Pooling**
   - Reuse HTTP connections
   - Reduces connection overhead
   - Faster API calls

5. **Parallel Processing**
   - Independent pattern detectors can run in parallel
   - Future enhancement opportunity

### Performance Benchmarks

| Operation | Data Points | Time | Memory |
|-----------|-------------|------|--------|
| Data Fetch | 1000 | ~2s | ~5MB |
| Pattern Detection | 1000 | ~1s | ~10MB |
| Indicator Calculation | 1000 | ~0.1s | ~2MB |
| ML Prediction | 1000 | ~0.5s | ~20MB |
| **Total Analysis** | **1000** | **~4s** | **~40MB** |

## Security Architecture

### Security Measures

1. **Input Validation**
   - All user input validated before processing
   - Ticker symbols checked against whitelist
   - Date ranges validated
   - SQL injection prevention (no SQL used)

2. **Credential Management**
   - API keys stored in environment variables
   - Never logged or displayed
   - Secure storage recommendations in docs

3. **Rate Limiting**
   - Prevents API abuse
   - Respects provider rate limits
   - Exponential backoff on errors

4. **Error Information**
   - Stack traces never shown to users
   - Sensitive information filtered from logs
   - User-friendly error messages

5. **Dependency Security**
   - Regular security audits
   - Automated vulnerability scanning
   - Pinned dependency versions

### Threat Model

| Threat | Mitigation |
|--------|------------|
| API Key Exposure | Environment variables, no logging |
| Malicious Input | Input validation, sanitization |
| DoS via API Abuse | Rate limiting, caching |
| Dependency Vulnerabilities | Automated scanning, updates |
| Data Injection | Type validation, no eval() |

## Scalability Considerations

### Current Limitations

- Single-threaded analysis
- In-memory caching only
- No distributed processing
- Limited to single machine

### Scalability Enhancements (Future)

1. **Horizontal Scaling**
   - Microservices architecture
   - API gateway for load balancing
   - Distributed caching (Redis)
   - Message queue for async processing

2. **Vertical Scaling**
   - Multi-threading for pattern detection
   - GPU acceleration for ML
   - Larger cache sizes
   - More efficient algorithms

3. **Data Scaling**
   - Database for historical data
   - Streaming data processing
   - Incremental analysis
   - Partitioned data storage

## Testing Strategy

### Test Pyramid

```
        ┌─────────────┐
        │   Manual    │  (Exploratory testing)
        ├─────────────┤
        │     E2E     │  (Full workflow tests)
        ├─────────────┤
        │ Integration │  (Component interaction)
        ├─────────────┤
        │    Unit     │  (Individual functions)
        └─────────────┘
```

### Test Coverage Goals

- **Unit Tests**: 85% coverage
- **Integration Tests**: All major workflows
- **Performance Tests**: Key operations benchmarked
- **Security Tests**: Input validation, error handling

### Testing Approach

1. **Unit Tests**
   - Test individual functions in isolation
   - Mock external dependencies
   - Fast execution (< 1s total)
   - Run on every commit

2. **Integration Tests**
   - Test component interactions
   - Use real data sources (marked as slow)
   - Verify end-to-end workflows
   - Run before releases

3. **Performance Tests**
   - Benchmark critical operations
   - Track performance over time
   - Identify regressions
   - Run weekly

4. **Security Tests**
   - Validate input handling
   - Test error scenarios
   - Check for information leakage
   - Run before releases

## Deployment Architecture

### Deployment Options

1. **Local Installation**
   ```
   pip install cryptvault
   cryptvault analyze BTC
   ```

2. **Docker Container**
   ```
   docker run cryptvault analyze BTC
   ```

3. **Cloud Deployment**
   - AWS Lambda for serverless
   - ECS for containerized
   - EC2 for traditional

### Environment Configuration

```
Development:
- Debug logging enabled
- Detailed error messages
- No caching
- Mock data sources

Testing:
- Info logging
- Real data sources
- Caching enabled
- Performance monitoring

Production:
- Warning/Error logging only
- All optimizations enabled
- Full caching
- Error tracking
```

## Monitoring and Observability

### Logging Strategy

**Log Levels**:
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (non-fatal issues)
- **ERROR**: Error messages (component failures)
- **CRITICAL**: Critical errors (system failures)

**Log Structure**:
```python
{
    "timestamp": "2024-01-15T10:30:00Z",
    "level": "INFO",
    "component": "PatternAnalyzer",
    "message": "Analysis completed",
    "context": {
        "symbol": "BTC",
        "patterns_found": 5,
        "analysis_time": 3.2
    }
}
```

### Metrics to Track

- Analysis success rate
- Average analysis time
- Pattern detection accuracy
- ML prediction accuracy
- API call success rate
- Cache hit rate
- Error frequency by type

### Health Checks

- Data source availability
- API connectivity
- Cache functionality
- Model loading status
- Configuration validity

## Future Enhancements

### Planned Improvements

1. **Real-time Analysis**
   - WebSocket connections for live data
   - Streaming pattern detection
   - Real-time alerts

2. **Advanced ML**
   - Deep learning models
   - Reinforcement learning for trading
   - Transfer learning from similar assets

3. **Web Interface**
   - Interactive charts
   - Portfolio dashboard
   - Alert management

4. **Mobile App**
   - iOS and Android apps
   - Push notifications
   - Simplified interface

5. **Social Features**
   - Share analysis results
   - Community patterns
   - Collaborative analysis

### Technical Debt

- Increase test coverage to 90%
- Add type hints to all functions
- Improve documentation coverage
- Refactor complex functions
- Add more integration tests

## Conclusion

CryptVault's architecture is designed for:
- **Modularity**: Easy to extend and modify
- **Reliability**: Graceful degradation and error handling
- **Performance**: Optimized for speed and efficiency
- **Maintainability**: Clean code and comprehensive documentation
- **Scalability**: Ready for future enhancements

The layered architecture with clear separation of concerns makes it easy to understand, test, and extend the system while maintaining high code quality and reliability.
