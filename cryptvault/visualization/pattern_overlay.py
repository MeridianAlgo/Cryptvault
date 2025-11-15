"""
Pattern Overlay Visualization for Matplotlib Charts
Draws detected patterns directly on candlestick charts with proper alignment
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime


class PatternOverlay:
    """Overlay detected patterns on matplotlib charts."""

    def __init__(self, ax):
        """
        Initialize pattern overlay.

        Args:
            ax: Matplotlib axis to draw on
        """
        self.ax = ax
        self.pattern_colors = {
            'bullish': '#00ff88',
            'bearish': '#ff4444',
            'neutral': '#ffaa00',
            'divergence': '#8844ff'
        }

    def draw_pattern(self, pattern: Dict[str, Any], dates: list,
                    opens: list, highs: list, lows: list, closes: list):
        """
        Draw a single pattern on the chart.

        Args:
            pattern: Pattern dictionary with type, confidence, and key_levels
            dates: List of datetime objects
            opens, highs, lows, closes: Price data lists
        """
        pattern_type = pattern.get('type', '').lower()
        confidence = float(pattern.get('confidence', '0').rstrip('%')) / 100
        key_levels = pattern.get('key_levels', {})
        is_bullish = pattern.get('is_bullish', False)
        is_bearish = pattern.get('is_bearish', False)

        # Determine color
        if is_bullish:
            color = self.pattern_colors['bullish']
        elif is_bearish:
            color = self.pattern_colors['bearish']
        else:
            color = self.pattern_colors['neutral']

        # Adjust alpha based on confidence
        alpha = 0.4 + (confidence * 0.4)  # Range: 0.4 to 0.8

        # Draw pattern based on type
        if 'triangle' in pattern_type:
            self._draw_triangle_pattern(pattern, dates, highs, lows, color, alpha)
        elif 'rectangle' in pattern_type or 'channel' in pattern_type:
            self._draw_rectangle_pattern(pattern, dates, highs, lows, color, alpha)
        elif 'wedge' in pattern_type:
            self._draw_wedge_pattern(pattern, dates, highs, lows, color, alpha)
        elif 'flag' in pattern_type:
            self._draw_flag_pattern(pattern, dates, highs, lows, closes, color, alpha)
        elif 'head' in pattern_type and 'shoulder' in pattern_type:
            self._draw_head_shoulders(pattern, dates, highs, lows, color, alpha)
        elif 'double' in pattern_type or 'triple' in pattern_type:
            self._draw_double_triple_pattern(pattern, dates, highs, lows, color, alpha)
        elif 'divergence' in pattern_type:
            self._draw_divergence_pattern(pattern, dates, closes, color, alpha)
        elif 'diamond' in pattern_type:
            self._draw_diamond_pattern(pattern, dates, highs, lows, color, alpha)
        else:
            # Generic pattern - draw support/resistance levels
            self._draw_generic_pattern(pattern, dates, key_levels, color, alpha)

    def _draw_triangle_pattern(self, pattern: Dict, dates: list, highs: list,
                               lows: list, color: str, alpha: float):
        """Draw triangle patterns (ascending, descending, symmetrical, expanding)."""
        pattern_type = pattern.get('type', '').lower()
        key_levels = pattern.get('key_levels', {})

        # Get pattern boundaries
        start_idx = self._find_closest_index(dates, pattern.get('start_time'))
        end_idx = self._find_closest_index(dates, pattern.get('end_time'))

        if start_idx is None or end_idx is None or start_idx >= end_idx:
            return

        # Extract data for pattern range
        pattern_dates = dates[start_idx:end_idx+1]
        pattern_highs = highs[start_idx:end_idx+1]
        pattern_lows = lows[start_idx:end_idx+1]

        if len(pattern_dates) < 2:
            return

        # Draw upper and lower trendlines
        if 'ascending' in pattern_type:
            # Flat resistance, rising support
            resistance = max(pattern_highs)
            self.ax.plot([pattern_dates[0], pattern_dates[-1]],
                        [resistance, resistance],
                        color=color, linestyle='--', linewidth=2, alpha=alpha, label='Resistance')
            self.ax.plot([pattern_dates[0], pattern_dates[-1]],
                        [pattern_lows[0], pattern_lows[-1]],
                        color=color, linestyle='-', linewidth=2, alpha=alpha, label='Support')

        elif 'descending' in pattern_type:
            # Declining resistance, flat support
            support = min(pattern_lows)
            self.ax.plot([pattern_dates[0], pattern_dates[-1]],
                        [pattern_highs[0], pattern_highs[-1]],
                        color=color, linestyle='-', linewidth=2, alpha=alpha, label='Resistance')
            self.ax.plot([pattern_dates[0], pattern_dates[-1]],
                        [support, support],
                        color=color, linestyle='--', linewidth=2, alpha=alpha, label='Support')

        elif 'expanding' in pattern_type:
            # Expanding triangle - diverging lines
            self.ax.plot([pattern_dates[0], pattern_dates[-1]],
                        [pattern_highs[0], max(pattern_highs)],
                        color=color, linestyle='-', linewidth=2, alpha=alpha)
            self.ax.plot([pattern_dates[0], pattern_dates[-1]],
                        [pattern_lows[0], min(pattern_lows)],
                        color=color, linestyle='-', linewidth=2, alpha=alpha)

        else:  # Symmetrical
            # Converging lines
            self.ax.plot([pattern_dates[0], pattern_dates[-1]],
                        [pattern_highs[0], pattern_highs[-1]],
                        color=color, linestyle='-', linewidth=2, alpha=alpha)
            self.ax.plot([pattern_dates[0], pattern_dates[-1]],
                        [pattern_lows[0], pattern_lows[-1]],
                        color=color, linestyle='-', linewidth=2, alpha=alpha)

        # Add label
        mid_idx = len(pattern_dates) // 2
        mid_price = (pattern_highs[mid_idx] + pattern_lows[mid_idx]) / 2
        self.ax.annotate(pattern.get('type', ''),
                        xy=(pattern_dates[mid_idx], mid_price),
                        xytext=(0, 20), textcoords='offset points',
                        ha='center', fontsize=9, color=color, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))

    def _draw_rectangle_pattern(self, pattern: Dict, dates: list, highs: list,
                                lows: list, color: str, alpha: float):
        """Draw rectangle/channel patterns."""
        key_levels = pattern.get('key_levels', {})

        # Get pattern boundaries
        start_idx = self._find_closest_index(dates, pattern.get('start_time'))
        end_idx = self._find_closest_index(dates, pattern.get('end_time'))

        if start_idx is None or end_idx is None or start_idx >= end_idx:
            return

        pattern_dates = dates[start_idx:end_idx+1]
        pattern_highs = highs[start_idx:end_idx+1]
        pattern_lows = lows[start_idx:end_idx+1]

        # Get support and resistance levels
        resistance = key_levels.get('resistance', max(pattern_highs))
        support = key_levels.get('support', min(pattern_lows))

        # Draw horizontal lines
        self.ax.plot([pattern_dates[0], pattern_dates[-1]],
                    [resistance, resistance],
                    color=color, linestyle='-', linewidth=2, alpha=alpha, label='Resistance')
        self.ax.plot([pattern_dates[0], pattern_dates[-1]],
                    [support, support],
                    color=color, linestyle='-', linewidth=2, alpha=alpha, label='Support')

        # Fill between for visual emphasis
        self.ax.fill_between([pattern_dates[0], pattern_dates[-1]],
                            [support, support], [resistance, resistance],
                            color=color, alpha=0.1)

        # Add label
        mid_price = (resistance + support) / 2
        self.ax.annotate(pattern.get('type', ''),
                        xy=(pattern_dates[len(pattern_dates)//2], mid_price),
                        xytext=(0, 0), textcoords='offset points',
                        ha='center', fontsize=9, color=color, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))

    def _draw_wedge_pattern(self, pattern: Dict, dates: list, highs: list,
                           lows: list, color: str, alpha: float):
        """Draw wedge patterns (rising/falling)."""
        start_idx = self._find_closest_index(dates, pattern.get('start_time'))
        end_idx = self._find_closest_index(dates, pattern.get('end_time'))

        if start_idx is None or end_idx is None or start_idx >= end_idx:
            return

        pattern_dates = dates[start_idx:end_idx+1]
        pattern_highs = highs[start_idx:end_idx+1]
        pattern_lows = lows[start_idx:end_idx+1]

        # Draw converging trendlines
        self.ax.plot([pattern_dates[0], pattern_dates[-1]],
                    [pattern_highs[0], pattern_highs[-1]],
                    color=color, linestyle='-', linewidth=2, alpha=alpha)
        self.ax.plot([pattern_dates[0], pattern_dates[-1]],
                    [pattern_lows[0], pattern_lows[-1]],
                    color=color, linestyle='-', linewidth=2, alpha=alpha)

        # Add label
        mid_idx = len(pattern_dates) // 2
        mid_price = (pattern_highs[mid_idx] + pattern_lows[mid_idx]) / 2
        self.ax.annotate(pattern.get('type', ''),
                        xy=(pattern_dates[mid_idx], mid_price),
                        xytext=(0, 20), textcoords='offset points',
                        ha='center', fontsize=9, color=color, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))

    def _draw_flag_pattern(self, pattern: Dict, dates: list, highs: list,
                          lows: list, closes: list, color: str, alpha: float):
        """Draw flag/pennant patterns."""
        start_idx = self._find_closest_index(dates, pattern.get('start_time'))
        end_idx = self._find_closest_index(dates, pattern.get('end_time'))

        if start_idx is None or end_idx is None or start_idx >= end_idx:
            return

        pattern_dates = dates[start_idx:end_idx+1]
        pattern_highs = highs[start_idx:end_idx+1]
        pattern_lows = lows[start_idx:end_idx+1]

        # Draw flag pole (first third of pattern)
        pole_end = len(pattern_dates) // 3
        if pole_end > 0:
            self.ax.plot([pattern_dates[0], pattern_dates[pole_end]],
                        [closes[start_idx], closes[start_idx + pole_end]],
                        color=color, linestyle='-', linewidth=3, alpha=alpha+0.2)

        # Draw flag (consolidation area)
        if pole_end < len(pattern_dates) - 1:
            flag_dates = pattern_dates[pole_end:]
            flag_highs = pattern_highs[pole_end:]
            flag_lows = pattern_lows[pole_end:]

            self.ax.plot([flag_dates[0], flag_dates[-1]],
                        [flag_highs[0], flag_highs[-1]],
                        color=color, linestyle='--', linewidth=2, alpha=alpha)
            self.ax.plot([flag_dates[0], flag_dates[-1]],
                        [flag_lows[0], flag_lows[-1]],
                        color=color, linestyle='--', linewidth=2, alpha=alpha)

        # Add label
        mid_idx = len(pattern_dates) // 2
        mid_price = (pattern_highs[mid_idx] + pattern_lows[mid_idx]) / 2
        self.ax.annotate(pattern.get('type', ''),
                        xy=(pattern_dates[mid_idx], mid_price),
                        xytext=(0, 20), textcoords='offset points',
                        ha='center', fontsize=9, color=color, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))

    def _draw_head_shoulders(self, pattern: Dict, dates: list, highs: list,
                            lows: list, color: str, alpha: float):
        """Draw head and shoulders pattern."""
        start_idx = self._find_closest_index(dates, pattern.get('start_time'))
        end_idx = self._find_closest_index(dates, pattern.get('end_time'))

        if start_idx is None or end_idx is None or start_idx >= end_idx:
            return

        pattern_dates = dates[start_idx:end_idx+1]
        pattern_highs = highs[start_idx:end_idx+1]
        pattern_lows = lows[start_idx:end_idx+1]

        if len(pattern_highs) < 5:
            return

        # Find peaks (shoulders and head)
        peaks_idx = []
        for i in range(1, len(pattern_highs) - 1):
            if pattern_highs[i] > pattern_highs[i-1] and pattern_highs[i] > pattern_highs[i+1]:
                peaks_idx.append(i)

        if len(peaks_idx) >= 3:
            # Draw lines connecting peaks
            peak_dates = [pattern_dates[i] for i in peaks_idx[:3]]
            peak_prices = [pattern_highs[i] for i in peaks_idx[:3]]

            self.ax.plot(peak_dates, peak_prices,
                        color=color, linestyle='--', linewidth=2, alpha=alpha, marker='o')

            # Draw neckline
            key_levels = pattern.get('key_levels', {})
            neckline = key_levels.get('neckline', min(pattern_lows))
            self.ax.plot([pattern_dates[0], pattern_dates[-1]],
                        [neckline, neckline],
                        color=color, linestyle='-', linewidth=2, alpha=alpha)

        # Add label
        mid_idx = len(pattern_dates) // 2
        mid_price = max(pattern_highs)
        self.ax.annotate(pattern.get('type', ''),
                        xy=(pattern_dates[mid_idx], mid_price),
                        xytext=(0, 20), textcoords='offset points',
                        ha='center', fontsize=9, color=color, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))

    def _draw_double_triple_pattern(self, pattern: Dict, dates: list, highs: list,
                                    lows: list, color: str, alpha: float):
        """Draw double/triple top/bottom patterns."""
        pattern_type = pattern.get('type', '').lower()
        start_idx = self._find_closest_index(dates, pattern.get('start_time'))
        end_idx = self._find_closest_index(dates, pattern.get('end_time'))

        if start_idx is None or end_idx is None or start_idx >= end_idx:
            return

        pattern_dates = dates[start_idx:end_idx+1]
        pattern_highs = highs[start_idx:end_idx+1]
        pattern_lows = lows[start_idx:end_idx+1]

        # Determine if top or bottom
        is_top = 'top' in pattern_type
        data_to_use = pattern_highs if is_top else pattern_lows

        # Find peaks/troughs
        extrema_idx = []
        for i in range(1, len(data_to_use) - 1):
            if is_top:
                if data_to_use[i] > data_to_use[i-1] and data_to_use[i] > data_to_use[i+1]:
                    extrema_idx.append(i)
            else:
                if data_to_use[i] < data_to_use[i-1] and data_to_use[i] < data_to_use[i+1]:
                    extrema_idx.append(i)

        # Draw horizontal line at the level
        if extrema_idx:
            level = np.mean([data_to_use[i] for i in extrema_idx])
            self.ax.plot([pattern_dates[0], pattern_dates[-1]],
                        [level, level],
                        color=color, linestyle='-', linewidth=2, alpha=alpha)

            # Mark the extrema points
            extrema_dates = [pattern_dates[i] for i in extrema_idx]
            extrema_prices = [data_to_use[i] for i in extrema_idx]
            self.ax.scatter(extrema_dates, extrema_prices,
                          color=color, s=100, alpha=alpha, marker='o', zorder=5)

        # Add label
        mid_idx = len(pattern_dates) // 2
        mid_price = (max(pattern_highs) + min(pattern_lows)) / 2
        self.ax.annotate(pattern.get('type', ''),
                        xy=(pattern_dates[mid_idx], mid_price),
                        xytext=(0, 20), textcoords='offset points',
                        ha='center', fontsize=9, color=color, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))

    def _draw_divergence_pattern(self, pattern: Dict, dates: list, closes: list,
                                color: str, alpha: float):
        """Draw divergence patterns."""
        start_idx = self._find_closest_index(dates, pattern.get('start_time'))
        end_idx = self._find_closest_index(dates, pattern.get('end_time'))

        if start_idx is None or end_idx is None or start_idx >= end_idx:
            return

        pattern_dates = dates[start_idx:end_idx+1]
        pattern_closes = closes[start_idx:end_idx+1]

        # Draw trend line on price
        self.ax.plot([pattern_dates[0], pattern_dates[-1]],
                    [pattern_closes[0], pattern_closes[-1]],
                    color=color, linestyle='--', linewidth=2, alpha=alpha,
                    label='Price Trend')

        # Add arrows to indicate divergence
        mid_idx = len(pattern_dates) // 2
        pattern_type = pattern.get('type', '').lower()

        if 'bullish' in pattern_type:
            arrow_props = dict(arrowstyle='->', color=color, lw=2, alpha=alpha)
            self.ax.annotate('', xy=(pattern_dates[-1], pattern_closes[-1]),
                           xytext=(pattern_dates[0], pattern_closes[0]),
                           arrowprops=arrow_props)
        elif 'bearish' in pattern_type:
            arrow_props = dict(arrowstyle='->', color=color, lw=2, alpha=alpha)
            self.ax.annotate('', xy=(pattern_dates[-1], pattern_closes[-1]),
                           xytext=(pattern_dates[0], pattern_closes[0]),
                           arrowprops=arrow_props)

        # Add label
        mid_price = (max(pattern_closes) + min(pattern_closes)) / 2
        self.ax.annotate(pattern.get('type', ''),
                        xy=(pattern_dates[mid_idx], mid_price),
                        xytext=(0, 30), textcoords='offset points',
                        ha='center', fontsize=9, color=color, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))

    def _draw_diamond_pattern(self, pattern: Dict, dates: list, highs: list,
                             lows: list, color: str, alpha: float):
        """Draw diamond pattern."""
        start_idx = self._find_closest_index(dates, pattern.get('start_time'))
        end_idx = self._find_closest_index(dates, pattern.get('end_time'))

        if start_idx is None or end_idx is None or start_idx >= end_idx:
            return

        pattern_dates = dates[start_idx:end_idx+1]
        pattern_highs = highs[start_idx:end_idx+1]
        pattern_lows = lows[start_idx:end_idx+1]

        if len(pattern_dates) < 4:
            return

        # Diamond has expanding then contracting shape
        mid_idx = len(pattern_dates) // 2

        # Draw expanding phase
        self.ax.plot([pattern_dates[0], pattern_dates[mid_idx]],
                    [pattern_highs[0], max(pattern_highs[:mid_idx+1])],
                    color=color, linestyle='-', linewidth=2, alpha=alpha)
        self.ax.plot([pattern_dates[0], pattern_dates[mid_idx]],
                    [pattern_lows[0], min(pattern_lows[:mid_idx+1])],
                    color=color, linestyle='-', linewidth=2, alpha=alpha)

        # Draw contracting phase
        self.ax.plot([pattern_dates[mid_idx], pattern_dates[-1]],
                    [max(pattern_highs[:mid_idx+1]), pattern_highs[-1]],
                    color=color, linestyle='-', linewidth=2, alpha=alpha)
        self.ax.plot([pattern_dates[mid_idx], pattern_dates[-1]],
                    [min(pattern_lows[:mid_idx+1]), pattern_lows[-1]],
                    color=color, linestyle='-', linewidth=2, alpha=alpha)

        # Add label
        mid_price = (max(pattern_highs) + min(pattern_lows)) / 2
        self.ax.annotate(pattern.get('type', ''),
                        xy=(pattern_dates[mid_idx], mid_price),
                        xytext=(0, 0), textcoords='offset points',
                        ha='center', fontsize=9, color=color, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))

    def _draw_generic_pattern(self, pattern: Dict, dates: list, key_levels: Dict,
                             color: str, alpha: float):
        """Draw generic pattern using key levels."""
        start_idx = self._find_closest_index(dates, pattern.get('start_time'))
        end_idx = self._find_closest_index(dates, pattern.get('end_time'))

        if start_idx is None or end_idx is None:
            return

        pattern_dates = dates[start_idx:end_idx+1]

        # Draw support and resistance if available
        if 'support' in key_levels:
            support = key_levels['support']
            self.ax.plot([pattern_dates[0], pattern_dates[-1]],
                        [support, support],
                        color=color, linestyle='--', linewidth=2, alpha=alpha,
                        label='Support')

        if 'resistance' in key_levels:
            resistance = key_levels['resistance']
            self.ax.plot([pattern_dates[0], pattern_dates[-1]],
                        [resistance, resistance],
                        color=color, linestyle='--', linewidth=2, alpha=alpha,
                        label='Resistance')

        # Add label
        if pattern_dates:
            mid_idx = len(pattern_dates) // 2
            mid_price = key_levels.get('resistance', key_levels.get('support', 0))
            if mid_price > 0:
                self.ax.annotate(pattern.get('type', ''),
                                xy=(pattern_dates[mid_idx], mid_price),
                                xytext=(0, 20), textcoords='offset points',
                                ha='center', fontsize=9, color=color, fontweight='bold',
                                bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))

    def _find_closest_index(self, dates: list, target_time) -> int:
        """Find the closest index in dates list to target_time."""
        if target_time is None or not dates:
            return None

        # Convert string to datetime if needed
        if isinstance(target_time, str):
            try:
                target_time = datetime.fromisoformat(target_time.replace('Z', '+00:00'))
            except:
                return None

        # Make both datetimes timezone-naive for comparison
        if hasattr(target_time, 'tzinfo') and target_time.tzinfo is not None:
            target_time = target_time.replace(tzinfo=None)

        # Find closest date
        min_diff = float('inf')
        closest_idx = None

        for i, date in enumerate(dates):
            # Make date timezone-naive if needed
            compare_date = date
            if hasattr(compare_date, 'tzinfo') and compare_date.tzinfo is not None:
                compare_date = compare_date.replace(tzinfo=None)

            # Calculate difference safely
            try:
                diff = abs((compare_date - target_time).total_seconds())
                if diff < min_diff:
                    min_diff = diff
                    closest_idx = i
            except (TypeError, ValueError) as e:
                # Skip this date if there's a timezone mismatch
                continue

        return closest_idx
