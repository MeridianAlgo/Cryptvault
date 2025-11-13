"""Divergence pattern detection algorithms."""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from ..data.models import PriceDataFrame
from ..indicators.technical import TechnicalIndicators
from ..indicators.trend_analysis import TrendAnalysis
from .types import PatternType, PatternCategory, DetectedPattern, VolumeProfile, PATTERN_CATEGORIES


class DivergenceAnalyzer:
    """Analyze divergence patterns between price and technical indicators."""

    def __init__(self):
        """Initialize divergence analyzer."""
        self.technical_indicators = TechnicalIndicators()
        self.trend_analysis = TrendAnalysis()
        self.min_divergence_length = 10
        self.max_divergence_length = 50

    def detect_divergence_patterns(self, data: PriceDataFrame,
                                 sensitivity: float = 0.5) -> List[DetectedPattern]:
        """
        Detect price and indicator divergence patterns.

        Args:
            data: Price data frame
            sensitivity: Detection sensitivity (0.0 to 1.0)

        Returns:
            List of detected divergence patterns
        """
        if len(data) < 30:  # Need sufficient data for indicators
            return []

        patterns = []

        try:
            # Calculate technical indicators
            rsi_values = self.technical_indicators.calculate_rsi(data)
            macd_data = self.technical_indicators.calculate_macd(data)

            # Detect RSI divergences
            rsi_divergences = self._detect_rsi_divergences(data, rsi_values, sensitivity)
            patterns.extend(rsi_divergences)

            # Detect MACD divergences
            macd_divergences = self._detect_macd_divergences(data, macd_data, sensitivity)
            patterns.extend(macd_divergences)

        except Exception as e:
            print(f"Warning: Divergence detection error: {e}")

        return self._filter_overlapping_patterns(patterns)

    def _detect_rsi_divergences(self, data: PriceDataFrame, rsi_values: List[float],
                              sensitivity: float) -> List[DetectedPattern]:
        """Detect divergences between price and RSI."""
        patterns = []

        closes = data.get_closes()
        highs = data.get_highs()
        lows = data.get_lows()

        # Find peaks and troughs in price and RSI
        price_peaks = self.technical_indicators.find_peaks_and_troughs(closes, min_distance=5)
        rsi_peaks = self.technical_indicators.find_peaks_and_troughs(rsi_values, min_distance=5)

        # Detect bullish divergences (price makes lower lows, RSI makes higher lows)
        bullish_divergences = self._find_bullish_divergences(
            data, lows, rsi_values, price_peaks['troughs'], rsi_peaks['troughs'], 'RSI', sensitivity
        )
        patterns.extend(bullish_divergences)

        # Detect bearish divergences (price makes higher highs, RSI makes lower highs)
        bearish_divergences = self._find_bearish_divergences(
            data, highs, rsi_values, price_peaks['peaks'], rsi_peaks['peaks'], 'RSI', sensitivity
        )
        patterns.extend(bearish_divergences)

        # Detect hidden divergences
        hidden_divergences = self._find_hidden_divergences(
            data, closes, rsi_values, price_peaks, rsi_peaks, 'RSI', sensitivity
        )
        patterns.extend(hidden_divergences)

        return patterns

    def _detect_macd_divergences(self, data: PriceDataFrame, macd_data: Dict[str, List[float]],
                               sensitivity: float) -> List[DetectedPattern]:
        """Detect divergences between price and MACD."""
        patterns = []

        closes = data.get_closes()
        highs = data.get_highs()
        lows = data.get_lows()
        macd_line = macd_data['macd']

        # Find peaks and troughs in price and MACD
        price_peaks = self.technical_indicators.find_peaks_and_troughs(closes, min_distance=5)
        macd_peaks = self.technical_indicators.find_peaks_and_troughs(macd_line, min_distance=5)

        # Detect bullish divergences
        bullish_divergences = self._find_bullish_divergences(
            data, lows, macd_line, price_peaks['troughs'], macd_peaks['troughs'], 'MACD', sensitivity
        )
        patterns.extend(bullish_divergences)

        # Detect bearish divergences
        bearish_divergences = self._find_bearish_divergences(
            data, highs, macd_line, price_peaks['peaks'], macd_peaks['peaks'], 'MACD', sensitivity
        )
        patterns.extend(bearish_divergences)

        # Detect hidden divergences
        hidden_divergences = self._find_hidden_divergences(
            data, closes, macd_line, price_peaks, macd_peaks, 'MACD', sensitivity
        )
        patterns.extend(hidden_divergences)

        return patterns

    def _find_bullish_divergences(self, data: PriceDataFrame, price_values: List[float],
                                indicator_values: List[float], price_troughs: List[int],
                                indicator_troughs: List[int], indicator_name: str,
                                sensitivity: float) -> List[DetectedPattern]:
        """Find bullish divergences (price lower lows, indicator higher lows)."""
        patterns = []

        # Look for pairs of troughs
        for i in range(len(price_troughs) - 1):
            for j in range(i + 1, len(price_troughs)):
                price_trough1_idx = price_troughs[i]
                price_trough2_idx = price_troughs[j]

                # Skip if too close or too far apart
                distance = price_trough2_idx - price_trough1_idx
                if distance < self.min_divergence_length or distance > self.max_divergence_length:
                    continue

                # Find corresponding indicator troughs in the same time range
                indicator_trough1_idx = self._find_closest_trough(
                    indicator_troughs, price_trough1_idx, tolerance=5
                )
                indicator_trough2_idx = self._find_closest_trough(
                    indicator_troughs, price_trough2_idx, tolerance=5
                )

                if indicator_trough1_idx is None or indicator_trough2_idx is None:
                    continue

                # Check for bullish divergence
                price_trough1 = price_values[price_trough1_idx]
                price_trough2 = price_values[price_trough2_idx]
                indicator_trough1 = indicator_values[indicator_trough1_idx]
                indicator_trough2 = indicator_values[indicator_trough2_idx]

                if (price_trough2 < price_trough1 and  # Price makes lower low
                    indicator_trough2 > indicator_trough1):  # Indicator makes higher low

                    # Calculate divergence strength
                    divergence_pattern = self._create_divergence_pattern(
                        data, PatternType.BULLISH_DIVERGENCE, price_trough1_idx, price_trough2_idx,
                        price_trough1, price_trough2, indicator_trough1, indicator_trough2,
                        indicator_name, sensitivity
                    )

                    if divergence_pattern:
                        patterns.append(divergence_pattern)

        return patterns

    def _find_bearish_divergences(self, data: PriceDataFrame, price_values: List[float],
                                indicator_values: List[float], price_peaks: List[int],
                                indicator_peaks: List[int], indicator_name: str,
                                sensitivity: float) -> List[DetectedPattern]:
        """Find bearish divergences (price higher highs, indicator lower highs)."""
        patterns = []

        # Look for pairs of peaks
        for i in range(len(price_peaks) - 1):
            for j in range(i + 1, len(price_peaks)):
                price_peak1_idx = price_peaks[i]
                price_peak2_idx = price_peaks[j]

                # Skip if too close or too far apart
                distance = price_peak2_idx - price_peak1_idx
                if distance < self.min_divergence_length or distance > self.max_divergence_length:
                    continue

                # Find corresponding indicator peaks
                indicator_peak1_idx = self._find_closest_peak(
                    indicator_peaks, price_peak1_idx, tolerance=5
                )
                indicator_peak2_idx = self._find_closest_peak(
                    indicator_peaks, price_peak2_idx, tolerance=5
                )

                if indicator_peak1_idx is None or indicator_peak2_idx is None:
                    continue

                # Check for bearish divergence
                price_peak1 = price_values[price_peak1_idx]
                price_peak2 = price_values[price_peak2_idx]
                indicator_peak1 = indicator_values[indicator_peak1_idx]
                indicator_peak2 = indicator_values[indicator_peak2_idx]

                if (price_peak2 > price_peak1 and  # Price makes higher high
                    indicator_peak2 < indicator_peak1):  # Indicator makes lower high

                    # Create divergence pattern
                    divergence_pattern = self._create_divergence_pattern(
                        data, PatternType.BEARISH_DIVERGENCE, price_peak1_idx, price_peak2_idx,
                        price_peak1, price_peak2, indicator_peak1, indicator_peak2,
                        indicator_name, sensitivity
                    )

                    if divergence_pattern:
                        patterns.append(divergence_pattern)

        return patterns

    def _find_hidden_divergences(self, data: PriceDataFrame, price_values: List[float],
                               indicator_values: List[float], price_peaks: Dict[str, List[int]],
                               indicator_peaks: Dict[str, List[int]], indicator_name: str,
                               sensitivity: float) -> List[DetectedPattern]:
        """Find hidden divergences."""
        patterns = []

        # Hidden bullish divergence: price higher lows, indicator lower lows
        for i in range(len(price_peaks['troughs']) - 1):
            for j in range(i + 1, len(price_peaks['troughs'])):
                price_trough1_idx = price_peaks['troughs'][i]
                price_trough2_idx = price_peaks['troughs'][j]

                distance = price_trough2_idx - price_trough1_idx
                if distance < self.min_divergence_length or distance > self.max_divergence_length:
                    continue

                indicator_trough1_idx = self._find_closest_trough(
                    indicator_peaks['troughs'], price_trough1_idx, tolerance=5
                )
                indicator_trough2_idx = self._find_closest_trough(
                    indicator_peaks['troughs'], price_trough2_idx, tolerance=5
                )

                if indicator_trough1_idx is None or indicator_trough2_idx is None:
                    continue

                price_trough1 = price_values[price_trough1_idx]
                price_trough2 = price_values[price_trough2_idx]
                indicator_trough1 = indicator_values[indicator_trough1_idx]
                indicator_trough2 = indicator_values[indicator_trough2_idx]

                if (price_trough2 > price_trough1 and  # Price makes higher low
                    indicator_trough2 < indicator_trough1):  # Indicator makes lower low

                    divergence_pattern = self._create_divergence_pattern(
                        data, PatternType.HIDDEN_BULLISH_DIVERGENCE, price_trough1_idx, price_trough2_idx,
                        price_trough1, price_trough2, indicator_trough1, indicator_trough2,
                        indicator_name, sensitivity
                    )

                    if divergence_pattern:
                        patterns.append(divergence_pattern)

        # Hidden bearish divergence: price lower highs, indicator higher highs
        for i in range(len(price_peaks['peaks']) - 1):
            for j in range(i + 1, len(price_peaks['peaks'])):
                price_peak1_idx = price_peaks['peaks'][i]
                price_peak2_idx = price_peaks['peaks'][j]

                distance = price_peak2_idx - price_peak1_idx
                if distance < self.min_divergence_length or distance > self.max_divergence_length:
                    continue

                indicator_peak1_idx = self._find_closest_peak(
                    indicator_peaks['peaks'], price_peak1_idx, tolerance=5
                )
                indicator_peak2_idx = self._find_closest_peak(
                    indicator_peaks['peaks'], price_peak2_idx, tolerance=5
                )

                if indicator_peak1_idx is None or indicator_peak2_idx is None:
                    continue

                price_peak1 = price_values[price_peak1_idx]
                price_peak2 = price_values[price_peak2_idx]
                indicator_peak1 = indicator_values[indicator_peak1_idx]
                indicator_peak2 = indicator_values[indicator_peak2_idx]

                if (price_peak2 < price_peak1 and  # Price makes lower high
                    indicator_peak2 > indicator_peak1):  # Indicator makes higher high

                    divergence_pattern = self._create_divergence_pattern(
                        data, PatternType.HIDDEN_BEARISH_DIVERGENCE, price_peak1_idx, price_peak2_idx,
                        price_peak1, price_peak2, indicator_peak1, indicator_peak2,
                        indicator_name, sensitivity
                    )

                    if divergence_pattern:
                        patterns.append(divergence_pattern)

        return patterns

    def _find_closest_peak(self, peaks: List[int], target_index: int, tolerance: int) -> Optional[int]:
        """Find the closest peak to target index within tolerance."""
        closest_peak = None
        min_distance = float('inf')

        for peak_idx in peaks:
            distance = abs(peak_idx - target_index)
            if distance <= tolerance and distance < min_distance:
                min_distance = distance
                closest_peak = peak_idx

        return closest_peak

    def _find_closest_trough(self, troughs: List[int], target_index: int, tolerance: int) -> Optional[int]:
        """Find the closest trough to target index within tolerance."""
        closest_trough = None
        min_distance = float('inf')

        for trough_idx in troughs:
            distance = abs(trough_idx - target_index)
            if distance <= tolerance and distance < min_distance:
                min_distance = distance
                closest_trough = trough_idx

        return closest_trough

    def _create_divergence_pattern(self, data: PriceDataFrame, pattern_type: PatternType,
                                 price_idx1: int, price_idx2: int, price_val1: float, price_val2: float,
                                 indicator_val1: float, indicator_val2: float, indicator_name: str,
                                 sensitivity: float) -> Optional[DetectedPattern]:
        """Create a divergence pattern."""

        # Calculate divergence strength
        confidence = self._calculate_divergence_confidence(
            price_val1, price_val2, indicator_val1, indicator_val2,
            price_idx2 - price_idx1, sensitivity
        )

        if confidence < (0.3 + sensitivity * 0.3):
            return None

        # Calculate volume profile
        volume_profile = self._calculate_volume_profile(data, price_idx1, price_idx2)

        # Determine divergence direction and strength
        price_change = (price_val2 - price_val1) / price_val1 if price_val1 != 0 else 0
        indicator_change = (indicator_val2 - indicator_val1) / abs(indicator_val1) if indicator_val1 != 0 else 0

        return DetectedPattern(
            pattern_type=pattern_type,
            category=PATTERN_CATEGORIES[pattern_type],
            confidence=confidence,
            start_time=data[price_idx1].timestamp,
            end_time=data[price_idx2].timestamp,
            start_index=price_idx1,
            end_index=price_idx2,
            key_levels={
                'price_point1': price_val1,
                'price_point2': price_val2,
                'indicator_point1': indicator_val1,
                'indicator_point2': indicator_val2,
                'price_change_percent': price_change * 100,
                'indicator_change_percent': indicator_change * 100,
                'divergence_strength': abs(price_change - indicator_change),
                'indicator_name': indicator_name
            },
            volume_profile=volume_profile,
            description=f"{pattern_type.value.replace('_', ' ').title()} with {indicator_name}. Price change: {price_change:.1%}, {indicator_name} change: {indicator_change:.1%}. Confidence: {confidence:.1%}"
        )

    def _calculate_divergence_confidence(self, price_val1: float, price_val2: float,
                                       indicator_val1: float, indicator_val2: float,
                                       time_span: int, sensitivity: float) -> float:
        """Calculate confidence score for divergence pattern."""
        confidence_factors = []

        # 1. Magnitude of divergence
        if price_val1 != 0 and indicator_val1 != 0:
            price_change = abs(price_val2 - price_val1) / abs(price_val1)
            indicator_change = abs(indicator_val2 - indicator_val1) / abs(indicator_val1)

            # Stronger divergence = higher confidence
            divergence_magnitude = abs(price_change - indicator_change)
            magnitude_score = min(1.0, divergence_magnitude / 0.1)  # Normalize to 10% divergence
            confidence_factors.append(magnitude_score * 0.4)
        else:
            confidence_factors.append(0.0)

        # 2. Time span appropriateness
        if self.min_divergence_length <= time_span <= self.max_divergence_length:
            time_score = 1.0
        elif time_span < self.min_divergence_length:
            time_score = time_span / self.min_divergence_length
        else:
            time_score = self.max_divergence_length / time_span

        confidence_factors.append(time_score * 0.3)

        # 3. Clarity of divergence direction
        price_direction = 1 if price_val2 > price_val1 else -1
        indicator_direction = 1 if indicator_val2 > indicator_val1 else -1

        # For regular divergence, directions should be opposite
        # For hidden divergence, specific patterns apply
        direction_clarity = 1.0 if price_direction != indicator_direction else 0.5
        confidence_factors.append(direction_clarity * 0.2)

        # 4. Relative strength of moves
        if price_val1 != 0 and indicator_val1 != 0:
            price_strength = abs(price_val2 - price_val1) / abs(price_val1)
            indicator_strength = abs(indicator_val2 - indicator_val1) / abs(indicator_val1)

            # Both moves should be significant
            min_strength = min(price_strength, indicator_strength)
            strength_score = min(1.0, min_strength / 0.05)  # Normalize to 5% minimum move
            confidence_factors.append(strength_score * 0.1)
        else:
            confidence_factors.append(0.0)

        base_confidence = sum(confidence_factors)

        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        final_confidence = max(0.0, min(1.0, base_confidence + sensitivity_adjustment))

        return final_confidence

    def _calculate_volume_profile(self, data: PriceDataFrame,
                                start_index: int, end_index: int) -> VolumeProfile:
        """Calculate volume profile for the divergence period."""
        volumes = data.get_volumes()[start_index:end_index+1]
        valid_volumes = [v for v in volumes if v is not None and v > 0]

        if not valid_volumes:
            return VolumeProfile(
                avg_volume=0.0,
                volume_trend="unknown",
                volume_confirmation=False
            )

        avg_volume = sum(valid_volumes) / len(valid_volumes)

        # Determine volume trend
        if len(valid_volumes) >= 3:
            first_half = valid_volumes[:len(valid_volumes)//2]
            second_half = valid_volumes[len(valid_volumes)//2:]

            avg_first = sum(first_half) / len(first_half)
            avg_second = sum(second_half) / len(second_half)

            change_ratio = (avg_second - avg_first) / avg_first if avg_first > 0 else 0

            if change_ratio > 0.1:
                volume_trend = "increasing"
            elif change_ratio < -0.1:
                volume_trend = "decreasing"
            else:
                volume_trend = "stable"
        else:
            volume_trend = "stable"

        # Volume confirmation (increasing volume can confirm divergence)
        volume_confirmation = volume_trend == "increasing"

        return VolumeProfile(
            avg_volume=avg_volume,
            volume_trend=volume_trend,
            volume_confirmation=volume_confirmation
        )

    def _filter_overlapping_patterns(self, patterns: List[DetectedPattern]) -> List[DetectedPattern]:
        """Filter out overlapping divergence patterns."""
        if not patterns:
            return patterns

        # Sort by confidence (highest first)
        sorted_patterns = sorted(patterns, key=lambda p: p.confidence, reverse=True)
        filtered_patterns = []

        for pattern in sorted_patterns:
            # Check if this pattern overlaps significantly with any already accepted pattern
            overlaps = False

            for accepted_pattern in filtered_patterns:
                overlap_start = max(pattern.start_index, accepted_pattern.start_index)
                overlap_end = min(pattern.end_index, accepted_pattern.end_index)

                if overlap_start < overlap_end:
                    overlap_length = overlap_end - overlap_start
                    pattern_length = pattern.end_index - pattern.start_index

                    # If overlap is more than 60% of pattern length, consider it overlapping
                    if overlap_length > pattern_length * 0.6:
                        overlaps = True
                        break

            if not overlaps:
                filtered_patterns.append(pattern)

        return filtered_patterns

    def detect_price_indicator_divergence(self, data: PriceDataFrame, sensitivity: float = 0.5) -> List[DetectedPattern]:
        """Alias for detect_divergence_patterns for backward compatibility."""
        return self.detect_divergence_patterns(data, sensitivity)
