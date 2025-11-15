"""
Output Formatting Module

This module provides output formatting utilities for the CLI, including
color coding, table formatting, and progress indicators.

Functions:
    - format_analysis_results: Format analysis results for display
    - format_pattern_table: Format patterns as a table
    - format_price_info: Format price information
    - format_error: Format error messages
    - create_progress_indicator: Create progress indicator
"""

import sys
import platform
from typing import Dict, List, Any, Optional
from datetime import datetime

# Windows-safe character replacements
def safe_char(char: str) -> str:
    """Replace Unicode characters with ASCII equivalents on Windows."""
    if platform.system() == 'Windows':
        replacements = {
            '•': '*',
            '─': '-',
            '⩗': 'DB', '⩘': 'DT', '⫸': 'TB', '⫷': 'TT',
            '⩙': 'HS', '⩚': 'IHS',
            '△': '^', '▽': 'v', '◇': '<>', '◊': '<>',
            '⚑': '^', '⚐': 'v',
            '↗': '->', '↘': '<-',
            '⤴': '->', '⤵': '<-',
            '▭': '[]', '◈': '<>',
            '⭐': '*',
            '█': '#', '░': '.',
        }
        return replacements.get(char, char)
    return char

def safe_string(text: str) -> str:
    """Replace Unicode characters in string for Windows compatibility."""
    if platform.system() == 'Windows':
        for unicode_char, ascii_char in {
            '•': '*', '─': '-', '⩗': 'DB', '⩘': 'DT', '⫸': 'TB', '⫷': 'TT',
            '⩙': 'HS', '⩚': 'IHS', '△': '^', '▽': 'v', '◇': '<>', '◊': '<>',
            '⚑': '^', '⚐': 'v', '↗': '->', '↘': '<-', '⤴': '->', '⤵': '<-',
            '▭': '[]', '◈': '<>', '⭐': '*', '█': '#', '░': '.',
        }.items():
            text = text.replace(unicode_char, ascii_char)
    return text


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright foreground colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'

    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'


def supports_color() -> bool:
    """
    Check if terminal supports color output.

    Returns:
        True if terminal supports color, False otherwise
    """
    # Check if stdout is a terminal
    if not hasattr(sys.stdout, 'isatty') or not sys.stdout.isatty():
        return False

    # Check for common environment variables
    import os
    if os.environ.get('NO_COLOR'):
        return False

    if os.environ.get('TERM') == 'dumb':
        return False

    return True


def colorize(text: str, color: str) -> str:
    """
    Colorize text if terminal supports it.

    Args:
        text: Text to colorize
        color: Color code from Colors class

    Returns:
        Colorized text or plain text if colors not supported
    """
    if supports_color():
        return f"{color}{text}{Colors.RESET}"
    return text


def format_header(text: str) -> str:
    """
    Format text as a header.

    Args:
        text: Header text

    Returns:
        Formatted header string
    """
    return colorize(f"\n{text}", Colors.BOLD + Colors.CYAN)


def format_success(text: str) -> str:
    """Format success message."""
    return colorize(f"[OK] {text}", Colors.GREEN)


def format_error(text: str) -> str:
    """Format error message."""
    return colorize(f"[ERROR] {text}", Colors.BRIGHT_RED)


def format_warning(text: str) -> str:
    """Format warning message."""
    return colorize(f"[WARNING] {text}", Colors.YELLOW)


def format_info(text: str) -> str:
    """Format info message."""
    return colorize(f"[INFO] {text}", Colors.CYAN)


def format_analysis_results(results: Dict[str, Any], verbose: bool = False) -> str:
    """
    Format analysis results for display.

    Args:
        results: Analysis results dictionary
        verbose: Whether to include verbose output

    Returns:
        Formatted results string
    """
    output = []

    # Header
    symbol = results.get('symbol', 'Unknown')
    output.append(format_header(f"Analysis Results: {symbol}"))

    # Success status
    if not results.get('success'):
        output.append(format_error(f"Analysis failed: {results.get('error', 'Unknown error')}"))

        if 'suggestions' in results:
            output.append("\nSuggestions:")
            for suggestion in results['suggestions']:
                output.append(f"  * {suggestion}")

        return '\n'.join(output)

    # Analysis time
    analysis_time = results.get('analysis_time_seconds', 0)
    patterns_found = results.get('patterns_found', 0)
    output.append(f"Completed in {colorize(f'{analysis_time:.2f}s', Colors.GREEN)} | "
                  f"{colorize(str(patterns_found), Colors.BOLD)} patterns detected")

    # Price information
    if 'ticker_info' in results:
        price_info = format_price_info(results['ticker_info'])
        if price_info:
            output.append(price_info)

    # ML Predictions
    if results.get('ml_predictions'):
        ml_info = format_ml_predictions(results['ml_predictions'])
        if ml_info:
            output.append(ml_info)

    # Patterns
    if patterns_found > 0:
        pattern_table = format_pattern_table(results.get('patterns', []), max_patterns=5)
        output.append(pattern_table)

        if patterns_found > 5:
            remaining = patterns_found - 5
            output.append(colorize(f"  ... and {remaining} more patterns", Colors.DIM))

    return '\n'.join(output)


