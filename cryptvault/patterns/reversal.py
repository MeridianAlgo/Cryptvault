"""
Reversal Pattern Detection

Detects reversal patterns including double/triple tops/bottoms and head & shoulders patterns.
These patterns signal potential trend reversals and are critical for identifying market turning points.
"""

from typing import List, Dict, Optional
from datetime import datetime
from .base import BasePatternDetector, DetectedPattern
from ..data.models import PriceDataFrame
from ..indicators.trend_analysis import TrendAnalysis, PeakTrough
from .types import PatternType, PatternCategory, VolumeProfile, PATTERN_CATEGORIES


class ReversalPatternDetector(BasePatternDetector):
    """
    Detect reversal chart patterns that signal potential trend changes.

    This detector identifies classic reversal patterns including:
    - Double Top/Bottom: Two peaks/troughs at similar price levels
    - Triple Top/Bottom: Three peaks/troughs at similar price levels
    - Head and Shoulders: Three peaks with middle peak highest (bearish)
    - Inverse Head and Shoulders: Three troughs with middle trough lowest (bullish)

    Confidence Calculation Methodology:
    ------------------------------------
    Confidence scores (0.0 to 1.0) are calculated using weighted factors:

    For Double/Triple Patterns:
    - Peak/Trough Similarity (30%): How closely aligned the peaks/troughs are
    - Retracement Depth (30%): Depth of valley/peak between formations
    - Volume Confirmation (20%): Volume pattern supporting reversal
    - Time Spacing (20%): Appropriate duration between formations

    For Head & Shoulders:
    - Shoulder Symmetry (25%): How similar the shoulders are in height
    - Head Prominence (25%): How much the head stands out
    - Neckline Break (20%): Price position relative to neckline
    - Volume Pattern (15%): Increasing volume on right shoulder
    - Time Symmetry (15%): Balance between left and right sides

    The sensitivity parameter (0.0-1.0) adjusts the final confidence by ±20%.

    Example:
        >>> detector = ReversalPatternDetector()
        >>> patterns = detector.detect(price_data, sensitivity=0.6)
        >>> for pattern in patterns:
        ...     print(f"{pattern.pattern_type}: {pattern.confidence:.1%}")
    """

    def __init__(self):
        """Initialize reversal pattern detector with trend analysis tools."""
        super().__init__()
        self.trend_analysis = TrendAnalysis()
        self.min_pattern_length = 15
        self.max_pattern_length = 100

    def detect(self, data: PriceDataFrame, sensitivity: float = 0.5) -> List[DetectedPattern]:
        """
        Detect all reversal patterns in price data.

        This is the main entry point for reversal pattern detection. It orchestrates
        detection of all reversal pattern types and returns a filtered list of
        non-overlapping patterns.

        Args:
            data: Price data frame containing OHLCV data
            sensitivity: Detection sensitivity (0.0 to 1.0)
                - Lower values (0.0-0.4): Stricter detection, fewer false positives
                - Medium values (0.4-0.6): Balanced detection
                - Higher values (0.6-1.0): More lenient, catches more patterns

        Returns:
            List of detected reversal patterns, sorted by confidence

        Example:
            >>> detector = ReversalPatternDetector()
            >>> patterns = detector.detect(price_data, sensitivity=0.5)
            >>> print(f"Found {len(patterns)} reversal patterns")
        """
        if len(data) < self.min_pattern_length:
            return []

        patterns = []

        # Detect double and triple patterns
        patterns.extend(self.detect_double_triple_patterns(data, sensitivity))

        # Detect head and shoulders patterns
        patterns.extend(self.detect_head_and_shoulders_patterns(data, sensitivity))

        # Filter overlapping patterns using base class method
        return self._filter_overlapping(patterns)

    def get_pattern_types(self) -> List[str]:
        """
        Get list of pattern types this detector can identify.

        Returns:
            List of pattern type names
        """
        return [
            'Double Top',
            'Double Bottom',
            'Triple Top',
            'Triple Bottom',
            'Head and Shoulders',
            'Inverse Head and Shoulders'
        ]

    def detect_double_triple_patterns(self, data: PriceDataFrame,
                                    sensitivity: float = 0.5) -> List[DetectedPattern]:
        """
        Detect double/triple top and bottom patterns.

        Args:
            data: Price data frame
            sensitivity: Detection sensitivity (0.0 to 1.0)

        Returns:
            List of detected double/triple patterns
        """
        if len(data) < self.min_pattern_length:
            return []

        patterns = []
        highs = data.get_highs()
        lows = data.get_lows()

        # Find peaks and troughs
        high_peaks = [pt for pt in self.trend_analysis.find_peaks_and_troughs(highs, min_distance=5)
                     if pt.type == 'peak']
        low_troughs = [pt for pt in self.trend_analysis.find_peaks_and_troughs(lows, min_distance=5)
                      if pt.type == 'trough']

        # Detect double/triple tops
        if len(high_peaks) >= 2:
            top_patterns = self._find_multiple_top_patterns(data, high_peaks, sensitivity)
            patterns.extend(top_patterns)

        # Detect double/triple bottoms
        if len(low_troughs) >= 2:
            bottom_patterns = self._find_multiple_bottom_patterns(data, low_troughs, sensitivity)
            patterns.extend(bottom_patterns)

        return self._filter_overlapping_patterns(patterns)

    def _find_multiple_top_patterns(self, data: PriceDataFrame, peaks: List[PeakTrough],
                                  sensitivity: float) -> List[DetectedPattern]:
        """
        Find double and triple top patterns in peak data.

        A double top is a bearish reversal pattern with two peaks at similar levels.
        A triple top extends this with three similar peaks, indicating strong resistance.

        Args:
            data: Price data frame
            peaks: List of identified peaks
            sensitivity: Detection sensitivity

        Returns:
            List of detected double/triple top patterns
        """
        patterns = []

        # Look for double tops
        for i in range(len(peaks) - 1):
            for j in range(i + 1, len(peaks)):
                peak1, peak2 = peaks[i], peaks[j]

                # Check if peaks are similar in height
                if self._are_peaks_similar(peak1.value, peak2.value, tolerance=0.03):
                    double_top = self._analyze_double_top(data, peak1, peak2, sensitivity)
                    if double_top:
                        patterns.append(double_top)

        # Look for triple tops
        for i in range(len(peaks) - 2):
            for j in range(i + 1, len(peaks) - 1):
                for k in range(j + 1, len(peaks)):
                    peak1, peak2, peak3 = peaks[i], peaks[j], peaks[k]

                    # Check if all three peaks are similar
                    if (self._are_peaks_similar(peak1.value, peak2.value, tolerance=0.03) and
                        self._are_peaks_similar(peak2.value, peak3.value, tolerance=0.03)):
                        triple_top = self._analyze_triple_top(data, peak1, peak2, peak3, sensitivity)
                        if triple_top:
                            patterns.append(triple_top)

        return patterns

    def _find_multiple_bottom_patterns(self, data: PriceDataFrame, troughs: List[PeakTrough],
                                     sensitivity: float) -> List[DetectedPattern]:
        """
        Find double and triple bottom patterns in trough data.

        A double bottom is a bullish reversal pattern with two troughs at similar levels.
        A triple bottom extends this with three similar troughs, indicating strong support.

        Args:
            data: Price data frame
            troughs: List of identified troughs
            sensitivity: Detection sensitivity

        Returns:
            List of detected double/triple bottom patterns
        """
        patterns = []

        # Look for double bottoms
        for i in range(len(troughs) - 1):
            for j in range(i + 1, len(troughs)):
                trough1, trough2 = troughs[i], troughs[j]

                # Check if troughs are similar in depth
                if self._are_peaks_similar(trough1.value, trough2.value, tolerance=0.03):
                    double_bottom = self._analyze_double_bottom(data, trough1, trough2, sensitivity)
                    if double_bottom:
                        patterns.append(double_bottom)

        # Look for triple bottoms
        for i in range(len(troughs) - 2):
            for j in range(i + 1, len(troughs) - 1):
                for k in range(j + 1, len(troughs)):
                    trough1, trough2, trough3 = troughs[i], troughs[j], troughs[k]

                    # Check if all three troughs are similar
                    if (self._are_peaks_similar(trough1.value, trough2.value, tolerance=0.03) and
                        self._are_peaks_similar(trough2.value, trough3.value, tolerance=0.03)):
                        triple_bottom = self._analyze_triple_bottom(data, trough1, trough2, trough3, sensitivity)
                        if triple_bottom:
                            patterns.append(triple_bottom)

        return patterns

    def _are_peaks_similar(self, value1: float, value2: float, tolerance: float) -> bool:
        """
        Check if two peak/trough values are similar within tolerance.

        Uses percentage difference to determine similarity, which is scale-independent.

        Args:
            value1: First price value
            value2: Second price value
            tolerance: Maximum allowed percentage difference (e.g., 0.03 for 3%)

        Returns:
            True if values are within tolerance, False otherwise
        """
        if value1 == 0:
            return abs(value2) < tolerance

        return abs(value1 - value2) / abs(value1) <= tolerance

    def _analyze_double_top(self, data: PriceDataFrame, peak1: PeakTrough, peak2: PeakTrough,
                          sensitivity: float) -> Optional[DetectedPattern]:
        """
        Analyze and validate a double top pattern.

        Double top is a bearish reversal pattern characterized by:
        - Two peaks at approximately the same price level
        - A valley (neckline) between the peaks
        - Minimum 10% retracement from peaks to valley
        - Measured move target: valley - (peak - valley)

        Args:
            data: Price data frame
            peak1: First peak
            peak2: Second peak
            sensitivity: Detection sensitivity

        Returns:
            DetectedPattern if valid, None otherwise
        """

        # Find the valley between peaks
        valley_start = peak1.index
        valley_end = peak2.index

        if valley_end - valley_start < 5:  # Too close together
            return None

        lows = data.get_lows()[valley_start:valley_end+1]
        valley_low = min(l for l in lows if l is not None)
        valley_index = valley_start + next(i for i, l in enumerate(lows) if l == valley_low)

        # Validate double top characteristics
        if not self._validate_double_top(peak1, peak2, valley_low, valley_index):
            return None

        # Calculate confidence
        confidence = self._calculate_double_top_confidence(data, peak1, peak2, valley_low, sensitivity)

        if confidence < (0.4 + sensitivity * 0.3):
            return None

        # Calculate volume profile
        volume_profile = self._calculate_volume_profile(data, peak1.index, peak2.index)

        return DetectedPattern(
            pattern_type=PatternType.DOUBLE_TOP,
            category=PATTERN_CATEGORIES[PatternType.DOUBLE_TOP],
            confidence=confidence,
            start_time=data[peak1.index].timestamp,
            end_time=data[peak2.index].timestamp,
            start_index=peak1.index,
            end_index=peak2.index,
            key_levels={
                'peak1_price': peak1.value,
                'peak2_price': peak2.value,
                'valley_price': valley_low,
                'neckline_price': valley_low,
                'target_price': valley_low - (peak1.value - valley_low)  # Measured move
            },
            volume_profile=volume_profile,
            description=f"Double Top reversal pattern. Peaks at {peak1.value:.2f} and {peak2.value:.2f}, neckline at {valley_low:.2f}. Confidence: {confidence:.1%}"
        )

    def _analyze_double_bottom(self, data: PriceDataFrame, trough1: PeakTrough, trough2: PeakTrough,
                             sensitivity: float) -> Optional[DetectedPattern]:
        """
        Analyze and validate a double bottom pattern.

        Double bottom is a bullish reversal pattern characterized by:
        - Two troughs at approximately the same price level
        - A peak (neckline) between the troughs
        - Minimum 10% bounce from troughs to peak
        - Measured move target: peak + (peak - trough)

        Args:
            data: Price data frame
            trough1: First trough
            trough2: Second trough
            sensitivity: Detection sensitivity

        Returns:
            DetectedPattern if valid, None otherwise
        """

        # Find the peak between troughs
        peak_start = trough1.index
        peak_end = trough2.index

        if peak_end - peak_start < 5:  # Too close together
            return None

        highs = data.get_highs()[peak_start:peak_end+1]
        peak_high = max(h for h in highs if h is not None)
        peak_index = peak_start + next(i for i, h in enumerate(highs) if h == peak_high)

        # Validate double bottom characteristics
        if not self._validate_double_bottom(trough1, trough2, peak_high, peak_index):
            return None

        # Calculate confidence
        confidence = self._calculate_double_bottom_confidence(data, trough1, trough2, peak_high, sensitivity)

        if confidence < (0.4 + sensitivity * 0.3):
            return None

        # Calculate volume profile
        volume_profile = self._calculate_volume_profile(data, trough1.index, trough2.index)

        return DetectedPattern(
            pattern_type=PatternType.DOUBLE_BOTTOM,
            category=PATTERN_CATEGORIES[PatternType.DOUBLE_BOTTOM],
            confidence=confidence,
            start_time=data[trough1.index].timestamp,
            end_time=data[trough2.index].timestamp,
            start_index=trough1.index,
            end_index=trough2.index,
            key_levels={
                'trough1_price': trough1.value,
                'trough2_price': trough2.value,
                'peak_price': peak_high,
                'neckline_price': peak_high,
                'target_price': peak_high + (peak_high - trough1.value)  # Measured move
            },
            volume_profile=volume_profile,
            description=f"Double Bottom reversal pattern. Troughs at {trough1.value:.2f} and {trough2.value:.2f}, neckline at {peak_high:.2f}. Confidence: {confidence:.1%}"
        )

    def _analyze_triple_top(self, data: PriceDataFrame, peak1: PeakTrough, peak2: PeakTrough,
                          peak3: PeakTrough, sensitivity: float) -> Optional[DetectedPattern]:
        """Analyze triple top pattern."""

        # Find valleys between peaks
        valley1_lows = data.get_lows()[peak1.index:peak2.index+1]
        valley2_lows = data.get_lows()[peak2.index:peak3.index+1]

        valley1_low = min(l for l in valley1_lows if l is not None)
        valley2_low = min(l for l in valley2_lows if l is not None)

        # Use the higher of the two valleys as neckline
        neckline_price = max(valley1_low, valley2_low)

        # Calculate confidence
        confidence = self._calculate_triple_top_confidence(data, peak1, peak2, peak3, neckline_price, sensitivity)

        if confidence < (0.4 + sensitivity * 0.3):
            return None

        # Calculate volume profile
        volume_profile = self._calculate_volume_profile(data, peak1.index, peak3.index)

        return DetectedPattern(
            pattern_type=PatternType.TRIPLE_TOP,
            category=PATTERN_CATEGORIES[PatternType.TRIPLE_TOP],
            confidence=confidence,
            start_time=data[peak1.index].timestamp,
            end_time=data[peak3.index].timestamp,
            start_index=peak1.index,
            end_index=peak3.index,
            key_levels={
                'peak1_price': peak1.value,
                'peak2_price': peak2.value,
                'peak3_price': peak3.value,
                'neckline_price': neckline_price,
                'target_price': neckline_price - (peak1.value - neckline_price)
            },
            volume_profile=volume_profile,
            description=f"Triple Top reversal pattern. Peaks at {peak1.value:.2f}, {peak2.value:.2f}, {peak3.value:.2f}. Confidence: {confidence:.1%}"
        )

    def _analyze_triple_bottom(self, data: PriceDataFrame, trough1: PeakTrough, trough2: PeakTrough,
                             trough3: PeakTrough, sensitivity: float) -> Optional[DetectedPattern]:
        """Analyze triple bottom pattern."""

        # Find peaks between troughs
        peak1_highs = data.get_highs()[trough1.index:trough2.index+1]
        peak2_highs = data.get_highs()[trough2.index:trough3.index+1]

        peak1_high = max(h for h in peak1_highs if h is not None)
        peak2_high = max(h for h in peak2_highs if h is not None)

        # Use the lower of the two peaks as neckline
        neckline_price = min(peak1_high, peak2_high)

        # Calculate confidence
        confidence = self._calculate_triple_bottom_confidence(data, trough1, trough2, trough3, neckline_price, sensitivity)

        if confidence < (0.4 + sensitivity * 0.3):
            return None

        # Calculate volume profile
        volume_profile = self._calculate_volume_profile(data, trough1.index, trough3.index)

        return DetectedPattern(
            pattern_type=PatternType.TRIPLE_BOTTOM,
            category=PATTERN_CATEGORIES[PatternType.TRIPLE_BOTTOM],
            confidence=confidence,
            start_time=data[trough1.index].timestamp,
            end_time=data[trough3.index].timestamp,
            start_index=trough1.index,
            end_index=trough3.index,
            key_levels={
                'trough1_price': trough1.value,
                'trough2_price': trough2.value,
                'trough3_price': trough3.value,
                'neckline_price': neckline_price,
                'target_price': neckline_price + (neckline_price - trough1.value)
            },
            volume_profile=volume_profile,
            description=f"Triple Bottom reversal pattern. Troughs at {trough1.value:.2f}, {trough2.value:.2f}, {trough3.value:.2f}. Confidence: {confidence:.1%}"
        )

    def _validate_double_top(self, peak1: PeakTrough, peak2: PeakTrough,
                           valley_low: float, valley_index: int) -> bool:
        """
        Validate double top pattern meets structural requirements.

        Validation checks:
        - Valley must be at least 10% below peaks (minimum retracement)
        - Valley must be positioned between 20-80% of pattern duration (not at edges)

        Args:
            peak1: First peak
            peak2: Second peak
            valley_low: Lowest price in valley
            valley_index: Index of valley low

        Returns:
            True if pattern is valid, False otherwise
        """

        # Valley should be significantly lower than peaks
        min_retracement = 0.1  # 10% minimum retracement
        peak_avg = (peak1.value + peak2.value) / 2

        if (peak_avg - valley_low) / peak_avg < min_retracement:
            return False

        # Valley should be roughly in the middle
        total_time = peak2.index - peak1.index
        valley_time = valley_index - peak1.index

        if valley_time < total_time * 0.2 or valley_time > total_time * 0.8:
            return False

        return True

    def _validate_double_bottom(self, trough1: PeakTrough, trough2: PeakTrough,
                              peak_high: float, peak_index: int) -> bool:
        """Validate double bottom pattern characteristics."""

        # Peak should be significantly higher than troughs
        min_retracement = 0.1  # 10% minimum retracement
        trough_avg = (trough1.value + trough2.value) / 2

        if (peak_high - trough_avg) / trough_avg < min_retracement:
            return False

        # Peak should be roughly in the middle
        total_time = trough2.index - trough1.index
        peak_time = peak_index - trough1.index

        if peak_time < total_time * 0.2 or peak_time > total_time * 0.8:
            return False

        return True

    def _calculate_double_top_confidence(self, data: PriceDataFrame, peak1: PeakTrough, peak2: PeakTrough,
                                       valley_low: float, sensitivity: float) -> float:
        """
        Calculate confidence score for double top pattern.

        Confidence Factors (weighted):
        1. Peak Similarity (30%): How closely the two peaks align in price
        2. Valley Depth (30%): Depth of retracement (normalized to 20%)
        3. Volume Confirmation (20%): Volume pattern supporting reversal
        4. Time Spacing (20%): Appropriateness of pattern duration

        The base confidence is then adjusted by sensitivity parameter (±20%).

        Args:
            data: Price data frame
            peak1: First peak
            peak2: Second peak
            valley_low: Valley price
            sensitivity: Detection sensitivity (0.0-1.0)

        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence_factors = []

        # 1. Peak similarity
        peak_similarity = 1.0 - abs(peak1.value - peak2.value) / max(peak1.value, peak2.value)
        confidence_factors.append(peak_similarity * 0.3)

        # 2. Valley depth
        peak_avg = (peak1.value + peak2.value) / 2
        valley_depth = (peak_avg - valley_low) / peak_avg
        depth_score = min(1.0, valley_depth / 0.2)  # Normalize to 20% depth
        confidence_factors.append(depth_score * 0.3)

        # 3. Volume confirmation
        volumes = data.get_volumes()
        volume_score = self._analyze_reversal_volume_pattern(volumes, peak1.index, peak2.index)
        confidence_factors.append(volume_score * 0.2)

        # 4. Time spacing
        time_spacing = peak2.index - peak1.index
        spacing_score = self._score_pattern_length(time_spacing)
        confidence_factors.append(spacing_score * 0.2)

        base_confidence = sum(confidence_factors)

        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        final_confidence = max(0.0, min(1.0, base_confidence + sensitivity_adjustment))

        return final_confidence

    def _calculate_double_bottom_confidence(self, data: PriceDataFrame, trough1: PeakTrough, trough2: PeakTrough,
                                          peak_high: float, sensitivity: float) -> float:
        """Calculate confidence for double bottom pattern."""
        confidence_factors = []

        # 1. Trough similarity
        trough_similarity = 1.0 - abs(trough1.value - trough2.value) / max(trough1.value, trough2.value)
        confidence_factors.append(trough_similarity * 0.3)

        # 2. Peak height
        trough_avg = (trough1.value + trough2.value) / 2
        peak_height = (peak_high - trough_avg) / trough_avg
        height_score = min(1.0, peak_height / 0.2)  # Normalize to 20% height
        confidence_factors.append(height_score * 0.3)

        # 3. Volume confirmation
        volumes = data.get_volumes()
        volume_score = self._analyze_reversal_volume_pattern(volumes, trough1.index, trough2.index)
        confidence_factors.append(volume_score * 0.2)

        # 4. Time spacing
        time_spacing = trough2.index - trough1.index
        spacing_score = self._score_pattern_length(time_spacing)
        confidence_factors.append(spacing_score * 0.2)

        base_confidence = sum(confidence_factors)

        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        final_confidence = max(0.0, min(1.0, base_confidence + sensitivity_adjustment))

        return final_confidence

    def _calculate_triple_top_confidence(self, data: PriceDataFrame, peak1: PeakTrough, peak2: PeakTrough,
                                       peak3: PeakTrough, neckline_price: float, sensitivity: float) -> float:
        """Calculate confidence for triple top pattern."""
        confidence_factors = []

        # 1. Peak similarity
        peaks = [peak1.value, peak2.value, peak3.value]
        peak_avg = sum(peaks) / 3
        peak_variance = sum((p - peak_avg) ** 2 for p in peaks) / 3
        peak_similarity = max(0.0, 1.0 - (peak_variance / (peak_avg ** 2)))
        confidence_factors.append(peak_similarity * 0.4)

        # 2. Neckline retracement
        retracement = (peak_avg - neckline_price) / peak_avg
        retracement_score = min(1.0, retracement / 0.15)  # Normalize to 15%
        confidence_factors.append(retracement_score * 0.3)

        # 3. Volume pattern
        volumes = data.get_volumes()
        volume_score = self._analyze_reversal_volume_pattern(volumes, peak1.index, peak3.index)
        confidence_factors.append(volume_score * 0.2)

        # 4. Pattern duration
        pattern_length = peak3.index - peak1.index
        length_score = self._score_pattern_length(pattern_length)
        confidence_factors.append(length_score * 0.1)

        base_confidence = sum(confidence_factors)

        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        final_confidence = max(0.0, min(1.0, base_confidence + sensitivity_adjustment))

        return final_confidence

    def _calculate_triple_bottom_confidence(self, data: PriceDataFrame, trough1: PeakTrough, trough2: PeakTrough,
                                          trough3: PeakTrough, neckline_price: float, sensitivity: float) -> float:
        """Calculate confidence for triple bottom pattern."""
        confidence_factors = []

        # 1. Trough similarity
        troughs = [trough1.value, trough2.value, trough3.value]
        trough_avg = sum(troughs) / 3
        trough_variance = sum((t - trough_avg) ** 2 for t in troughs) / 3
        trough_similarity = max(0.0, 1.0 - (trough_variance / (trough_avg ** 2)))
        confidence_factors.append(trough_similarity * 0.4)

        # 2. Neckline bounce
        bounce = (neckline_price - trough_avg) / trough_avg
        bounce_score = min(1.0, bounce / 0.15)  # Normalize to 15%
        confidence_factors.append(bounce_score * 0.3)

        # 3. Volume pattern
        volumes = data.get_volumes()
        volume_score = self._analyze_reversal_volume_pattern(volumes, trough1.index, trough3.index)
        confidence_factors.append(volume_score * 0.2)

        # 4. Pattern duration
        pattern_length = trough3.index - trough1.index
        length_score = self._score_pattern_length(pattern_length)
        confidence_factors.append(length_score * 0.1)

        base_confidence = sum(confidence_factors)

        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        final_confidence = max(0.0, min(1.0, base_confidence + sensitivity_adjustment))

        return final_confidence

    def _analyze_reversal_volume_pattern(self, volumes: List[float], start_idx: int, end_idx: int) -> float:
        """
        Analyze volume pattern for reversal confirmation.

        For reversal patterns, increasing volume towards the end of the pattern
        indicates stronger conviction and higher probability of reversal.

        Compares average volume in first third vs last third of pattern.

        Args:
            volumes: List of volume values
            start_idx: Pattern start index
            end_idx: Pattern end index

        Returns:
            Volume score between 0.0 and 1.0 (0.5 if insufficient data)
        """
        if end_idx >= len(volumes) or start_idx >= end_idx:
            return 0.5

        pattern_volumes = volumes[start_idx:end_idx+1]
        valid_volumes = [v for v in pattern_volumes if v is not None and v > 0]

        if len(valid_volumes) < 3:
            return 0.5

        # For reversals, volume should increase towards the end (confirmation)
        first_third = valid_volumes[:len(valid_volumes)//3]
        last_third = valid_volumes[-len(valid_volumes)//3:]

        if not first_third or not last_third:
            return 0.5

        avg_early = sum(first_third) / len(first_third)
        avg_late = sum(last_third) / len(last_third)

        if avg_early > 0:
            volume_change = (avg_late - avg_early) / avg_early
            # Positive volume change is good for reversals
            volume_score = max(0.0, min(1.0, (volume_change + 0.5)))
        else:
            volume_score = 0.5

        return volume_score

    def _score_pattern_length(self, pattern_length: int) -> float:
        """
        Score pattern length appropriateness.

        Patterns that are too short may be noise, while patterns that are too long
        may be less reliable. Ideal range is 10-60 periods.

        Args:
            pattern_length: Number of periods in pattern

        Returns:
            Score between 0.3 and 1.0
        """
        ideal_min = 10
        ideal_max = 60

        if ideal_min <= pattern_length <= ideal_max:
            return 1.0
        elif pattern_length < ideal_min:
            return pattern_length / ideal_min
        else:  # pattern_length > ideal_max
            return max(0.3, ideal_max / pattern_length)

    def _calculate_volume_profile(self, data: PriceDataFrame,
                                start_index: int, end_index: int) -> VolumeProfile:
        """
        Calculate volume profile for the pattern period.

        Analyzes volume characteristics including:
        - Average volume during pattern
        - Volume trend (increasing/decreasing/stable)
        - Volume confirmation (increasing volume supports reversal)

        Args:
            data: Price data frame
            start_index: Pattern start index
            end_index: Pattern end index

        Returns:
            VolumeProfile with volume analysis
        """
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

        # Volume confirmation (increasing volume is good for reversals)
        volume_confirmation = volume_trend == "increasing"

        return VolumeProfile(
            avg_volume=avg_volume,
            volume_trend=volume_trend,
            volume_confirmation=volume_confirmation
        )



    def detect_head_and_shoulders_patterns(self, data: PriceDataFrame,
                                         sensitivity: float = 0.5) -> List[DetectedPattern]:
        """
        Detect head and shoulders and inverse head and shoulders patterns.

        Head and Shoulders (Bearish):
        - Three peaks: left shoulder, head (highest), right shoulder
        - Shoulders at similar heights
        - Head significantly higher than shoulders
        - Neckline connects valleys between peaks

        Inverse Head and Shoulders (Bullish):
        - Three troughs: left shoulder, head (lowest), right shoulder
        - Shoulders at similar depths
        - Head significantly lower than shoulders
        - Neckline connects peaks between troughs

        Args:
            data: Price data frame containing OHLCV data
            sensitivity: Detection sensitivity (0.0 to 1.0)

        Returns:
            List of detected head and shoulders patterns
        """
        if len(data) < self.min_pattern_length:
            return []

        patterns = []
        highs = data.get_highs()
        lows = data.get_lows()

        # Find peaks for head and shoulders
        high_peaks = [pt for pt in self.trend_analysis.find_peaks_and_troughs(highs, min_distance=4)
                     if pt.type == 'peak']

        # Find troughs for inverse head and shoulders
        low_troughs = [pt for pt in self.trend_analysis.find_peaks_and_troughs(lows, min_distance=4)
                      if pt.type == 'trough']

        # Detect head and shoulders (bearish reversal)
        if len(high_peaks) >= 3:
            hs_patterns = self._find_head_and_shoulders(data, high_peaks, sensitivity)
            patterns.extend(hs_patterns)

        # Detect inverse head and shoulders (bullish reversal)
        if len(low_troughs) >= 3:
            ihs_patterns = self._find_inverse_head_and_shoulders(data, low_troughs, sensitivity)
            patterns.extend(ihs_patterns)

        return self._filter_overlapping_patterns(patterns)

    def _find_head_and_shoulders(self, data: PriceDataFrame, peaks: List[PeakTrough],
                               sensitivity: float) -> List[DetectedPattern]:
        """
        Find head and shoulders patterns in peak data.

        Searches for three consecutive peaks where the middle peak is the highest
        and the two shoulders are at similar levels.

        Args:
            data: Price data frame
            peaks: List of identified peaks
            sensitivity: Detection sensitivity

        Returns:
            List of detected head and shoulders patterns
        """
        patterns = []

        # Look for three consecutive peaks where middle is highest
        for i in range(len(peaks) - 2):
            left_shoulder = peaks[i]
            head = peaks[i + 1]
            right_shoulder = peaks[i + 2]

            # Validate head and shoulders structure
            if self._validate_head_and_shoulders_structure(left_shoulder, head, right_shoulder):
                hs_pattern = self._analyze_head_and_shoulders(
                    data, left_shoulder, head, right_shoulder, sensitivity
                )
                if hs_pattern:
                    patterns.append(hs_pattern)

        return patterns

    def _find_inverse_head_and_shoulders(self, data: PriceDataFrame, troughs: List[PeakTrough],
                                       sensitivity: float) -> List[DetectedPattern]:
        """Find inverse head and shoulders patterns in troughs."""
        patterns = []

        # Look for three consecutive troughs where middle is lowest
        for i in range(len(troughs) - 2):
            left_shoulder = troughs[i]
            head = troughs[i + 1]
            right_shoulder = troughs[i + 2]

            # Validate inverse head and shoulders structure
            if self._validate_inverse_head_and_shoulders_structure(left_shoulder, head, right_shoulder):
                ihs_pattern = self._analyze_inverse_head_and_shoulders(
                    data, left_shoulder, head, right_shoulder, sensitivity
                )
                if ihs_pattern:
                    patterns.append(ihs_pattern)

        return patterns

    def _validate_head_and_shoulders_structure(self, left_shoulder: PeakTrough,
                                             head: PeakTrough, right_shoulder: PeakTrough) -> bool:
        """
        Validate head and shoulders pattern meets structural requirements.

        Validation checks:
        - Head must be higher than both shoulders
        - Shoulders must be similar in height (within 5%)
        - Head must be at least 3% higher than shoulders
        - Head must be positioned between 20-80% of pattern duration

        Args:
            left_shoulder: Left shoulder peak
            head: Head peak (should be highest)
            right_shoulder: Right shoulder peak

        Returns:
            True if structure is valid, False otherwise
        """

        # Head should be higher than both shoulders
        if head.value <= left_shoulder.value or head.value <= right_shoulder.value:
            return False

        # Shoulders should be roughly similar in height (within 5%)
        shoulder_diff = abs(left_shoulder.value - right_shoulder.value)
        avg_shoulder = (left_shoulder.value + right_shoulder.value) / 2

        if avg_shoulder > 0 and shoulder_diff / avg_shoulder > 0.05:
            return False

        # Head should be significantly higher than shoulders (at least 3%)
        min_head_prominence = 0.03
        head_prominence = (head.value - avg_shoulder) / avg_shoulder

        if head_prominence < min_head_prominence:
            return False

        # Time spacing should be reasonable
        total_time = right_shoulder.index - left_shoulder.index
        head_time = head.index - left_shoulder.index

        # Head should be roughly in the middle (20% to 80% of total time)
        if head_time < total_time * 0.2 or head_time > total_time * 0.8:
            return False

        return True

    def _validate_inverse_head_and_shoulders_structure(self, left_shoulder: PeakTrough,
                                                     head: PeakTrough, right_shoulder: PeakTrough) -> bool:
        """Validate inverse head and shoulders pattern structure."""

        # Head should be lower than both shoulders
        if head.value >= left_shoulder.value or head.value >= right_shoulder.value:
            return False

        # Shoulders should be roughly similar in depth (within 5%)
        shoulder_diff = abs(left_shoulder.value - right_shoulder.value)
        avg_shoulder = (left_shoulder.value + right_shoulder.value) / 2

        if avg_shoulder > 0 and shoulder_diff / avg_shoulder > 0.05:
            return False

        # Head should be significantly lower than shoulders (at least 3%)
        min_head_prominence = 0.03
        head_prominence = (avg_shoulder - head.value) / avg_shoulder

        if head_prominence < min_head_prominence:
            return False

        # Time spacing should be reasonable
        total_time = right_shoulder.index - left_shoulder.index
        head_time = head.index - left_shoulder.index

        # Head should be roughly in the middle (20% to 80% of total time)
        if head_time < total_time * 0.2 or head_time > total_time * 0.8:
            return False

        return True

    def _analyze_head_and_shoulders(self, data: PriceDataFrame, left_shoulder: PeakTrough,
                                  head: PeakTrough, right_shoulder: PeakTrough,
                                  sensitivity: float) -> Optional[DetectedPattern]:
        """
        Analyze and validate head and shoulders pattern.

        Calculates neckline by connecting valleys between peaks, computes confidence
        based on pattern characteristics, and determines price target using measured move.

        Measured Move Target: neckline - (head - neckline)

        Args:
            data: Price data frame
            left_shoulder: Left shoulder peak
            head: Head peak
            right_shoulder: Right shoulder peak
            sensitivity: Detection sensitivity

        Returns:
            DetectedPattern if valid, None otherwise
        """

        # Find neckline (connect the valleys between shoulders and head)
        left_valley_start = left_shoulder.index
        left_valley_end = head.index
        right_valley_start = head.index
        right_valley_end = right_shoulder.index

        # Find valley lows
        left_valley_lows = data.get_lows()[left_valley_start:left_valley_end+1]
        right_valley_lows = data.get_lows()[right_valley_start:right_valley_end+1]

        left_valley_low = min(l for l in left_valley_lows if l is not None)
        right_valley_low = min(l for l in right_valley_lows if l is not None)

        # Neckline is the line connecting the two valleys
        neckline_price = (left_valley_low + right_valley_low) / 2

        # Calculate confidence
        confidence = self._calculate_head_shoulders_confidence(
            data, left_shoulder, head, right_shoulder, neckline_price, sensitivity
        )

        if confidence < (0.4 + sensitivity * 0.3):
            return None

        # Calculate volume profile
        volume_profile = self._calculate_volume_profile(data, left_shoulder.index, right_shoulder.index)

        # Calculate target price (measured move)
        head_to_neckline = head.value - neckline_price
        target_price = neckline_price - head_to_neckline

        return DetectedPattern(
            pattern_type=PatternType.HEAD_SHOULDERS,
            category=PATTERN_CATEGORIES[PatternType.HEAD_SHOULDERS],
            confidence=confidence,
            start_time=data[left_shoulder.index].timestamp,
            end_time=data[right_shoulder.index].timestamp,
            start_index=left_shoulder.index,
            end_index=right_shoulder.index,
            key_levels={
                'left_shoulder_price': left_shoulder.value,
                'head_price': head.value,
                'right_shoulder_price': right_shoulder.value,
                'neckline_price': neckline_price,
                'target_price': target_price,
                'left_valley_low': left_valley_low,
                'right_valley_low': right_valley_low
            },
            volume_profile=volume_profile,
            description=f"Head and Shoulders reversal pattern. Head at {head.value:.2f}, neckline at {neckline_price:.2f}, target {target_price:.2f}. Confidence: {confidence:.1%}"
        )

    def _analyze_inverse_head_and_shoulders(self, data: PriceDataFrame, left_shoulder: PeakTrough,
                                          head: PeakTrough, right_shoulder: PeakTrough,
                                          sensitivity: float) -> Optional[DetectedPattern]:
        """Analyze inverse head and shoulders pattern."""

        # Find neckline (connect the peaks between shoulders and head)
        left_peak_start = left_shoulder.index
        left_peak_end = head.index
        right_peak_start = head.index
        right_peak_end = right_shoulder.index

        # Find peak highs
        left_peak_highs = data.get_highs()[left_peak_start:left_peak_end+1]
        right_peak_highs = data.get_highs()[right_peak_start:right_peak_end+1]

        left_peak_high = max(h for h in left_peak_highs if h is not None)
        right_peak_high = max(h for h in right_peak_highs if h is not None)

        # Neckline is the line connecting the two peaks
        neckline_price = (left_peak_high + right_peak_high) / 2

        # Calculate confidence
        confidence = self._calculate_inverse_head_shoulders_confidence(
            data, left_shoulder, head, right_shoulder, neckline_price, sensitivity
        )

        if confidence < (0.4 + sensitivity * 0.3):
            return None

        # Calculate volume profile
        volume_profile = self._calculate_volume_profile(data, left_shoulder.index, right_shoulder.index)

        # Calculate target price (measured move)
        neckline_to_head = neckline_price - head.value
        target_price = neckline_price + neckline_to_head

        return DetectedPattern(
            pattern_type=PatternType.INVERSE_HEAD_SHOULDERS,
            category=PATTERN_CATEGORIES[PatternType.INVERSE_HEAD_SHOULDERS],
            confidence=confidence,
            start_time=data[left_shoulder.index].timestamp,
            end_time=data[right_shoulder.index].timestamp,
            start_index=left_shoulder.index,
            end_index=right_shoulder.index,
            key_levels={
                'left_shoulder_price': left_shoulder.value,
                'head_price': head.value,
                'right_shoulder_price': right_shoulder.value,
                'neckline_price': neckline_price,
                'target_price': target_price,
                'left_peak_high': left_peak_high,
                'right_peak_high': right_peak_high
            },
            volume_profile=volume_profile,
            description=f"Inverse Head and Shoulders reversal pattern. Head at {head.value:.2f}, neckline at {neckline_price:.2f}, target {target_price:.2f}. Confidence: {confidence:.1%}"
        )

    def _calculate_head_shoulders_confidence(self, data: PriceDataFrame, left_shoulder: PeakTrough,
                                           head: PeakTrough, right_shoulder: PeakTrough,
                                           neckline_price: float, sensitivity: float) -> float:
        """
        Calculate confidence score for head and shoulders pattern.

        Confidence Factors (weighted):
        1. Shoulder Symmetry (25%): How similar the shoulders are in height
        2. Head Prominence (25%): How much the head stands out (normalized to 10%)
        3. Neckline Break (20%): Current price position relative to neckline
        4. Volume Pattern (15%): Increasing volume on right shoulder
        5. Time Symmetry (15%): Balance between left and right sides

        The base confidence is then adjusted by sensitivity parameter (±20%).

        Args:
            data: Price data frame
            left_shoulder: Left shoulder peak
            head: Head peak
            right_shoulder: Right shoulder peak
            neckline_price: Calculated neckline price
            sensitivity: Detection sensitivity (0.0-1.0)

        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence_factors = []

        # 1. Shoulder symmetry
        shoulder_diff = abs(left_shoulder.value - right_shoulder.value)
        avg_shoulder = (left_shoulder.value + right_shoulder.value) / 2

        if avg_shoulder > 0:
            shoulder_symmetry = 1.0 - (shoulder_diff / avg_shoulder)
            confidence_factors.append(max(0.0, shoulder_symmetry) * 0.25)
        else:
            confidence_factors.append(0.0)

        # 2. Head prominence
        head_prominence = (head.value - avg_shoulder) / avg_shoulder if avg_shoulder > 0 else 0
        prominence_score = min(1.0, head_prominence / 0.1)  # Normalize to 10% prominence
        confidence_factors.append(prominence_score * 0.25)

        # 3. Neckline break potential
        current_price = data.get_closes()[-1]
        if current_price < neckline_price:  # Price below neckline is bearish confirmation
            neckline_score = 1.0
        else:
            # Score based on how close price is to neckline
            distance_to_neckline = abs(current_price - neckline_price) / neckline_price
            neckline_score = max(0.0, 1.0 - distance_to_neckline * 5)  # Penalize distance

        confidence_factors.append(neckline_score * 0.2)

        # 4. Volume pattern (should increase on right shoulder)
        volumes = data.get_volumes()
        volume_score = self._analyze_head_shoulders_volume_pattern(
            volumes, left_shoulder.index, head.index, right_shoulder.index
        )
        confidence_factors.append(volume_score * 0.15)

        # 5. Time symmetry
        left_time = head.index - left_shoulder.index
        right_time = right_shoulder.index - head.index

        if max(left_time, right_time) > 0:
            time_symmetry = min(left_time, right_time) / max(left_time, right_time)
            confidence_factors.append(time_symmetry * 0.15)
        else:
            confidence_factors.append(0.0)

        base_confidence = sum(confidence_factors)

        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        final_confidence = max(0.0, min(1.0, base_confidence + sensitivity_adjustment))

        return final_confidence

    def _calculate_inverse_head_shoulders_confidence(self, data: PriceDataFrame, left_shoulder: PeakTrough,
                                                   head: PeakTrough, right_shoulder: PeakTrough,
                                                   neckline_price: float, sensitivity: float) -> float:
        """Calculate confidence for inverse head and shoulders pattern."""
        confidence_factors = []

        # 1. Shoulder symmetry
        shoulder_diff = abs(left_shoulder.value - right_shoulder.value)
        avg_shoulder = (left_shoulder.value + right_shoulder.value) / 2

        if avg_shoulder > 0:
            shoulder_symmetry = 1.0 - (shoulder_diff / avg_shoulder)
            confidence_factors.append(max(0.0, shoulder_symmetry) * 0.25)
        else:
            confidence_factors.append(0.0)

        # 2. Head prominence (depth)
        head_prominence = (avg_shoulder - head.value) / avg_shoulder if avg_shoulder > 0 else 0
        prominence_score = min(1.0, head_prominence / 0.1)  # Normalize to 10% prominence
        confidence_factors.append(prominence_score * 0.25)

        # 3. Neckline break potential
        current_price = data.get_closes()[-1]
        if current_price > neckline_price:  # Price above neckline is bullish confirmation
            neckline_score = 1.0
        else:
            # Score based on how close price is to neckline
            distance_to_neckline = abs(current_price - neckline_price) / neckline_price
            neckline_score = max(0.0, 1.0 - distance_to_neckline * 5)  # Penalize distance

        confidence_factors.append(neckline_score * 0.2)

        # 4. Volume pattern (should increase on right shoulder)
        volumes = data.get_volumes()
        volume_score = self._analyze_head_shoulders_volume_pattern(
            volumes, left_shoulder.index, head.index, right_shoulder.index
        )
        confidence_factors.append(volume_score * 0.15)

        # 5. Time symmetry
        left_time = head.index - left_shoulder.index
        right_time = right_shoulder.index - head.index

        if max(left_time, right_time) > 0:
            time_symmetry = min(left_time, right_time) / max(left_time, right_time)
            confidence_factors.append(time_symmetry * 0.15)
        else:
            confidence_factors.append(0.0)

        base_confidence = sum(confidence_factors)

        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        final_confidence = max(0.0, min(1.0, base_confidence + sensitivity_adjustment))

        return final_confidence

    def _analyze_head_shoulders_volume_pattern(self, volumes: List[float],
                                             left_shoulder_idx: int, head_idx: int,
                                             right_shoulder_idx: int) -> float:
        """
        Analyze volume pattern for head and shoulders confirmation.

        Ideal volume pattern for head and shoulders:
        - High volume on left shoulder (initial selling)
        - Lower volume on head (weakening buying pressure)
        - High volume on right shoulder (renewed selling pressure)

        This pattern indicates increasing selling conviction and higher reversal probability.

        Args:
            volumes: List of volume values
            left_shoulder_idx: Index of left shoulder
            head_idx: Index of head
            right_shoulder_idx: Index of right shoulder

        Returns:
            Volume score between 0.0 and 1.0 (0.5 if insufficient data)
        """
        if right_shoulder_idx >= len(volumes):
            return 0.5

        try:
            # Get volume at each key point
            left_shoulder_vol = volumes[left_shoulder_idx] if volumes[left_shoulder_idx] is not None else 0
            head_vol = volumes[head_idx] if volumes[head_idx] is not None else 0
            right_shoulder_vol = volumes[right_shoulder_idx] if volumes[right_shoulder_idx] is not None else 0

            if left_shoulder_vol == 0 or head_vol == 0 or right_shoulder_vol == 0:
                return 0.5

            # Ideal volume pattern: high on left shoulder, lower on head, high on right shoulder
            # This indicates selling pressure increasing

            # Score based on volume relationships
            score = 0.0

            # Left shoulder should have decent volume
            if left_shoulder_vol > 0:
                score += 0.3

            # Head volume should be lower than left shoulder (weakening buying)
            if head_vol < left_shoulder_vol:
                score += 0.3

            # Right shoulder volume should be higher than head (selling pressure)
            if right_shoulder_vol > head_vol:
                score += 0.4

            return min(1.0, score)

        except (IndexError, TypeError):
            return 0.5
