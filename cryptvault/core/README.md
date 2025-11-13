# Core Module

This module contains the core business logic for CryptVault.

## Components

- **analyzer.py**: Main analysis orchestrator that coordinates pattern detection, ML predictions, and data fetching
- **portfolio.py**: Portfolio analysis and management functionality

## Purpose

The core module serves as the central orchestration layer that:
- Coordinates data fetching from multiple sources
- Manages pattern detection workflows
- Integrates ML predictions
- Handles portfolio analysis
- Provides a unified interface for analysis operations

## Usage

```python
from cryptvault.core import analyzer

# Create analyzer instance
pattern_analyzer = analyzer.PatternAnalyzer()

# Analyze a ticker
result = pattern_analyzer.analyze_ticker('BTC', days=60, interval='1d')

# Access results
print(f"Found {len(result.patterns)} patterns")
print(f"ML Prediction: {result.ml_predictions}")
```
