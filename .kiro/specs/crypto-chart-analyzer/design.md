# Design Document

## Overview

The crypto chart pattern analyzer is a terminal-based application that identifies technical analysis patterns in cryptocurrency price data without requiring external APIs. The system uses mathematical algorithms to detect geometric patterns in price movements, calculates technical indicators for divergence analysis, and presents results through ASCII-based visualizations in the terminal.

The architecture follows a modular design with separate components for data processing, pattern detection, technical analysis, and terminal visualization. This allows for easy extension of new pattern types and visualization methods.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Input    │───▶│  Pattern Engine  │───▶│  Terminal UI    │
│   - CSV Parser  │    │  - Geometric     │    │  - ASCII Charts │
│   - JSON Parser │    │  - Technical     │    │  - Pattern      │
│   - Validator   │    │  - Confidence    │    │    Highlights   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Config Store   │
                       │  - Sensitivity   │
                       │  - Thresholds    │
                       │  - User Prefs    │
                       └──────────────────┘
```

## Components and Interfaces

### 1. Data Input Module

**Purpose:** Handle various input formats and validate price data

**Key Classes:**
- `DataParser`: Abstract base class for different input formats
- `CSVParser`: Handles CSV price data (OHLCV format)
- `JSONParser`: Handles JSON price data
- `DataValidator`: Validates data integrity and completeness

**Interface:**
```python
class DataParser:
    def parse(self, input_data: str) -> PriceDataFrame
    def validate_format(self, data: Any) -> bool
    
class PriceDataFrame:
    timestamp: List[datetime]
    open: List[float]
    high: List[float] 
    low: List[float]
    close: List[float]
    volume: List[float]
```

### 2. Pattern Detection Engine

**Purpose:** Core pattern recognition using mathematical algorithms

**Key Classes:**
- `PatternDetector`: Main orchestrator for pattern detection
- `GeometricPatternAnalyzer`: Detects shape-based patterns (triangles, flags, channels)
- `TechnicalIndicatorAnalyzer`: Calculates RSI, MACD for divergence detection
- `ConfidenceCalculator`: Scores pattern reliability

**Pattern Detection Algorithms:**

*Continuation Patterns:*
- Ascending/Descending Triangles: Horizontal resistance/support with converging trend lines
- Bull/Bear Flags: Strong directional move followed by counter-trend consolidation
- Rising/Falling Wedges: Converging trend lines with directional bias
- Rectangles: Horizontal support and resistance levels with sideways movement
- Cup and Handle: U-shaped recovery followed by smaller consolidation

*Reversal Patterns:*
- Double/Triple Tops/Bottoms: Multiple tests of key levels with failure to break
- Head and Shoulders: Three peaks with middle peak highest, neckline break
- Inverse Head and Shoulders: Three troughs with middle trough lowest
- Rising/Falling Wedge Reversals: Converging lines against prevailing trend

*Bilateral Patterns:*
- Symmetrical Triangles: Converging trend lines with no directional bias
- Diamonds: Expanding then contracting price action forming diamond shape
- Expanding Triangles: Diverging trend lines creating broadening formation

*Harmonic Patterns:*
- Gartley (222): XABCD structure with specific Fibonacci ratios (0.618 AB=CD)
- Butterfly: Extended CD leg beyond 1.27 of AB with 0.786 XA retracement
- Bat: 0.886 XA retracement with specific BC and CD ratios
- Crab: 1.618 XA extension with precise harmonic ratios
- ABCD: Simple harmonic structure with equal legs and time symmetry
- Cypher: 0.786 XA retracement with 1.272 CD extension

*Candlestick Patterns:*
- Single: Hammer, Shooting Star, Doji, Spinning Top, Marubozu
- Double: Engulfing, Harami, Piercing Line, Dark Cloud Cover, Tweezer Tops/Bottoms
- Triple: Morning/Evening Star, Three White Soldiers/Black Crows, Three Inside/Outside

*Divergence Detection:*
- Regular Divergence: Price makes new highs/lows while indicators don't
- Hidden Divergence: Price makes higher lows/lower highs while indicators make opposite
- Multiple timeframe divergence analysis

**Interface:**
```python
class PatternDetector:
    def detect_all_patterns(self, data: PriceDataFrame) -> List[DetectedPattern]
    def detect_pattern_type(self, data: PriceDataFrame, pattern_type: str) -> List[DetectedPattern]

class DetectedPattern:
    pattern_type: str
    confidence: float
    start_index: int
    end_index: int
    key_levels: Dict[str, float]
    description: str