def format_price_info(ticker_info: Dict[str, Any]) -> str:
    """
    Format price information.

    Args:
        ticker_info: Ticker information dictionary

    Returns:
        Formatted price information string
    """
    output = []

    current_price = ticker_info.get('current_price')
    if current_price:
        output.append(f"\nCurrent Price: {colorize(f'${current_price:,.2f}', Colors.BOLD)}")

    if 'price_change' in ticker_info:
        change = ticker_info['price_change']
        percentage = change.get('percentage', 0)

        # Color based on positive/negative
        if percentage >= 0:
            color = Colors.GREEN
            sign = '+'
        else:
            color = Colors.RED
            sign = ''

        change_text = f"{sign}{percentage:.2%}"
        output.append(f"24h Change: {colorize(change_text, color)}")

    return '\n'.join(output) if output else ''


def format_ml_predictions(ml_predictions: Dict[str, Any]) -> str:
    """
    Format ML prediction information.

    Args:
        ml_predictions: ML predictions dictionary

    Returns:
        Formatted ML predictions string
    """
    output = []

    if 'trend_forecast' in ml_predictions:
        trend = ml_predictions['trend_forecast']
        trend_7d = trend.get('trend_7d', 'Unknown')
        strength = trend.get('trend_strength', 'Unknown')

        # Color based on trend
        if 'bullish' in trend_7d.lower():
            color = Colors.GREEN
        elif 'bearish' in trend_7d.lower():
            color = Colors.RED
        else:
            color = Colors.YELLOW

        output.append(f"\nML Forecast: {colorize(trend_7d, color)} ({strength})")

    return '\n'.join(output) if output else ''


