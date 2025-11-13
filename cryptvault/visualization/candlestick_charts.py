"""
Modern Professional Candlestick Charts
Beautiful terminal-based charts with advanced pattern visualization and proper dating
"""

import logging
import subprocess
import json
import tempfile
import os
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import math
import re

from ..data.models import PriceDataFrame


class CandlestickChartGenerator:
    """Generate beautiful candlestick charts using Candlestick-CLI npm package."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cli_available = self._check_cli_availability()

        if not self.cli_available:
            self.logger.warning("Candlestick-CLI not available. Using fallback charts.")

    def _check_cli_availability(self) -> bool:
        """Check if the Candlestick-CLI npm package is available."""
        try:
            # Try different ways to run npx on Windows
            commands_to_try = [
                ['npx', '@neabyte/candlestick-cli', '--help'],
                ['npx.cmd', '@neabyte/candlestick-cli', '--help'],
                ['cmd', '/c', 'npx', '@neabyte/candlestick-cli', '--help']
            ]

            for cmd in commands_to_try:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5, encoding='utf-8', errors='ignore')
                    if result.returncode == 0:
                        return True
                except:
                    continue

            return False
        except Exception:
            return False

    def generate_candlestick_chart(self, data: PriceDataFrame, symbol: str,
                                 width: int = 80, height: int = 15, patterns: list = None,
                                 ml_predictions: dict = None) -> str:
        """Generate modern professional candlestick chart with enhanced features."""
        if self.cli_available:
            chart = self._generate_cli_chart(data, symbol, width, height)
            if chart:
                # Add modern pattern overlays and ML predictions
                chart = self._add_pattern_info(chart, patterns, ml_predictions)
                return chart

        # Fallback to modern simple chart
        return self._generate_modern_fallback(data, symbol, patterns, ml_predictions)

    def _generate_cli_chart(self, data: PriceDataFrame, symbol: str, width: int, height: int) -> str:
        """Generate chart using Candlestick-CLI npm package."""
        try:
            # Prepare data for CLI
            chart_data = []
            data_points = data.data[-min(50, len(data.data)):]  # Last 50 candles for good scale

            for point in data_points:
                chart_data.append({
                    'timestamp': point.timestamp.isoformat(),
                    'open': float(point.open),
                    'high': float(point.high),
                    'low': float(point.low),
                    'close': float(point.close),
                    'volume': float(point.volume) if hasattr(point, 'volume') and point.volume else 0
                })

            # Create temporary file for data
            temp_file = f'temp_chart_data_{symbol}.json'
            with open(temp_file, 'w') as f:
                json.dump(chart_data, f)

            try:
                # Run Candlestick-CLI with Windows compatibility
                cmd = [
                    'cmd', '/c', 'npx', '@neabyte/candlestick-cli',
                    '-f', temp_file,
                    '-w', str(width),
                    '-h', str(height),
                    '-t', f'{symbol.upper()} Chart'
                ]

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, encoding='utf-8', errors='ignore')

                if result.returncode == 0:
                    # Clean up the output by removing the ASCII header
                    output = result.stdout.strip()
                    return self._clean_cli_output(output)
                else:
                    self.logger.error(f"CLI error: {result.stderr}")
                    return None

            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except:
                    pass

        except Exception as e:
            self.logger.error(f"Error generating CLI chart: {e}")
            return None

    def _clean_cli_output(self, output: str) -> str:
        """Clean and modernize CLI output with professional formatting."""
        import re

        # Remove ANSI color codes first
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        output = ansi_escape.sub('', output)

        lines = output.split('\n')
        cleaned_lines = []

        # Skip the ASCII art header (usually the first several lines)
        skip_header = True
        for line in lines:
            # Look for the start of actual chart data (price levels)
            if skip_header:
                # Check if line contains price data (numbers followed by ┤ or similar)
                if any(char in line for char in ['┤', '│']) and any(char.isdigit() for char in line):
                    skip_header = False
                    cleaned_lines.append(line)
                # Skip header lines
                continue
            else:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _format_modern_date(self, date: datetime) -> str:
        """Format date in modern, readable format"""
        now = datetime.now()
        diff = now - date

        if diff.days == 0:
            return date.strftime('%H:%M')
        elif diff.days == 1:
            return 'Yesterday'
        elif diff.days < 7:
            return date.strftime('%a')  # Mon, Tue, etc.
        elif diff.days < 30:
            return date.strftime('%m/%d')
        else:
            return date.strftime('%m/%y')

    def _create_modern_header(self, symbol: str, current_price: float,
                            price_change: float, timeframe: str) -> str:
        """Create modern professional header"""

        # Price change formatting
        change_symbol = "▲" if price_change >= 0 else "▼"
        change_color = "🟢" if price_change >= 0 else "🔴"

        # Timeframe display
        tf_display = {
            '1h': '1H', '4h': '4H', '1d': '1D',
            '1w': '1W', '1m': '1M'
        }.get(timeframe, timeframe.upper())

        # Current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')

        header = f"""
