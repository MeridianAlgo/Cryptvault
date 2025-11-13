"""Advanced pattern detection algorithms for complex geometric patterns."""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from ..data.models import PriceDataFrame
from ..indicators.trend_analysis import TrendAnalysis, PeakTrough
from .types import PatternType, PatternCategory, DetectedPattern, VolumeProfile, PATTERN_CATEGORIES


class AdvancedPatternAnalyzer:
    """Analyze advanced chart patterns like diamonds, expanding triangles, and complex formations."""

    def __init__(self):
        """Initialize advanced pattern analyzer."""
        self.trend_analysis = TrendAnalysis()
        self.min_pattern_length = 20
        self.max_pattern_length = 120

    def detect_diamond_patterns(self, data: PriceDataFrame,
                              sensitivity: float = 0.5) -> List[DetectedPattern]:
        """
        Detect diamond patterns (expanding then contracting formations).

        Args:
            data: Price data frame
            sensitivity: Detection sensitivity (0.0 to 1.0)

        Returns:
            List of detected diamond patterns
        """
        if len(data) < self.min_pattern_length:
            return []

        patterns = []
        highs = data.get_highs()
        lows = data.get_lows()

        # Find peaks and troughs for diamond analysis
        high_peaks = [pt for pt in self.trend_analysis.find_peaks_and_troughs(highs, min_distance=3)
                     if pt.type == 'peak']
        low_troughs = [pt for pt in self.trend_analysis.find_peaks_and_troughs(lows, min_distance=3)
                      if pt.type == 'trough']

        if len(high_peaks) < 4 or len(low_troughs) < 4:
            return patterns

        # Look for diamond formations
        diamond_candidates = self._find_diamond_candidates(high_peaks, low_troughs)

        for candidate in diamond_candidates:
            diamond_pattern = self._analyze_diamond_formation(data, candidate, sensitivity)
            if diamond_pattern:
                patterns.append(diamond_pattern)

        return self._filter_overlapping_patterns(patterns)

    def detect_expanding_triangle_patterns(self, data: PriceDataFrame,
                                         sensitivity: float = 0.5) -> List[DetectedPattern]:
        """
        Detect expanding triangle (broadening formation) patterns.

        Args:
            data: Price data frame
            sensitivity: Detection sensitivity (0.0 to 1.0)

        Returns:
            List of detected expanding triangle patterns
        """
        if len(data) < self.min_pattern_length:
            return []

        patterns = []
        highs = data.get_highs()
        lows = data.get_lows()

        # Find peaks and troughs
        high_peaks = [pt for pt in self.trend_analysis.find_peaks_and_troughs(highs, min_distance=4)
                     if pt.type == 'peak']
        low_troughs = [pt for pt in self.trend_analysis.find_peaks_and_troughs(lows, min_distance=4)
                      if pt.type == 'trough']

        if len(high_peaks) < 3 or len(low_troughs) < 3:
            return patterns

        # Look for expanding formations
        expanding_candidates = self._find_expanding_triangle_candidates(high_peaks, low_troughs)

        for candidate in expanding_candidates:
            expanding_pattern = self._analyze_expanding_triangle(data, candidate, sensitivity)
            if expanding_pattern:
                patterns.append(expanding_pattern)

        return self._filter_overlapping_patterns(patterns)

    def _find_diamond_candidates(self, high_peaks: List[PeakTrough],
                               low_troughs: List[PeakTrough]) -> List[Dict]:
        """Find potential diamond formations."""
        candidates = []

        # Diamond pattern: expanding then contracting
        # Need at least 4 peaks and 4 troughs
        for i in range(len(high_peaks) - 3):
            for j in range(i + 3, min(i + 8, len(high_peaks))):  # Limit search range
                peak_group = high_peaks[i:j+1]

                # Find corresponding troughs in the same time range
                start_time = peak_group[0].index
                end_time = peak_group[-1].index

                relevant_troughs = [t for t in low_troughs
                                  if start_time <= t.index <= end_time]

                if len(relevant_troughs) < 4:
                    continue

                # Check if this forms a diamond pattern
                diamond_data = self._analyze_diamond_structure(peak_group, relevant_troughs)

                if diamond_data['is_diamond']:
                    candidates.append({
                        'peaks': peak_group,
                        'troughs': relevant_troughs,
                        'start_index': start_time,
                        'end_index': end_time,
                        'expansion_score': diamond_data['expansion_score'],
                        'contraction_score': diamond_data['contraction_score']
                    })

        return candidates

    def _analyze_diamond_structure(self, peaks: List[PeakTrough],
                                 troughs: List[PeakTrough]) -> Dict:
        """Analyze if peaks and troughs form a diamond structure."""

        if len(peaks) < 4 or len(troughs) < 4:
            return {'is_diamond': False}

        # Sort by time
        all_points = sorted(peaks + troughs, key=lambda x: x.index)

        if len(all_points) < 8:
            return {'is_diamond': False}

        # Diamond should have expanding then contracting price range
        # Calculate range at different points in time
        quarter_points = len(all_points) // 4

        # Early range (first quarter)
        early_points = all_points[:quarter_points*2]
        early_highs = [p.value for p in early_points if p in peaks]
        early_lows = [p.value for p in early_points if p in troughs]

        if not early_highs or not early_lows:
            return {'is_diamond': False}

        early_range = max(early_highs) - min(early_lows)

        # Middle range (second and third quarters)
        middle_points = all_points[quarter_points:quarter_points*3]
        middle_highs = [p.value for p in middle_points if p in peaks]
        middle_lows = [p.value for p in middle_points if p in troughs]

        if not middle_highs or not middle_lows:
            return {'is_diamond': False}

        middle_range = max(middle_highs) - min(middle_lows)

        # Late range (last quarter)
        late_points = all_points[quarter_points*3:]
        late_highs = [p.value for p in late_points if p in peaks]
        late_lows = [p.value for p in late_points if p in troughs]

        if not late_highs or not late_lows:
            return {'is_diamond': False}

        late_range = max(late_highs) - min(late_lows)

        # Check for expansion then contraction
        expansion_score = 0.0
        contraction_score = 0.0

        # Range should expand from early to middle
        if middle_range > early_range * 1.2:  # At least 20% expansion
            expansion_score = min(1.0, (middle_range / early_range - 1.0) / 0.5)  # Normalize

        # Range should contract from middle to late
        if late_range < middle_range * 0.8:  # At least 20% contraction
            contraction_score = min(1.0, (1.0 - late_range / middle_range) / 0.5)  # Normalize

        # Diamond requires both expansion and contraction
        is_diamond = expansion_score > 0.3 and contraction_score > 0.3

        return {
            'is_diamond': is_diamond,
            'expansion_score': expansion_score,
            'contraction_score': contraction_score,
            'early_range': early_range,
            'middle_range': middle_range,
            'late_range': late_range
        }

    def _analyze_diamond_formation(self, data: PriceDataFrame, candidate: Dict,
                                 sensitivity: float) -> Optional[DetectedPattern]:
        """Analyze diamond candidate and create pattern if valid."""

        start_idx = candidate['start_index']
        end_idx = candidate['end_index']
        pattern_length = end_idx - start_idx

        # Validate pattern length
        if pattern_length < self.min_pattern_length or pattern_length > self.max_pattern_length:
            return None

        # Calculate confidence
        confidence = self._calculate_diamond_confidence(data, candidate, sensitivity)

        if confidence < (0.4 + sensitivity * 0.3):
            return None

        # Calculate volume profile
        volume_profile = self._calculate_volume_profile(data, start_idx, end_idx)

        # Get price levels
        peaks = candidate['peaks']
        troughs = candidate['troughs']

        highest_peak = max(peaks, key=lambda x: x.value)
        lowest_trough = min(troughs, key=lambda x: x.value)

        return DetectedPattern(
            pattern_type=PatternType.DIAMOND,
            category=PATTERN_CATEGORIES[PatternType.DIAMOND],
            confidence=confidence,
            start_time=data[start_idx].timestamp,
            end_time=data[end_idx].timestamp,
            start_index=start_idx,
            end_index=end_idx,
            key_levels={
                'highest_peak': highest_peak.value,
                'lowest_trough': lowest_trough.value,
                'expansion_score': candidate['expansion_score'],
                'contraction_score': candidate['contraction_score'],
                'pattern_range': highest_peak.value - lowest_trough.value
            },
            volume_profile=volume_profile,
            description=f"Diamond pattern with expanding then contracting price action. Range: {highest_peak.value - lowest_trough.value:.2f}. Confidence: {confidence:.1%}"
        )

    def _find_expanding_triangle_candidates(self, high_peaks: List[PeakTrough],
                                          low_troughs: List[PeakTrough]) -> List[Dict]:
        """Find potential expanding triangle formations."""
        candidates = []

        # Look for diverging trend lines
        for i in range(len(high_peaks) - 2):
            for j in range(i + 2, min(i + 6, len(high_peaks))):
                peak1, peak2 = high_peaks[i], high_peaks[j]

                # Find troughs in the same time range
                relevant_troughs = [t for t in low_troughs
                                  if peak1.index <= t.index <= peak2.index]

                if len(relevant_troughs) < 2:
                    continue

                # Try different trough combinations
                for k in range(len(relevant_troughs) - 1):
                    for l in range(k + 1, len(relevant_troughs)):
                        trough1, trough2 = relevant_troughs[k], relevant_troughs[l]

                        # Check for expanding pattern
                        expanding_data = self._analyze_expanding_structure(
                            peak1, peak2, trough1, trough2
                        )

                        if expanding_data['is_expanding']:
                            candidates.append({
                                'peak1': peak1,
                                'peak2': peak2,
                                'trough1': trough1,
                                'trough2': trough2,
                                'start_index': min(peak1.index, trough1.index),
                                'end_index': max(peak2.index, trough2.index),
                                'divergence_score': expanding_data['divergence_score']
                            })

        return candidates

    def _analyze_expanding_structure(self, peak1: PeakTrough, peak2: PeakTrough,
                                   trough1: PeakTrough, trough2: PeakTrough) -> Dict:
        """Analyze if four points form an expanding triangle."""

        # Calculate slopes
        if peak2.index == peak1.index or trough2.index == trough1.index:
            return {'is_expanding': False}

        upper_slope = (peak2.value - peak1.value) / (peak2.index - peak1.index)
        lower_slope = (trough2.value - trough1.value) / (trough2.index - trough1.index)

        # For expanding triangle, upper line should be rising and lower line falling
        # OR both lines should be diverging from a central point

        is_expanding = False
        divergence_score = 0.0

        # Check for classic expanding triangle (upper rising, lower falling)
        if upper_slope > 0.001 and lower_slope < -0.001:
            # Lines are diverging
            divergence_score = min(abs(upper_slope), abs(lower_slope)) / max(abs(upper_slope), abs(lower_slope))
            is_expanding = divergence_score > 0.3

        # Check for expanding range over time
        if not is_expanding:
            # Calculate range at start and end
            start_time = min(peak1.index, trough1.index)
            end_time = max(peak2.index, trough2.index)

            # Approximate range expansion
            start_range = abs(peak1.value - trough1.value)
            end_range = abs(peak2.value - trough2.value)

            if start_range > 0 and end_range > start_range * 1.3:  # 30% expansion
                divergence_score = min(1.0, (end_range / start_range - 1.0) / 0.5)
                is_expanding = divergence_score > 0.4

        return {
            'is_expanding': is_expanding,
            'divergence_score': divergence_score,
            'upper_slope': upper_slope,
            'lower_slope': lower_slope
        }

    def _analyze_expanding_triangle(self, data: PriceDataFrame, candidate: Dict,
                                  sensitivity: float) -> Optional[DetectedPattern]:
        """Analyze expanding triangle candidate."""

        start_idx = candidate['start_index']
        end_idx = candidate['end_index']
        pattern_length = end_idx - start_idx

        # Validate pattern length
        if pattern_length < self.min_pattern_length or pattern_length > self.max_pattern_length:
            return None

        # Calculate confidence
        confidence = self._calculate_expanding_triangle_confidence(data, candidate, sensitivity)

        if confidence < (0.4 + sensitivity * 0.3):
            return None

        # Calculate volume profile
        volume_profile = self._calculate_volume_profile(data, start_idx, end_idx)

        peak1 = candidate['peak1']
        peak2 = candidate['peak2']
        trough1 = candidate['trough1']
        trough2 = candidate['trough2']

        return DetectedPattern(
            pattern_type=PatternType.EXPANDING_TRIANGLE,
            category=PATTERN_CATEGORIES[PatternType.EXPANDING_TRIANGLE],
            confidence=confidence,
            start_time=data[start_idx].timestamp,
            end_time=data[end_idx].timestamp,
            start_index=start_idx,
            end_index=end_idx,
            key_levels={
                'peak1_price': peak1.value,
                'peak2_price': peak2.value,
                'trough1_price': trough1.value,
                'trough2_price': trough2.value,
                'divergence_score': candidate['divergence_score'],
                'range_expansion': abs(peak2.value - trough2.value) - abs(peak1.value - trough1.value)
            },
            volume_profile=volume_profile,
            description=f"Expanding Triangle with diverging trend lines. Divergence score: {candidate['divergence_score']:.2f}. Confidence: {confidence:.1%}"
        )

    def _calculate_diamond_confidence(self, data: PriceDataFrame, candidate: Dict,
                                    sensitivity: float) -> float:
        """Calculate confidence for diamond pattern."""
        confidence_factors = []

        # 1. Expansion and contraction scores
        expansion_score = candidate['expansion_score']
        contraction_score = candidate['contraction_score']

        confidence_factors.append(expansion_score * 0.3)
        confidence_factors.append(contraction_score * 0.3)

        # 2. Symmetry of the diamond
        peaks = candidate['peaks']
        troughs = candidate['troughs']

        if len(peaks) >= 2 and len(troughs) >= 2:
            # Check time symmetry
            total_time = candidate['end_index'] - candidate['start_index']
            mid_time = candidate['start_index'] + total_time // 2

            # Count points before and after midpoint
            early_points = sum(1 for p in peaks + troughs if p.index < mid_time)
            late_points = sum(1 for p in peaks + troughs if p.index >= mid_time)

            if early_points + late_points > 0:
                time_symmetry = min(early_points, late_points) / max(early_points, late_points)
                confidence_factors.append(time_symmetry * 0.2)
            else:
                confidence_factors.append(0.0)
        else:
            confidence_factors.append(0.0)

        # 3. Volume pattern (should increase with expansion)
        volumes = data.get_volumes()[candidate['start_index']:candidate['end_index']+1]
        volume_score = self._analyze_diamond_volume_pattern(volumes)
        confidence_factors.append(volume_score * 0.1)

        # 4. Pattern length appropriateness
        pattern_length = candidate['end_index'] - candidate['start_index']
        length_score = self._score_pattern_length(pattern_length)
        confidence_factors.append(length_score * 0.1)

        base_confidence = sum(confidence_factors)

        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        final_confidence = max(0.0, min(1.0, base_confidence + sensitivity_adjustment))

        return final_confidence

    def _calculate_expanding_triangle_confidence(self, data: PriceDataFrame, candidate: Dict,
                                               sensitivity: float) -> float:
        """Calculate confidence for expanding triangle pattern."""
        confidence_factors = []

        # 1. Divergence quality
        divergence_score = candidate['divergence_score']
        confidence_factors.append(divergence_score * 0.4)

        # 2. Volume pattern (should increase with expansion)
        start_idx = candidate['start_index']
        end_idx = candidate['end_index']
        volumes = data.get_volumes()[start_idx:end_idx+1]
        volume_score = self._analyze_expanding_volume_pattern(volumes)
        confidence_factors.append(volume_score * 0.3)

        # 3. Pattern length
        pattern_length = end_idx - start_idx
        length_score = self._score_pattern_length(pattern_length)
        confidence_factors.append(length_score * 0.2)

        # 4. Range expansion consistency
        peak1 = candidate['peak1']
        peak2 = candidate['peak2']
        trough1 = candidate['trough1']
        trough2 = candidate['trough2']

        start_range = abs(peak1.value - trough1.value)
        end_range = abs(peak2.value - trough2.value)

        if start_range > 0:
            expansion_ratio = end_range / start_range
            expansion_consistency = min(1.0, max(0.0, (expansion_ratio - 1.0) / 0.5))
            confidence_factors.append(expansion_consistency * 0.1)
        else:
            confidence_factors.append(0.0)

        base_confidence = sum(confidence_factors)

        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        final_confidence = max(0.0, min(1.0, base_confidence + sensitivity_adjustment))

        return final_confidence

    def _analyze_diamond_volume_pattern(self, volumes: List[float]) -> float:
        """Analyze volume pattern for diamond (should increase with expansion)."""
        if len(volumes) < 6:
            return 0.5

        valid_volumes = [v for v in volumes if v is not None and v > 0]
        if len(valid_volumes) < 6:
            return 0.5

        # Volume should increase in middle (expansion phase)
        third = len(valid_volumes) // 3

        early_vol = sum(valid_volumes[:third]) / third
        middle_vol = sum(valid_volumes[third:2*third]) / third
        late_vol = sum(valid_volumes[2*third:]) / (len(valid_volumes) - 2*third)

        # Score based on volume pattern
        score = 0.0

        if middle_vol > early_vol:  # Volume increases during expansion
            score += 0.5

        if late_vol < middle_vol:  # Volume decreases during contraction
            score += 0.5

        return score

    def _analyze_expanding_volume_pattern(self, volumes: List[float]) -> float:
        """Analyze volume pattern for expanding triangle."""
        if len(volumes) < 3:
            return 0.5

        valid_volumes = [v for v in volumes if v is not None and v > 0]
        if len(valid_volumes) < 3:
            return 0.5

        # Volume should generally increase with expansion
        first_half = valid_volumes[:len(valid_volumes)//2]
        second_half = valid_volumes[len(valid_volumes)//2:]

        if not first_half or not second_half:
            return 0.5

        avg_early = sum(first_half) / len(first_half)
        avg_late = sum(second_half) / len(second_half)

        if avg_early > 0:
            volume_change = (avg_late - avg_early) / avg_early
            # Positive volume change is good for expanding patterns
            return max(0.0, min(1.0, volume_change + 0.5))

        return 0.5

    def _score_pattern_length(self, pattern_length: int) -> float:
        """Score pattern length appropriateness."""
        ideal_min = 20
        ideal_max = 80

        if ideal_min <= pattern_length <= ideal_max:
            return 1.0
        elif pattern_length < ideal_min:
            return pattern_length / ideal_min
        else:  # pattern_length > ideal_max
            return max(0.3, ideal_max / pattern_length)

    def _calculate_volume_profile(self, data: PriceDataFrame,
                                start_index: int, end_index: int) -> VolumeProfile:
        """Calculate volume profile for the pattern period."""
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

        # Volume confirmation (increasing volume is generally good for these patterns)
        volume_confirmation = volume_trend == "increasing"

        return VolumeProfile(
            avg_volume=avg_volume,
            volume_trend=volume_trend,
            volume_confirmation=volume_confirmation
        )

    def _filter_overlapping_patterns(self, patterns: List[DetectedPattern]) -> List[DetectedPattern]:
        """Filter out overlapping patterns, keeping the highest confidence ones."""
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

                    # If overlap is more than 50% of pattern length, consider it overlapping
                    if overlap_length > pattern_length * 0.5:
                        overlaps = True
                        break

            if not overlaps:
                filtered_patterns.append(pattern)

        return filtered_patterns

    def detect_harmonic_patterns(self, data: PriceDataFrame,
                                sensitivity: float = 0.5) -> List[DetectedPattern]:
        """
        Detect harmonic patterns (Gartley, Butterfly, Bat, Crab, ABCD, Cypher).

        Args:
            data: Price data frame
            sensitivity: Detection sensitivity (0.0 to 1.0)

        Returns:
            List of detected harmonic patterns
        """
        if len(data) < 30:  # Harmonic patterns need sufficient data
            return []

        patterns = []
        highs = data.get_highs()
        lows = data.get_lows()

        # Find significant peaks and troughs for harmonic analysis
        high_peaks = [pt for pt in self.trend_analysis.find_peaks_and_troughs(highs, min_distance=5)
                     if pt.type == 'peak']
        low_troughs = [pt for pt in self.trend_analysis.find_peaks_and_troughs(lows, min_distance=5)
                      if pt.type == 'trough']

        # Combine and sort all turning points
        all_points = sorted(high_peaks + low_troughs, key=lambda x: x.index)

        if len(all_points) < 5:  # Need at least 5 points for XABCD structure
            return patterns

        # Look for 5-point harmonic patterns (XABCD)
        harmonic_patterns = self._find_harmonic_patterns(data, all_points, sensitivity)
        patterns.extend(harmonic_patterns)

        # Look for 4-point ABCD patterns
        abcd_patterns = self._find_abcd_patterns(data, all_points, sensitivity)
        patterns.extend(abcd_patterns)

        return self._filter_overlapping_patterns(patterns)

    def _find_harmonic_patterns(self, data: PriceDataFrame, points: List,
                              sensitivity: float) -> List[DetectedPattern]:
        """Find 5-point harmonic patterns (XABCD structure)."""
        patterns = []

        # Look for 5 consecutive turning points
        for i in range(len(points) - 4):
            X, A, B, C, D = points[i:i+5]

            # Validate time spacing
            total_time = D.index - X.index
            if total_time < 20 or total_time > 100:  # Reasonable time span
                continue

            # Calculate Fibonacci ratios
            ratios = self._calculate_fibonacci_ratios(X, A, B, C, D)

            if not ratios:
                continue

            # Check for specific harmonic patterns
            pattern_type = self._identify_harmonic_pattern_type(ratios)

            if pattern_type:
                harmonic_pattern = self._create_harmonic_pattern(
                    data, pattern_type, X, A, B, C, D, ratios, sensitivity
                )
                if harmonic_pattern:
                    patterns.append(harmonic_pattern)

        return patterns

    def _find_abcd_patterns(self, data: PriceDataFrame, points: List,
                          sensitivity: float) -> List[DetectedPattern]:
        """Find 4-point ABCD patterns."""
        patterns = []

        # Look for 4 consecutive turning points
        for i in range(len(points) - 3):
            A, B, C, D = points[i:i+4]

            # Validate ABCD structure
            if not self._validate_abcd_structure(A, B, C, D):
                continue

            # Calculate ABCD ratios
            ratios = self._calculate_abcd_ratios(A, B, C, D)

            if ratios and self._is_valid_abcd_ratios(ratios):
                abcd_pattern = self._create_abcd_pattern(
                    data, A, B, C, D, ratios, sensitivity
                )
                if abcd_pattern:
                    patterns.append(abcd_pattern)

        return patterns

    def _calculate_fibonacci_ratios(self, X, A, B, C, D):
        """Calculate Fibonacci ratios for harmonic pattern analysis."""
        try:
            # Calculate price movements
            XA = abs(A.value - X.value)
            AB = abs(B.value - A.value)
            BC = abs(C.value - B.value)
            CD = abs(D.value - C.value)
            XB = abs(B.value - X.value)
            XC = abs(C.value - X.value)
            XD = abs(D.value - X.value)

            if XA == 0 or AB == 0 or BC == 0 or XB == 0:
                return None

            ratios = {
                'AB_XA': AB / XA,
                'BC_AB': BC / AB,
                'CD_BC': CD / BC if BC != 0 else 0,
                'XB_XA': XB / XA,
                'XC_XA': XC / XA,
                'XD_XA': XD / XA,
                'CD_AB': CD / AB if AB != 0 else 0
            }

            return ratios

        except (ZeroDivisionError, AttributeError):
            return None

    def _identify_harmonic_pattern_type(self, ratios: Dict[str, float]) -> Optional[PatternType]:
        """Identify specific harmonic pattern type based on Fibonacci ratios."""

        # Define tolerance for ratio matching
        tolerance = 0.05

        def ratio_matches(actual: float, expected: float, tol: float = tolerance) -> bool:
            return abs(actual - expected) <= tol

        # Gartley Pattern (222)
        if (ratio_matches(ratios['AB_XA'], 0.618) and
            ratio_matches(ratios['BC_AB'], 0.382, 0.1) and
            ratio_matches(ratios['XD_XA'], 0.786)):
            return PatternType.GARTLEY

        # Butterfly Pattern
        if (ratio_matches(ratios['AB_XA'], 0.786) and
            ratio_matches(ratios['BC_AB'], 0.382, 0.1) and
            ratio_matches(ratios['XD_XA'], 1.27, 0.1)):
            return PatternType.BUTTERFLY

        # Bat Pattern
        if (ratio_matches(ratios['AB_XA'], 0.382, 0.1) and
            ratio_matches(ratios['BC_AB'], 0.382, 0.1) and
            ratio_matches(ratios['XD_XA'], 0.886, 0.05)):
            return PatternType.BAT

        # Crab Pattern
        if (ratio_matches(ratios['AB_XA'], 0.382, 0.1) and
            ratio_matches(ratios['BC_AB'], 0.382, 0.1) and
            ratio_matches(ratios['XD_XA'], 1.618, 0.1)):
            return PatternType.CRAB

        # Cypher Pattern
        if (ratio_matches(ratios['AB_XA'], 0.382, 0.1) and
            ratio_matches(ratios['BC_AB'], 1.272, 0.1) and
            ratio_matches(ratios['XD_XA'], 0.786)):
            return PatternType.CYPHER

        return None

    def _calculate_abcd_ratios(self, A, B, C, D):
        """Calculate ratios for ABCD pattern."""
        try:
            AB = abs(B.value - A.value)
            CD = abs(D.value - C.value)
            BC = abs(C.value - B.value)

            if AB == 0 or BC == 0:
                return None

            return {
                'CD_AB': CD / AB,
                'time_AB': B.index - A.index,
                'time_CD': D.index - C.index
            }

        except (ZeroDivisionError, AttributeError):
            return None

    def _validate_abcd_structure(self, A, B, C, D) -> bool:
        """Validate ABCD pattern structure."""

        # Check alternating pattern (peak-trough-peak-trough or vice versa)
        if A.type == B.type or B.type == C.type or C.type == D.type:
            return False

        # Check time progression
        if not (A.index < B.index < C.index < D.index):
            return False

        # Check reasonable time spacing
        total_time = D.index - A.index
        if total_time < 10 or total_time > 80:
            return False

        return True

    def _is_valid_abcd_ratios(self, ratios: Dict[str, float]) -> bool:
        """Check if ABCD ratios are valid."""

        # CD should be 0.618 to 1.618 times AB
        cd_ab_ratio = ratios['CD_AB']
        if not (0.618 <= cd_ab_ratio <= 1.618):
            return False

        # Time symmetry check (optional)
        time_ab = ratios['time_AB']
        time_cd = ratios['time_CD']

        if time_ab > 0:
            time_ratio = time_cd / time_ab
            # Allow some time variation
            if not (0.5 <= time_ratio <= 2.0):
                return False

        return True

    def _create_harmonic_pattern(self, data: PriceDataFrame, pattern_type: PatternType,
                               X, A, B, C, D, ratios: Dict[str, float],
                               sensitivity: float) -> Optional[DetectedPattern]:
        """Create harmonic pattern from XABCD points."""

        # Calculate confidence based on ratio accuracy
        confidence = self._calculate_harmonic_confidence(ratios, pattern_type, sensitivity)

        if confidence < (0.4 + sensitivity * 0.3):
            return None

        # Calculate Fibonacci levels for targets
        fibonacci_levels = self._calculate_fibonacci_levels(X, A, B, C, D)

        # Calculate volume profile
        volume_profile = self._calculate_volume_profile(data, X.index, D.index)

        return DetectedPattern(
            pattern_type=pattern_type,
            category=PATTERN_CATEGORIES[pattern_type],
            confidence=confidence,
            start_time=data[X.index].timestamp,
            end_time=data[D.index].timestamp,
            start_index=X.index,
            end_index=D.index,
            key_levels={
                'X_price': X.value,
                'A_price': A.value,
                'B_price': B.value,
                'C_price': C.value,
                'D_price': D.value,
                'AB_XA_ratio': ratios['AB_XA'],
                'BC_AB_ratio': ratios['BC_AB'],
                'XD_XA_ratio': ratios['XD_XA'],
                'target_1': fibonacci_levels.get('target_1'),
                'target_2': fibonacci_levels.get('target_2')
            },
            volume_profile=volume_profile,
            fibonacci_levels=fibonacci_levels,
            description=f"{pattern_type.value.replace('_', ' ').title()} harmonic pattern. XD/XA ratio: {ratios['XD_XA']:.3f}. Confidence: {confidence:.1%}"
        )

    def _create_abcd_pattern(self, data: PriceDataFrame, A, B, C, D,
                           ratios: Dict[str, float], sensitivity: float) -> Optional[DetectedPattern]:
        """Create ABCD pattern."""

        # Calculate confidence
        confidence = self._calculate_abcd_confidence(ratios, sensitivity)

        if confidence < (0.4 + sensitivity * 0.3):
            return None

        # Calculate volume profile
        volume_profile = self._calculate_volume_profile(data, A.index, D.index)

        # Calculate target levels
        AB = abs(B.value - A.value)
        target_1 = D.value + (AB * 0.618) * (1 if D.value > C.value else -1)
        target_2 = D.value + (AB * 1.272) * (1 if D.value > C.value else -1)

        return DetectedPattern(
            pattern_type=PatternType.ABCD,
            category=PATTERN_CATEGORIES[PatternType.ABCD],
            confidence=confidence,
            start_time=data[A.index].timestamp,
            end_time=data[D.index].timestamp,
            start_index=A.index,
            end_index=D.index,
            key_levels={
                'A_price': A.value,
                'B_price': B.value,
                'C_price': C.value,
                'D_price': D.value,
                'CD_AB_ratio': ratios['CD_AB'],
                'target_1': target_1,
                'target_2': target_2
            },
            volume_profile=volume_profile,
            fibonacci_levels={'target_1': target_1, 'target_2': target_2},
            description=f"ABCD harmonic pattern. CD/AB ratio: {ratios['CD_AB']:.3f}. Confidence: {confidence:.1%}"
        )

    def _calculate_fibonacci_levels(self, X, A, B, C, D) -> Dict[str, float]:
        """Calculate Fibonacci retracement and extension levels."""

        XA = A.value - X.value
        AB = B.value - A.value
        BC = C.value - B.value
        CD = D.value - C.value

        # Common Fibonacci levels
        fib_levels = {}

        # Retracement levels from D
        fib_levels['D_236'] = D.value + CD * 0.236
        fib_levels['D_382'] = D.value + CD * 0.382
        fib_levels['D_618'] = D.value + CD * 0.618
        fib_levels['D_786'] = D.value + CD * 0.786

        # Extension levels
        fib_levels['target_1'] = D.value + abs(XA) * 0.618 * (1 if CD > 0 else -1)
        fib_levels['target_2'] = D.value + abs(XA) * 1.272 * (1 if CD > 0 else -1)

        return fib_levels

    def _calculate_harmonic_confidence(self, ratios: Dict[str, float],
                                     pattern_type: PatternType, sensitivity: float) -> float:
        """Calculate confidence for harmonic pattern based on ratio accuracy."""

        confidence_factors = []

        # Define ideal ratios for each pattern type
        ideal_ratios = {
            PatternType.GARTLEY: {'AB_XA': 0.618, 'BC_AB': 0.382, 'XD_XA': 0.786},
            PatternType.BUTTERFLY: {'AB_XA': 0.786, 'BC_AB': 0.382, 'XD_XA': 1.27},
            PatternType.BAT: {'AB_XA': 0.382, 'BC_AB': 0.382, 'XD_XA': 0.886},
            PatternType.CRAB: {'AB_XA': 0.382, 'BC_AB': 0.382, 'XD_XA': 1.618},
            PatternType.CYPHER: {'AB_XA': 0.382, 'BC_AB': 1.272, 'XD_XA': 0.786}
        }

        if pattern_type not in ideal_ratios:
            return 0.0

        ideal = ideal_ratios[pattern_type]

        # Calculate accuracy for each key ratio
        for ratio_name, ideal_value in ideal.items():
            if ratio_name in ratios:
                actual_value = ratios[ratio_name]
                accuracy = 1.0 - min(1.0, abs(actual_value - ideal_value) / ideal_value)
                confidence_factors.append(accuracy * (1.0 / len(ideal)))

        # Base confidence from ratio accuracy
        base_confidence = sum(confidence_factors)

        # Bonus for very accurate ratios
        if base_confidence > 0.9:
            base_confidence = min(1.0, base_confidence * 1.1)

        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        final_confidence = max(0.0, min(1.0, base_confidence + sensitivity_adjustment))

        return final_confidence

    def _calculate_abcd_confidence(self, ratios: Dict[str, float], sensitivity: float) -> float:
        """Calculate confidence for ABCD pattern."""

        confidence_factors = []

        # 1. CD/AB ratio accuracy (ideal is around 0.786 or 1.272)
        cd_ab_ratio = ratios['CD_AB']

        # Score based on proximity to ideal Fibonacci ratios
        ideal_ratios = [0.618, 0.786, 1.0, 1.272, 1.618]
        best_match_score = 0.0

        for ideal in ideal_ratios:
            accuracy = 1.0 - min(1.0, abs(cd_ab_ratio - ideal) / ideal)
            best_match_score = max(best_match_score, accuracy)

        confidence_factors.append(best_match_score * 0.6)

        # 2. Time symmetry
        time_ab = ratios['time_AB']
        time_cd = ratios['time_CD']

        if time_ab > 0:
            time_ratio = time_cd / time_ab
            time_symmetry = 1.0 - min(1.0, abs(time_ratio - 1.0))
            confidence_factors.append(time_symmetry * 0.4)
        else:
            confidence_factors.append(0.0)

        base_confidence = sum(confidence_factors)

        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        final_confidence = max(0.0, min(1.0, base_confidence + sensitivity_adjustment))

        return final_confidence