def format_pattern_table(patterns: List[Dict[str, Any]], max_patterns: int = 10) -> str:
    """
    Format patterns as a table.

    Args:
        patterns: List of pattern dictionaries
        max_patterns: Maximum number of patterns to display

    Returns:
        Formatted pattern table string
    """
    if not patterns:
        return ""

    output = [format_header("Detected Patterns:")]
    output.append("-" * 70)

    # Pattern symbols for visualization (Windows-safe)
    if platform.system() == 'Windows':
        pattern_symbols = {
            'Double Bottom': 'DB', 'Double Top': 'DT',
            'Triple Bottom': 'TB', 'Triple Top': 'TT',
            'Head and Shoulders': 'HS', 'Inverse Head and Shoulders': 'IHS',
            'Ascending Triangle': '^', 'Descending Triangle': 'v',
            'Expanding Triangle': '<>', 'Symmetrical Triangle': '<>',
            'Bull Flag': '^', 'Bear Flag': 'v',
            'Bullish Divergence': '->', 'Bearish Divergence': '<-',
            'Hidden Bullish Divergence': '->', 'Hidden Bearish Divergence': '<-',
            'Rectangle': '[]', 'Diamond': '<>',
            'Gartley': 'G', 'Butterfly': 'B', 'ABCD': 'A',
            'Hammer': 'H', 'Shooting Star': 'S', 'Doji': '+'
        }
    else:
        pattern_symbols = {
            'Double Bottom': '⩗', 'Double Top': '⩘',
            'Triple Bottom': '⫸', 'Triple Top': '⫷',
            'Head and Shoulders': '⩙', 'Inverse Head and Shoulders': '⩚',
            'Ascending Triangle': '△', 'Descending Triangle': '▽',
            'Expanding Triangle': '◇', 'Symmetrical Triangle': '◊',
            'Bull Flag': '⚑', 'Bear Flag': '⚐',
            'Bullish Divergence': '↗', 'Bearish Divergence': '↘',
            'Hidden Bullish Divergence': '⤴', 'Hidden Bearish Divergence': '⤵',
            'Rectangle': '▭', 'Diamond': '◈',
            'Gartley': 'G', 'Butterfly': 'B', 'ABCD': 'A',
            'Hammer': 'H', 'Shooting Star': 'S', 'Doji': '+'
        }

    for i, pattern in enumerate(patterns[:max_patterns], 1):
        pattern_type = pattern.get('type', 'Unknown Pattern')
        confidence = pattern.get('confidence', '0%')
        category = pattern.get('category', 'Unknown')

        # Get symbol
        symbol = pattern_symbols.get(pattern_type, '*' if platform.system() == 'Windows' else '⭐')

        # Create confidence bar
        conf_value = float(confidence.rstrip('%'))
        conf_bars = int(conf_value / 10)
        if platform.system() == 'Windows':
            conf_bar = '#' * conf_bars + '.' * (10 - conf_bars)
        else:
            conf_bar = '█' * conf_bars + '░' * (10 - conf_bars)

        # Color based on category
        if 'bullish' in category.lower():
            category_color = Colors.GREEN
        elif 'bearish' in category.lower():
            category_color = Colors.RED
        else:
            category_color = Colors.YELLOW

        # Format pattern line
        pattern_line = (
            f"  {i}. {symbol} {pattern_type:<28} "
            f"[{colorize(category, category_color)}] "
            f"[{conf_bar}] {confidence}"
        )
        output.append(pattern_line)

        # Add key levels if available
        if 'key_levels' in pattern and pattern['key_levels']:
            key_info = []
            levels = pattern['key_levels']

            if 'support_level' in levels:
                key_info.append(f"Support: ${levels['support_level']:.2f}")
            if 'resistance_level' in levels:
                key_info.append(f"Resistance: ${levels['resistance_level']:.2f}")
            if 'target_price' in levels:
                key_info.append(f"Target: ${levels['target_price']:.2f}")

            if key_info:
                output.append(colorize(f"      {' | '.join(key_info)}", Colors.DIM))

    return '\n'.join(output)


def format_portfolio_results(results: Dict[str, Any]) -> str:
    """
    Format portfolio analysis results.

    Args:
        results: Portfolio analysis results

    Returns:
        Formatted portfolio results string
    """
    output = []

    output.append(format_header("Portfolio Analysis"))

    if not results.get('success'):
        output.append(format_error(f"Analysis failed: {results.get('error', 'Unknown error')}"))
        return '\n'.join(output)

    # Total value
    portfolio_metrics = results.get('portfolio_metrics')
    total_usd = portfolio_metrics.total_value if portfolio_metrics else 0
    output.append(f"\nTotal Value: {colorize(f'${total_usd:,.2f}', Colors.BOLD + Colors.GREEN)}")

    # Asset allocation
    output.append("\nAsset Allocation:")
    correlation_matrix = results.get('correlation_matrix')
    asset_analysis = results.get('asset_analysis', {})
    
    # Calculate allocation percentages from asset_analysis
    asset_allocation = {}
    asset_values = {}
    total_value = portfolio_metrics.total_value if portfolio_metrics else 0
    
    for symbol, analysis in asset_analysis.items():
        # For now, assume equal allocation since we don't have actual monetary amounts
        if total_value > 0:
            asset_value = total_value / len(asset_analysis)
            asset_values[symbol] = asset_value
            asset_allocation[symbol] = (asset_value / total_value) * 100

    for symbol, percentage in sorted(asset_allocation.items(), key=lambda x: x[1], reverse=True):
        value = asset_values.get(symbol, 0)
        bar_length = int(percentage / 2)  # Scale to 50 chars max
        bar = '█' * bar_length
        output.append(f"  {symbol:6} {percentage:5.1f}% {bar} ${value:,.2f}")

    # Diversification score
    div_score = results.get('diversification_score', 0)
    if div_score >= 70:
        color = Colors.GREEN
    elif div_score >= 40:
        color = Colors.YELLOW
    else:
        color = Colors.RED

    output.append(f"\nDiversification Score: {colorize(f'{div_score:.1f}/100', color)}")

    # Suggestions
    if results.get('rebalancing_suggestions'):
        output.append("\nRebalancing Suggestions:")
        for suggestion in results['rebalancing_suggestions'][:3]:
            output.append(f"  * {suggestion}")

    return '\n'.join(output)