```

### 3. Terminal Visualization Module

**Purpose:** Render charts and patterns in terminal using ASCII characters

**Key Classes:**
- `TerminalChart`: Main chart rendering engine
- `ASCIIRenderer`: Converts price data to ASCII representation
- `PatternHighlighter`: Overlays pattern markers on charts
- `ColorManager`: Handles terminal color support detection

**Chart Rendering Approach:**
- Use Unicode box-drawing characters for chart framework
- Scale price data to fit terminal dimensions
- Implement candlestick representation using ASCII characters
- Overlay pattern boundaries with different symbols/colors

**Interface:**
```python
class TerminalChart:
    def render_chart(self, data: PriceDataFrame, patterns: List[DetectedPattern]) -> str
    def set_dimensions(self, width: int, height: int)
    def enable_colors(self, enabled: bool)
```

### 4. Configuration Management

**Purpose:** Handle user preferences and pattern detection parameters

**Key Classes:**
- `ConfigManager`: Load/save configuration settings
- `SensitivitySettings`: Pattern detection threshold management
- `DisplaySettings`: Terminal output preferences

## Data Models

### PriceData Structure
```python
@dataclass
class PricePoint:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass
class PriceDataFrame:
    data: List[PricePoint]
    symbol: str
    timeframe: str
    
    def get_highs(self) -> List[float]
    def get_lows(self) -> List[float]
    def get_closes(self) -> List[float]
    def slice(self, start: int, end: int) -> 'PriceDataFrame'
```

### Pattern Detection Results
```python
@dataclass
class DetectedPattern:
    pattern_type: PatternType
    confidence: float  # 0.0 to 1.0
    start_time: datetime
    end_time: datetime
    key_levels: Dict[str, float]  # support, resistance, target levels
    volume_profile: VolumeProfile
    description: str
    
@dataclass
class PatternAnalysisResult:
    patterns: List[DetectedPattern]
    analysis_timestamp: datetime
    data_summary: DataSummary
    settings_used: SensitivitySettings
```

## Error Handling

### Input Validation Errors
- **Invalid Data Format**: Clear error messages with format examples
- **Missing Required Fields**: Specify which fields are missing
- **Data Quality Issues**: Warn about gaps, outliers, or insufficient data points

### Pattern Detection Errors
- **Insufficient Data**: Require minimum data points for reliable pattern detection
- **Calculation Errors**: Handle edge cases in mathematical computations
- **Memory Constraints**: Implement data chunking for large datasets

### Terminal Display Errors
- **Terminal Size Constraints**: Adapt chart size to available terminal space
- **Color Support Detection**: Gracefully fallback to monochrome display
- **Character Encoding Issues**: Use safe ASCII fallbacks for unsupported terminals

## Testing Strategy

### Unit Testing
- **Data Parsing**: Test various input formats and edge cases
- **Pattern Algorithms**: Verify mathematical correctness with known pattern examples
- **Visualization**: Test ASCII rendering with different terminal sizes
- **Configuration**: Validate settings persistence and loading

### Integration Testing
- **End-to-End Workflows**: Test complete analysis pipeline from input to output
- **Cross-Platform Compatibility**: Verify terminal rendering across different OS
- **Performance Testing**: Ensure reasonable response times with large datasets

### Pattern Validation Testing
- **Historical Data Validation**: Test against known historical patterns
- **False Positive Minimization**: Tune algorithms to reduce incorrect pattern detection
- **Confidence Score Accuracy**: Validate that confidence scores correlate with pattern reliability

### Test Data Strategy
- Create synthetic price data with known patterns for algorithm validation
- Use historical cryptocurrency data samples for integration testing
- Include edge cases: trending markets, sideways markets, high volatility periods

## Implementation Considerations

### Performance Optimization
- Implement sliding window algorithms for pattern detection
- Use numpy/pandas for efficient numerical computations
- Cache calculated indicators to avoid redundant calculations

### Terminal Compatibility
- Detect terminal capabilities (size, color support, Unicode support)
- Provide fallback ASCII characters for limited terminals
- Implement responsive chart sizing based on terminal dimensions

### Extensibility
- Plugin architecture for adding new pattern types
- Configurable pattern parameters through external files
- Modular indicator system for easy addition of new technical indicators

### User Experience
- Progressive disclosure: show summary first, details on demand
- Interactive mode for exploring detected patterns
- Export capabilities for further analysis in external tools