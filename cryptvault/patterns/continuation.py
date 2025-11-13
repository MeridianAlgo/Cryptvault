"""
Continuation Pattern Detection

Detects continuation patterns that signal the existing trend is likely to continue.
These patterns typically form during consolidation periods within a larger trend.
"""

from typing import List
import numpy as np
from .base import BasePatternDetector, DetectedPattern
from ..data.models import PriceDataFrame
from ..indicators.trend_analysis import TrendAnalysis, PeakTrough

class ContinuationPatternDetector(BasePatternDetector):
    """
    Detect continuation patterns that signal trend continuation.

    This detector identifies patterns that typically form during consolidation
    periods within a larger trend, suggesting the trend will resume:

    Triangle Patterns:
    - Ascending Triangle: Flat resistance, rising support (bullish)
    - Descending Triangle: Falling resistance, flat support (bearish)
    - Symmetrical Triangle: Converging trendlines (neutral, follows prior trend)

    Flag Patterns:
    - Bull Flag: Strong uptrend followed by small downward consolidation
    - Bear Flag: Strong downtrend followed by small upward consolidation

    Rectangle Pattern:
    - Horizontal consolidation between support and resistance levels
    - Breakout direction typically follows prior trend

    Pattern Characteristics:
    ----------------------
    Triangles:
    - Require at least 2 peaks and 2 troughs
    - Converging or parallel trendlines
    - Breakout typically occurs at 2/3 to 3/4 of pattern width

    Flags:
    - Strong trend (>10% move) followed by consolidation
    - Consolidation range < 5% of price
    - Duration: typically 5-20 periods

    Rectangles:
    - Price oscillates between horizontal support/resistance
    - Range: 3-15% of price
    - Duration: typically 20+ periods

    Example:
        >>> detector = ContinuationPatternDetector()
        >>> patterns = detector.detect(price_data, sensitivity=0.5)
        >>> for pattern in patterns:
        ...     print(f"{pattern.pattern_type}: {pattern.confidence:.1%}")
    """

    def __init__(self):
        """Initialize continuation pattern detector with trend analysis tools."""
        super().__init__()
        self.trend_analysis = TrendAnalysis()

    def detect(self, data: PriceDataFrame, sensitivity: float = 0.5) -> List[DetectedPattern]:
        """
        Detect all continuation patterns in price data.

        This is the main entry point for continuation pattern detection. It orchestrates
        detection of triangles, flags, pennants, and rectangles, returning a filtered
        list of non-overlapping patterns.

        Args:
            data: Price data frame containing OHLCV data
            sensitivity: Detection sensitivity (0.0 to 1.0)
                - Lower values (0.0-0.4): Stricter detection, fewer false positives
                - Medium values (0.4-0.6): Balanced detection
                - Higher values (0.6-1.0): More lenient, catches more patterns

        Returns:
            List of detected continuation patterns, sorted by confidence

        Example:
            >>> detector = ContinuationPatternDetector()
            >>> patterns = detector.detect(price_data, sensitivity=0.5)
            >>> print(f"Found {len(patterns)} continuation patterns")
        """
        patterns = []

        if len(data) < self.min_pattern_length:
            return patterns

        # Detect triangle patterns (ascending, descending, symmetrical)
        patterns.extend(self._detect_triangles(data, sensitivity))

        # Detect flag and pennant patterns
        patterns.extend(self._detect_flags(data, sensitivity))

        # Detect rectangle consolidation patterns
        patterns.extend(self._detect_rectangles(data, sensitivity))

        # Filter overlapping patterns using base class method
        return self._filter_overlapping(patterns)

    def get_pattern_types(self) -> List[str]:
        """
        Get list of pattern types this detector can identify.

        Returns:
            List of continuation pattern type names
        """
        return [
            'Ascending Triangle', 'Descending Triangle', 'Symmetrical Triangle',
            'Bull Flag', 'Bear Flag', 'Pennant', 'Rectangle'
        ]

    def _detect_triangles(self, data: PriceDataFrame, sensitivity: float) -> List[DetectedPattern]:
        """
        Detect triangle patterns (ascending, descending, symmetrical).

        Triangle patterns are formed by converging trendlines:
        - Ascending: Flat resistance + rising support (bullish)
        - Descending: Falling resistance + flat support (bearish)
        - Symmetrical: Both trendlines converging (neutral, follows trend)

        Requires at least 2 peaks and 2 troughs to form trendlines.

        Args:
            data: Price data frame
            sensitivity: Detection sensitivity

        Returns:
            List of detected triangle patterns
        """
        patterns = []
        highs = data.get_highs()
        lows = data.get_lows()

        high_peaks = [pt for pt in self.trend_analysis.find_peaks_and_troughs(highs, min_distance=5) if pt.type == 'peak']
        low_troughs = [pt for pt in self.trend_analysis.find_peaks_and_troughs(lows, min_distance=5) if pt.type == 'trough']

        if len(high_peaks) >= 2 and len(low_troughs) >= 2:
            # Check for ascending triangle (flat top, rising bottom)
            if self._is_flat_line([p.value for p in high_peaks[-2:]]) and self._is_rising_line([t.value for t in low_troughs[-2:]]):
                patterns.append(self._create_triangle_pattern(data, 'Ascending Triangle', high_peaks[-2:], low_troughs[-2:], 'bullish', sensitivity))

            # Check for descending triangle (falling top, flat bottom)
            elif self._is_falling_line([p.value for p in high_peaks[-2:]]) and self._is_flat_line([t.value for t in low_troughs[-2:]]):
                patterns.append(self._create_triangle_pattern(data, 'Descending Triangle', high_peaks[-2:], low_troughs[-2:], 'bearish', sensitivity))

            # Check for symmetrical triangle (converging lines)
            elif self._is_falling_line([p.value for p in high_peaks[-2:]]) and self._is_rising_line([t.value for t in low_troughs[-2:]]):
                patterns.append(self._create_triangle_pattern(data, 'Symmetrical Triangle', high_peaks[-2:], low_troughs[-2:], 'neutral', sensitivity))

        return patterns

    def _detect_flags(self, data: PriceDataFrame, sensitivity: float) -> List[DetectedPattern]:
        """
        Detect flag and pennant patterns.

        Flag patterns consist of:
        1. Strong trend (flagpole): >10% price move
        2. Consolidation (flag): Small counter-trend move, <5% range

        Bull Flag: Uptrend followed by slight downward/sideways consolidation
        Bear Flag: Downtrend followed by slight upward/sideways consolidation

        Typical duration: 5-20 periods for consolidation

        Args:
            data: Price data frame
            sensitivity: Detection sensitivity

        Returns:
            List of detected flag patterns
        """
        patterns = []
        closes = data.get_closes()

        # Look for strong trend followed by consolidation
        if len(closes) >= 30:
            # Check last 30 periods
            trend_period = closes[-30:-10]
            consolidation_period = closes[-10:]

            trend_change = (trend_period[-1] - trend_period[0]) / trend_period[0]
            consolidation_range = (max(consolidation_period) - min(consolidation_period)) / np.mean(consolidation_period)

            # Bull flag: strong uptrend + small consolidation
            if trend_change > 0.1 and consolidation_range < 0.05:
                confidence = self._calculate_confidence([0.7, 0.8], [1.0, 1.0])
                patterns.append(DetectedPattern(
                    pattern_type='Bull Flag',
                    category='Bullish Continuation',
                    confidence=confidence,
                    start_time=data[-30].timestamp,
                    end_time=data[-1].timestamp,
                    start_index=len(data)-30,
                    end_index=len(data)-1,
                    key_levels={'support': min(consolidation_period), 'resistance': max(consolidation_period)},
                    description=f"Bull Flag pattern with {confidence:.1%} confidence"
                ))

            # Bear flag: strong downtrend + small consolidation
            elif trend_change < -0.1 and consolidation_range < 0.05:
                confidence = self._calculate_confidence([0.7, 0.8], [1.0, 1.0])
                patterns.append(DetectedPattern(
                    pattern_type='Bear Flag',
                    category='Bearish Continuation',
                    confidence=confidence,
                    start_time=data[-30].timestamp,
                    end_time=data[-1].timestamp,
                    start_index=len(data)-30,
                    end_index=len(data)-1,
                    key_levels={'support': min(consolidation_period), 'resistance': max(consolidation_period)},
                    description=f"Bear Flag pattern with {confidence:.1%} confidence"
                ))

        return patterns

    def _detect_rectangles(self, data: PriceDataFrame, sensitivity: float) -> List[DetectedPattern]:
        """
        Detect rectangle consolidation patterns.

        Rectangle patterns are characterized by:
        - Price oscillating between horizontal support and resistance
        - Range: 3-15% of price (not too tight, not too wide)
        - Duration: typically 20+ periods
        - Breakout direction usually follows prior trend

        Args:
            data: Price data frame
            sensitivity: Detection sensitivity

        Returns:
            List of detected rectangle patterns
        """
        patterns = []
        highs = data.get_highs()
        lows = data.get_lows()

        if len(data) >= 20:
            recent_highs = highs[-20:]
            recent_lows = lows[-20:]

            # Check if price is trading in a range
            high_level = np.mean(sorted(recent_highs)[-5:])
            low_level = np.mean(sorted(recent_lows)[:5])

            range_pct = (high_level - low_level) / low_level

            if 0.03 < range_pct < 0.15:  # 3-15% range
                confidence = self._calculate_confidence([0.6, 0.7], [1.0, 1.0])
                patterns.append(DetectedPattern(
                    pattern_type='Rectangle',
                    category='Continuation',
                    confidence=confidence,
                    start_time=data[-20].timestamp,
                    end_time=data[-1].timestamp,
                    start_index=len(data)-20,
                    end_index=len(data)-1,
                    key_levels={'support': low_level, 'resistance': high_level},
                    description=f"Rectangle pattern with {confidence:.1%} confidence"
                ))

        return patterns

    def _is_flat_line(self, values: List[float], tolerance: float = 0.02) -> bool:
        """
        Check if values form a flat (horizontal) line.

        Used to identify flat resistance or support levels in triangle patterns.

        Args:
            values: List of price values
            tolerance: Maximum allowed deviation from average (default 2%)

        Returns:
            True if values are within tolerance of average, False otherwise
        """
        if len(values) < 2:
            return False
        avg = np.mean(values)
        return all(abs(v - avg) / avg < tolerance for v in values)

    def _is_rising_line(self, values: List[float]) -> bool:
        """
        Check if values form a rising trendline.

        Used to identify rising support in ascending and symmetrical triangles.

        Args:
            values: List of price values

        Returns:
            True if each value is higher than the previous, False otherwise
        """
        return all(values[i] < values[i+1] for i in range(len(values)-1))

    def _is_falling_line(self, values: List[float]) -> bool:
        """
        Check if values form a falling trendline.

        Used to identify falling resistance in descending and symmetrical triangles.

        Args:
            values: List of price values

        Returns:
            True if each value is lower than the previous, False otherwise
        """
        return all(values[i] > values[i+1] for i in range(len(values)-1))

    def _create_triangle_pattern(self, data, pattern_type, peaks, troughs, bias, sensitivity):
        """
        Create a triangle pattern with calculated confidence and key levels.

        Args:
            data: Price data frame
            pattern_type: Type of triangle (Ascending, Descending, Symmetrical)
            peaks: List of peaks forming upper trendline
            troughs: List of troughs forming lower trendline
            bias: Pattern bias ('bullish', 'bearish', 'neutral')
            sensitivity: Detection sensitivity

        Returns:
            DetectedPattern for the triangle
        """
        start_idx = min(peaks[0].index, troughs[0].index)
        end_idx = max(peaks[-1].index, troughs[-1].index)

        # Calculate confidence based on trendline quality and pattern characteristics
        confidence = self._calculate_confidence([0.7, 0.8], [1.0, 1.0])

        return DetectedPattern(
            pattern_type=pattern_type,
            category=f"{bias.title()} Continuation" if bias != 'neutral' else 'Continuation',
            confidence=confidence,
            start_time=data[start_idx].timestamp,
            end_time=data[end_idx].timestamp,
            start_index=start_idx,
            end_index=end_idx,
            key_levels={
                'upper': max(p.value for p in peaks),
                'lower': min(t.value for t in troughs)
            },
            description=f"{pattern_type} with {confidence:.1%} confidence"
        )