def format_comparison_results(results: Dict[str, Any]) -> str:
    """
    Format asset comparison results.

    Args:
        results: Comparison results

    Returns:
        Formatted comparison results string
    """
    output = []

    output.append(format_header("Asset Comparison (30 days)"))

    if not results.get('success'):
        output.append(format_error(f"Comparison failed: {results.get('error', 'Unknown error')}"))
        return '\n'.join(output)

    # Table header
    output.append(f"\n{'Symbol':<8} {'Price':<12} {'Return':<10} {'Volatility':<12}")
    output.append("-" * 50)

    # Comparison data
    asset_analysis = results.get('asset_analysis', {})
    for symbol, data in sorted(asset_analysis.items()):
        price = data.get('current_price', 0)
        period_return = data.get('price_change_24h', 0)
        volatility = data.get('volatility', 0)

        # Color return based on value
        if period_return >= 0:
            return_color = Colors.GREEN
            return_sign = '+'
        else:
            return_color = Colors.RED
            return_sign = ''

        return_text = colorize(f"{return_sign}{period_return:.1f}%", return_color)

        output.append(f"{symbol:<8} ${price:>10,.2f} {return_text:<18} {volatility:>6.1f}%")

    # Insights
    insights = results.get('insights', [])
    if insights:
        output.append("\n" + format_header("Key Insights"))
        for insight in insights:
            output.append(f"  • {insight}")

    return '\n'.join(output)


class ProgressIndicator:
    """Simple progress indicator for long-running operations."""

    def __init__(self, message: str = "Processing"):
        """
        Initialize progress indicator.

        Args:
            message: Message to display
        """
        self.message = message
        # Use ASCII-compatible spinners on Windows to avoid encoding issues
        if platform.system() == 'Windows':
            self.spinner_chars = ['|', '/', '-', '\\']
        else:
            self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.current = 0
        self.active = False

    def start(self):
        """Start the progress indicator."""
        self.active = True
        self._update()

    def stop(self, final_message: Optional[str] = None):
        """
        Stop the progress indicator.

        Args:
            final_message: Optional final message to display
        """
        self.active = False
        if final_message:
            sys.stdout.write(f'\r{final_message}\n')
        else:
            sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        sys.stdout.flush()

    def _update(self):
        """Update the spinner display."""
        if not self.active:
            return

        spinner = self.spinner_chars[self.current % len(self.spinner_chars)]
        try:
            output = f'\r{spinner} {self.message}...'
            sys.stdout.write(output)
            sys.stdout.flush()
        except (UnicodeEncodeError, UnicodeError):
            # Fallback to ASCII spinner if encoding fails
            ascii_spinner = ['|', '/', '-', '\\'][self.current % 4]
            output = f'\r{ascii_spinner} {self.message}...'
            sys.stdout.write(output)
            sys.stdout.flush()
        self.current += 1


def create_progress_indicator(message: str = "Processing") -> ProgressIndicator:
    """
    Create a progress indicator.

    Args:
        message: Message to display

    Returns:
        ProgressIndicator instance

    Example:
        >>> progress = create_progress_indicator("Analyzing")
        >>> progress.start()
        >>> # Do work...
        >>> progress.stop("Analysis complete!")
    """
    return ProgressIndicator(message)


def format_table(headers: List[str], rows: List[List[str]],
                 column_widths: Optional[List[int]] = None) -> str:
    """
    Format data as a table.

    Args:
        headers: List of column headers
        rows: List of rows (each row is a list of strings)
        column_widths: Optional list of column widths

    Returns:
        Formatted table string
    """
    if not rows:
        return ""

    # Calculate column widths if not provided
    if column_widths is None:
        column_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                column_widths[i] = max(column_widths[i], len(str(cell)))

    # Format header
    header_line = ' | '.join(
        h.ljust(w) for h, w in zip(headers, column_widths)
    )
    separator = '-+-'.join('-' * w for w in column_widths)

    # Format rows
    row_lines = []
    for row in rows:
        row_line = ' | '.join(
            str(cell).ljust(w) for cell, w in zip(row, column_widths)
        )
        row_lines.append(row_line)

    return '\n'.join([header_line, separator] + row_lines)
