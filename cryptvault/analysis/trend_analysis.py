"""Trend line analysis and peak/trough detection utilities."""

from typing import List, Tuple, Optional, Dict
import math
from dataclasses import dataclass
from ..data.models import PriceDataFrame


@dataclass
class TrendLine:
    """Represents a trend line with slope and intercept."""
    slope: float
    intercept: float
    start_index: int
    end_index: int
    r_squared: float  # Correlation coefficient squared

    def get_value_at_index(self, index: int) -> float:
        """Get trend line value at given index."""
        return self.slope * index + self.intercept

    def get_angle_degrees(self) -> float:
        """Get trend line angle in degrees."""
        return math.degrees(math.atan(self.slope))


@dataclass
class PeakTrough:
    """Represents a peak or trough point."""
    index: int
    value: float
    type: str  # 'peak' or 'trough'
    strength: float  # Relative strength (0-1)


class TrendAnalysis:
    """Analyze trends, fit trend lines, and identify peaks/troughs."""

    def __init__(self):
        """Initialize trend analysis utilities."""
        pass

    def fit_trend_line(self, values: List[float], start_index: int = 0,
                      end_index: Optional[int] = None) -> TrendLine:
        """
        Fit a trend line using linear regression.

        Args:
            values: List of values to fit trend line to
            start_index: Starting index for trend line fitting
            end_index: Ending index (None for end of data)

        Returns:
            TrendLine object with slope, intercept, and correlation
        """
        if end_index is None:
            end_index = len(values) - 1

        if start_index >= end_index or start_index < 0 or end_index >= len(values):
            raise ValueError("Invalid start/end indices")

        # Extract data for the specified range
        x_values = list(range(start_index, end_index + 1))
        y_values = values[start_index:end_index + 1]

        # Remove None values
        valid_points = [(x, y) for x, y in zip(x_values, y_values) if y is not None]

        if len(valid_points) < 2:
            raise ValueError("Need at least 2 valid data points for trend line")

        x_vals = [point[0] for point in valid_points]
        y_vals = [point[1] for point in valid_points]

        # Calculate linear regression
        n = len(valid_points)
        sum_x = sum(x_vals)
        sum_y = sum(y_vals)
        sum_xy = sum(x * y for x, y in valid_points)
        sum_x2 = sum(x * x for x in x_vals)
        sum_y2 = sum(y * y for y in y_vals)

        # Calculate slope and intercept
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            slope = 0
            intercept = sum_y / n
        else:
            slope = (n * sum_xy - sum_x * sum_y) / denominator
            intercept = (sum_y - slope * sum_x) / n

        # Calculate R-squared
        if n > 1:
            y_mean = sum_y / n
            ss_tot = sum((y - y_mean) ** 2 for y in y_vals)
            ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in valid_points)

            if ss_tot == 0:
                r_squared = 1.0
            else:
                r_squared = 1 - (ss_res / ss_tot)
        else:
            r_squared = 1.0

        return TrendLine(
            slope=slope,
            intercept=intercept,
            start_index=start_index,
            end_index=end_index,
            r_squared=max(0, r_squared)  # Ensure non-negative
        )

    def find_peaks_and_troughs(self, values: List[float], min_distance: int = 5,
                              prominence_threshold: float = 0.01) -> List[PeakTrough]:
        """
        Find peaks and troughs with strength calculation.

        Args:
            values: List of values to analyze
            min_distance: Minimum distance between peaks/troughs
            prominence_threshold: Minimum prominence as fraction of value range

        Returns:
            List of PeakTrough objects sorted by index
        """
        if len(values) < 3:
            return []

        # Calculate value range for prominence threshold
        valid_values = [v for v in values if v is not None]
        if not valid_values:
            return []

        value_range = max(valid_values) - min(valid_values)
        min_prominence = value_range * prominence_threshold

        peaks_troughs = []

        for i in range(1, len(values) - 1):
            if values[i] is None:
                continue

            left_val = values[i-1]
            right_val = values[i+1]

            if left_val is None or right_val is None:
                continue

            current_val = values[i]

            # Check for peak
            if current_val > left_val and current_val > right_val:
                prominence = self._calculate_prominence(values, i, 'peak')
                if prominence >= min_prominence:
                    # Check minimum distance from last peak
                    last_peak = next((pt for pt in reversed(peaks_troughs)
                                    if pt.type == 'peak'), None)
                    if not last_peak or i - last_peak.index >= min_distance:
                        strength = min(1.0, prominence / (value_range * 0.1))  # Normalize strength
                        peaks_troughs.append(PeakTrough(i, current_val, 'peak', strength))

            # Check for trough
            elif current_val < left_val and current_val < right_val:
                prominence = self._calculate_prominence(values, i, 'trough')
                if prominence >= min_prominence:
                    # Check minimum distance from last trough
                    last_trough = next((pt for pt in reversed(peaks_troughs)
                                      if pt.type == 'trough'), None)
                    if not last_trough or i - last_trough.index >= min_distance:
                        strength = min(1.0, prominence / (value_range * 0.1))  # Normalize strength
                        peaks_troughs.append(PeakTrough(i, current_val, 'trough', strength))

        return sorted(peaks_troughs, key=lambda x: x.index)

    def _calculate_prominence(self, values: List[float], index: int, peak_type: str) -> float:
        """Calculate prominence of a peak or trough."""
        if index <= 0 or index >= len(values) - 1:
            return 0.0

        current_val = values[index]
        if current_val is None:
            return 0.0

        # Find the range to check for prominence
        search_range = min(20, len(values) // 4)  # Adaptive search range

        left_bound = max(0, index - search_range)
        right_bound = min(len(values), index + search_range + 1)

        if peak_type == 'peak':
            # For peaks, find the lowest point on each side
            left_min = min(v for v in values[left_bound:index] if v is not None)
            right_min = min(v for v in values[index+1:right_bound] if v is not None)
            prominence = current_val - max(left_min, right_min)
        else:  # trough
            # For troughs, find the highest point on each side
            left_max = max(v for v in values[left_bound:index] if v is not None)
            right_max = max(v for v in values[index+1:right_bound] if v is not None)
            prominence = min(left_max, right_max) - current_val

        return max(0, prominence)

    def find_support_resistance_levels(self, data: PriceDataFrame,
                                     lookback_period: int = 50) -> Dict[str, List[float]]:
        """
        Identify support and resistance levels based on peaks and troughs.

        Args:
            data: Price data frame
            lookback_period: Number of periods to look back for level identification

        Returns:
            Dictionary with 'support' and 'resistance' level lists
        """
        highs = data.get_highs()
        lows = data.get_lows()

        # Find peaks in highs (resistance levels)
        high_peaks = self.find_peaks_and_troughs(highs, min_distance=10)
        resistance_candidates = [pt.value for pt in high_peaks if pt.type == 'peak']

        # Find troughs in lows (support levels)
        low_troughs = self.find_peaks_and_troughs(lows, min_distance=10)
        support_candidates = [pt.value for pt in low_troughs if pt.type == 'trough']

        # Cluster similar levels
        support_levels = self._cluster_levels(support_candidates)
        resistance_levels = self._cluster_levels(resistance_candidates)

        return {
            'support': support_levels,
            'resistance': resistance_levels
        }

    def _cluster_levels(self, levels: List[float], tolerance: float = 0.02) -> List[float]:
        """Cluster similar price levels together."""
        if not levels:
            return []

        levels = sorted(levels)
        clustered = []
        current_cluster = [levels[0]]

        for level in levels[1:]:
            # Check if level is within tolerance of current cluster
            cluster_avg = sum(current_cluster) / len(current_cluster)
            if abs(level - cluster_avg) / cluster_avg <= tolerance:
                current_cluster.append(level)
            else:
                # Finalize current cluster and start new one
                clustered.append(sum(current_cluster) / len(current_cluster))
                current_cluster = [level]

        # Add the last cluster
        if current_cluster:
            clustered.append(sum(current_cluster) / len(current_cluster))

        return clustered

    def detect_trend_direction(self, values: List[float], period: int = 20) -> str:
        """
        Detect overall trend direction.

        Args:
            values: List of values to analyze
            period: Period for trend analysis

        Returns:
            'uptrend', 'downtrend', or 'sideways'
        """
        if len(values) < period:
            return 'sideways'

        # Use the last 'period' values
        recent_values = values[-period:]
        valid_values = [v for v in recent_values if v is not None]

        if len(valid_values) < period // 2:
            return 'sideways'

        # Fit trend line to recent data
        try:
            start_idx = len(values) - len(recent_values)
            trend_line = self.fit_trend_line(values, start_idx, len(values) - 1)

            # Determine trend based on slope and R-squared
            if trend_line.r_squared < 0.3:  # Low correlation
                return 'sideways'

            # Calculate slope as percentage of average value
            avg_value = sum(valid_values) / len(valid_values)
            slope_percent = (trend_line.slope * period) / avg_value

            if slope_percent > 0.05:  # 5% increase over period
                return 'uptrend'
            elif slope_percent < -0.05:  # 5% decrease over period
                return 'downtrend'
            else:
                return 'sideways'

        except ValueError:
            return 'sideways'

    def find_trend_channels(self, data: PriceDataFrame, min_touches: int = 3) -> List[Dict]:
        """
        Find trend channels (parallel support and resistance lines).

        Args:
            data: Price data frame
            min_touches: Minimum number of touches required for a valid channel

        Returns:
            List of channel dictionaries with upper/lower trend lines
        """
        highs = data.get_highs()
        lows = data.get_lows()

        # Find peaks and troughs
        high_peaks = [pt for pt in self.find_peaks_and_troughs(highs) if pt.type == 'peak']
        low_troughs = [pt for pt in self.find_peaks_and_troughs(lows) if pt.type == 'trough']

        channels = []

        # Try to find channels by connecting peaks and troughs
        if len(high_peaks) >= 2 and len(low_troughs) >= 2:
            # Try different combinations of peaks for upper trend line
            for i in range(len(high_peaks) - 1):
                for j in range(i + 1, len(high_peaks)):
                    peak1, peak2 = high_peaks[i], high_peaks[j]

                    # Calculate slope from these two peaks
                    if peak2.index == peak1.index:
                        continue

                    slope = (peak2.value - peak1.value) / (peak2.index - peak1.index)

                    # Find parallel line through troughs
                    best_trough_line = None
                    max_touches = 0

                    for k in range(len(low_troughs) - 1):
                        for l in range(k + 1, len(low_troughs)):
                            trough1, trough2 = low_troughs[k], low_troughs[l]

                            if trough2.index == trough1.index:
                                continue

                            # Check if trough line is roughly parallel
                            trough_slope = (trough2.value - trough1.value) / (trough2.index - trough1.index)

                            if abs(slope - trough_slope) / abs(slope + 1e-10) < 0.3:  # Within 30% slope difference
                                # Count touches for this channel
                                touches = self._count_channel_touches(
                                    highs, lows, peak1, peak2, trough1, trough2
                                )

                                if touches >= max_touches:
                                    max_touches = touches
                                    best_trough_line = (trough1, trough2)

                    if best_trough_line and max_touches >= min_touches:
                        channels.append({
                            'upper_line': {
                                'start': (peak1.index, peak1.value),
                                'end': (peak2.index, peak2.value),
                                'slope': slope
                            },
                            'lower_line': {
                                'start': (best_trough_line[0].index, best_trough_line[0].value),
                                'end': (best_trough_line[1].index, best_trough_line[1].value),
                                'slope': (best_trough_line[1].value - best_trough_line[0].value) /
                                        (best_trough_line[1].index - best_trough_line[0].index)
                            },
                            'touches': max_touches,
                            'width': abs(peak1.value - best_trough_line[0].value)  # Approximate channel width
                        })

        # Sort channels by number of touches (best first)
        return sorted(channels, key=lambda x: x['touches'], reverse=True)

    def _count_channel_touches(self, highs: List[float], lows: List[float],
                              peak1: PeakTrough, peak2: PeakTrough,
                              trough1: PeakTrough, trough2: PeakTrough,
                              tolerance: float = 0.02) -> int:
        """Count how many points touch the channel lines."""
        touches = 4  # Start with the 4 defining points

        # Calculate upper trend line parameters
        upper_slope = (peak2.value - peak1.value) / (peak2.index - peak1.index)
        upper_intercept = peak1.value - upper_slope * peak1.index

        # Calculate lower trend line parameters
        lower_slope = (trough2.value - trough1.value) / (trough2.index - trough1.index)
        lower_intercept = trough1.value - lower_slope * trough1.index

        # Check channel range
        start_idx = min(peak1.index, peak2.index, trough1.index, trough2.index)
        end_idx = max(peak1.index, peak2.index, trough1.index, trough2.index)

        for i in range(start_idx, end_idx + 1):
            if i >= len(highs) or i >= len(lows):
                continue

            high_val = highs[i]
            low_val = lows[i]

            if high_val is None or low_val is None:
                continue

            # Calculate expected trend line values at this index
            upper_expected = upper_slope * i + upper_intercept
            lower_expected = lower_slope * i + lower_intercept

            # Check if high touches upper trend line
            if abs(high_val - upper_expected) / upper_expected <= tolerance:
                touches += 1

            # Check if low touches lower trend line
            if abs(low_val - lower_expected) / lower_expected <= tolerance:
                touches += 1

        return touches
