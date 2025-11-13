"""Main terminal chart rendering class with pattern highlighting and color support."""

import os
import sys
from typing import List, Dict, Tuple, Optional
from ..data.models import PriceDataFrame
from ..patterns.types import DetectedPattern, PatternType, PatternCategory


class ColorManager:
    """Manages terminal color output with fallback support."""

    def __init__(self):
        """Initialize color manager with terminal capability detection."""
        self.colors_supported = self._detect_color_support()
        self.color_codes = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'dim': '\033[2m',

            # Foreground colors
            'black': '\033[30m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',

            # Bright foreground colors
            'bright_black': '\033[90m',
            'bright_red': '\033[91m',
            'bright_green': '\033[92m',
            'bright_yellow': '\033[93m',
            'bright_blue': '\033[94m',
            'bright_magenta': '\033[95m',
            'bright_cyan': '\033[96m',
            'bright_white': '\033[97m',

            # Background colors
            'bg_black': '\033[40m',
            'bg_red': '\033[41m',
            'bg_green': '\033[42m',
            'bg_yellow': '\033[43m',
            'bg_blue': '\033[44m',
            'bg_magenta': '\033[45m',
            'bg_cyan': '\033[46m',
            'bg_white': '\033[47m'
        }

        # ASCII fallback symbols for non-color terminals
        self.ascii_symbols = {
            'candle_up': '^',
            'candle_down': 'v',
            'candle_body': '#',
            'candle_wick': '|',
            'horizontal': '-',
            'vertical': '|',
            'corner_tl': '+',
            'corner_tr': '+',
            'corner_bl': '+',
            'corner_br': '+',
            'cross': '+',
            'pattern_mark': '*',
            'support_line': '=',
            'resistance_line': '=',
            'trend_line': '-',
            'fibonacci_line': '.'
        }

    def _detect_color_support(self) -> bool:
        """Detect if terminal supports color output."""
        # Check environment variables
        if os.getenv('NO_COLOR'):
            return False

        if os.getenv('FORCE_COLOR'):
            return True

        # Check if stdout is a TTY
        if not sys.stdout.isatty():
            return False

        # Check TERM environment variable
        term = os.getenv('TERM', '').lower()
        if any(color_term in term for color_term in ['color', 'ansi', 'xterm', 'screen', 'tmux']):
            return True

        # Check COLORTERM
        if os.getenv('COLORTERM'):
            return True

        # Default to no color for safety
        return False

    def colorize(self, text: str, color: str, bold: bool = False) -> str:
        """Apply color to text if colors are supported."""
        if not self.colors_supported:
            return text

        color_code = self.color_codes.get(color, '')
        bold_code = self.color_codes['bold'] if bold else ''
        reset_code = self.color_codes['reset']

        return f"{bold_code}{color_code}{text}{reset_code}"

    def get_pattern_color_scheme(self, category: PatternCategory) -> Dict[str, str]:
        """Get color scheme for pattern category."""
        color_schemes = {
            PatternCategory.BULLISH_CONTINUATION: {
                'primary': 'green',
                'secondary': 'bright_green',
                'accent': 'bg_green'
            },
            PatternCategory.BULLISH_REVERSAL: {
                'primary': 'bright_green',
                'secondary': 'green',
                'accent': 'bg_bright_green'
            },
            PatternCategory.BEARISH_CONTINUATION: {
                'primary': 'red',
                'secondary': 'bright_red',
                'accent': 'bg_red'
            },
            PatternCategory.BEARISH_REVERSAL: {
                'primary': 'bright_red',
                'secondary': 'red',
                'accent': 'bg_bright_red'
            },
            PatternCategory.BILATERAL_NEUTRAL: {
                'primary': 'yellow',
                'secondary': 'bright_yellow',
                'accent': 'bg_yellow'
            },
            PatternCategory.HARMONIC_PATTERN: {
                'primary': 'magenta',
                'secondary': 'bright_magenta',
                'accent': 'bg_magenta'
            },
            PatternCategory.CANDLESTICK_PATTERN: {
                'primary': 'cyan',
                'secondary': 'bright_cyan',
                'accent': 'bg_cyan'
            },
            PatternCategory.DIVERGENCE_PATTERN: {
                'primary': 'blue',
                'secondary': 'bright_blue',
                'accent': 'bg_blue'
            }
        }

        return color_schemes.get(category, {
            'primary': 'white',
            'secondary': 'bright_white',
            'accent': 'bg_white'
        })

    def get_symbols(self, use_unicode: bool = True) -> Dict[str, str]:
        """Get symbol set based on terminal capabilities."""
        if not use_unicode or not self.colors_supported:
            return self.ascii_symbols

        return {
            'candle_up': '▲',
            'candle_down': '▼',
            'candle_body': '█',
            'candle_wick': '│',
            'horizontal': '─',
            'vertical': '│',
            'corner_tl': '┌',
            'corner_tr': '┐',
            'corner_bl': '└',
            'corner_br': '┘',
            'cross': '┼',
            'pattern_mark': '*',
            'support_line': '═',
            'resistance_line': '═',
            'trend_line': '─',
            'fibonacci_line': '┈'
        }


