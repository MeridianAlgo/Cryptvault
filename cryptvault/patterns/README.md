# Patterns Module

This module provides comprehensive chart pattern detection for technical analysis.

## Components

- **base.py**: Base pattern detector abstract class and common utilities
- **reversal.py**: Reversal pattern detection (Head & Shoulders, Double Top/Bottom, etc.)
- **continuation.py**: Continuation pattern detection (Flags, Pennants, Triangles)
- **harmonic.py**: Harmonic pattern detection (Gartley, Butterfly, Bat, Crab)
- **candlestick.py**: Candlestick pattern detection (Doji, Hammer, Engulfing, etc.)

## Purpose

The patterns module provides:
- Standardized interface for all pattern detectors
- Confidence scores for detected patterns
- Detailed pattern metadata (key levels, timeframes)
- Efficient detection algorithms

## Usage

```python
from cryptvault.patterns import ContinuationPatternDetector, HarmonicPatternDetector
from cryptvault.data import PriceDataFrame

# Create detector
detector = ContinuationPatternDetector()

# Detect patterns
patterns = detector.detect(price_data, sensitivity=0.5)

# Process results
for pattern in patterns:
    print(f"Found {pattern.pattern_type} with {pattern.confidence:.2%} confidence")
    print(f"Key levels: {pattern.key_levels}")
```
