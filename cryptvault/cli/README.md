# CLI Module

Command-line interface components for CryptVault.

## Overview

The CLI module provides a modular, well-structured command-line interface for CryptVault. It separates concerns into three main components:

- **commands.py**: Command implementations and business logic
- **validators.py**: Input validation and sanitization
- **formatters.py**: Output formatting and display utilities

## Architecture

```
cryptvault/cli/
├── __init__.py       # Module initialization
├── commands.py       # Command implementations
├── validators.py     # Input validation
├── formatters.py     # Output formatting
└── README.md         # This file
```

## Components

### commands.py

Implements all CLI commands with proper error handling and progress indicators:

- `analyze_ticker()`: Analyze a single cryptocurrency or stock
- `analyze_portfolio()`: Analyze a portfolio of holdings
- `compare_assets()`: Compare multiple assets
- `show_demo()`: Display demo information
- `show_api_status()`: Show data source availability
- `show_prediction_accuracy()`: Display ML prediction accuracy
- `start_live_analysis()`: Start live price analysis
- `open_desktop_charts()`: Open desktop chart interface

### validators.py

Provides comprehensive input validation:

- `validate_ticker()`: Validate ticker symbols with suggestions
- `validate_days()`: Validate day ranges (1-3650)
- `validate_interval()`: Validate data intervals (1m, 1h, 1d, etc.)
- `validate_portfolio_holdings()`: Parse and validate portfolio format
- `validate_file_path()`: Validate file paths for security
- `sanitize_input()`: Remove dangerous characters from input

### formatters.py

Handles all output formatting with color support:

- `format_analysis_results()`: Format complete analysis output
- `format_pattern_table()`: Display patterns in table format
- `format_price_info()`: Format price and change information
- `format_ml_predictions()`: Format ML forecast data
- `format_portfolio_results()`: Format portfolio analysis
- `format_comparison_results()`: Format asset comparison
- `ProgressIndicator`: Animated progress indicator for long operations
- Color utilities for terminal output

## Usage Examples

### Basic Analysis

```python
from cryptvault.cli.commands import analyze_ticker

# Analyze Bitcoin
success = analyze_ticker('BTC', days=60, interval='1d')
```

### Input Validation

```python
from cryptvault.cli.validators import validate_ticker, ValidationError

try:
    ticker = validate_ticker('btc', supported_tickers=['BTC', 'ETH'])
    print(f"Valid ticker: {ticker}")  # Output: BTC
except ValidationError as e:
    print(f"Error: {e}")
```

### Output Formatting

```python
from cryptvault.cli.formatters import format_success, format_error

print(format_success("Analysis complete!"))
print(format_error("Failed to fetch data"))
```

### Progress Indicators

```python
from cryptvault.cli.formatters import create_progress_indicator

progress = create_progress_indicator("Analyzing")
progress.start()
# ... do work ...
progress.stop("Analysis complete!")
```

## Features

### Input Validation

- **Ticker Validation**: Checks format and provides suggestions for typos
- **Range Validation**: Ensures days and intervals are within valid ranges
- **Security**: Sanitizes all user input to prevent injection attacks
- **Helpful Errors**: Provides clear, actionable error messages

### Output Formatting

- **Color Support**: Automatic color detection for terminal output
- **Pattern Symbols**: Visual symbols for different pattern types
- **Confidence Bars**: Visual representation of pattern confidence
- **Progress Indicators**: Animated spinners for long operations
- **Table Formatting**: Clean, aligned table output

### Error Handling

- **Graceful Degradation**: Continues operation when possible
- **Detailed Logging**: Logs errors with full context
- **User-Friendly Messages**: Clear error messages without technical jargon
- **Suggestions**: Provides helpful suggestions for common errors

## Command-Line Interface

The main CLI script (`cryptvault_cli.py`) uses these modules to provide:

### Commands

- `python cryptvault_cli.py BTC 60 1d` - Analyze ticker
- `python cryptvault_cli.py --demo` - Show demo
- `python cryptvault_cli.py --status` - Show API status
- `python cryptvault_cli.py --portfolio BTC:0.5 ETH:10` - Analyze portfolio
- `python cryptvault_cli.py --compare BTC ETH ADA` - Compare assets
- `python cryptvault_cli.py --interactive` - Interactive mode

### Options

- `--verbose, -v` - Verbose output
- `--no-chart` - Disable chart generation
- `--save-chart PATH` - Save chart to file
- `--desktop, -d` - Open desktop charts
- `--version` - Show version

## Design Principles

1. **Separation of Concerns**: Commands, validation, and formatting are separate
2. **Reusability**: All functions can be used independently
3. **Testability**: Pure functions with clear inputs/outputs
4. **User Experience**: Clear messages, helpful errors, visual feedback
5. **Security**: Input sanitization and validation throughout
6. **Maintainability**: Well-documented, type-hinted code

## Error Messages

The CLI provides helpful error messages with suggestions:

```
[ERROR] Ticker 'BT' is not supported.
  Did you mean: BTC, BTT, BTCB, BTTC, BTCST?
  Use --demo to see all 150 supported tickers.
```

```
[ERROR] Days must be between 1 and 3650. Got: 5000
```

```
[ERROR] Invalid holding format: 'BTC-0.5'.
Expected format: SYMBOL:AMOUNT (e.g., BTC:0.5)
```

## Color Support

The CLI automatically detects terminal color support:

- **Green**: Success messages, positive changes, bullish patterns
- **Red**: Error messages, negative changes, bearish patterns
- **Yellow**: Warnings, neutral patterns
- **Cyan**: Info messages, headers
- **Bold**: Important values, headers

Colors are disabled automatically when:
- Output is redirected to a file
- `NO_COLOR` environment variable is set
- Terminal doesn't support colors

## Interactive Mode

The CLI includes an interactive mode for running multiple commands:

```
python cryptvault_cli.py --interactive

cryptvault> analyze BTC 60 1d
cryptvault> compare BTC ETH ADA
cryptvault> status
cryptvault> exit
```

## Requirements

The CLI module requires:

- Python 3.8+
- cryptvault.core.analyzer
- cryptvault.portfolio.analyzer (optional, for portfolio commands)
- cryptvault.ml.predictor (optional, for ML accuracy)

## Testing

To test the CLI module:

```bash
# Test help
python cryptvault_cli.py --help

# Test version
python cryptvault_cli.py --version

# Test demo
python cryptvault_cli.py --demo

# Test analysis
python cryptvault_cli.py BTC 30 1d --no-chart

# Test validation
python cryptvault_cli.py INVALID 30 1d
```

## Contributing

When contributing to the CLI module:

1. Follow the existing code structure
2. Add comprehensive docstrings
3. Include type hints
4. Validate all user input
5. Provide helpful error messages
6. Test with various terminal types
7. Update this README