class PatternHighlighter:
    """Handles pattern highlighting and overlay rendering."""

    def __init__(self):
        """Initialize pattern highlighter."""
        self.pattern_symbols = {
            # Geometric patterns
            PatternType.ASCENDING_TRIANGLE: '△',
            PatternType.DESCENDING_TRIANGLE: '▽',
            PatternType.SYMMETRICAL_TRIANGLE: '◇',
            PatternType.BULL_FLAG: '⚑',
            PatternType.BEAR_FLAG: '⚐',
            PatternType.CUP_AND_HANDLE: '∪',
            PatternType.HEAD_SHOULDERS: '⩙',
            PatternType.INVERSE_HEAD_SHOULDERS: '⩚',
            PatternType.DOUBLE_TOP: '⩘',
            PatternType.DOUBLE_BOTTOM: '⩗',
            PatternType.RISING_WEDGE_REVERSAL: '⟋',
            PatternType.FALLING_WEDGE_REVERSAL: '⟍',
            PatternType.DIAMOND: '◊',
            PatternType.RECTANGLE_BULLISH: '▭',
            PatternType.RECTANGLE_BEARISH: '▬',

            # Harmonic patterns
            PatternType.GARTLEY: 'G',
            PatternType.BUTTERFLY: 'B',
            PatternType.BAT: 'T',
            PatternType.CRAB: 'C',
            PatternType.ABCD: 'A',
            PatternType.CYPHER: 'Y',

            # Candlestick patterns
            PatternType.HAMMER: '🔨',
            PatternType.SHOOTING_STAR: '☄',
            PatternType.DOJI: '✚',
            PatternType.SPINNING_TOP: '⊕',
            PatternType.MARUBOZU: '█',
            PatternType.BULLISH_ENGULFING: '⬆',
            PatternType.BEARISH_ENGULFING: '⬇',
            PatternType.MORNING_STAR: '☆',
            PatternType.EVENING_STAR: '★',

            # Divergence patterns
            PatternType.BULLISH_DIVERGENCE: '↗',
            PatternType.BEARISH_DIVERGENCE: '↘',
            PatternType.HIDDEN_BULLISH_DIVERGENCE: '⤴',
            PatternType.HIDDEN_BEARISH_DIVERGENCE: '⤵'
        }

        self.pattern_colors = {
            PatternCategory.BULLISH_CONTINUATION: 'green',
            PatternCategory.BULLISH_REVERSAL: 'bright_green',
            PatternCategory.BEARISH_CONTINUATION: 'red',
            PatternCategory.BEARISH_REVERSAL: 'bright_red',
            PatternCategory.BILATERAL_NEUTRAL: 'yellow',
            PatternCategory.HARMONIC_PATTERN: 'magenta',
            PatternCategory.CANDLESTICK_PATTERN: 'cyan',
            PatternCategory.DIVERGENCE_PATTERN: 'blue'
        }

    def get_pattern_symbol(self, pattern_type: PatternType) -> str:
        """Get symbol for pattern type."""
        return self.pattern_symbols.get(pattern_type, '*')

    def get_pattern_color(self, category: PatternCategory) -> str:
        """Get color for pattern category."""
        return self.pattern_colors.get(category, 'white')