╭─────────────────────────────────────────────────────────────────────────────╮
│  {symbol.upper()} • {tf_display} CHART                    {timestamp}  │
│                                                                             │
│  💰 ${current_price:,.2f}  {change_color} {change_symbol} {abs(price_change):+.2f}%                                    │
╰─────────────────────────────────────────────────────────────────────────────╯
"""
        return header

    def _create_modern_footer(self, patterns: List[Dict], ml_predictions: Dict = None) -> str:
        """Create modern professional footer with pattern and ML info"""

        footer_lines = []
        footer_lines.append("╭─────────────────────────────────────────────────────────────────────────────╮")

        # Pattern section
        if patterns:
            footer_lines.append("│  📊 DETECTED PATTERNS                                                      │")
            footer_lines.append("│                                                                             │")

            for i, pattern in enumerate(patterns[:3], 1):  # Top 3 patterns
                pattern_type = pattern.get('type', 'Unknown')
                confidence = pattern.get('confidence', '0%')

                # Pattern emoji mapping
                emoji_map = {
                    'Expanding Triangle': '📐',
                    'Double Bottom': '⬆️',
                    'Double Top': '⬇️',
                    'Bearish Divergence': '📉',
                    'Bullish Divergence': '📈',
                    'Rectangle': '⬜',
                    'Rising Channel': '📈',
                    'Falling Channel': '📉'
                }

                emoji = emoji_map.get(pattern_type, '⭐')
                confidence_bar = self._create_confidence_bar(float(confidence.rstrip('%')))

                line = f"│  {i}. {emoji} {pattern_type:<25} {confidence_bar} {confidence:>6}  │"
                footer_lines.append(line)

        # ML Predictions section
        if ml_predictions:
            footer_lines.append("│                                                                             │")
            footer_lines.append("│  🧠 AI FORECAST                                                            │")
            footer_lines.append("│                                                                             │")

            if 'trend_forecast' in ml_predictions:
                trend = ml_predictions['trend_forecast']
                trend_7d = trend.get('trend_7d', 'Unknown').upper()
                strength = trend.get('trend_strength', 'Unknown')

                trend_emoji = "🚀" if trend_7d == "BULLISH" else "📉" if trend_7d == "BEARISH" else "➡️"
                line = f"│     {trend_emoji} 7-Day Trend: {trend_7d} ({strength})                                    │"
                footer_lines.append(line)

            if 'target_price' in ml_predictions:
                target = ml_predictions['target_price']
                line = f"│     🎯 Target Price: ${target:,.2f}                                           │"
                footer_lines.append(line)

        footer_lines.append("╰─────────────────────────────────────────────────────────────────────────────╯")

        return '\n'.join(footer_lines)

    def _create_confidence_bar(self, confidence: float) -> str:
        """Create visual confidence bar"""
        filled_blocks = int(confidence / 10)  # 0-10 blocks
        empty_blocks = 10 - filled_blocks

        bar = "█" * filled_blocks + "░" * empty_blocks
        return f"[{bar}]"

    def _add_pattern_info(self, chart: str, patterns: list, ml_predictions: dict = None) -> str:
        """Add modern pattern overlays and professional info sections."""
        if not patterns and not ml_predictions:
            return chart

        chart_lines = chart.split('\n')

        # Add pattern overlays directly on the chart
        if patterns:
            chart_lines = self._overlay_patterns_on_chart(chart_lines, patterns)

        # Extract price info for modern header
        symbol = "CRYPTO"  # Default, should be passed in
        current_price = 0.0
        price_change = 0.0

        # Try to extract price from chart (basic parsing)
        for line in chart_lines:
            if '$' in line and any(char.isdigit() for char in line):
                try:
                    # Extract price and change from line
                    import re
                    price_match = re.search(r'\$([0-9,]+\.?\d*)', line)
                    change_match = re.search(r'([+-]?\d+\.?\d*)%', line)

                    if price_match:
                        current_price = float(price_match.group(1).replace(',', ''))
                    if change_match:
                        price_change = float(change_match.group(1))
                    break
                except:
                    pass

        # Create modern header
        modern_header = self._create_modern_header(symbol, current_price, price_change, '1d')

        # Create modern footer
        modern_footer = self._create_modern_footer(patterns, ml_predictions)

        # Combine everything
        result = modern_header + '\n' + '\n'.join(chart_lines) + '\n' + modern_footer

        return result

    def _overlay_patterns_on_chart(self, chart_lines: list, patterns: list) -> list:
        """Overlay ONLY the most important pattern with clear labeling."""
        if not patterns or len(chart_lines) < 5:
            return chart_lines

        # Find chart area (lines with price data and candlesticks)
        chart_start = -1
        chart_end = -1

        for i, line in enumerate(chart_lines):
            if any(char in line for char in ['┤', '│']) and any(char.isdigit() for char in line):
                if chart_start == -1:
                    chart_start = i
                chart_end = i

        if chart_start == -1:
            return chart_lines

        # Convert chart lines to character arrays for easier manipulation
        chart_arrays = [list(line) for line in chart_lines]

        # Only draw the MOST IMPORTANT pattern (highest confidence)
        sorted_patterns = sorted(patterns, key=lambda p: float(p.get('confidence', '0').rstrip('%')), reverse=True)

        if sorted_patterns:
            # Draw only the top pattern with clear labeling
            top_pattern = sorted_patterns[0]
            pattern_type = top_pattern.get('type', '')
            symbol_char = self._get_pattern_symbol(pattern_type)

            # Draw only this one pattern with label
            self._draw_single_pattern_with_label(chart_arrays, pattern_type, symbol_char, chart_start, chart_end)

        # Convert back to strings
        return [''.join(line) for line in chart_arrays]

    def _draw_aligned_line(self, chart_arrays: list, x1: int, y1: int, x2: int, y2: int, char: str):
        """Draw properly aligned lines that connect chart elements."""
        if not chart_arrays or len(chart_arrays) == 0:
            return

        # Ensure coordinates are within bounds
        max_y = len(chart_arrays) - 1
        max_x = max(len(line) for line in chart_arrays) - 1 if chart_arrays else 0

        x1 = max(16, min(x1, max_x))  # Start after price labels
        x2 = max(16, min(x2, max_x))
        y1 = max(0, min(y1, max_y))
        y2 = max(0, min(y2, max_y))

        # Calculate line parameters
        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            return

        # Determine number of steps for smooth line
        steps = max(abs(dx), abs(dy))
        if steps == 0:
            return

        # Draw line with proper spacing
        for i in range(steps + 1):
            t = i / steps if steps > 0 else 0
            x = int(x1 + t * dx)
            y = int(y1 + t * dy)

            # Ensure we're within bounds
            if (0 <= y < len(chart_arrays) and
                0 <= x < len(chart_arrays[y])):

                current_char = chart_arrays[y][x]
                # Only draw in empty spaces or over existing pattern chars
                if current_char in [' ', '│', '┤']:
                    chart_arrays[y][x] = char

    def _draw_strategic_line(self, chart_arrays: list, x1: int, y1: int, x2: int, y2: int, char: str):
        """Draw properly aligned strategic line with better positioning."""
        if not chart_arrays:
            return

        # Ensure coordinates are valid
        max_y = len(chart_arrays) - 1
        max_x = max(len(line) for line in chart_arrays) - 1 if chart_arrays else 0

        # Clamp coordinates to valid ranges
        x1 = max(18, min(x1, max_x - 5))  # Safe margins
        x2 = max(18, min(x2, max_x - 5))
        y1 = max(0, min(y1, max_y))
        y2 = max(0, min(y2, max_y))

        # Calculate optimal number of points based on line length
        line_length = max(abs(x2 - x1), abs(y2 - y1))
        num_points = min(12, max(3, line_length // 2))  # Adaptive point count

        for i in range(num_points + 1):
            if num_points == 0:
                x, y = x1, y1
            else:
                t = i / num_points
                x = int(x1 + t * (x2 - x1))
                y = int(y1 + t * (y2 - y1))

            # Place character with better alignment
            if (0 <= y < len(chart_arrays) and
                0 <= x < len(chart_arrays[y])):

                current_char = chart_arrays[y][x]
                # Draw over empty spaces and some chart elements for visibility
                if current_char in [' ', '│']:
                    chart_arrays[y][x] = char

    def _draw_single_pattern_with_label(self, chart_arrays: list, pattern_type: str, symbol_char: str,
                                       chart_start: int, chart_end: int):
        """Draw ONE pattern with clear labeling."""

        if pattern_type == 'Expanding Triangle':
            self._draw_labeled_expanding_triangle(chart_arrays, symbol_char, chart_start, chart_end)
        elif pattern_type == 'Bearish Divergence':
            self._draw_labeled_bearish_divergence(chart_arrays, symbol_char, chart_start, chart_end)
        elif pattern_type == 'Hidden Bullish Divergence':
            self._draw_labeled_bullish_divergence(chart_arrays, symbol_char, chart_start, chart_end)
        elif pattern_type == 'Rectangle Neutral':
            self._draw_labeled_rectangle(chart_arrays, symbol_char, chart_start, chart_end)
        else:
            # Just place a single marker for unknown patterns
            self._place_single_marker(chart_arrays, symbol_char, chart_start, chart_end)

    def _draw_labeled_expanding_triangle(self, chart_arrays: list, symbol_char: str, chart_start: int, chart_end: int):
        """Draw clean expanding triangle with strategic line placement."""
        if chart_start >= len(chart_arrays) or chart_end >= len(chart_arrays):
            return

        chart_height = chart_end - chart_start
        chart_width = len(chart_arrays[chart_start]) if chart_start < len(chart_arrays) else 80

        # Calculate safe drawing area
        safe_start_x = 25  # Start after price labels
        safe_end_x = min(chart_width - 5, safe_start_x + 30)  # Don't go too far right

        # Draw upper resistance line (ascending) - strategic placement
        upper_start_y = chart_start + chart_height // 2
        upper_end_y = max(chart_start + 1, chart_start + chart_height // 4)

        # Draw lower support line (descending) - strategic placement
        lower_start_y = chart_start + chart_height // 2
        lower_end_y = min(chart_end - 1, chart_start + 3 * chart_height // 4)

        # Draw properly aligned triangle lines
        self._draw_aligned_line(chart_arrays, safe_start_x, upper_start_y, safe_end_x, upper_end_y, '/')
        self._draw_aligned_line(chart_arrays, safe_start_x, lower_start_y, safe_end_x, lower_end_y, '\\')

        # Place emoji in a guaranteed empty spot
        emoji_x = safe_start_x - 2  # Just before the lines start
        emoji_y = chart_start + 1
        if (0 <= emoji_y < len(chart_arrays) and
            0 <= emoji_x < len(chart_arrays[emoji_y])):
            chart_arrays[emoji_y][emoji_x] = symbol_char

    def _draw_labeled_bearish_divergence(self, chart_arrays: list, symbol_char: str, chart_start: int, chart_end: int):
        """Draw bearish divergence with emoji at top and clean lines."""
        if chart_start >= len(chart_arrays) or chart_end >= len(chart_arrays):
            return

        chart_height = chart_end - chart_start
        chart_width = len(chart_arrays[chart_start]) if chart_start < len(chart_arrays) else 80

        # Draw clean horizontal divergence lines
        safe_start_x = 25
        safe_end_x = min(chart_width - 10, safe_start_x + 25)

        # Draw price trend line (higher highs)
        price_y = chart_start + chart_height // 4
        self._draw_aligned_line(chart_arrays, safe_start_x, price_y, safe_end_x, price_y, '─')

        # Draw indicator trend line (lower highs)
        indicator_y = chart_start + 3 * chart_height // 4
        self._draw_aligned_line(chart_arrays, safe_start_x, indicator_y, safe_end_x, indicator_y, '─')

        # Place emoji safely
        emoji_x = safe_start_x - 2
        emoji_y = chart_start + 1
        if (0 <= emoji_y < len(chart_arrays) and
            0 <= emoji_x < len(chart_arrays[emoji_y])):
            chart_arrays[emoji_y][emoji_x] = symbol_char

    def _draw_labeled_bullish_divergence(self, chart_arrays: list, symbol_char: str, chart_start: int, chart_end: int):
        """Draw bullish divergence with emoji at top and lines on chart."""
        if chart_start >= len(chart_arrays) or chart_end >= len(chart_arrays):
            return

        chart_height = chart_end - chart_start
        chart_width = len(chart_arrays[chart_start]) if chart_start < len(chart_arrays) else 80

        # Draw ascending trend line on the chart
        safe_start_x = 25
        safe_end_x = min(chart_width - 10, safe_start_x + 20)

        trend_start_y = chart_start + 2 * chart_height // 3
        trend_end_y = chart_start + chart_height // 3
        self._draw_aligned_line(chart_arrays, safe_start_x, trend_start_y, safe_end_x, trend_end_y, '/')

        # Place emoji safely
        emoji_x = safe_start_x - 2
        emoji_y = chart_start + 1
        if (0 <= emoji_y < len(chart_arrays) and
            0 <= emoji_x < len(chart_arrays[emoji_y])):
            chart_arrays[emoji_y][emoji_x] = symbol_char

    def _draw_labeled_rectangle(self, chart_arrays: list, symbol_char: str, chart_start: int, chart_end: int):
        """Draw rectangle pattern with emoji at top and lines on chart."""
        if chart_start >= len(chart_arrays) or chart_end >= len(chart_arrays):
            return

        chart_height = chart_end - chart_start
        chart_width = len(chart_arrays[chart_start]) if chart_start < len(chart_arrays) else 80

        # Draw rectangle lines on the chart
        safe_start_x = 25
        safe_end_x = min(chart_width - 10, safe_start_x + 20)

        # Top resistance line
        resistance_y = chart_start + chart_height // 3
        self._draw_aligned_line(chart_arrays, safe_start_x, resistance_y, safe_end_x, resistance_y, '─')

        # Bottom support line
        support_y = chart_start + 2 * chart_height // 3
        self._draw_aligned_line(chart_arrays, safe_start_x, support_y, safe_end_x, support_y, '─')

        # Place emoji safely
        emoji_x = safe_start_x - 2
        emoji_y = chart_start + 1
        if (0 <= emoji_y < len(chart_arrays) and
            0 <= emoji_x < len(chart_arrays[emoji_y])):
            chart_arrays[emoji_y][emoji_x] = symbol_char

    def _place_single_marker(self, chart_arrays: list, symbol_char: str, chart_start: int, chart_end: int):
        """Place emoji at top for unknown patterns."""
        chart_height = chart_end - chart_start
        emoji_x = 30  # Center position
        emoji_y = chart_start + 1  # Near the top of the chart area

        if (0 <= emoji_y < len(chart_arrays) and
            0 <= emoji_x < len(chart_arrays[emoji_y]) and
            chart_arrays[emoji_y][emoji_x] == ' '):
            chart_arrays[emoji_y][emoji_x] = symbol_char



    def _get_pattern_symbol(self, pattern_type: str) -> str:
        """Get symbol for pattern type."""
        pattern_symbols = {
            'Bullish Divergence': '🟢',
            'Bearish Divergence': '🔴',
            'Hidden Bullish Divergence': '🟡',
            'Diamond': '💎',
            'Expanding Triangle': '📐',
            'Rising Channel': '📈',
            'Falling Channel': '📉',
            'Rectangle': '⬜',
            'Rising Wedge': '🔺',
            'Falling Wedge': '🔻',
            'Abcd': '🅰️',
            'Rectangle Neutral': '⬜',
            'Rectangle Bullish': '🟩',
            'Rectangle Bearish': '🟥'
        }
        return pattern_symbols.get(pattern_type, '⭐')

    def _generate_modern_fallback(self, data: PriceDataFrame, symbol: str,
                                patterns: list = None, ml_predictions: dict = None) -> str:
        """Generate modern professional fallback chart with enhanced features."""
        if not data or len(data.data) < 2:
            return "Insufficient data for chart"

        data_points = data.data[-30:]  # Last 30 points for better visualization
        prices = [point.close for point in data_points]
        dates = [point.timestamp for point in data_points]

        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price or 1

        # Calculate price change
        price_change = ((prices[-1] - prices[0]) / prices[0]) * 100 if len(prices) > 1 else 0.0

        # Create modern header
        current_price = prices[-1]
        modern_header = self._create_modern_header(symbol, current_price, price_change, '1d')

        chart_lines = []

        # Enhanced price visualization with better scaling
        width = 60
        height = 12

        for i in range(height):
            line = ""
            y_level = max_price - (price_range * i / (height - 1))

            # Add price level label
            price_label = f"{y_level:8.2f} │"

            for j, price in enumerate(prices):
                x_pos = int(j * width / len(prices))
                if len(line) <= x_pos:
                    line += " " * (x_pos - len(line) + 1)

                if abs(price - y_level) < price_range / (height * 2):
                    # Use different symbols for different price movements
                    if j > 0:
                        prev_price = prices[j-1]
                        if price > prev_price:
                            line = line[:x_pos] + "▲" + line[x_pos+1:]
                        elif price < prev_price:
                            line = line[:x_pos] + "▼" + line[x_pos+1:]
                        else:
                            line = line[:x_pos] + "●" + line[x_pos+1:]
                    else:
                        line = line[:x_pos] + "●" + line[x_pos+1:]

            chart_lines.append(price_label + line)

        # Add time axis with modern date formatting
        time_axis = " " * 9 + "└" + "─" * width
        chart_lines.append(time_axis)

        # Add date labels
        if len(dates) >= 2:
            start_date = self._format_modern_date(dates[0])
            end_date = self._format_modern_date(dates[-1])
            date_line = f"          {start_date}" + " " * (width - len(start_date) - len(end_date)) + end_date
            chart_lines.append(date_line)

        # Create modern footer
        modern_footer = self._create_modern_footer(patterns, ml_predictions)

        # Combine everything
        result = modern_header + '\n' + '\n'.join(chart_lines) + '\n' + modern_footer

        return result

    def is_available(self) -> bool:
        """Check if candlestick charts are available."""
        return self.cli_available
