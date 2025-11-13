# Visualization Module

This module provides charting and visualization capabilities for CryptVault.

## Components

- **charts.py**: Chart generation and rendering
- **formatters.py**: Data formatting for visualization
- **terminal_chart.py**: Terminal-based chart rendering

## Purpose

The visualization module provides:
- Interactive and static chart generation
- Terminal-based ASCII charts for CLI usage
- Pattern overlay on price charts
- Indicator visualization
- Export capabilities for charts

## Usage

```python
from cryptvault.visualization import TerminalChart

# Create terminal chart
chart = TerminalChart()

# Render price chart with patterns
chart.render(
    price_data=data,
    patterns=detected_patterns,
    indicators={'RSI': rsi_values, 'MACD': macd_values}
)

# Display in terminal
chart.display()
```
