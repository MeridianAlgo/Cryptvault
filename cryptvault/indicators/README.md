# Indicators Module

This module provides comprehensive technical indicators for cryptocurrency and stock analysis.

## Components

- **trend.py**: Moving averages and trend indicators (SMA, EMA, WMA, DEMA, TEMA, HMA)
- **momentum.py**: Oscillators and momentum indicators (RSI, MACD, Stochastic, ROC, CCI, Williams %R)
- **volatility.py**: Volatility and range indicators (Bollinger Bands, ATR, Keltner Channels)
- **volume.py**: Volume-based indicators (OBV, VWAP, MFI)

## Purpose

The indicators module provides:
- Efficient vectorized calculations using NumPy
- Comprehensive documentation with mathematical formulas
- Consistent interfaces across all indicators
- Performance-optimized implementations

## Usage

```python
from cryptvault.indicators import calculate_rsi, calculate_macd, calculate_bollinger_bands

# Calculate RSI
prices = [44.34, 44.09, 43.61, 44.33, 44.83]
rsi = calculate_rsi(prices, period=14)

# Calculate MACD
macd_line, signal_line, histogram = calculate_macd(prices)

# Calculate Bollinger Bands
upper, middle, lower = calculate_bollinger_bands(prices, period=20, std_dev=2)
```