class TerminalChart:
    """Main chart rendering engine for terminal display with pattern highlighting and color support."""

    def __init__(self, width: int = 80, height: int = 24, enable_colors: bool = None):
        """Initialize terminal chart renderer."""
        self.width = width
        self.height = height
        self.chart_area_height = height - 8  # Reserve more space for pattern info
        self.chart_area_width = width - 12   # Reserve space for price axis
        self.highlighter = PatternHighlighter()
        self.color_manager = ColorManager()

        # Enable colors based on terminal capability if not explicitly set
        if enable_colors is None:
            self.colors_enabled = self.color_manager.colors_supported
        else:
            self.colors_enabled = enable_colors

        # Get appropriate symbol set
        self.symbols = self.color_manager.get_symbols(use_unicode=self.colors_enabled)

        # Pattern overlay data
        self.pattern_overlays = []

    def render_chart(self, data: PriceDataFrame, patterns: List[DetectedPattern]) -> str:
        """Render chart with patterns in terminal format."""
        if len(data) == 0:
            return "No data to display"

        # Calculate price range and scaling
        price_range = self._calculate_price_range(data)
        time_range = self._calculate_time_range(data)

        # Create chart grid
        chart_lines = self._create_chart_grid()

        # Plot price data
        self._plot_price_data(chart_lines, data, price_range)

        # Plot patterns
        if patterns:
            self._plot_patterns(chart_lines, data, patterns, price_range)

        # Add axes and labels
        chart_with_axes = self._add_axes_and_labels(chart_lines, data, price_range, time_range)

        # Add pattern legend
        if patterns:
            chart_with_axes += self._create_pattern_legend(patterns)

        return chart_with_axes

    def _calculate_price_range(self, data: PriceDataFrame) -> Dict:
        """Calculate price range for scaling."""
        highs = [h for h in data.get_highs() if h is not None]
        lows = [l for l in data.get_lows() if l is not None]

        if not highs or not lows:
            return {'min': 0, 'max': 100, 'range': 100}

        price_min = min(lows)
        price_max = max(highs)
        price_range = price_max - price_min

        # Add 5% padding
        padding = price_range * 0.05

        return {
            'min': price_min - padding,
            'max': price_max + padding,
            'range': price_range + (2 * padding)
        }

    def _calculate_time_range(self, data: PriceDataFrame) -> Dict:
        """Calculate time range for x-axis."""
        timestamps = data.get_timestamps()

        return {
            'start': timestamps[0],
            'end': timestamps[-1],
            'count': len(timestamps)
        }

    def _create_chart_grid(self) -> List[List[str]]:
        """Create empty chart grid."""
        grid = []
        for _ in range(self.chart_area_height):
            row = [' '] * self.chart_area_width
            grid.append(row)
        return grid

    def _plot_price_data(self, chart_lines: List[List[str]], data: PriceDataFrame,
                        price_range: Dict):
        """Plot price data as candlesticks on the chart with color support."""
        data_points = len(data)

        for i, point in enumerate(data.data):
            # Calculate x position
            x = int((i / max(1, data_points - 1)) * (self.chart_area_width - 1))

            # Calculate y positions for OHLC
            high_y = self._price_to_y(point.high, price_range)
            low_y = self._price_to_y(point.low, price_range)
            open_y = self._price_to_y(point.open, price_range)
            close_y = self._price_to_y(point.close, price_range)

            # Determine candle color/direction
            is_bullish = point.close >= point.open

            # Get candle color
            candle_color = 'green' if is_bullish else 'red'
            wick_color = 'bright_black' if self.colors_enabled else None

            # Draw wick (high to low)
            wick_char = self.symbols['candle_wick']
            if self.colors_enabled and wick_color:
                wick_char = self.color_manager.colorize(wick_char, wick_color)

            for y in range(min(high_y, low_y), max(high_y, low_y) + 1):
                if 0 <= y < len(chart_lines) and 0 <= x < len(chart_lines[0]):
                    if chart_lines[y][x] == ' ':
                        chart_lines[y][x] = wick_char

            # Draw body (open to close)
            body_top = min(open_y, close_y)
            body_bottom = max(open_y, close_y)

            for y in range(body_top, body_bottom + 1):
                if 0 <= y < len(chart_lines) and 0 <= x < len(chart_lines[0]):
                    if is_bullish:
                        body_char = self.symbols['candle_up'] if y == close_y else self.symbols['candle_body']
                    else:
                        body_char = self.symbols['candle_down'] if y == close_y else self.symbols['candle_body']

                    # Apply color if enabled
                    if self.colors_enabled:
                        body_char = self.color_manager.colorize(body_char, candle_color, bold=(y == close_y))

                    chart_lines[y][x] = body_char

    def _price_to_y(self, price: float, price_range: Dict) -> int:
        """Convert price to y coordinate (inverted for terminal display)."""
        if price_range['range'] == 0:
            return self.chart_area_height // 2

        # Normalize price to 0-1 range
        normalized = (price - price_range['min']) / price_range['range']

        # Convert to y coordinate (inverted)
        y = int((1 - normalized) * (self.chart_area_height - 1))

        return max(0, min(self.chart_area_height - 1, y))

    def _plot_patterns(self, chart_lines: List[List[str]], data: PriceDataFrame,
                      patterns: List[DetectedPattern], price_range: Dict):
        """Plot pattern markers and overlays on the chart."""
        data_points = len(data)

        # Sort patterns by confidence (highest first) for better visibility
        sorted_patterns = sorted(patterns, key=lambda p: p.confidence, reverse=True)

        for pattern in sorted_patterns:
            # Calculate pattern boundaries
            start_x = int((pattern.start_index / max(1, data_points - 1)) * (self.chart_area_width - 1))
            end_x = int((pattern.end_index / max(1, data_points - 1)) * (self.chart_area_width - 1))

            # Get pattern-specific rendering
            self._render_pattern_overlay(chart_lines, pattern, start_x, end_x, price_range, data)

            # Mark pattern boundaries with vertical lines
            self._draw_pattern_boundaries(chart_lines, start_x, end_x, pattern)

            # Add pattern annotation
            self._add_pattern_annotation(chart_lines, pattern, start_x, end_x, price_range)

    def _render_pattern_overlay(self, chart_lines: List[List[str]], pattern: DetectedPattern,
                              start_x: int, end_x: int, price_range: Dict, data: PriceDataFrame):
        """Render pattern-specific overlays."""

        # Draw support/resistance lines for geometric patterns
        if pattern.category in [PatternCategory.BULLISH_CONTINUATION, PatternCategory.BEARISH_CONTINUATION,
                               PatternCategory.BULLISH_REVERSAL, PatternCategory.BEARISH_REVERSAL]:
            self._draw_support_resistance_lines(chart_lines, pattern, start_x, end_x, price_range)

        # Draw Fibonacci levels for harmonic patterns
        elif pattern.category == PatternCategory.HARMONIC_PATTERN:
            self._draw_fibonacci_levels(chart_lines, pattern, start_x, end_x, price_range)

        # Highlight candlestick patterns
        elif pattern.category == PatternCategory.CANDLESTICK_PATTERN:
            self._highlight_candlestick_pattern(chart_lines, pattern, start_x, end_x, price_range)

        # Draw divergence lines
        elif pattern.category == PatternCategory.DIVERGENCE_PATTERN:
            self._draw_divergence_lines(chart_lines, pattern, start_x, end_x, price_range)

    def _draw_pattern_boundaries(self, chart_lines: List[List[str]], start_x: int, end_x: int,
                               pattern: DetectedPattern):
        """Draw vertical boundary lines for patterns."""
        boundary_char = '│'

        # Different boundary styles for different pattern types
        if pattern.category == PatternCategory.HARMONIC_PATTERN:
            boundary_char = '┊'
        elif pattern.category == PatternCategory.CANDLESTICK_PATTERN:
            boundary_char = '┆'

        for x in [start_x, end_x]:
            if 0 <= x < self.chart_area_width:
                for y in range(self.chart_area_height):
                    if 0 <= y < len(chart_lines) and chart_lines[y][x] == ' ':
                        chart_lines[y][x] = boundary_char

    def _add_pattern_annotation(self, chart_lines: List[List[str]], pattern: DetectedPattern,
                              start_x: int, end_x: int, price_range: Dict):
        """Add pattern symbol and confidence annotation with color support."""
        # Calculate center position
        center_x = (start_x + end_x) // 2

        # Get pattern symbol and color
        symbol = self.highlighter.get_pattern_symbol(pattern.pattern_type)

        # Apply color if enabled
        if self.colors_enabled:
            color_scheme = self.color_manager.get_pattern_color_scheme(pattern.category)
            symbol = self.color_manager.colorize(symbol, color_scheme['primary'], bold=True)

        # Find a good y position (try top, then middle, then bottom)
        annotation_positions = [1, self.chart_area_height // 2, self.chart_area_height - 2]

        for y in annotation_positions:
            if (0 <= y < len(chart_lines) and 0 <= center_x < len(chart_lines[0]) and
                chart_lines[y][center_x] == ' '):
                chart_lines[y][center_x] = symbol

                # Add confidence indicator next to symbol
                confidence_char = self._get_confidence_char(pattern.confidence)

                # Apply color to confidence indicator
                if self.colors_enabled:
                    confidence_color = self._get_confidence_color(pattern.confidence)
                    confidence_char = self.color_manager.colorize(confidence_char, confidence_color)

                if center_x + 1 < len(chart_lines[0]) and chart_lines[y][center_x + 1] == ' ':
                    chart_lines[y][center_x + 1] = confidence_char
                break

    def _get_confidence_char(self, confidence: float) -> str:
        """Get character representing confidence level."""
        if not self.colors_enabled:
            # ASCII fallback
            if confidence >= 0.8:
                return '#'  # High confidence
            elif confidence >= 0.6:
                return '+'  # Medium-high confidence
            elif confidence >= 0.4:
                return '-'  # Medium confidence
            else:
                return '.'  # Low confidence
        else:
            # Unicode symbols for color terminals
            if confidence >= 0.8:
                return '●'  # High confidence
            elif confidence >= 0.6:
                return '◐'  # Medium-high confidence
            elif confidence >= 0.4:
                return '◑'  # Medium confidence
            else:
                return '○'  # Low confidence

    def _get_confidence_color(self, confidence: float) -> str:
        """Get color for confidence level."""
        if confidence >= 0.8:
            return 'bright_green'
        elif confidence >= 0.6:
            return 'green'
        elif confidence >= 0.4:
            return 'yellow'
        else:
            return 'red'

    def _draw_support_resistance_lines(self, chart_lines: List[List[str]], pattern: DetectedPattern,
                                     start_x: int, end_x: int, price_range: Dict):
        """Draw support and resistance lines for geometric patterns."""
        key_levels = pattern.key_levels

        # Draw support line if available
        if 'support_level' in key_levels:
            support_y = self._price_to_y(key_levels['support_level'], price_range)
            self._draw_horizontal_line(chart_lines, start_x, end_x, support_y,
                                     self.symbols['support_line'], 'green')

        # Draw resistance line if available
        if 'resistance_level' in key_levels:
            resistance_y = self._price_to_y(key_levels['resistance_level'], price_range)
            self._draw_horizontal_line(chart_lines, start_x, end_x, resistance_y,
                                     self.symbols['resistance_line'], 'red')

        # Draw trend lines for triangles and wedges
        if pattern.pattern_type in [PatternType.ASCENDING_TRIANGLE, PatternType.DESCENDING_TRIANGLE,
                                   PatternType.SYMMETRICAL_TRIANGLE, PatternType.RISING_WEDGE_REVERSAL,
                                   PatternType.FALLING_WEDGE_REVERSAL]:
            self._draw_trend_lines(chart_lines, pattern, start_x, end_x, price_range)

    def _draw_fibonacci_levels(self, chart_lines: List[List[str]], pattern: DetectedPattern,
                             start_x: int, end_x: int, price_range: Dict):
        """Draw Fibonacci retracement levels for harmonic patterns."""
        if not pattern.fibonacci_levels:
            return

        # Draw key Fibonacci levels
        key_fib_levels = ['XA_0.618', 'XA_0.786', 'XA_1.0']

        for level_name in key_fib_levels:
            if level_name in pattern.fibonacci_levels:
                level_price = pattern.fibonacci_levels[level_name]
                level_y = self._price_to_y(level_price, price_range)
                self._draw_horizontal_line(chart_lines, start_x, end_x, level_y,
                                         self.symbols['fibonacci_line'], 'magenta')

    def _highlight_candlestick_pattern(self, chart_lines: List[List[str]], pattern: DetectedPattern,
                                     start_x: int, end_x: int, price_range: Dict):
        """Highlight candlestick patterns with special markers."""
        # For single candlestick patterns, highlight the specific candle
        if pattern.start_index == pattern.end_index:
            x = start_x
            # Add highlighting around the candle
            for y_offset in [-1, 0, 1]:
                for x_offset in [-1, 0, 1]:
                    new_x, new_y = x + x_offset, self.chart_area_height // 2 + y_offset
                    if (0 <= new_x < self.chart_area_width and 0 <= new_y < self.chart_area_height and
                        chart_lines[new_y][new_x] == ' '):
                        chart_lines[new_y][new_x] = '·'

        # For multi-candlestick patterns, draw connecting lines
        else:
            mid_y = self.chart_area_height // 2
            self._draw_horizontal_line(chart_lines, start_x, end_x, mid_y, '┈')

    def _draw_divergence_lines(self, chart_lines: List[List[str]], pattern: DetectedPattern,
                             start_x: int, end_x: int, price_range: Dict):
        """Draw divergence trend lines."""
        # Draw diagonal line to show divergence
        if end_x > start_x:
            y_start = self.chart_area_height - 3
            y_end = 2

            if pattern.pattern_type in [PatternType.BEARISH_DIVERGENCE, PatternType.HIDDEN_BEARISH_DIVERGENCE]:
                y_start, y_end = y_end, y_start

            self._draw_diagonal_line(chart_lines, start_x, y_start, end_x, y_end, '/', 'blue')

    def _draw_trend_lines(self, chart_lines: List[List[str]], pattern: DetectedPattern,
                        start_x: int, end_x: int, price_range: Dict):
        """Draw trend lines for triangle and wedge patterns."""
        key_levels = pattern.key_levels

        # Draw upper trend line
        if 'upper_trend_start' in key_levels and 'upper_trend_end' in key_levels:
            y1 = self._price_to_y(key_levels['upper_trend_start'], price_range)
            y2 = self._price_to_y(key_levels['upper_trend_end'], price_range)
            self._draw_diagonal_line(chart_lines, start_x, y1, end_x, y2, '/', 'red')

        # Draw lower trend line
        if 'lower_trend_start' in key_levels and 'lower_trend_end' in key_levels:
            y1 = self._price_to_y(key_levels['lower_trend_start'], price_range)
            y2 = self._price_to_y(key_levels['lower_trend_end'], price_range)
            self._draw_diagonal_line(chart_lines, start_x, y1, end_x, y2, '\\', 'green')

    def _draw_horizontal_line(self, chart_lines: List[List[str]], start_x: int, end_x: int,
                            y: int, char: str, color: str = None):
        """Draw a horizontal line with optional color."""
        if not (0 <= y < len(chart_lines)):
            return

        # Apply color if specified and colors are enabled
        if self.colors_enabled and color:
            char = self.color_manager.colorize(char, color)

        for x in range(max(0, start_x), min(self.chart_area_width, end_x + 1)):
            if x < len(chart_lines[y]) and chart_lines[y][x] == ' ':
                chart_lines[y][x] = char

    def _draw_diagonal_line(self, chart_lines: List[List[str]], x1: int, y1: int, x2: int, y2: int,
                          char: str, color: str = None):
        """Draw a diagonal line using Bresenham's algorithm with optional color."""

        # Apply color if specified and colors are enabled
        if self.colors_enabled and color:
            char = self.color_manager.colorize(char, color)

        if x1 == x2:  # Vertical line
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if (0 <= y < len(chart_lines) and 0 <= x1 < len(chart_lines[0]) and
                    chart_lines[y][x1] == ' '):
                    chart_lines[y][x1] = self.color_manager.colorize('│', color) if self.colors_enabled and color else '│'
            return

        # Simple diagonal line approximation
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        if dx > dy:
            # More horizontal than vertical
            step_x = 1 if x2 > x1 else -1
            step_y = (y2 - y1) / dx if dx > 0 else 0

            for i in range(dx + 1):
                x = x1 + i * step_x
                y = int(y1 + i * step_y)

                if (0 <= y < len(chart_lines) and 0 <= x < len(chart_lines[0]) and
                    chart_lines[y][x] == ' '):
                    chart_lines[y][x] = char
        else:
            # More vertical than horizontal
            step_y = 1 if y2 > y1 else -1
            step_x = (x2 - x1) / dy if dy > 0 else 0

            for i in range(dy + 1):
                y = y1 + i * step_y
                x = int(x1 + i * step_x)

                if (0 <= y < len(chart_lines) and 0 <= x < len(chart_lines[0]) and
                    chart_lines[y][x] == ' '):
                    chart_lines[y][x] = char

    def _add_axes_and_labels(self, chart_lines: List[List[str]], data: PriceDataFrame,
                           price_range: Dict, time_range: Dict) -> str:
        """Add axes, labels, and convert to string."""
        result_lines = []

        # Add title
        title = f"Chart Analysis - {data.symbol} ({data.timeframe})"
        result_lines.append(title.center(self.width))
        result_lines.append("")

        # Add price axis and chart content
        for i, line in enumerate(chart_lines):
            # Calculate price for this line
            y_ratio = i / max(1, len(chart_lines) - 1)
            price = price_range['max'] - (y_ratio * price_range['range'])

            # Format price label
            price_label = f"{price:8.2f}"

            # Combine price label with chart line
            chart_line = ''.join(line)
            full_line = f"{price_label} │{chart_line}│"
            result_lines.append(full_line)

        # Add bottom border and time axis
        bottom_border = " " * 9 + "└" + "─" * self.chart_area_width + "┘"
        result_lines.append(bottom_border)

        # Add time labels
        time_labels = self._create_time_labels(time_range)
        result_lines.append(" " * 10 + time_labels)

        return "\n".join(result_lines)

    def _create_time_labels(self, time_range: Dict) -> str:
        """Create time axis labels."""
        start_time = time_range['start']
        end_time = time_range['end']

        # Format timestamps
        start_str = start_time.strftime("%m/%d %H:%M")
        end_str = end_time.strftime("%m/%d %H:%M")

        # Create spaced labels
        label_width = self.chart_area_width
        start_label = start_str
        end_label = end_str

        # Calculate spacing
        total_label_len = len(start_label) + len(end_label)
        if total_label_len < label_width:
            spacing = " " * (label_width - total_label_len)
            return start_label + spacing + end_label
        else:
            # Truncate if too long
            return start_label[:label_width//2] + "..." + end_label[-(label_width//2-3):]

    def _create_pattern_legend(self, patterns: List[DetectedPattern]) -> str:
        """Create enhanced legend for detected patterns with color support."""
        if not patterns:
            return ""

        legend_lines = ["\nDetected Patterns:"]

        # Create separator line
        separator = "─" * 60
        if self.colors_enabled:
            separator = self.color_manager.colorize(separator, 'bright_black')
        legend_lines.append(separator)

        # Sort patterns by confidence
        sorted_patterns = sorted(patterns, key=lambda p: p.confidence, reverse=True)

        for i, pattern in enumerate(sorted_patterns[:8]):  # Show top 8 patterns
            # Get pattern symbol and apply color
            symbol = self.highlighter.get_pattern_symbol(pattern.pattern_type)
            if self.colors_enabled:
                color_scheme = self.color_manager.get_pattern_color_scheme(pattern.category)
                symbol = self.color_manager.colorize(symbol, color_scheme['primary'], bold=True)

            # Get confidence character with color
            confidence_char = self._get_confidence_char(pattern.confidence)
            if self.colors_enabled:
                confidence_color = self._get_confidence_color(pattern.confidence)
                confidence_char = self.color_manager.colorize(confidence_char, confidence_color)

            # Create confidence bar with color
            filled_bars = int(pattern.confidence * 10)
            if self.colors_enabled:
                confidence_bar = (self.color_manager.colorize("█" * filled_bars, 'green') +
                                self.color_manager.colorize("░" * (10 - filled_bars), 'bright_black'))
            else:
                confidence_bar = "#" * filled_bars + "." * (10 - filled_bars)

            # Format pattern name and category with color
            pattern_name = pattern.pattern_type.value.replace('_', ' ').title()
            category_name = pattern.category.value

            if self.colors_enabled:
                color_scheme = self.color_manager.get_pattern_color_scheme(pattern.category)
                category_name = self.color_manager.colorize(f"[{category_name}]", color_scheme['secondary'])
            else:
                category_name = f"[{category_name}]"

            # Create pattern line
            pattern_line = (f"{i+1:2d}. {symbol} {pattern_name:<25} {category_name:<25} "
                          f"[{confidence_bar}] {pattern.confidence:.1%} {confidence_char}")
            legend_lines.append(pattern_line)

            # Add key levels info for important patterns
            if pattern.confidence > 0.6 and i < 3:
                key_info = self._format_key_levels(pattern)
                if key_info:
                    if self.colors_enabled:
                        key_info = self.color_manager.colorize(f"    {key_info}", 'bright_black')
                    else:
                        key_info = f"    {key_info}"
                    legend_lines.append(key_info)

        if len(patterns) > 8:
            more_info = f"... and {len(patterns) - 8} more patterns"
            if self.colors_enabled:
                more_info = self.color_manager.colorize(more_info, 'bright_black')
            legend_lines.append(more_info)

        # Add legend explanation with color
        legend_lines.append("")

        if self.colors_enabled:
            confidence_legend = (
                f"Confidence: {self.color_manager.colorize('●', 'bright_green')} High (80%+)  "
                f"{self.color_manager.colorize('◐', 'green')} Med-High (60%+)  "
                f"{self.color_manager.colorize('◑', 'yellow')} Medium (40%+)  "
                f"{self.color_manager.colorize('○', 'red')} Low (<40%)"
            )
            boundary_legend = (
                f"Boundaries: {self.color_manager.colorize('│', 'white')} Geometric  "
                f"{self.color_manager.colorize('┊', 'magenta')} Harmonic  "
                f"{self.color_manager.colorize('┆', 'cyan')} Candlestick"
            )
        else:
            confidence_legend = "Confidence: # High (80%+)  + Med-High (60%+)  - Medium (40%+)  . Low (<40%)"
            boundary_legend = "Boundaries: | Geometric  : Harmonic  . Candlestick"

        legend_lines.append(confidence_legend)
        legend_lines.append(boundary_legend)

        return "\n".join(legend_lines)

    def _format_key_levels(self, pattern: DetectedPattern) -> str:
        """Format key levels information for pattern."""
        key_levels = pattern.key_levels
        info_parts = []

        # Support/Resistance levels
        if 'support_level' in key_levels:
            info_parts.append(f"Support: {key_levels['support_level']:.2f}")
        if 'resistance_level' in key_levels:
            info_parts.append(f"Resistance: {key_levels['resistance_level']:.2f}")

        # Target levels
        if 'target_price' in key_levels:
            info_parts.append(f"Target: {key_levels['target_price']:.2f}")

        # Harmonic pattern levels
        if pattern.category == PatternCategory.HARMONIC_PATTERN:
            if 'PRZ_level' in key_levels:
                info_parts.append(f"PRZ: {key_levels['PRZ_level']:.2f}")

        # Candlestick pattern levels
        if pattern.category == PatternCategory.CANDLESTICK_PATTERN:
            if 'pattern_high' in key_levels and 'pattern_low' in key_levels:
                info_parts.append(f"Range: {key_levels['pattern_low']:.2f}-{key_levels['pattern_high']:.2f}")

        return " | ".join(info_parts[:3])  # Limit to 3 items to avoid clutter

    def set_dimensions(self, width: int, height: int):
        """Set chart dimensions."""
        self.width = width
        self.height = height
        self.chart_area_height = height - 6
        self.chart_area_width = width - 12

    def enable_colors(self, enabled: bool):
        """Enable or disable color output."""
        self.colors_enabled = enabled and self.color_manager.colors_supported
        # Update symbols based on color capability
        self.symbols = self.color_manager.get_symbols(use_unicode=self.colors_enabled)

    def get_terminal_info(self) -> Dict[str, bool]:
        """Get information about terminal capabilities."""
        return {
            'colors_supported': self.color_manager.colors_supported,
            'colors_enabled': self.colors_enabled,
            'unicode_supported': self.colors_enabled  # Assume unicode support correlates with color support
        }
