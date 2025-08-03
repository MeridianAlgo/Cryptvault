"""Geometric pattern detection algorithms for triangles, flags, wedges, etc."""

from typing import List, Dict, Optional, Tuple
import math
from datetime import datetime
from ..data.models import PriceDataFrame
from ..indicators.trend_analysis import TrendAnalysis, TrendLine, PeakTrough
from .types import PatternType, PatternCategory, DetectedPattern, VolumeProfile, PATTERN_CATEGORIES


class GeometricPatternAnalyzer:
    """Analyze geometric chart patterns like triangles, flags, wedges, and channels."""
    
    def __init__(self):
        """Initialize geometric pattern analyzer."""
        self.trend_analysis = TrendAnalysis()
        self.min_pattern_length = 10  # Minimum number of data points for a pattern
        self.max_pattern_length = 100  # Maximum number of data points for a pattern
    
    def detect_triangle_patterns(self, data: PriceDataFrame, 
                               sensitivity: float = 0.5) -> List[DetectedPattern]:
        """
        Detect ascending, descending, and symmetrical triangle patterns.
        
        Args:
            data: Price data frame
            sensitivity: Detection sensitivity (0.0 to 1.0)
            
        Returns:
            List of detected triangle patterns
        """
        if len(data) < self.min_pattern_length:
            return []
        
        patterns = []
        highs = data.get_highs()
        lows = data.get_lows()
        
        # Find peaks and troughs
        high_peaks = [pt for pt in self.trend_analysis.find_peaks_and_troughs(highs, min_distance=3) 
                     if pt.type == 'peak']
        low_troughs = [pt for pt in self.trend_analysis.find_peaks_and_troughs(lows, min_distance=3) 
                      if pt.type == 'trough']
        
        if len(high_peaks) < 2 or len(low_troughs) < 2:
            return patterns
        
        # Try different combinations of peaks and troughs to form triangles
        for i in range(len(high_peaks) - 1):
            for j in range(i + 1, len(high_peaks)):
                peak1, peak2 = high_peaks[i], high_peaks[j]
                
                # Find troughs within the peak range
                relevant_troughs = [t for t in low_troughs 
                                  if peak1.index <= t.index <= peak2.index]
                
                if len(relevant_troughs) < 2:
                    continue
                
                # Try different trough combinations
                for k in range(len(relevant_troughs) - 1):
                    for l in range(k + 1, len(relevant_troughs)):
                        trough1, trough2 = relevant_troughs[k], relevant_troughs[l]
                        
                        triangle_pattern = self._analyze_triangle_formation(
                            data, peak1, peak2, trough1, trough2, sensitivity
                        )
                        
                        if triangle_pattern:
                            patterns.append(triangle_pattern)
        
        # Remove overlapping patterns and keep the best ones
        return self._filter_overlapping_patterns(patterns)
    
    def _analyze_triangle_formation(self, data: PriceDataFrame, 
                                  peak1: PeakTrough, peak2: PeakTrough,
                                  trough1: PeakTrough, trough2: PeakTrough,
                                  sensitivity: float) -> Optional[DetectedPattern]:
        """Analyze if four points form a valid triangle pattern."""
        
        # Calculate trend lines
        try:
            # Upper trend line (resistance)
            upper_slope = (peak2.value - peak1.value) / (peak2.index - peak1.index)
            upper_intercept = peak1.value - upper_slope * peak1.index
            
            # Lower trend line (support)
            lower_slope = (trough2.value - trough1.value) / (trough2.index - trough1.index)
            lower_intercept = trough1.value - lower_slope * trough1.index
            
        except ZeroDivisionError:
            return None
        
        # Determine triangle type and validate
        triangle_type = self._classify_triangle_type(upper_slope, lower_slope)
        if not triangle_type:
            return None
        
        # Calculate pattern boundaries
        start_index = min(peak1.index, peak2.index, trough1.index, trough2.index)
        end_index = max(peak1.index, peak2.index, trough1.index, trough2.index)
        
        # Validate pattern length
        pattern_length = end_index - start_index
        if pattern_length < self.min_pattern_length or pattern_length > self.max_pattern_length:
            return None
        
        # Calculate convergence point
        convergence_index = self._calculate_convergence_point(
            upper_slope, upper_intercept, lower_slope, lower_intercept
        )
        
        # Validate convergence
        if not self._validate_triangle_convergence(convergence_index, start_index, end_index):
            return None
        
        # Calculate pattern confidence
        confidence = self._calculate_triangle_confidence(
            data, start_index, end_index, upper_slope, upper_intercept,
            lower_slope, lower_intercept, triangle_type, sensitivity
        )
        
        if confidence < (0.3 + sensitivity * 0.4):  # Adjust threshold based on sensitivity
            return None
        
        # Calculate volume profile
        volume_profile = self._calculate_volume_profile(data, start_index, end_index)
        
        # Create pattern
        pattern_category = PATTERN_CATEGORIES[triangle_type]
        
        return DetectedPattern(
            pattern_type=triangle_type,
            category=pattern_category,
            confidence=confidence,
            start_time=data[start_index].timestamp,
            end_time=data[end_index].timestamp,
            start_index=start_index,
            end_index=end_index,
            key_levels={
                'upper_resistance': peak1.value,
                'lower_support': trough1.value,
                'convergence_price': upper_slope * convergence_index + upper_intercept,
                'upper_slope': upper_slope,
                'lower_slope': lower_slope
            },
            volume_profile=volume_profile,
            description=self._generate_triangle_description(triangle_type, confidence, pattern_length)
        )
    
    def _classify_triangle_type(self, upper_slope: float, lower_slope: float) -> Optional[PatternType]:
        """Classify triangle type based on trend line slopes."""
        slope_threshold = 0.001  # Threshold for considering a line horizontal
        
        # Ascending Triangle: horizontal resistance, ascending support
        if abs(upper_slope) < slope_threshold and lower_slope > slope_threshold:
            return PatternType.ASCENDING_TRIANGLE
        
        # Descending Triangle: descending resistance, horizontal support
        elif upper_slope < -slope_threshold and abs(lower_slope) < slope_threshold:
            return PatternType.DESCENDING_TRIANGLE
        
        # Symmetrical Triangle: converging lines with opposite slopes
        elif (upper_slope < -slope_threshold and lower_slope > slope_threshold and
              abs(abs(upper_slope) - abs(lower_slope)) < abs(upper_slope) * 0.5):
            return PatternType.SYMMETRICAL_TRIANGLE
        
        return None
    
    def _calculate_convergence_point(self, upper_slope: float, upper_intercept: float,
                                   lower_slope: float, lower_intercept: float) -> float:
        """Calculate where the two trend lines converge."""
        if abs(upper_slope - lower_slope) < 1e-10:  # Parallel lines
            return float('inf')
        
        # Solve: upper_slope * x + upper_intercept = lower_slope * x + lower_intercept
        convergence_x = (lower_intercept - upper_intercept) / (upper_slope - lower_slope)
        return convergence_x
    
    def _validate_triangle_convergence(self, convergence_index: float, 
                                     start_index: int, end_index: int) -> bool:
        """Validate that triangle convergence is reasonable."""
        if convergence_index == float('inf'):
            return False
        
        pattern_length = end_index - start_index
        
        # Convergence should be within reasonable distance from pattern end
        # Allow convergence up to 2x the pattern length beyond the end
        max_convergence = end_index + (pattern_length * 2)
        min_convergence = end_index - (pattern_length * 0.1)  # Allow slight past convergence
        
        return min_convergence <= convergence_index <= max_convergence
    
    def _calculate_triangle_confidence(self, data: PriceDataFrame, start_index: int, end_index: int,
                                     upper_slope: float, upper_intercept: float,
                                     lower_slope: float, lower_intercept: float,
                                     triangle_type: PatternType, sensitivity: float) -> float:
        """Calculate confidence score for triangle pattern."""
        highs = data.get_highs()
        lows = data.get_lows()
        volumes = data.get_volumes()
        
        confidence_factors = []
        
        # 1. Trend line fit quality
        upper_fit_score = self._calculate_trendline_fit(
            highs[start_index:end_index+1], upper_slope, upper_intercept, start_index, 'resistance'
        )
        lower_fit_score = self._calculate_trendline_fit(
            lows[start_index:end_index+1], lower_slope, lower_intercept, start_index, 'support'
        )
        
        confidence_factors.append(upper_fit_score * 0.3)
        confidence_factors.append(lower_fit_score * 0.3)
        
        # 2. Number of touches on trend lines
        upper_touches = self._count_trendline_touches(
            highs[start_index:end_index+1], upper_slope, upper_intercept, start_index
        )
        lower_touches = self._count_trendline_touches(
            lows[start_index:end_index+1], lower_slope, lower_intercept, start_index
        )
        
        touch_score = min(1.0, (upper_touches + lower_touches - 4) / 4)  # Normalize, 4 is minimum
        confidence_factors.append(touch_score * 0.2)
        
        # 3. Volume pattern (should decrease towards apex)
        volume_score = self._analyze_triangle_volume_pattern(volumes[start_index:end_index+1])
        confidence_factors.append(volume_score * 0.1)
        
        # 4. Pattern length appropriateness
        pattern_length = end_index - start_index
        length_score = self._score_pattern_length(pattern_length)
        confidence_factors.append(length_score * 0.1)
        
        # Calculate weighted confidence
        base_confidence = sum(confidence_factors)
        
        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        final_confidence = max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
        
        return final_confidence
    
    def _calculate_trendline_fit(self, values: List[float], slope: float, intercept: float,
                               start_index: int, line_type: str) -> float:
        """Calculate how well a trend line fits the data."""
        if not values:
            return 0.0
        
        total_error = 0.0
        valid_points = 0
        
        for i, value in enumerate(values):
            if value is None:
                continue
            
            expected_value = slope * (start_index + i) + intercept
            
            # For resistance lines, penalize points above the line more
            # For support lines, penalize points below the line more
            error = abs(value - expected_value)
            
            if line_type == 'resistance' and value > expected_value:
                error *= 2  # Penalize breaks above resistance
            elif line_type == 'support' and value < expected_value:
                error *= 2  # Penalize breaks below support
            
            total_error += error
            valid_points += 1
        
        if valid_points == 0:
            return 0.0
        
        # Calculate average error as percentage of value range
        avg_error = total_error / valid_points
        value_range = max(values) - min(values) if values else 1
        
        if value_range == 0:
            return 1.0
        
        error_percentage = avg_error / value_range
        fit_score = max(0.0, 1.0 - error_percentage * 2)  # Convert error to score
        
        return fit_score
    
    def _count_trendline_touches(self, values: List[float], slope: float, 
                               intercept: float, start_index: int, tolerance: float = 0.02) -> int:
        """Count how many points touch the trend line within tolerance."""
        touches = 0
        
        for i, value in enumerate(values):
            if value is None:
                continue
            
            expected_value = slope * (start_index + i) + intercept
            
            if expected_value == 0:
                continue
            
            relative_error = abs(value - expected_value) / abs(expected_value)
            
            if relative_error <= tolerance:
                touches += 1
        
        return touches
    
    def _analyze_triangle_volume_pattern(self, volumes: List[float]) -> float:
        """Analyze volume pattern in triangle (should generally decrease towards apex)."""
        if len(volumes) < 3:
            return 0.5  # Neutral score for insufficient data
        
        valid_volumes = [v for v in volumes if v is not None and v > 0]
        if len(valid_volumes) < 3:
            return 0.5
        
        # Calculate volume trend
        first_third = valid_volumes[:len(valid_volumes)//3]
        last_third = valid_volumes[-len(valid_volumes)//3:]
        
        if not first_third or not last_third:
            return 0.5
        
        avg_early_volume = sum(first_third) / len(first_third)
        avg_late_volume = sum(last_third) / len(last_third)
        
        # Volume should decrease (positive score for decreasing volume)
        if avg_early_volume > 0:
            volume_change = (avg_early_volume - avg_late_volume) / avg_early_volume
            # Score between 0 and 1, with 1 being ideal volume decrease
            volume_score = max(0.0, min(1.0, volume_change + 0.5))
        else:
            volume_score = 0.5
        
        return volume_score
    
    def _score_pattern_length(self, pattern_length: int) -> float:
        """Score pattern length appropriateness."""
        ideal_min = 15
        ideal_max = 50
        
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
        
        # Volume confirmation (decreasing volume is good for triangles)
        volume_confirmation = volume_trend == "decreasing"
        
        return VolumeProfile(
            avg_volume=avg_volume,
            volume_trend=volume_trend,
            volume_confirmation=volume_confirmation
        )
    
    def _generate_triangle_description(self, triangle_type: PatternType, 
                                     confidence: float, pattern_length: int) -> str:
        """Generate human-readable description of triangle pattern."""
        type_descriptions = {
            PatternType.ASCENDING_TRIANGLE: "Ascending Triangle - bullish continuation pattern with horizontal resistance and rising support",
            PatternType.DESCENDING_TRIANGLE: "Descending Triangle - bearish continuation pattern with horizontal support and falling resistance", 
            PatternType.SYMMETRICAL_TRIANGLE: "Symmetrical Triangle - neutral pattern with converging trend lines"
        }
        
        base_description = type_descriptions.get(triangle_type, "Triangle pattern")
        
        confidence_level = "high" if confidence > 0.7 else "medium" if confidence > 0.5 else "low"
        
        return f"{base_description}. Confidence: {confidence_level} ({confidence:.1%}). Duration: {pattern_length} periods."
    
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
    
    def detect_flag_patterns(self, data: PriceDataFrame, sensitivity: float = 0.5) -> List[DetectedPattern]:
        """Alias for detect_flag_and_pennant_patterns for backward compatibility."""
        return self.detect_flag_and_pennant_patterns(data, sensitivity)
    
    def detect_cup_and_handle(self, data: PriceDataFrame, sensitivity: float = 0.5) -> List[DetectedPattern]:
        """Alias for detect_cup_and_handle_patterns for backward compatibility."""
        return self.detect_cup_and_handle_patterns(data, sensitivity)
    
    def detect_rectangle_patterns(self, data: PriceDataFrame, sensitivity: float = 0.5) -> List[DetectedPattern]:
        """Alias for detect_rectangle_and_channel_patterns for backward compatibility."""
        return self.detect_rectangle_and_channel_patterns(data, sensitivity)
    
    def detect_flag_and_pennant_patterns(self, data: PriceDataFrame, 
                                       sensitivity: float = 0.5) -> List[DetectedPattern]:
        """
        Detect bull/bear flag and pennant patterns.
        
        Args:
            data: Price data frame
            sensitivity: Detection sensitivity (0.0 to 1.0)
            
        Returns:
            List of detected flag and pennant patterns
        """
        if len(data) < self.min_pattern_length:
            return []
        
        patterns = []
        closes = data.get_closes()
        highs = data.get_highs()
        lows = data.get_lows()
        volumes = data.get_volumes()
        
        # Look for potential flagpoles (strong directional moves)
        flagpoles = self._find_flagpoles(closes, volumes, sensitivity)
        
        for flagpole in flagpoles:
            # Look for consolidation after flagpole
            consolidation_start = flagpole['end_index'] + 1
            max_consolidation_length = min(flagpole['length'], 30)  # Consolidation should be shorter than flagpole
            
            for consolidation_length in range(5, max_consolidation_length):
                consolidation_end = consolidation_start + consolidation_length
                
                if consolidation_end >= len(data):
                    break
                
                # Analyze consolidation pattern
                flag_pattern = self._analyze_flag_consolidation(
                    data, flagpole, consolidation_start, consolidation_end, sensitivity
                )
                
                if flag_pattern:
                    patterns.append(flag_pattern)
                    break  # Found pattern for this flagpole
        
        return self._filter_overlapping_patterns(patterns)
    
    def _find_flagpoles(self, closes: List[float], volumes: List[float], 
                       sensitivity: float) -> List[Dict]:
        """Find strong directional moves that could be flagpoles."""
        flagpoles = []
        min_flagpole_length = 3
        max_flagpole_length = 20
        
        for start_idx in range(len(closes) - min_flagpole_length):
            for length in range(min_flagpole_length, min(max_flagpole_length, len(closes) - start_idx)):
                end_idx = start_idx + length
                
                if end_idx >= len(closes):
                    break
                
                # Calculate price change
                start_price = closes[start_idx]
                end_price = closes[end_idx]
                
                if start_price == 0:
                    continue
                
                price_change_percent = (end_price - start_price) / start_price
                
                # Check for strong move (adjust threshold based on sensitivity)
                min_move_threshold = 0.03 - (sensitivity * 0.015)  # 1.5% to 4.5%
                
                if abs(price_change_percent) < min_move_threshold:
                    continue
                
                # Check for volume confirmation
                flagpole_volumes = volumes[start_idx:end_idx+1]
                valid_volumes = [v for v in flagpole_volumes if v is not None and v > 0]
                
                if len(valid_volumes) < length // 2:
                    continue
                
                avg_flagpole_volume = sum(valid_volumes) / len(valid_volumes)
                
                # Calculate trend strength
                trend_strength = self._calculate_trend_strength(closes[start_idx:end_idx+1])
                
                if trend_strength < 0.6:  # Require strong trend
                    continue
                
                flagpoles.append({
                    'start_index': start_idx,
                    'end_index': end_idx,
                    'length': length,
                    'price_change_percent': price_change_percent,
                    'direction': 'bullish' if price_change_percent > 0 else 'bearish',
                    'avg_volume': avg_flagpole_volume,
                    'trend_strength': trend_strength
                })
        
        # Sort by trend strength and return best candidates
        flagpoles.sort(key=lambda x: x['trend_strength'], reverse=True)
        return flagpoles[:10]  # Limit to top 10 candidates
    
    def _calculate_trend_strength(self, prices: List[float]) -> float:
        """Calculate the strength of a trend (0 to 1)."""
        if len(prices) < 3:
            return 0.0
        
        valid_prices = [p for p in prices if p is not None]
        if len(valid_prices) < 3:
            return 0.0
        
        # Fit trend line and calculate R-squared
        try:
            trend_line = self.trend_analysis.fit_trend_line(valid_prices, 0, len(valid_prices) - 1)
            return trend_line.r_squared
        except:
            return 0.0
    
    def _analyze_flag_consolidation(self, data: PriceDataFrame, flagpole: Dict,
                                  consolidation_start: int, consolidation_end: int,
                                  sensitivity: float) -> Optional[DetectedPattern]:
        """Analyze consolidation period to determine if it forms a flag or pennant."""
        
        if consolidation_end >= len(data):
            return None
        
        highs = data.get_highs()[consolidation_start:consolidation_end+1]
        lows = data.get_lows()[consolidation_start:consolidation_end+1]
        closes = data.get_closes()[consolidation_start:consolidation_end+1]
        volumes = data.get_volumes()[consolidation_start:consolidation_end+1]
        
        # Find peaks and troughs in consolidation
        high_peaks = [pt for pt in self.trend_analysis.find_peaks_and_troughs(highs, min_distance=2) 
                     if pt.type == 'peak']
        low_troughs = [pt for pt in self.trend_analysis.find_peaks_and_troughs(lows, min_distance=2) 
                      if pt.type == 'trough']
        
        if len(high_peaks) < 2 or len(low_troughs) < 2:
            return None
        
        # Analyze consolidation pattern
        pattern_type, confidence = self._classify_flag_pennant_pattern(
            flagpole, high_peaks, low_troughs, highs, lows, volumes, sensitivity
        )
        
        if not pattern_type or confidence < 0.3:
            return None
        
        # Calculate volume profile
        full_start = flagpole['start_index']
        full_end = consolidation_end
        volume_profile = self._calculate_volume_profile(data, full_start, full_end)
        
        # Create pattern
        pattern_category = PATTERN_CATEGORIES[pattern_type]
        
        return DetectedPattern(
            pattern_type=pattern_type,
            category=pattern_category,
            confidence=confidence,
            start_time=data[full_start].timestamp,
            end_time=data[full_end].timestamp,
            start_index=full_start,
            end_index=full_end,
            key_levels={
                'flagpole_start': data.get_closes()[flagpole['start_index']],
                'flagpole_end': data.get_closes()[flagpole['end_index']],
                'consolidation_high': max(h for h in highs if h is not None),
                'consolidation_low': min(l for l in lows if l is not None),
                'flagpole_strength': flagpole['trend_strength'],
                'price_change_percent': flagpole['price_change_percent']
            },
            volume_profile=volume_profile,
            description=self._generate_flag_pennant_description(pattern_type, confidence, flagpole)
        )
    
    def _classify_flag_pennant_pattern(self, flagpole: Dict, high_peaks: List, low_troughs: List,
                                     highs: List[float], lows: List[float], volumes: List[float],
                                     sensitivity: float) -> Tuple[Optional[PatternType], float]:
        """Classify consolidation as flag or pennant pattern."""
        
        if len(high_peaks) < 2 or len(low_troughs) < 2:
            return None, 0.0
        
        # Calculate trend lines for consolidation
        try:
            # Upper trend line (resistance in consolidation)
            peak1, peak2 = high_peaks[0], high_peaks[-1]
            upper_slope = (peak2.value - peak1.value) / (peak2.index - peak1.index) if peak2.index != peak1.index else 0
            
            # Lower trend line (support in consolidation)
            trough1, trough2 = low_troughs[0], low_troughs[-1]
            lower_slope = (trough2.value - trough1.value) / (trough2.index - trough1.index) if trough2.index != trough1.index else 0
            
        except (IndexError, ZeroDivisionError):
            return None, 0.0
        
        # Determine pattern type based on flagpole direction and consolidation slopes
        flagpole_direction = flagpole['direction']
        
        # Check for flag patterns (parallel consolidation lines)
        slope_difference = abs(upper_slope - lower_slope)
        avg_slope = (abs(upper_slope) + abs(lower_slope)) / 2
        
        if avg_slope > 0:
            slope_similarity = 1 - (slope_difference / avg_slope)
        else:
            slope_similarity = 1.0 if slope_difference < 0.001 else 0.0
        
        # Check for pennant patterns (converging consolidation lines)
        convergence_factor = 0.0
        if upper_slope < 0 and lower_slope > 0:  # Converging
            convergence_factor = min(abs(upper_slope), abs(lower_slope)) / max(abs(upper_slope), abs(lower_slope))
        
        # Calculate confidence factors
        confidence_factors = []
        
        # 1. Flagpole strength
        confidence_factors.append(flagpole['trend_strength'] * 0.3)
        
        # 2. Volume pattern (should decrease during consolidation)
        volume_score = self._analyze_flag_volume_pattern(volumes)
        confidence_factors.append(volume_score * 0.2)
        
        # 3. Consolidation slope appropriateness
        if flagpole_direction == 'bullish':
            # For bull flags, consolidation should be slightly downward or sideways
            if upper_slope <= 0.001 and lower_slope <= 0.001:  # Sideways/downward
                slope_score = 0.8
            else:
                slope_score = max(0.0, 0.8 - abs(upper_slope + lower_slope) * 10)
        else:  # bearish
            # For bear flags, consolidation should be slightly upward or sideways
            if upper_slope >= -0.001 and lower_slope >= -0.001:  # Sideways/upward
                slope_score = 0.8
            else:
                slope_score = max(0.0, 0.8 - abs(upper_slope + lower_slope) * 10)
        
        confidence_factors.append(slope_score * 0.3)
        
        # 4. Pattern length appropriateness
        consolidation_length = len(highs)
        length_score = self._score_consolidation_length(consolidation_length, flagpole['length'])
        confidence_factors.append(length_score * 0.2)
        
        base_confidence = sum(confidence_factors)
        
        # Determine pattern type
        if slope_similarity > 0.7:  # Parallel lines = Flag
            if flagpole_direction == 'bullish':
                pattern_type = PatternType.BULL_FLAG
            else:
                pattern_type = PatternType.BEAR_FLAG
        elif convergence_factor > 0.5:  # Converging lines = Pennant
            if flagpole_direction == 'bullish':
                pattern_type = PatternType.BULL_PENNANT
            else:
                pattern_type = PatternType.BEAR_PENNANT
        else:
            return None, 0.0
        
        # Adjust confidence based on sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        final_confidence = max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
        
        return pattern_type, final_confidence
    
    def _analyze_flag_volume_pattern(self, volumes: List[float]) -> float:
        """Analyze volume pattern in flag/pennant (should decrease during consolidation)."""
        if len(volumes) < 3:
            return 0.5
        
        valid_volumes = [v for v in volumes if v is not None and v > 0]
        if len(valid_volumes) < 3:
            return 0.5
        
        # Volume should generally decrease during consolidation
        first_half = valid_volumes[:len(valid_volumes)//2]
        second_half = valid_volumes[len(valid_volumes)//2:]
        
        if not first_half or not second_half:
            return 0.5
        
        avg_early = sum(first_half) / len(first_half)
        avg_late = sum(second_half) / len(second_half)
        
        if avg_early > 0:
            volume_change = (avg_early - avg_late) / avg_early
            # Score between 0 and 1, with 1 being ideal volume decrease
            return max(0.0, min(1.0, volume_change + 0.5))
        
        return 0.5
    
    def _score_consolidation_length(self, consolidation_length: int, flagpole_length: int) -> float:
        """Score consolidation length relative to flagpole length."""
        # Ideal consolidation is 1/3 to 2/3 of flagpole length
        ideal_min = flagpole_length * 0.33
        ideal_max = flagpole_length * 0.67
        
        if ideal_min <= consolidation_length <= ideal_max:
            return 1.0
        elif consolidation_length < ideal_min:
            return consolidation_length / ideal_min
        else:  # consolidation_length > ideal_max
            return max(0.3, ideal_max / consolidation_length)
    
    def _generate_flag_pennant_description(self, pattern_type: PatternType, 
                                         confidence: float, flagpole: Dict) -> str:
        """Generate description for flag/pennant pattern."""
        type_descriptions = {
            PatternType.BULL_FLAG: "Bull Flag - bullish continuation pattern with strong upward move followed by sideways consolidation",
            PatternType.BEAR_FLAG: "Bear Flag - bearish continuation pattern with strong downward move followed by sideways consolidation",
            PatternType.BULL_PENNANT: "Bull Pennant - bullish continuation pattern with strong upward move followed by converging consolidation",
            PatternType.BEAR_PENNANT: "Bear Pennant - bearish continuation pattern with strong downward move followed by converging consolidation"
        }
        
        base_description = type_descriptions.get(pattern_type, "Flag/Pennant pattern")
        confidence_level = "high" if confidence > 0.7 else "medium" if confidence > 0.5 else "low"
        
        return (f"{base_description}. Flagpole move: {flagpole['price_change_percent']:.1%}. "
                f"Confidence: {confidence_level} ({confidence:.1%}).")
    
    def detect_cup_and_handle_patterns(self, data: PriceDataFrame, 
                                     sensitivity: float = 0.5) -> List[DetectedPattern]:
        """
        Detect cup and handle patterns.
        
        Args:
            data: Price data frame
            sensitivity: Detection sensitivity (0.0 to 1.0)
            
        Returns:
            List of detected cup and handle patterns
        """
        if len(data) < 30:  # Cup and handle needs more data
            return []
        
        patterns = []
        closes = data.get_closes()
        highs = data.get_highs()
        lows = data.get_lows()
        
        # Look for potential cup formations
        cups = self._find_cup_formations(closes, highs, lows, sensitivity)
        
        for cup in cups:
            # Look for handle after cup
            handle = self._find_handle_formation(data, cup, sensitivity)
            
            if handle:
                cup_handle_pattern = self._create_cup_handle_pattern(data, cup, handle, sensitivity)
                if cup_handle_pattern:
                    patterns.append(cup_handle_pattern)
        
        return self._filter_overlapping_patterns(patterns)
    
    def _find_cup_formations(self, closes: List[float], highs: List[float], 
                           lows: List[float], sensitivity: float) -> List[Dict]:
        """Find U-shaped cup formations in price data."""
        cups = []
        min_cup_length = 15
        max_cup_length = 80
        
        for start_idx in range(len(closes) - min_cup_length):
            for cup_length in range(min_cup_length, min(max_cup_length, len(closes) - start_idx)):
                end_idx = start_idx + cup_length
                
                if end_idx >= len(closes):
                    break
                
                cup_data = closes[start_idx:end_idx+1]
                cup_highs = highs[start_idx:end_idx+1]
                cup_lows = lows[start_idx:end_idx+1]
                
                # Analyze cup shape
                cup_analysis = self._analyze_cup_shape(cup_data, cup_highs, cup_lows, start_idx)
                
                if cup_analysis['is_valid_cup']:
                    cups.append({
                        'start_index': start_idx,
                        'end_index': end_idx,
                        'length': cup_length,
                        'left_rim': cup_analysis['left_rim'],
                        'right_rim': cup_analysis['right_rim'],
                        'bottom': cup_analysis['bottom'],
                        'depth_percent': cup_analysis['depth_percent'],
                        'symmetry_score': cup_analysis['symmetry_score'],
                        'u_shape_score': cup_analysis['u_shape_score']
                    })
        
        # Sort by quality and return best candidates
        cups.sort(key=lambda x: x['u_shape_score'] * x['symmetry_score'], reverse=True)
        return cups[:5]  # Top 5 candidates
    
    def _analyze_cup_shape(self, closes: List[float], highs: List[float], 
                         lows: List[float], start_index: int) -> Dict:
        """Analyze if price data forms a valid cup shape."""
        if len(closes) < 10:
            return {'is_valid_cup': False}
        
        # Find left and right rim levels (should be similar)
        left_rim = closes[0]
        right_rim = closes[-1]
        
        # Find the lowest point (cup bottom)
        min_low = min(l for l in lows if l is not None)
        bottom_index = next(i for i, l in enumerate(lows) if l == min_low)
        
        # Calculate cup depth
        rim_level = (left_rim + right_rim) / 2
        depth_percent = (rim_level - min_low) / rim_level if rim_level > 0 else 0
        
        # Cup should be at least 12% deep but not more than 50%
        if depth_percent < 0.12 or depth_percent > 0.50:
            return {'is_valid_cup': False}
        
        # Check rim similarity (rims should be within 5% of each other)
        rim_difference = abs(right_rim - left_rim) / left_rim if left_rim > 0 else 1
        if rim_difference > 0.05:
            return {'is_valid_cup': False}
        
        # Analyze U-shape quality
        u_shape_score = self._calculate_u_shape_score(closes, bottom_index)
        
        # Analyze symmetry
        symmetry_score = self._calculate_cup_symmetry(closes, bottom_index)
        
        # Check for valid cup criteria
        is_valid = (u_shape_score > 0.6 and symmetry_score > 0.5 and 
                   0.12 <= depth_percent <= 0.50)
        
        return {
            'is_valid_cup': is_valid,
            'left_rim': left_rim,
            'right_rim': right_rim,
            'bottom': min_low,
            'bottom_index': start_index + bottom_index,
            'depth_percent': depth_percent,
            'symmetry_score': symmetry_score,
            'u_shape_score': u_shape_score
        }
    
    def _calculate_u_shape_score(self, closes: List[float], bottom_index: int) -> float:
        """Calculate how well the price data resembles a U-shape."""
        if len(closes) < 5 or bottom_index <= 0 or bottom_index >= len(closes) - 1:
            return 0.0
        
        # Check left side (should decline towards bottom)
        left_side = closes[:bottom_index+1]
        left_trend = self._calculate_trend_strength(left_side)
        left_declining = closes[0] > closes[bottom_index]
        
        # Check right side (should rise from bottom)
        right_side = closes[bottom_index:]
        right_trend = self._calculate_trend_strength(right_side)
        right_rising = closes[bottom_index] < closes[-1]
        
        # U-shape should have declining left and rising right
        if not (left_declining and right_rising):
            return 0.0
        
        # Score based on trend strength
        u_score = (left_trend + right_trend) / 2
        
        # Bonus for smooth curves (penalize sharp V-shapes)
        smoothness_score = self._calculate_curve_smoothness(closes, bottom_index)
        
        return (u_score * 0.7) + (smoothness_score * 0.3)
    
    def _calculate_curve_smoothness(self, closes: List[float], bottom_index: int) -> float:
        """Calculate smoothness of the curve (prefer gradual curves over sharp V's)."""
        if len(closes) < 5:
            return 0.0
        
        # Calculate second derivatives to detect sharp changes
        second_derivatives = []
        for i in range(1, len(closes) - 1):
            if i - 1 >= 0 and i + 1 < len(closes):
                second_deriv = closes[i+1] - 2*closes[i] + closes[i-1]
                second_derivatives.append(abs(second_deriv))
        
        if not second_derivatives:
            return 0.5
        
        # Lower average second derivative = smoother curve
        avg_second_deriv = sum(second_derivatives) / len(second_derivatives)
        price_range = max(closes) - min(closes)
        
        if price_range == 0:
            return 1.0
        
        # Normalize and invert (lower = better)
        normalized_roughness = avg_second_deriv / price_range
        smoothness = max(0.0, 1.0 - normalized_roughness * 10)
        
        return smoothness
    
    def _calculate_cup_symmetry(self, closes: List[float], bottom_index: int) -> float:
        """Calculate symmetry of the cup formation."""
        if bottom_index <= 0 or bottom_index >= len(closes) - 1:
            return 0.0
        
        left_length = bottom_index
        right_length = len(closes) - bottom_index - 1
        
        # Compare lengths (should be roughly equal)
        length_ratio = min(left_length, right_length) / max(left_length, right_length)
        
        # Compare price movements
        left_movement = abs(closes[0] - closes[bottom_index])
        right_movement = abs(closes[-1] - closes[bottom_index])
        
        if max(left_movement, right_movement) == 0:
            movement_ratio = 1.0
        else:
            movement_ratio = min(left_movement, right_movement) / max(left_movement, right_movement)
        
        # Combine length and movement symmetry
        symmetry_score = (length_ratio * 0.6) + (movement_ratio * 0.4)
        
        return symmetry_score
    
    def _find_handle_formation(self, data: PriceDataFrame, cup: Dict, 
                             sensitivity: float) -> Optional[Dict]:
        """Find handle formation after cup."""
        cup_end = cup['end_index']
        max_handle_length = min(cup['length'] // 3, 20)  # Handle should be shorter than cup
        min_handle_length = 3
        
        if cup_end + min_handle_length >= len(data):
            return None
        
        closes = data.get_closes()
        highs = data.get_highs()
        lows = data.get_lows()
        volumes = data.get_volumes()
        
        for handle_length in range(min_handle_length, max_handle_length + 1):
            handle_end = cup_end + handle_length
            
            if handle_end >= len(data):
                break
            
            handle_closes = closes[cup_end:handle_end+1]
            handle_highs = highs[cup_end:handle_end+1]
            handle_lows = lows[cup_end:handle_end+1]
            handle_volumes = volumes[cup_end:handle_end+1]
            
            # Analyze handle characteristics
            handle_analysis = self._analyze_handle_shape(
                handle_closes, handle_highs, handle_lows, handle_volumes, cup
            )
            
            if handle_analysis['is_valid_handle']:
                return {
                    'start_index': cup_end,
                    'end_index': handle_end,
                    'length': handle_length,
                    'retracement_percent': handle_analysis['retracement_percent'],
                    'volume_decline': handle_analysis['volume_decline'],
                    'handle_score': handle_analysis['handle_score']
                }
        
        return None
    
    def _analyze_handle_shape(self, closes: List[float], highs: List[float], 
                            lows: List[float], volumes: List[float], cup: Dict) -> Dict:
        """Analyze if consolidation forms a valid handle."""
        if len(closes) < 3:
            return {'is_valid_handle': False}
        
        cup_right_rim = cup['right_rim']
        handle_low = min(l for l in lows if l is not None)
        
        # Calculate retracement from cup rim
        retracement_percent = (cup_right_rim - handle_low) / cup_right_rim if cup_right_rim > 0 else 0
        
        # Handle should retrace 10-50% of cup depth
        cup_depth_percent = cup['depth_percent']
        max_handle_retracement = cup_depth_percent * 0.5  # Max 50% of cup depth
        
        if retracement_percent < 0.05 or retracement_percent > max_handle_retracement:
            return {'is_valid_handle': False}
        
        # Check volume decline in handle
        valid_volumes = [v for v in volumes if v is not None and v > 0]
        volume_decline = len(valid_volumes) > 2 and valid_volumes[-1] < valid_volumes[0]
        
        # Check handle slope (should be sideways or slightly declining)
        handle_slope = (closes[-1] - closes[0]) / len(closes) if len(closes) > 1 else 0
        slope_appropriate = handle_slope <= 0.01  # Slightly declining or sideways
        
        # Calculate overall handle score
        handle_score = 0.0
        if 0.05 <= retracement_percent <= max_handle_retracement:
            handle_score += 0.4
        if volume_decline:
            handle_score += 0.3
        if slope_appropriate:
            handle_score += 0.3
        
        is_valid = handle_score >= 0.6
        
        return {
            'is_valid_handle': is_valid,
            'retracement_percent': retracement_percent,
            'volume_decline': volume_decline,
            'handle_score': handle_score
        }
    
    def _create_cup_handle_pattern(self, data: PriceDataFrame, cup: Dict, 
                                 handle: Dict, sensitivity: float) -> Optional[DetectedPattern]:
        """Create cup and handle pattern from cup and handle data."""
        
        # Calculate overall confidence
        confidence_factors = []
        
        # Cup quality
        confidence_factors.append(cup['u_shape_score'] * 0.4)
        confidence_factors.append(cup['symmetry_score'] * 0.2)
        
        # Handle quality
        confidence_factors.append(handle['handle_score'] * 0.3)
        
        # Volume pattern
        volume_profile = self._calculate_volume_profile(data, cup['start_index'], handle['end_index'])
        volume_score = 1.0 if volume_profile.volume_trend == "decreasing" else 0.5
        confidence_factors.append(volume_score * 0.1)
        
        base_confidence = sum(confidence_factors)
        
        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        final_confidence = max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
        
        if final_confidence < 0.4:
            return None
        
        # Determine pattern type (regular or inverted)
        pattern_type = PatternType.CUP_AND_HANDLE
        if cup['left_rim'] < cup['bottom']:  # Inverted cup
            pattern_type = PatternType.INVERTED_CUP_HANDLE
        
        pattern_category = PATTERN_CATEGORIES[pattern_type]
        
        return DetectedPattern(
            pattern_type=pattern_type,
            category=pattern_category,
            confidence=final_confidence,
            start_time=data[cup['start_index']].timestamp,
            end_time=data[handle['end_index']].timestamp,
            start_index=cup['start_index'],
            end_index=handle['end_index'],
            key_levels={
                'cup_left_rim': cup['left_rim'],
                'cup_right_rim': cup['right_rim'],
                'cup_bottom': cup['bottom'],
                'cup_depth_percent': cup['depth_percent'],
                'handle_low': data.get_lows()[handle['start_index']:handle['end_index']+1],
                'handle_retracement': handle['retracement_percent'],
                'breakout_level': cup['right_rim']
            },
            volume_profile=volume_profile,
            description=self._generate_cup_handle_description(pattern_type, final_confidence, cup, handle)
        )
    
    def _generate_cup_handle_description(self, pattern_type: PatternType, confidence: float,
                                       cup: Dict, handle: Dict) -> str:
        """Generate description for cup and handle pattern."""
        if pattern_type == PatternType.CUP_AND_HANDLE:
            base_desc = "Cup and Handle - bullish continuation pattern with U-shaped cup followed by small consolidation"
        else:
            base_desc = "Inverted Cup and Handle - bearish continuation pattern with inverted U-shape"
        
        confidence_level = "high" if confidence > 0.7 else "medium" if confidence > 0.5 else "low"
        
        return (f"{base_desc}. Cup depth: {cup['depth_percent']:.1%}, "
                f"Handle retracement: {handle['retracement_percent']:.1%}. "
                f"Confidence: {confidence_level} ({confidence:.1%}).")
    
    def detect_wedge_patterns(self, data: PriceDataFrame, 
                            sensitivity: float = 0.5) -> List[DetectedPattern]:
        """
        Detect rising and falling wedge patterns.
        
        Args:
            data: Price data frame
            sensitivity: Detection sensitivity (0.0 to 1.0)
            
        Returns:
            List of detected wedge patterns
        """
        if len(data) < self.min_pattern_length:
            return []
        
        patterns = []
        highs = data.get_highs()
        lows = data.get_lows()
        
        # Find peaks and troughs for wedge analysis
        high_peaks = [pt for pt in self.trend_analysis.find_peaks_and_troughs(highs, min_distance=3) 
                     if pt.type == 'peak']
        low_troughs = [pt for pt in self.trend_analysis.find_peaks_and_troughs(lows, min_distance=3) 
                      if pt.type == 'trough']
        
        if len(high_peaks) < 3 or len(low_troughs) < 3:
            return patterns
        
        # Analyze potential wedge formations
        wedge_candidates = self._find_wedge_candidates(high_peaks, low_troughs, data)
        
        for candidate in wedge_candidates:
            wedge_pattern = self._analyze_wedge_formation(data, candidate, sensitivity)
            if wedge_pattern:
                patterns.append(wedge_pattern)
        
        return self._filter_overlapping_patterns(patterns)
    
    def _find_wedge_candidates(self, high_peaks: List, low_troughs: List, 
                             data: PriceDataFrame) -> List[Dict]:
        """Find potential wedge formations from peaks and troughs."""
        candidates = []
        
        # Look for converging trend lines with same directional bias
        for i in range(len(high_peaks) - 2):
            for j in range(i + 2, len(high_peaks)):
                # Upper trend line from peaks
                peak1, peak2 = high_peaks[i], high_peaks[j]
                upper_slope = (peak2.value - peak1.value) / (peak2.index - peak1.index)
                
                # Find relevant troughs in the same time range
                relevant_troughs = [t for t in low_troughs 
                                  if peak1.index <= t.index <= peak2.index]
                
                if len(relevant_troughs) < 2:
                    continue
                
                # Try different trough combinations for lower trend line
                for k in range(len(relevant_troughs) - 1):
                    for l in range(k + 1, len(relevant_troughs)):
                        trough1, trough2 = relevant_troughs[k], relevant_troughs[l]
                        lower_slope = (trough2.value - trough1.value) / (trough2.index - trough1.index)
                        
                        # Check for wedge characteristics
                        wedge_type = self._classify_wedge_type(upper_slope, lower_slope)
                        if wedge_type:
                            candidates.append({
                                'type': wedge_type,
                                'peak1': peak1,
                                'peak2': peak2,
                                'trough1': trough1,
                                'trough2': trough2,
                                'upper_slope': upper_slope,
                                'lower_slope': lower_slope,
                                'start_index': min(peak1.index, trough1.index),
                                'end_index': max(peak2.index, trough2.index)
                            })
        
        return candidates
    
    def _classify_wedge_type(self, upper_slope: float, lower_slope: float) -> Optional[str]:
        """Classify wedge type based on trend line slopes."""
        slope_threshold = 0.001
        
        # Rising Wedge: both lines rising, but lower rises faster (converging upward)
        if (upper_slope > slope_threshold and lower_slope > slope_threshold and 
            lower_slope > upper_slope * 1.2):  # Lower slope significantly steeper
            return 'rising_wedge'
        
        # Falling Wedge: both lines falling, but upper falls faster (converging downward)  
        elif (upper_slope < -slope_threshold and lower_slope < -slope_threshold and
              upper_slope < lower_slope * 1.2):  # Upper slope more negative
            return 'falling_wedge'
        
        return None
    
    def _analyze_wedge_formation(self, data: PriceDataFrame, candidate: Dict, 
                               sensitivity: float) -> Optional[DetectedPattern]:
        """Analyze wedge candidate and create pattern if valid."""
        
        start_idx = candidate['start_index']
        end_idx = candidate['end_index']
        pattern_length = end_idx - start_idx
        
        # Validate pattern length
        if pattern_length < self.min_pattern_length or pattern_length > self.max_pattern_length:
            return None
        
        # Calculate convergence point
        convergence_index = self._calculate_convergence_point(
            candidate['upper_slope'], candidate['peak1'].value - candidate['upper_slope'] * candidate['peak1'].index,
            candidate['lower_slope'], candidate['trough1'].value - candidate['lower_slope'] * candidate['trough1'].index
        )
        
        # Validate convergence (should be reasonable)
        if not self._validate_wedge_convergence(convergence_index, start_idx, end_idx):
            return None
        
        # Calculate confidence
        confidence = self._calculate_wedge_confidence(data, candidate, sensitivity)
        
        if confidence < (0.3 + sensitivity * 0.3):
            return None
        
        # Determine pattern type and category
        wedge_type = candidate['type']
        if wedge_type == 'rising_wedge':
            # Rising wedge can be continuation (bearish) or reversal (bearish)
            pattern_type = PatternType.RISING_WEDGE_REVERSAL  # Default to reversal
        else:  # falling_wedge
            # Falling wedge can be continuation (bullish) or reversal (bullish)
            pattern_type = PatternType.FALLING_WEDGE_REVERSAL  # Default to reversal
        
        pattern_category = PATTERN_CATEGORIES[pattern_type]
        
        # Calculate volume profile
        volume_profile = self._calculate_volume_profile(data, start_idx, end_idx)
        
        return DetectedPattern(
            pattern_type=pattern_type,
            category=pattern_category,
            confidence=confidence,
            start_time=data[start_idx].timestamp,
            end_time=data[end_idx].timestamp,
            start_index=start_idx,
            end_index=end_idx,
            key_levels={
                'upper_slope': candidate['upper_slope'],
                'lower_slope': candidate['lower_slope'],
                'convergence_price': candidate['upper_slope'] * convergence_index + 
                                   (candidate['peak1'].value - candidate['upper_slope'] * candidate['peak1'].index),
                'upper_start': candidate['peak1'].value,
                'upper_end': candidate['peak2'].value,
                'lower_start': candidate['trough1'].value,
                'lower_end': candidate['trough2'].value
            },
            volume_profile=volume_profile,
            description=self._generate_wedge_description(pattern_type, confidence, wedge_type, pattern_length)
        )
    
    def _validate_wedge_convergence(self, convergence_index: float, 
                                  start_index: int, end_index: int) -> bool:
        """Validate wedge convergence point."""
        if convergence_index == float('inf'):
            return False
        
        pattern_length = end_index - start_index
        
        # Convergence should be within reasonable distance
        max_convergence = end_index + (pattern_length * 1.5)
        min_convergence = end_index - (pattern_length * 0.2)
        
        return min_convergence <= convergence_index <= max_convergence
    
    def _calculate_wedge_confidence(self, data: PriceDataFrame, candidate: Dict, 
                                  sensitivity: float) -> float:
        """Calculate confidence score for wedge pattern."""
        confidence_factors = []
        
        start_idx = candidate['start_index']
        end_idx = candidate['end_index']
        
        # 1. Trend line fit quality
        highs = data.get_highs()[start_idx:end_idx+1]
        lows = data.get_lows()[start_idx:end_idx+1]
        
        upper_fit = self._calculate_trendline_fit(
            highs, candidate['upper_slope'], 
            candidate['peak1'].value - candidate['upper_slope'] * candidate['peak1'].index,
            start_idx, 'resistance'
        )
        lower_fit = self._calculate_trendline_fit(
            lows, candidate['lower_slope'],
            candidate['trough1'].value - candidate['lower_slope'] * candidate['trough1'].index,
            start_idx, 'support'
        )
        
        confidence_factors.append(upper_fit * 0.3)
        confidence_factors.append(lower_fit * 0.3)
        
        # 2. Convergence quality
        convergence_score = self._score_wedge_convergence(candidate)
        confidence_factors.append(convergence_score * 0.2)
        
        # 3. Volume pattern (should decrease in wedges)
        volumes = data.get_volumes()[start_idx:end_idx+1]
        volume_score = self._analyze_triangle_volume_pattern(volumes)  # Reuse triangle volume analysis
        confidence_factors.append(volume_score * 0.1)
        
        # 4. Pattern length
        pattern_length = end_idx - start_idx
        length_score = self._score_pattern_length(pattern_length)
        confidence_factors.append(length_score * 0.1)
        
        base_confidence = sum(confidence_factors)
        
        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        final_confidence = max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
        
        return final_confidence
    
    def _score_wedge_convergence(self, candidate: Dict) -> float:
        """Score the quality of wedge convergence."""
        upper_slope = candidate['upper_slope']
        lower_slope = candidate['lower_slope']
        
        # Check slope relationship for wedge type
        wedge_type = candidate['type']
        
        if wedge_type == 'rising_wedge':
            # Both should be positive, lower should be steeper
            if upper_slope > 0 and lower_slope > 0 and lower_slope > upper_slope:
                slope_ratio = upper_slope / lower_slope
                return max(0.0, min(1.0, 1.0 - slope_ratio))  # Better when upper is much less steep
            else:
                return 0.0
        
        elif wedge_type == 'falling_wedge':
            # Both should be negative, upper should be steeper (more negative)
            if upper_slope < 0 and lower_slope < 0 and upper_slope < lower_slope:
                slope_ratio = lower_slope / upper_slope
                return max(0.0, min(1.0, 1.0 - slope_ratio))  # Better when lower is much less steep
            else:
                return 0.0
        
        return 0.0
    
    def _generate_wedge_description(self, pattern_type: PatternType, confidence: float,
                                  wedge_type: str, pattern_length: int) -> str:
        """Generate description for wedge pattern."""
        if wedge_type == 'rising_wedge':
            base_desc = "Rising Wedge - bearish reversal pattern with converging upward trend lines"
        else:
            base_desc = "Falling Wedge - bullish reversal pattern with converging downward trend lines"
        
        confidence_level = "high" if confidence > 0.7 else "medium" if confidence > 0.5 else "low"
        
        return (f"{base_desc}. Duration: {pattern_length} periods. "
                f"Confidence: {confidence_level} ({confidence:.1%}).")
    
    def detect_rectangle_and_channel_patterns(self, data: PriceDataFrame, 
                                            sensitivity: float = 0.5) -> List[DetectedPattern]:
        """
        Detect rectangle and channel patterns.
        
        Args:
            data: Price data frame
            sensitivity: Detection sensitivity (0.0 to 1.0)
            
        Returns:
            List of detected rectangle and channel patterns
        """
        if len(data) < self.min_pattern_length:
            return []
        
        patterns = []
        highs = data.get_highs()
        lows = data.get_lows()
        
        # Find support and resistance levels
        support_resistance = self.trend_analysis.find_support_resistance_levels(data)
        
        if not support_resistance['support'] or not support_resistance['resistance']:
            return patterns
        
        # Find horizontal channels (rectangles)
        rectangle_patterns = self._find_rectangle_patterns(data, support_resistance, sensitivity)
        patterns.extend(rectangle_patterns)
        
        # Find trending channels
        channel_patterns = self._find_trending_channels(data, sensitivity)
        patterns.extend(channel_patterns)
        
        return self._filter_overlapping_patterns(patterns)
    
    def _find_rectangle_patterns(self, data: PriceDataFrame, support_resistance: Dict,
                               sensitivity: float) -> List[DetectedPattern]:
        """Find horizontal rectangle patterns."""
        patterns = []
        
        for support_level in support_resistance['support']:
            for resistance_level in support_resistance['resistance']:
                if resistance_level <= support_level:
                    continue
                
                # Find price action within this range
                rectangle_data = self._analyze_rectangle_formation(
                    data, support_level, resistance_level, sensitivity
                )
                
                if rectangle_data:
                    patterns.append(rectangle_data)
        
        return patterns
    
    def _analyze_rectangle_formation(self, data: PriceDataFrame, support_level: float,
                                   resistance_level: float, sensitivity: float) -> Optional[DetectedPattern]:
        """Analyze if price action forms a rectangle pattern."""
        
        highs = data.get_highs()
        lows = data.get_lows()
        closes = data.get_closes()
        
        # Find periods where price is within the rectangle
        in_rectangle_indices = []
        
        for i, (high, low) in enumerate(zip(highs, lows)):
            if high is None or low is None:
                continue
            
            # Check if price action is within the rectangle bounds
            tolerance = (resistance_level - support_level) * 0.05  # 5% tolerance
            
            if (low >= support_level - tolerance and 
                high <= resistance_level + tolerance):
                in_rectangle_indices.append(i)
        
        if len(in_rectangle_indices) < self.min_pattern_length:
            return None
        
        # Find continuous rectangle periods
        rectangle_periods = self._find_continuous_periods(in_rectangle_indices)
        
        if not rectangle_periods:
            return None
        
        # Use the longest rectangle period
        best_period = max(rectangle_periods, key=lambda x: x[1] - x[0])
        start_idx, end_idx = best_period
        
        # Calculate confidence
        confidence = self._calculate_rectangle_confidence(
            data, start_idx, end_idx, support_level, resistance_level, sensitivity
        )
        
        if confidence < (0.3 + sensitivity * 0.3):
            return None
        
        # Determine pattern type based on breakout direction or trend context
        pattern_type = self._classify_rectangle_type(data, start_idx, end_idx)
        pattern_category = PATTERN_CATEGORIES[pattern_type]
        
        # Calculate volume profile
        volume_profile = self._calculate_volume_profile(data, start_idx, end_idx)
        
        return DetectedPattern(
            pattern_type=pattern_type,
            category=pattern_category,
            confidence=confidence,
            start_time=data[start_idx].timestamp,
            end_time=data[end_idx].timestamp,
            start_index=start_idx,
            end_index=end_idx,
            key_levels={
                'support_level': support_level,
                'resistance_level': resistance_level,
                'range_size': resistance_level - support_level,
                'range_percent': (resistance_level - support_level) / support_level * 100
            },
            volume_profile=volume_profile,
            description=self._generate_rectangle_description(pattern_type, confidence, 
                                                           resistance_level - support_level)
        )
    
    def _find_continuous_periods(self, indices: List[int]) -> List[Tuple[int, int]]:
        """Find continuous periods from list of indices."""
        if not indices:
            return []
        
        periods = []
        start = indices[0]
        prev = indices[0]
        
        for i in indices[1:]:
            if i - prev > 2:  # Gap of more than 2 periods breaks continuity
                if prev - start >= self.min_pattern_length:
                    periods.append((start, prev))
                start = i
            prev = i
        
        # Add the last period
        if prev - start >= self.min_pattern_length:
            periods.append((start, prev))
        
        return periods
    
    def _calculate_rectangle_confidence(self, data: PriceDataFrame, start_idx: int, end_idx: int,
                                      support_level: float, resistance_level: float,
                                      sensitivity: float) -> float:
        """Calculate confidence for rectangle pattern."""
        confidence_factors = []
        
        highs = data.get_highs()[start_idx:end_idx+1]
        lows = data.get_lows()[start_idx:end_idx+1]
        volumes = data.get_volumes()[start_idx:end_idx+1]
        
        # 1. Level respect (how well price respects support/resistance)
        level_respect_score = self._calculate_level_respect(highs, lows, support_level, resistance_level)
        confidence_factors.append(level_respect_score * 0.4)
        
        # 2. Number of touches on levels
        support_touches = self._count_level_touches(lows, support_level, tolerance=0.02)
        resistance_touches = self._count_level_touches(highs, resistance_level, tolerance=0.02)
        
        touch_score = min(1.0, (support_touches + resistance_touches - 4) / 6)  # Normalize
        confidence_factors.append(touch_score * 0.3)
        
        # 3. Pattern duration
        pattern_length = end_idx - start_idx
        length_score = self._score_pattern_length(pattern_length)
        confidence_factors.append(length_score * 0.2)
        
        # 4. Volume pattern (should be relatively stable)
        volume_score = self._analyze_rectangle_volume_pattern(volumes)
        confidence_factors.append(volume_score * 0.1)
        
        base_confidence = sum(confidence_factors)
        
        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        final_confidence = max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
        
        return final_confidence
    
    def _calculate_level_respect(self, highs: List[float], lows: List[float],
                               support_level: float, resistance_level: float) -> float:
        """Calculate how well price respects support and resistance levels."""
        violations = 0
        total_points = 0
        
        tolerance = (resistance_level - support_level) * 0.03  # 3% tolerance
        
        for high, low in zip(highs, lows):
            if high is None or low is None:
                continue
            
            total_points += 1
            
            # Check for violations
            if low < support_level - tolerance or high > resistance_level + tolerance:
                violations += 1
        
        if total_points == 0:
            return 0.0
        
        respect_ratio = 1.0 - (violations / total_points)
        return max(0.0, respect_ratio)
    
    def _count_level_touches(self, values: List[float], level: float, tolerance: float) -> int:
        """Count how many times price touches a level."""
        touches = 0
        
        for value in values:
            if value is None:
                continue
            
            if abs(value - level) / level <= tolerance:
                touches += 1
        
        return touches
    
    def _analyze_rectangle_volume_pattern(self, volumes: List[float]) -> float:
        """Analyze volume pattern in rectangle (should be relatively stable)."""
        if len(volumes) < 3:
            return 0.5
        
        valid_volumes = [v for v in volumes if v is not None and v > 0]
        if len(valid_volumes) < 3:
            return 0.5
        
        # Calculate volume stability (lower coefficient of variation is better)
        import statistics
        
        avg_volume = statistics.mean(valid_volumes)
        if avg_volume == 0:
            return 0.5
        
        volume_std = statistics.stdev(valid_volumes) if len(valid_volumes) > 1 else 0
        coefficient_of_variation = volume_std / avg_volume
        
        # Score based on stability (lower CV = higher score)
        stability_score = max(0.0, 1.0 - coefficient_of_variation)
        
        return min(1.0, stability_score)
    
    def _classify_rectangle_type(self, data: PriceDataFrame, start_idx: int, end_idx: int) -> PatternType:
        """Classify rectangle as bullish, bearish, or neutral based on context."""
        
        # Look at trend before the rectangle
        pre_trend_length = min(10, start_idx)
        if pre_trend_length < 3:
            return PatternType.RECTANGLE_NEUTRAL
        
        pre_trend_closes = data.get_closes()[start_idx - pre_trend_length:start_idx]
        
        if len(pre_trend_closes) < 3:
            return PatternType.RECTANGLE_NEUTRAL
        
        # Calculate trend direction
        trend_direction = self.trend_analysis.detect_trend_direction(pre_trend_closes, period=pre_trend_length)
        
        if trend_direction == 'uptrend':
            return PatternType.RECTANGLE_BULLISH  # Bullish continuation expected
        elif trend_direction == 'downtrend':
            return PatternType.RECTANGLE_BEARISH  # Bearish continuation expected
        else:
            return PatternType.RECTANGLE_NEUTRAL
    
    def _find_trending_channels(self, data: PriceDataFrame, sensitivity: float) -> List[DetectedPattern]:
        """Find trending channel patterns."""
        patterns = []
        
        # Use trend analysis to find channels
        channels = self.trend_analysis.find_trend_channels(data, min_touches=3)
        
        for channel in channels:
            channel_pattern = self._analyze_trending_channel(data, channel, sensitivity)
            if channel_pattern:
                patterns.append(channel_pattern)
        
        return patterns
    
    def _analyze_trending_channel(self, data: PriceDataFrame, channel: Dict,
                                sensitivity: float) -> Optional[DetectedPattern]:
        """Analyze trending channel and create pattern."""
        
        upper_line = channel['upper_line']
        lower_line = channel['lower_line']
        
        # Determine start and end indices from channel data
        start_idx = min(upper_line['start'][0], lower_line['start'][0])
        end_idx = max(upper_line['end'][0], lower_line['end'][0])
        
        # Calculate confidence based on channel quality
        confidence = self._calculate_channel_confidence(channel, sensitivity)
        
        if confidence < (0.4 + sensitivity * 0.3):
            return None
        
        # Determine channel type
        upper_slope = upper_line['slope']
        lower_slope = lower_line['slope']
        
        if upper_slope > 0.001 and lower_slope > 0.001:
            pattern_type = PatternType.RISING_CHANNEL
        elif upper_slope < -0.001 and lower_slope < -0.001:
            pattern_type = PatternType.FALLING_CHANNEL
        else:
            return None  # Not a clear trending channel
        
        pattern_category = PATTERN_CATEGORIES[pattern_type]
        
        # Calculate volume profile
        volume_profile = self._calculate_volume_profile(data, start_idx, end_idx)
        
        return DetectedPattern(
            pattern_type=pattern_type,
            category=pattern_category,
            confidence=confidence,
            start_time=data[start_idx].timestamp,
            end_time=data[end_idx].timestamp,
            start_index=start_idx,
            end_index=end_idx,
            key_levels={
                'upper_slope': upper_slope,
                'lower_slope': lower_slope,
                'channel_width': channel['width'],
                'touches': channel['touches'],
                'upper_start_price': upper_line['start'][1],
                'upper_end_price': upper_line['end'][1],
                'lower_start_price': lower_line['start'][1],
                'lower_end_price': lower_line['end'][1]
            },
            volume_profile=volume_profile,
            description=self._generate_channel_description(pattern_type, confidence, channel)
        )
    
    def _calculate_channel_confidence(self, channel: Dict, sensitivity: float) -> float:
        """Calculate confidence for trending channel."""
        confidence_factors = []
        
        # 1. Number of touches (more touches = higher confidence)
        touch_score = min(1.0, channel['touches'] / 8)  # Normalize to max 8 touches
        confidence_factors.append(touch_score * 0.4)
        
        # 2. Slope consistency
        upper_slope = channel['upper_line']['slope']
        lower_slope = channel['lower_line']['slope']
        
        if abs(upper_slope) > 0 and abs(lower_slope) > 0:
            slope_ratio = min(abs(upper_slope), abs(lower_slope)) / max(abs(upper_slope), abs(lower_slope))
            confidence_factors.append(slope_ratio * 0.3)
        else:
            confidence_factors.append(0.0)
        
        # 3. Channel width consistency
        width_score = 0.8 if channel['width'] > 0 else 0.0
        confidence_factors.append(width_score * 0.2)
        
        # 4. Pattern length
        start_x = min(channel['upper_line']['start'][0], channel['lower_line']['start'][0])
        end_x = max(channel['upper_line']['end'][0], channel['lower_line']['end'][0])
        pattern_length = end_x - start_x
        
        length_score = self._score_pattern_length(pattern_length)
        confidence_factors.append(length_score * 0.1)
        
        base_confidence = sum(confidence_factors)
        
        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        final_confidence = max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
        
        return final_confidence
    
    def _generate_rectangle_description(self, pattern_type: PatternType, confidence: float,
                                      range_size: float) -> str:
        """Generate description for rectangle pattern."""
        type_descriptions = {
            PatternType.RECTANGLE_BULLISH: "Bullish Rectangle - horizontal consolidation in uptrend, expecting upward breakout",
            PatternType.RECTANGLE_BEARISH: "Bearish Rectangle - horizontal consolidation in downtrend, expecting downward breakout",
            PatternType.RECTANGLE_NEUTRAL: "Rectangle - horizontal consolidation, breakout direction uncertain"
        }
        
        base_description = type_descriptions.get(pattern_type, "Rectangle pattern")
        confidence_level = "high" if confidence > 0.7 else "medium" if confidence > 0.5 else "low"
        
        return (f"{base_description}. Range size: {range_size:.2f}. "
                f"Confidence: {confidence_level} ({confidence:.1%}).")
    
    def _generate_channel_description(self, pattern_type: PatternType, confidence: float,
                                    channel: Dict) -> str:
        """Generate description for channel pattern."""
        if pattern_type == PatternType.RISING_CHANNEL:
            base_desc = "Rising Channel - upward trending parallel lines, bullish continuation pattern"
        else:
            base_desc = "Falling Channel - downward trending parallel lines, bearish continuation pattern"
        
        confidence_level = "high" if confidence > 0.7 else "medium" if confidence > 0.5 else "low"
        
        return (f"{base_desc}. Channel touches: {channel['touches']}. "
                f"Confidence: {confidence_level} ({confidence:.1%}).")