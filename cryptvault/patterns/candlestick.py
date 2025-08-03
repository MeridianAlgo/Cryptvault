"""Candlestick pattern detection algorithms."""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from ..data.models import PriceDataFrame, PricePoint
from .types import PatternType, PatternCategory, DetectedPattern, VolumeProfile, PATTERN_CATEGORIES


class CandlestickPatternAnalyzer:
    """Analyze candlestick patterns for reversal and continuation signals."""
    
    def __init__(self):
        """Initialize candlestick pattern analyzer."""
        self.min_body_ratio = 0.1  # Minimum body size relative to range
        self.doji_threshold = 0.05  # Maximum body size for doji (relative to range)
        self.long_candle_threshold = 0.7  # Minimum body size for long candles
    
    def detect_single_candlestick_patterns(self, data: PriceDataFrame,
                                         sensitivity: float = 0.5) -> List[DetectedPattern]:
        """
        Detect single candlestick patterns.
        
        Args:
            data: Price data frame
            sensitivity: Detection sensitivity (0.0 to 1.0)
            
        Returns:
            List of detected single candlestick patterns
        """
        if len(data) < 10:  # Need context for candlestick analysis
            return []
        
        patterns = []
        
        # Analyze each candlestick with context
        for i in range(2, len(data) - 2):  # Need 2 candles before and after for context
            candle = data[i]
            
            # Get context candles
            prev_candles = [data[j] for j in range(max(0, i-5), i)]
            next_candles = [data[j] for j in range(i+1, min(len(data), i+6))]
            
            # Detect various single candlestick patterns
            single_patterns = self._analyze_single_candle(
                candle, i, prev_candles, next_candles, data, sensitivity
            )
            
            patterns.extend(single_patterns)
        
        return self._filter_overlapping_patterns(patterns)
    
    def detect_multi_candlestick_patterns(self, data: PriceDataFrame,
                                        sensitivity: float = 0.5) -> List[DetectedPattern]:
        """
        Detect multi-candlestick patterns (2-3 candles).
        
        Args:
            data: Price data frame
            sensitivity: Detection sensitivity (0.0 to 1.0)
            
        Returns:
            List of detected multi-candlestick patterns
        """
        if len(data) < 10:  # Need sufficient data for multi-candle patterns
            return []
        
        patterns = []
        
        # Analyze 2-candle patterns
        for i in range(2, len(data) - 2):  # Need context before and after
            two_candle_patterns = self._analyze_two_candle_patterns(
                data, i, sensitivity
            )
            patterns.extend(two_candle_patterns)
        
        # Analyze 3-candle patterns
        for i in range(2, len(data) - 3):  # Need one more candle for 3-candle patterns
            three_candle_patterns = self._analyze_three_candle_patterns(
                data, i, sensitivity
            )
            patterns.extend(three_candle_patterns)
        
        return self._filter_overlapping_patterns(patterns)
    
    def _analyze_two_candle_patterns(self, data: PriceDataFrame, index: int,
                                   sensitivity: float) -> List[DetectedPattern]:
        """Analyze two-candle patterns starting at index."""
        patterns = []
        
        if index + 1 >= len(data):
            return patterns
        
        candle1 = data[index]
        candle2 = data[index + 1]
        
        # Get context
        prev_candles = [data[j] for j in range(max(0, index-3), index)]
        context = self._analyze_market_context(prev_candles, [])
        
        # Calculate candle statistics
        stats1 = self._calculate_candle_stats(candle1)
        stats2 = self._calculate_candle_stats(candle2)
        
        # Detect specific 2-candle patterns
        pattern_detectors = [
            self._detect_bullish_engulfing,
            self._detect_bearish_engulfing,
            self._detect_bullish_harami,
            self._detect_bearish_harami,
            self._detect_piercing_line,
            self._detect_dark_cloud_cover,
            self._detect_tweezer_tops,
            self._detect_tweezer_bottoms
        ]
        
        for detector in pattern_detectors:
            pattern = detector(candle1, candle2, index, stats1, stats2, context, data, sensitivity)
            if pattern:
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_three_candle_patterns(self, data: PriceDataFrame, index: int,
                                     sensitivity: float) -> List[DetectedPattern]:
        """Analyze three-candle patterns starting at index."""
        patterns = []
        
        if index + 2 >= len(data):
            return patterns
        
        candle1 = data[index]
        candle2 = data[index + 1]
        candle3 = data[index + 2]
        
        # Get context
        prev_candles = [data[j] for j in range(max(0, index-3), index)]
        context = self._analyze_market_context(prev_candles, [])
        
        # Calculate candle statistics
        stats1 = self._calculate_candle_stats(candle1)
        stats2 = self._calculate_candle_stats(candle2)
        stats3 = self._calculate_candle_stats(candle3)
        
        # Detect specific 3-candle patterns
        pattern_detectors = [
            self._detect_morning_star,
            self._detect_evening_star,
            self._detect_three_white_soldiers,
            self._detect_three_black_crows,
            self._detect_rising_three_methods,
            self._detect_falling_three_methods
        ]
        
        for detector in pattern_detectors:
            pattern = detector(candle1, candle2, candle3, index, stats1, stats2, stats3, context, data, sensitivity)
            if pattern:
                patterns.append(pattern)
        
        return patterns
    
    # Two-candle pattern detectors
    def _detect_bullish_engulfing(self, candle1: PricePoint, candle2: PricePoint, index: int,
                                stats1: Dict, stats2: Dict, context: Dict, data: PriceDataFrame,
                                sensitivity: float) -> Optional[DetectedPattern]:
        """Detect bullish engulfing pattern."""
        
        # Bullish engulfing characteristics:
        # - First candle is bearish
        # - Second candle is bullish and completely engulfs the first
        # - Appears after downtrend
        
        if (not stats1['is_bullish'] and  # First candle bearish
            stats2['is_bullish'] and      # Second candle bullish
            candle2.open < candle1.close and  # Second opens below first close
            candle2.close > candle1.open and  # Second closes above first open
            stats2['body_ratio'] > 0.5 and   # Second candle has substantial body
            context['trend'] in ['downtrend', 'sideways']):  # Appropriate context
            
            confidence = self._calculate_engulfing_confidence(
                candle1, candle2, stats1, stats2, context, sensitivity, bullish=True
            )
            
            if confidence >= (0.4 + sensitivity * 0.3):
                return self._create_multi_candlestick_pattern(
                    PatternType.BULLISH_ENGULFING, [candle1, candle2], index, index + 1,
                    confidence, data, "Bullish Engulfing - strong reversal signal"
                )
        
        return None
    
    def _detect_bearish_engulfing(self, candle1: PricePoint, candle2: PricePoint, index: int,
                                stats1: Dict, stats2: Dict, context: Dict, data: PriceDataFrame,
                                sensitivity: float) -> Optional[DetectedPattern]:
        """Detect bearish engulfing pattern."""
        
        # Bearish engulfing characteristics:
        # - First candle is bullish
        # - Second candle is bearish and completely engulfs the first
        # - Appears after uptrend
        
        if (stats1['is_bullish'] and      # First candle bullish
            not stats2['is_bullish'] and  # Second candle bearish
            candle2.open > candle1.close and  # Second opens above first close
            candle2.close < candle1.open and  # Second closes below first open
            stats2['body_ratio'] > 0.5 and   # Second candle has substantial body
            context['trend'] in ['uptrend', 'sideways']):  # Appropriate context
            
            confidence = self._calculate_engulfing_confidence(
                candle1, candle2, stats1, stats2, context, sensitivity, bullish=False
            )
            
            if confidence >= (0.4 + sensitivity * 0.3):
                return self._create_multi_candlestick_pattern(
                    PatternType.BEARISH_ENGULFING, [candle1, candle2], index, index + 1,
                    confidence, data, "Bearish Engulfing - strong reversal signal"
                )
        
        return None
    
    def _detect_bullish_harami(self, candle1: PricePoint, candle2: PricePoint, index: int,
                             stats1: Dict, stats2: Dict, context: Dict, data: PriceDataFrame,
                             sensitivity: float) -> Optional[DetectedPattern]:
        """Detect bullish harami pattern."""
        
        # Bullish harami characteristics:
        # - First candle is large and bearish
        # - Second candle is small and contained within first candle's body
        # - Appears after downtrend
        
        if (not stats1['is_bullish'] and  # First candle bearish
            stats1['body_ratio'] > 0.6 and   # First candle large
            candle2.open < candle1.open and  # Second contained within first
            candle2.close > candle1.close and
            stats2['body_ratio'] < stats1['body_ratio'] * 0.5 and  # Second much smaller
            context['trend'] in ['downtrend', 'sideways']):
            
            confidence = self._calculate_harami_confidence(
                candle1, candle2, stats1, stats2, context, sensitivity, bullish=True
            )
            
            if confidence >= (0.3 + sensitivity * 0.3):
                return self._create_multi_candlestick_pattern(
                    PatternType.BULLISH_HARAMI, [candle1, candle2], index, index + 1,
                    confidence, data, "Bullish Harami - potential reversal signal"
                )
        
        return None
    
    def _detect_bearish_harami(self, candle1: PricePoint, candle2: PricePoint, index: int,
                             stats1: Dict, stats2: Dict, context: Dict, data: PriceDataFrame,
                             sensitivity: float) -> Optional[DetectedPattern]:
        """Detect bearish harami pattern."""
        
        # Bearish harami characteristics:
        # - First candle is large and bullish
        # - Second candle is small and contained within first candle's body
        # - Appears after uptrend
        
        if (stats1['is_bullish'] and      # First candle bullish
            stats1['body_ratio'] > 0.6 and   # First candle large
            candle2.open > candle1.close and  # Second contained within first
            candle2.close < candle1.open and
            stats2['body_ratio'] < stats1['body_ratio'] * 0.5 and  # Second much smaller
            context['trend'] in ['uptrend', 'sideways']):
            
            confidence = self._calculate_harami_confidence(
                candle1, candle2, stats1, stats2, context, sensitivity, bullish=False
            )
            
            if confidence >= (0.3 + sensitivity * 0.3):
                return self._create_multi_candlestick_pattern(
                    PatternType.BEARISH_HARAMI, [candle1, candle2], index, index + 1,
                    confidence, data, "Bearish Harami - potential reversal signal"
                )
        
        return None
    
    def _detect_piercing_line(self, candle1: PricePoint, candle2: PricePoint, index: int,
                            stats1: Dict, stats2: Dict, context: Dict, data: PriceDataFrame,
                            sensitivity: float) -> Optional[DetectedPattern]:
        """Detect piercing line pattern."""
        
        # Piercing line characteristics:
        # - First candle is bearish
        # - Second candle opens below first's low, closes above first's midpoint
        # - Appears after downtrend
        
        if (not stats1['is_bullish'] and  # First candle bearish
            stats2['is_bullish'] and      # Second candle bullish
            candle2.open < candle1.low and   # Second opens below first's low
            candle2.close > (candle1.open + candle1.close) / 2 and  # Closes above midpoint
            stats1['body_ratio'] > 0.4 and   # First candle substantial
            stats2['body_ratio'] > 0.4 and   # Second candle substantial
            context['trend'] in ['downtrend', 'sideways']):
            
            confidence = self._calculate_piercing_confidence(
                candle1, candle2, stats1, stats2, context, sensitivity
            )
            
            if confidence >= (0.4 + sensitivity * 0.3):
                return self._create_multi_candlestick_pattern(
                    PatternType.PIERCING_LINE, [candle1, candle2], index, index + 1,
                    confidence, data, "Piercing Line - bullish reversal signal"
                )
        
        return None
    
    def _detect_dark_cloud_cover(self, candle1: PricePoint, candle2: PricePoint, index: int,
                               stats1: Dict, stats2: Dict, context: Dict, data: PriceDataFrame,
                               sensitivity: float) -> Optional[DetectedPattern]:
        """Detect dark cloud cover pattern."""
        
        # Dark cloud cover characteristics:
        # - First candle is bullish
        # - Second candle opens above first's high, closes below first's midpoint
        # - Appears after uptrend
        
        if (stats1['is_bullish'] and      # First candle bullish
            not stats2['is_bullish'] and  # Second candle bearish
            candle2.open > candle1.high and   # Second opens above first's high
            candle2.close < (candle1.open + candle1.close) / 2 and  # Closes below midpoint
            stats1['body_ratio'] > 0.4 and   # First candle substantial
            stats2['body_ratio'] > 0.4 and   # Second candle substantial
            context['trend'] in ['uptrend', 'sideways']):
            
            confidence = self._calculate_dark_cloud_confidence(
                candle1, candle2, stats1, stats2, context, sensitivity
            )
            
            if confidence >= (0.4 + sensitivity * 0.3):
                return self._create_multi_candlestick_pattern(
                    PatternType.DARK_CLOUD_COVER, [candle1, candle2], index, index + 1,
                    confidence, data, "Dark Cloud Cover - bearish reversal signal"
                )
        
        return None
    
    def _detect_tweezer_tops(self, candle1: PricePoint, candle2: PricePoint, index: int,
                           stats1: Dict, stats2: Dict, context: Dict, data: PriceDataFrame,
                           sensitivity: float) -> Optional[DetectedPattern]:
        """Detect tweezer tops pattern."""
        
        # Tweezer tops characteristics:
        # - Two candles with similar highs
        # - Appears after uptrend
        # - Bearish reversal signal
        
        high_diff = abs(candle1.high - candle2.high)
        avg_range = (stats1['total_range'] + stats2['total_range']) / 2
        
        if (high_diff <= avg_range * 0.02 and  # Similar highs (within 2% of average range)
            context['trend'] in ['uptrend', 'sideways'] and
            avg_range > 0):  # Valid range
            
            confidence = self._calculate_tweezer_confidence(
                candle1, candle2, stats1, stats2, context, sensitivity, tops=True
            )
            
            if confidence >= (0.3 + sensitivity * 0.3):
                return self._create_multi_candlestick_pattern(
                    PatternType.TWEEZER_TOPS, [candle1, candle2], index, index + 1,
                    confidence, data, "Tweezer Tops - bearish reversal signal"
                )
        
        return None
    
    def _detect_tweezer_bottoms(self, candle1: PricePoint, candle2: PricePoint, index: int,
                              stats1: Dict, stats2: Dict, context: Dict, data: PriceDataFrame,
                              sensitivity: float) -> Optional[DetectedPattern]:
        """Detect tweezer bottoms pattern."""
        
        # Tweezer bottoms characteristics:
        # - Two candles with similar lows
        # - Appears after downtrend
        # - Bullish reversal signal
        
        low_diff = abs(candle1.low - candle2.low)
        avg_range = (stats1['total_range'] + stats2['total_range']) / 2
        
        if (low_diff <= avg_range * 0.02 and  # Similar lows (within 2% of average range)
            context['trend'] in ['downtrend', 'sideways'] and
            avg_range > 0):  # Valid range
            
            confidence = self._calculate_tweezer_confidence(
                candle1, candle2, stats1, stats2, context, sensitivity, tops=False
            )
            
            if confidence >= (0.3 + sensitivity * 0.3):
                return self._create_multi_candlestick_pattern(
                    PatternType.TWEEZER_BOTTOMS, [candle1, candle2], index, index + 1,
                    confidence, data, "Tweezer Bottoms - bullish reversal signal"
                )
        
        return None
    
    # Three-candle pattern detectors
    def _detect_morning_star(self, candle1: PricePoint, candle2: PricePoint, candle3: PricePoint,
                           index: int, stats1: Dict, stats2: Dict, stats3: Dict, context: Dict,
                           data: PriceDataFrame, sensitivity: float) -> Optional[DetectedPattern]:
        """Detect morning star pattern."""
        
        # Morning star characteristics:
        # - First candle: large bearish
        # - Second candle: small (star) - gaps down
        # - Third candle: large bullish - gaps up and closes well into first candle
        
        if (not stats1['is_bullish'] and  # First bearish
            stats3['is_bullish'] and      # Third bullish
            stats1['body_ratio'] > 0.5 and   # First large
            stats3['body_ratio'] > 0.5 and   # Third large
            stats2['body_ratio'] < 0.3 and   # Second small (star)
            candle2.high < candle1.close and  # Gap down
            candle3.open > candle2.high and   # Gap up
            candle3.close > (candle1.open + candle1.close) / 2 and  # Third closes well into first
            context['trend'] in ['downtrend', 'sideways']):
            
            confidence = self._calculate_star_confidence(
                candle1, candle2, candle3, stats1, stats2, stats3, context, sensitivity, morning=True
            )
            
            if confidence >= (0.4 + sensitivity * 0.3):
                return self._create_multi_candlestick_pattern(
                    PatternType.MORNING_STAR, [candle1, candle2, candle3], index, index + 2,
                    confidence, data, "Morning Star - strong bullish reversal signal"
                )
        
        return None
    
    def _detect_evening_star(self, candle1: PricePoint, candle2: PricePoint, candle3: PricePoint,
                           index: int, stats1: Dict, stats2: Dict, stats3: Dict, context: Dict,
                           data: PriceDataFrame, sensitivity: float) -> Optional[DetectedPattern]:
        """Detect evening star pattern."""
        
        # Evening star characteristics:
        # - First candle: large bullish
        # - Second candle: small (star) - gaps up
        # - Third candle: large bearish - gaps down and closes well into first candle
        
        if (stats1['is_bullish'] and      # First bullish
            not stats3['is_bullish'] and  # Third bearish
            stats1['body_ratio'] > 0.5 and   # First large
            stats3['body_ratio'] > 0.5 and   # Third large
            stats2['body_ratio'] < 0.3 and   # Second small (star)
            candle2.low > candle1.close and   # Gap up
            candle3.open < candle2.low and    # Gap down
            candle3.close < (candle1.open + candle1.close) / 2 and  # Third closes well into first
            context['trend'] in ['uptrend', 'sideways']):
            
            confidence = self._calculate_star_confidence(
                candle1, candle2, candle3, stats1, stats2, stats3, context, sensitivity, morning=False
            )
            
            if confidence >= (0.4 + sensitivity * 0.3):
                return self._create_multi_candlestick_pattern(
                    PatternType.EVENING_STAR, [candle1, candle2, candle3], index, index + 2,
                    confidence, data, "Evening Star - strong bearish reversal signal"
                )
        
        return None
    
    def _detect_three_white_soldiers(self, candle1: PricePoint, candle2: PricePoint, candle3: PricePoint,
                                   index: int, stats1: Dict, stats2: Dict, stats3: Dict, context: Dict,
                                   data: PriceDataFrame, sensitivity: float) -> Optional[DetectedPattern]:
        """Detect three white soldiers pattern."""
        
        # Three white soldiers characteristics:
        # - Three consecutive bullish candles
        # - Each opens within previous body and closes higher
        # - Strong bullish continuation/reversal
        
        if (stats1['is_bullish'] and stats2['is_bullish'] and stats3['is_bullish'] and  # All bullish
            stats1['body_ratio'] > 0.4 and stats2['body_ratio'] > 0.4 and stats3['body_ratio'] > 0.4 and  # All substantial
            candle2.open > candle1.open and candle2.open < candle1.close and  # Second opens in first body
            candle3.open > candle2.open and candle3.open < candle2.close and  # Third opens in second body
            candle2.close > candle1.close and candle3.close > candle2.close):  # Progressive closes
            
            confidence = self._calculate_soldiers_crows_confidence(
                candle1, candle2, candle3, stats1, stats2, stats3, context, sensitivity, bullish=True
            )
            
            if confidence >= (0.4 + sensitivity * 0.3):
                return self._create_multi_candlestick_pattern(
                    PatternType.THREE_WHITE_SOLDIERS, [candle1, candle2, candle3], index, index + 2,
                    confidence, data, "Three White Soldiers - strong bullish signal"
                )
        
        return None
    
    def _detect_three_black_crows(self, candle1: PricePoint, candle2: PricePoint, candle3: PricePoint,
                                index: int, stats1: Dict, stats2: Dict, stats3: Dict, context: Dict,
                                data: PriceDataFrame, sensitivity: float) -> Optional[DetectedPattern]:
        """Detect three black crows pattern."""
        
        # Three black crows characteristics:
        # - Three consecutive bearish candles
        # - Each opens within previous body and closes lower
        # - Strong bearish continuation/reversal
        
        if (not stats1['is_bullish'] and not stats2['is_bullish'] and not stats3['is_bullish'] and  # All bearish
            stats1['body_ratio'] > 0.4 and stats2['body_ratio'] > 0.4 and stats3['body_ratio'] > 0.4 and  # All substantial
            candle2.open < candle1.open and candle2.open > candle1.close and  # Second opens in first body
            candle3.open < candle2.open and candle3.open > candle2.close and  # Third opens in second body
            candle2.close < candle1.close and candle3.close < candle2.close):  # Progressive closes
            
            confidence = self._calculate_soldiers_crows_confidence(
                candle1, candle2, candle3, stats1, stats2, stats3, context, sensitivity, bullish=False
            )
            
            if confidence >= (0.4 + sensitivity * 0.3):
                return self._create_multi_candlestick_pattern(
                    PatternType.THREE_BLACK_CROWS, [candle1, candle2, candle3], index, index + 2,
                    confidence, data, "Three Black Crows - strong bearish signal"
                )
        
        return None
    
    def _detect_rising_three_methods(self, candle1: PricePoint, candle2: PricePoint, candle3: PricePoint,
                                   index: int, stats1: Dict, stats2: Dict, stats3: Dict, context: Dict,
                                   data: PriceDataFrame, sensitivity: float) -> Optional[DetectedPattern]:
        """Detect rising three methods pattern."""
        
        # Rising three methods characteristics:
        # - First candle: large bullish
        # - Second candle: small bearish (pullback)
        # - Third candle: large bullish (continuation)
        # - Bullish continuation pattern
        
        if (stats1['is_bullish'] and      # First bullish
            not stats2['is_bullish'] and  # Second bearish (pullback)
            stats3['is_bullish'] and      # Third bullish
            stats1['body_ratio'] > 0.5 and   # First large
            stats3['body_ratio'] > 0.5 and   # Third large
            stats2['body_ratio'] < 0.4 and   # Second smaller
            candle2.close > candle1.open and  # Pullback stays above first open
            candle3.close > candle1.close and  # Third closes higher than first
            context['trend'] in ['uptrend', 'sideways']):
            
            confidence = self._calculate_three_methods_confidence(
                candle1, candle2, candle3, stats1, stats2, stats3, context, sensitivity, rising=True
            )
            
            if confidence >= (0.3 + sensitivity * 0.3):
                return self._create_multi_candlestick_pattern(
                    PatternType.RISING_THREE_METHODS, [candle1, candle2, candle3], index, index + 2,
                    confidence, data, "Rising Three Methods - bullish continuation"
                )
        
        return None
    
    def _detect_falling_three_methods(self, candle1: PricePoint, candle2: PricePoint, candle3: PricePoint,
                                    index: int, stats1: Dict, stats2: Dict, stats3: Dict, context: Dict,
                                    data: PriceDataFrame, sensitivity: float) -> Optional[DetectedPattern]:
        """Detect falling three methods pattern."""
        
        # Falling three methods characteristics:
        # - First candle: large bearish
        # - Second candle: small bullish (pullback)
        # - Third candle: large bearish (continuation)
        # - Bearish continuation pattern
        
        if (not stats1['is_bullish'] and  # First bearish
            stats2['is_bullish'] and      # Second bullish (pullback)
            not stats3['is_bullish'] and  # Third bearish
            stats1['body_ratio'] > 0.5 and   # First large
            stats3['body_ratio'] > 0.5 and   # Third large
            stats2['body_ratio'] < 0.4 and   # Second smaller
            candle2.close < candle1.open and  # Pullback stays below first open
            candle3.close < candle1.close and  # Third closes lower than first
            context['trend'] in ['downtrend', 'sideways']):
            
            confidence = self._calculate_three_methods_confidence(
                candle1, candle2, candle3, stats1, stats2, stats3, context, sensitivity, rising=False
            )
            
            if confidence >= (0.3 + sensitivity * 0.3):
                return self._create_multi_candlestick_pattern(
                    PatternType.FALLING_THREE_METHODS, [candle1, candle2, candle3], index, index + 2,
                    confidence, data, "Falling Three Methods - bearish continuation"
                )
        
        return None
    
    def _analyze_single_candle(self, candle: PricePoint, index: int,
                             prev_candles: List[PricePoint], next_candles: List[PricePoint],
                             data: PriceDataFrame, sensitivity: float) -> List[DetectedPattern]:
        """Analyze a single candle for patterns."""
        patterns = []
        
        # Calculate candle characteristics
        candle_stats = self._calculate_candle_stats(candle)
        
        # Get market context
        context = self._analyze_market_context(prev_candles, next_candles)
        
        # Detect specific patterns
        pattern_detectors = [
            self._detect_hammer,
            self._detect_shooting_star,
            self._detect_doji,
            self._detect_spinning_top,
            self._detect_marubozu,
            self._detect_gravestone_doji
        ]
        
        for detector in pattern_detectors:
            pattern = detector(candle, index, candle_stats, context, data, sensitivity)
            if pattern:
                patterns.append(pattern)
        
        return patterns
    
    def _calculate_candle_stats(self, candle: PricePoint) -> Dict:
        """Calculate statistical properties of a candlestick."""
        
        body_size = abs(candle.close - candle.open)
        total_range = candle.high - candle.low
        upper_wick = candle.high - max(candle.open, candle.close)
        lower_wick = min(candle.open, candle.close) - candle.low
        
        # Avoid division by zero
        if total_range == 0:
            return {
                'body_ratio': 0,
                'upper_wick_ratio': 0,
                'lower_wick_ratio': 0,
                'is_bullish': candle.close >= candle.open,
                'body_size': body_size,
                'total_range': total_range,
                'upper_wick': upper_wick,
                'lower_wick': lower_wick
            }
        
        return {
            'body_ratio': body_size / total_range,
            'upper_wick_ratio': upper_wick / total_range,
            'lower_wick_ratio': lower_wick / total_range,
            'is_bullish': candle.close >= candle.open,
            'body_size': body_size,
            'total_range': total_range,
            'upper_wick': upper_wick,
            'lower_wick': lower_wick
        }
    
    def _analyze_market_context(self, prev_candles: List[PricePoint], 
                              next_candles: List[PricePoint]) -> Dict:
        """Analyze market context around the candle."""
        
        if not prev_candles:
            return {'trend': 'neutral', 'volatility': 'normal'}
        
        # Determine trend from previous candles
        prev_closes = [c.close for c in prev_candles]
        
        if len(prev_closes) >= 3:
            if prev_closes[-1] > prev_closes[-3]:
                trend = 'uptrend'
            elif prev_closes[-1] < prev_closes[-3]:
                trend = 'downtrend'
            else:
                trend = 'sideways'
        else:
            trend = 'neutral'
        
        # Calculate average volatility
        prev_ranges = [c.high - c.low for c in prev_candles]
        avg_range = sum(prev_ranges) / len(prev_ranges) if prev_ranges else 0
        
        return {
            'trend': trend,
            'avg_range': avg_range,
            'prev_closes': prev_closes
        }
    
    def _detect_hammer(self, candle: PricePoint, index: int, stats: Dict, context: Dict,
                      data: PriceDataFrame, sensitivity: float) -> Optional[DetectedPattern]:
        """Detect hammer candlestick pattern."""
        
        # Hammer characteristics:
        # - Small body at upper end of range
        # - Long lower wick (at least 2x body size)
        # - Little or no upper wick
        # - Appears after downtrend
        
        if (stats['lower_wick_ratio'] >= 0.6 and  # Long lower wick
            stats['body_ratio'] <= 0.3 and        # Small body
            stats['upper_wick_ratio'] <= 0.1 and  # Little upper wick
            context['trend'] in ['downtrend', 'sideways']):  # Appropriate context
            
            # Calculate confidence
            confidence = self._calculate_hammer_confidence(stats, context, sensitivity)
            
            if confidence >= (0.4 + sensitivity * 0.3):
                return self._create_candlestick_pattern(
                    PatternType.HAMMER, candle, index, confidence, data,
                    f"Hammer pattern - bullish reversal signal. Lower wick: {stats['lower_wick_ratio']:.1%} of range"
                )
        
        return None
    
    def _detect_shooting_star(self, candle: PricePoint, index: int, stats: Dict, context: Dict,
                            data: PriceDataFrame, sensitivity: float) -> Optional[DetectedPattern]:
        """Detect shooting star candlestick pattern."""
        
        # Shooting star characteristics:
        # - Small body at lower end of range
        # - Long upper wick (at least 2x body size)
        # - Little or no lower wick
        # - Appears after uptrend
        
        if (stats['upper_wick_ratio'] >= 0.6 and  # Long upper wick
            stats['body_ratio'] <= 0.3 and        # Small body
            stats['lower_wick_ratio'] <= 0.1 and  # Little lower wick
            context['trend'] in ['uptrend', 'sideways']):  # Appropriate context
            
            # Calculate confidence
            confidence = self._calculate_shooting_star_confidence(stats, context, sensitivity)
            
            if confidence >= (0.4 + sensitivity * 0.3):
                return self._create_candlestick_pattern(
                    PatternType.SHOOTING_STAR, candle, index, confidence, data,
                    f"Shooting Star pattern - bearish reversal signal. Upper wick: {stats['upper_wick_ratio']:.1%} of range"
                )
        
        return None
    
    def _detect_doji(self, candle: PricePoint, index: int, stats: Dict, context: Dict,
                    data: PriceDataFrame, sensitivity: float) -> Optional[DetectedPattern]:
        """Detect doji candlestick pattern."""
        
        # Doji characteristics:
        # - Very small body (open ≈ close)
        # - Can have wicks of any length
        # - Indicates indecision
        
        if stats['body_ratio'] <= self.doji_threshold:
            
            # Calculate confidence
            confidence = self._calculate_doji_confidence(stats, context, sensitivity)
            
            if confidence >= (0.3 + sensitivity * 0.3):
                return self._create_candlestick_pattern(
                    PatternType.DOJI, candle, index, confidence, data,
                    f"Doji pattern - market indecision. Body: {stats['body_ratio']:.1%} of range"
                )
        
        return None
    
    def _detect_spinning_top(self, candle: PricePoint, index: int, stats: Dict, context: Dict,
                           data: PriceDataFrame, sensitivity: float) -> Optional[DetectedPattern]:
        """Detect spinning top candlestick pattern."""
        
        # Spinning top characteristics:
        # - Small body (but larger than doji)
        # - Long upper and lower wicks
        # - Indicates indecision
        
        if (self.doji_threshold < stats['body_ratio'] <= 0.3 and  # Small but visible body
            stats['upper_wick_ratio'] >= 0.3 and                  # Decent upper wick
            stats['lower_wick_ratio'] >= 0.3):                    # Decent lower wick
            
            # Calculate confidence
            confidence = self._calculate_spinning_top_confidence(stats, context, sensitivity)
            
            if confidence >= (0.3 + sensitivity * 0.3):
                return self._create_candlestick_pattern(
                    PatternType.SPINNING_TOP, candle, index, confidence, data,
                    f"Spinning Top pattern - market indecision. Body: {stats['body_ratio']:.1%}, wicks: {stats['upper_wick_ratio']:.1%}/{stats['lower_wick_ratio']:.1%}"
                )
        
        return None
    
    def _detect_marubozu(self, candle: PricePoint, index: int, stats: Dict, context: Dict,
                        data: PriceDataFrame, sensitivity: float) -> Optional[DetectedPattern]:
        """Detect marubozu candlestick pattern."""
        
        # Marubozu characteristics:
        # - Large body with little or no wicks
        # - Strong directional movement
        
        if (stats['body_ratio'] >= 0.8 and  # Large body
            stats['upper_wick_ratio'] <= 0.1 and  # Little upper wick
            stats['lower_wick_ratio'] <= 0.1):     # Little lower wick
            
            # Calculate confidence
            confidence = self._calculate_marubozu_confidence(stats, context, sensitivity)
            
            if confidence >= (0.4 + sensitivity * 0.3):
                return self._create_candlestick_pattern(
                    PatternType.MARUBOZU, candle, index, confidence, data,
                    f"Marubozu pattern - strong {'bullish' if stats['is_bullish'] else 'bearish'} momentum. Body: {stats['body_ratio']:.1%} of range"
                )
        
        return None
    
    def _detect_gravestone_doji(self, candle: PricePoint, index: int, stats: Dict, context: Dict,
                              data: PriceDataFrame, sensitivity: float) -> Optional[DetectedPattern]:
        """Detect gravestone doji candlestick pattern."""
        
        # Gravestone doji characteristics:
        # - Very small body (doji)
        # - Long upper wick
        # - Little or no lower wick
        # - Bearish reversal signal
        
        if (stats['body_ratio'] <= self.doji_threshold and  # Doji body
            stats['upper_wick_ratio'] >= 0.7 and            # Long upper wick
            stats['lower_wick_ratio'] <= 0.1 and            # Little lower wick
            context['trend'] in ['uptrend', 'sideways']):   # Appropriate context
            
            # Calculate confidence
            confidence = self._calculate_gravestone_doji_confidence(stats, context, sensitivity)
            
            if confidence >= (0.4 + sensitivity * 0.3):
                return self._create_candlestick_pattern(
                    PatternType.GRAVESTONE_DOJI, candle, index, confidence, data,
                    f"Gravestone Doji pattern - bearish reversal signal. Upper wick: {stats['upper_wick_ratio']:.1%} of range"
                )
        
        return None
    
    def _calculate_hammer_confidence(self, stats: Dict, context: Dict, sensitivity: float) -> float:
        """Calculate confidence for hammer pattern."""
        confidence_factors = []
        
        # 1. Lower wick length (longer is better)
        wick_score = min(1.0, stats['lower_wick_ratio'] / 0.7)
        confidence_factors.append(wick_score * 0.4)
        
        # 2. Body size (smaller is better for hammer)
        body_score = 1.0 - min(1.0, stats['body_ratio'] / 0.3)
        confidence_factors.append(body_score * 0.3)
        
        # 3. Context appropriateness (downtrend is better)
        context_score = 1.0 if context['trend'] == 'downtrend' else 0.7 if context['trend'] == 'sideways' else 0.3
        confidence_factors.append(context_score * 0.2)
        
        # 4. Upper wick absence (smaller is better)
        upper_wick_score = 1.0 - min(1.0, stats['upper_wick_ratio'] / 0.1)
        confidence_factors.append(upper_wick_score * 0.1)
        
        base_confidence = sum(confidence_factors)
        
        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        return max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
    
    def _calculate_shooting_star_confidence(self, stats: Dict, context: Dict, sensitivity: float) -> float:
        """Calculate confidence for shooting star pattern."""
        confidence_factors = []
        
        # 1. Upper wick length (longer is better)
        wick_score = min(1.0, stats['upper_wick_ratio'] / 0.7)
        confidence_factors.append(wick_score * 0.4)
        
        # 2. Body size (smaller is better)
        body_score = 1.0 - min(1.0, stats['body_ratio'] / 0.3)
        confidence_factors.append(body_score * 0.3)
        
        # 3. Context appropriateness (uptrend is better)
        context_score = 1.0 if context['trend'] == 'uptrend' else 0.7 if context['trend'] == 'sideways' else 0.3
        confidence_factors.append(context_score * 0.2)
        
        # 4. Lower wick absence (smaller is better)
        lower_wick_score = 1.0 - min(1.0, stats['lower_wick_ratio'] / 0.1)
        confidence_factors.append(lower_wick_score * 0.1)
        
        base_confidence = sum(confidence_factors)
        
        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        return max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
    
    def _calculate_doji_confidence(self, stats: Dict, context: Dict, sensitivity: float) -> float:
        """Calculate confidence for doji pattern."""
        confidence_factors = []
        
        # 1. Body size (smaller is better)
        body_score = 1.0 - min(1.0, stats['body_ratio'] / self.doji_threshold)
        confidence_factors.append(body_score * 0.6)
        
        # 2. Context (more significant in trending markets)
        context_score = 0.8 if context['trend'] in ['uptrend', 'downtrend'] else 0.5
        confidence_factors.append(context_score * 0.4)
        
        base_confidence = sum(confidence_factors)
        
        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        return max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
    
    def _calculate_spinning_top_confidence(self, stats: Dict, context: Dict, sensitivity: float) -> float:
        """Calculate confidence for spinning top pattern."""
        confidence_factors = []
        
        # 1. Wick balance (both wicks should be significant)
        wick_balance = 1.0 - abs(stats['upper_wick_ratio'] - stats['lower_wick_ratio'])
        confidence_factors.append(wick_balance * 0.4)
        
        # 2. Body size (should be small but visible)
        ideal_body_ratio = 0.2
        body_score = 1.0 - abs(stats['body_ratio'] - ideal_body_ratio) / ideal_body_ratio
        confidence_factors.append(max(0.0, body_score) * 0.3)
        
        # 3. Total wick length
        total_wick_ratio = stats['upper_wick_ratio'] + stats['lower_wick_ratio']
        wick_score = min(1.0, total_wick_ratio / 0.6)
        confidence_factors.append(wick_score * 0.3)
        
        base_confidence = sum(confidence_factors)
        
        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        return max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
    
    def _calculate_marubozu_confidence(self, stats: Dict, context: Dict, sensitivity: float) -> float:
        """Calculate confidence for marubozu pattern."""
        confidence_factors = []
        
        # 1. Body size (larger is better)
        body_score = min(1.0, stats['body_ratio'] / 0.9)
        confidence_factors.append(body_score * 0.5)
        
        # 2. Wick absence (smaller wicks are better)
        total_wick_ratio = stats['upper_wick_ratio'] + stats['lower_wick_ratio']
        wick_score = 1.0 - min(1.0, total_wick_ratio / 0.2)
        confidence_factors.append(wick_score * 0.3)
        
        # 3. Context (continuation patterns work better in trends)
        context_score = 0.9 if context['trend'] in ['uptrend', 'downtrend'] else 0.6
        confidence_factors.append(context_score * 0.2)
        
        base_confidence = sum(confidence_factors)
        
        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        return max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
    
    def _calculate_gravestone_doji_confidence(self, stats: Dict, context: Dict, sensitivity: float) -> float:
        """Calculate confidence for gravestone doji pattern."""
        confidence_factors = []
        
        # 1. Upper wick length (longer is better)
        wick_score = min(1.0, stats['upper_wick_ratio'] / 0.8)
        confidence_factors.append(wick_score * 0.4)
        
        # 2. Body size (smaller is better)
        body_score = 1.0 - min(1.0, stats['body_ratio'] / self.doji_threshold)
        confidence_factors.append(body_score * 0.3)
        
        # 3. Context appropriateness (uptrend is better for bearish reversal)
        context_score = 1.0 if context['trend'] == 'uptrend' else 0.7 if context['trend'] == 'sideways' else 0.3
        confidence_factors.append(context_score * 0.2)
        
        # 4. Lower wick absence
        lower_wick_score = 1.0 - min(1.0, stats['lower_wick_ratio'] / 0.1)
        confidence_factors.append(lower_wick_score * 0.1)
        
        base_confidence = sum(confidence_factors)
        
        # Adjust for sensitivity
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        return max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
    
    # Multi-candlestick confidence calculations
    def _calculate_engulfing_confidence(self, candle1: PricePoint, candle2: PricePoint,
                                      stats1: Dict, stats2: Dict, context: Dict,
                                      sensitivity: float, bullish: bool) -> float:
        """Calculate confidence for engulfing patterns."""
        confidence_factors = []
        
        # 1. Engulfment completeness
        engulf_ratio = stats2['body_size'] / max(stats1['body_size'], 0.001)
        engulf_score = min(1.0, engulf_ratio / 1.5)
        confidence_factors.append(engulf_score * 0.4)
        
        # 2. Body sizes (both should be substantial)
        body_score = min(stats1['body_ratio'], stats2['body_ratio']) / 0.6
        confidence_factors.append(min(1.0, body_score) * 0.3)
        
        # 3. Context appropriateness
        expected_trend = 'downtrend' if bullish else 'uptrend'
        context_score = 1.0 if context['trend'] == expected_trend else 0.7 if context['trend'] == 'sideways' else 0.3
        confidence_factors.append(context_score * 0.2)
        
        # 4. Volume confirmation (if available)
        volume_score = 0.8  # Default when volume data not detailed
        if candle2.volume > candle1.volume:
            volume_score = 1.0
        confidence_factors.append(volume_score * 0.1)
        
        base_confidence = sum(confidence_factors)
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        return max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
    
    def _calculate_harami_confidence(self, candle1: PricePoint, candle2: PricePoint,
                                   stats1: Dict, stats2: Dict, context: Dict,
                                   sensitivity: float, bullish: bool) -> float:
        """Calculate confidence for harami patterns."""
        confidence_factors = []
        
        # 1. Size relationship (first large, second small)
        size_ratio = stats2['body_size'] / max(stats1['body_size'], 0.001)
        size_score = 1.0 - min(1.0, size_ratio / 0.5)  # Smaller second candle is better
        confidence_factors.append(size_score * 0.4)
        
        # 2. First candle size
        first_size_score = min(1.0, stats1['body_ratio'] / 0.7)
        confidence_factors.append(first_size_score * 0.3)
        
        # 3. Context appropriateness
        expected_trend = 'downtrend' if bullish else 'uptrend'
        context_score = 1.0 if context['trend'] == expected_trend else 0.7 if context['trend'] == 'sideways' else 0.3
        confidence_factors.append(context_score * 0.3)
        
        base_confidence = sum(confidence_factors)
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        return max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
    
    def _calculate_piercing_confidence(self, candle1: PricePoint, candle2: PricePoint,
                                     stats1: Dict, stats2: Dict, context: Dict,
                                     sensitivity: float) -> float:
        """Calculate confidence for piercing line pattern."""
        confidence_factors = []
        
        # 1. Penetration depth (how far into first candle)
        midpoint = (candle1.open + candle1.close) / 2
        penetration = (candle2.close - midpoint) / max(stats1['body_size'], 0.001)
        penetration_score = min(1.0, penetration / 0.5)
        confidence_factors.append(max(0.0, penetration_score) * 0.4)
        
        # 2. Gap size
        gap_size = (candle1.low - candle2.open) / max(stats1['total_range'], 0.001)
        gap_score = min(1.0, gap_size / 0.1)
        confidence_factors.append(max(0.0, gap_score) * 0.2)
        
        # 3. Body sizes
        body_score = min(stats1['body_ratio'], stats2['body_ratio']) / 0.5
        confidence_factors.append(min(1.0, body_score) * 0.2)
        
        # 4. Context
        context_score = 1.0 if context['trend'] == 'downtrend' else 0.7 if context['trend'] == 'sideways' else 0.3
        confidence_factors.append(context_score * 0.2)
        
        base_confidence = sum(confidence_factors)
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        return max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
    
    def _calculate_dark_cloud_confidence(self, candle1: PricePoint, candle2: PricePoint,
                                       stats1: Dict, stats2: Dict, context: Dict,
                                       sensitivity: float) -> float:
        """Calculate confidence for dark cloud cover pattern."""
        confidence_factors = []
        
        # 1. Penetration depth (how far into first candle)
        midpoint = (candle1.open + candle1.close) / 2
        penetration = (midpoint - candle2.close) / max(stats1['body_size'], 0.001)
        penetration_score = min(1.0, penetration / 0.5)
        confidence_factors.append(max(0.0, penetration_score) * 0.4)
        
        # 2. Gap size
        gap_size = (candle2.open - candle1.high) / max(stats1['total_range'], 0.001)
        gap_score = min(1.0, gap_size / 0.1)
        confidence_factors.append(max(0.0, gap_score) * 0.2)
        
        # 3. Body sizes
        body_score = min(stats1['body_ratio'], stats2['body_ratio']) / 0.5
        confidence_factors.append(min(1.0, body_score) * 0.2)
        
        # 4. Context
        context_score = 1.0 if context['trend'] == 'uptrend' else 0.7 if context['trend'] == 'sideways' else 0.3
        confidence_factors.append(context_score * 0.2)
        
        base_confidence = sum(confidence_factors)
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        return max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
    
    def _calculate_tweezer_confidence(self, candle1: PricePoint, candle2: PricePoint,
                                    stats1: Dict, stats2: Dict, context: Dict,
                                    sensitivity: float, tops: bool) -> float:
        """Calculate confidence for tweezer patterns."""
        confidence_factors = []
        
        # 1. Level similarity
        if tops:
            level_diff = abs(candle1.high - candle2.high)
            avg_range = (stats1['total_range'] + stats2['total_range']) / 2
        else:
            level_diff = abs(candle1.low - candle2.low)
            avg_range = (stats1['total_range'] + stats2['total_range']) / 2
        
        if avg_range > 0:
            similarity_score = 1.0 - min(1.0, level_diff / (avg_range * 0.05))
            confidence_factors.append(similarity_score * 0.5)
        
        # 2. Context appropriateness
        expected_trend = 'uptrend' if tops else 'downtrend'
        context_score = 1.0 if context['trend'] == expected_trend else 0.7 if context['trend'] == 'sideways' else 0.3
        confidence_factors.append(context_score * 0.3)
        
        # 3. Candle quality
        quality_score = (stats1['body_ratio'] + stats2['body_ratio']) / 2 / 0.4
        confidence_factors.append(min(1.0, quality_score) * 0.2)
        
        base_confidence = sum(confidence_factors)
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        return max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
    
    def _calculate_star_confidence(self, candle1: PricePoint, candle2: PricePoint, candle3: PricePoint,
                                 stats1: Dict, stats2: Dict, stats3: Dict, context: Dict,
                                 sensitivity: float, morning: bool) -> float:
        """Calculate confidence for star patterns."""
        confidence_factors = []
        
        # 1. Star size (should be small)
        star_score = 1.0 - min(1.0, stats2['body_ratio'] / 0.3)
        confidence_factors.append(star_score * 0.3)
        
        # 2. First and third candle sizes
        size_score = min(stats1['body_ratio'], stats3['body_ratio']) / 0.6
        confidence_factors.append(min(1.0, size_score) * 0.3)
        
        # 3. Gap quality
        if morning:
            gap1_size = max(0, candle1.close - candle2.high)
            gap2_size = max(0, candle3.open - candle2.high)
        else:
            gap1_size = max(0, candle2.low - candle1.close)
            gap2_size = max(0, candle2.low - candle3.open)
        
        avg_range = (stats1['total_range'] + stats3['total_range']) / 2
        if avg_range > 0:
            gap_score = min(1.0, (gap1_size + gap2_size) / (avg_range * 0.1))
            confidence_factors.append(gap_score * 0.2)
        
        # 4. Context appropriateness
        expected_trend = 'downtrend' if morning else 'uptrend'
        context_score = 1.0 if context['trend'] == expected_trend else 0.7 if context['trend'] == 'sideways' else 0.3
        confidence_factors.append(context_score * 0.2)
        
        base_confidence = sum(confidence_factors)
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        return max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
    
    def _calculate_soldiers_crows_confidence(self, candle1: PricePoint, candle2: PricePoint, candle3: PricePoint,
                                           stats1: Dict, stats2: Dict, stats3: Dict, context: Dict,
                                           sensitivity: float, bullish: bool) -> float:
        """Calculate confidence for three soldiers/crows patterns."""
        confidence_factors = []
        
        # 1. Progressive movement
        if bullish:
            progress_score = min(1.0, (candle3.close - candle1.open) / max(stats1['total_range'] * 3, 0.001))
        else:
            progress_score = min(1.0, (candle1.open - candle3.close) / max(stats1['total_range'] * 3, 0.001))
        confidence_factors.append(max(0.0, progress_score) * 0.4)
        
        # 2. Body sizes (all should be substantial)
        avg_body_ratio = (stats1['body_ratio'] + stats2['body_ratio'] + stats3['body_ratio']) / 3
        body_score = min(1.0, avg_body_ratio / 0.5)
        confidence_factors.append(body_score * 0.3)
        
        # 3. Opening relationships
        open_score = 1.0  # Assume good if we got this far
        confidence_factors.append(open_score * 0.2)
        
        # 4. Context (can be continuation or reversal)
        context_score = 0.8  # Generally strong pattern regardless of context
        confidence_factors.append(context_score * 0.1)
        
        base_confidence = sum(confidence_factors)
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        return max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
    
    def _calculate_three_methods_confidence(self, candle1: PricePoint, candle2: PricePoint, candle3: PricePoint,
                                          stats1: Dict, stats2: Dict, stats3: Dict, context: Dict,
                                          sensitivity: float, rising: bool) -> float:
        """Calculate confidence for three methods patterns."""
        confidence_factors = []
        
        # 1. Size relationships
        first_third_avg = (stats1['body_ratio'] + stats3['body_ratio']) / 2
        size_score = min(1.0, first_third_avg / 0.6)
        confidence_factors.append(size_score * 0.3)
        
        # 2. Pullback quality (second candle should be smaller)
        pullback_score = 1.0 - min(1.0, stats2['body_ratio'] / 0.4)
        confidence_factors.append(pullback_score * 0.3)
        
        # 3. Continuation strength
        if rising:
            continuation_score = min(1.0, (candle3.close - candle1.close) / max(stats1['body_size'], 0.001))
        else:
            continuation_score = min(1.0, (candle1.close - candle3.close) / max(stats1['body_size'], 0.001))
        confidence_factors.append(max(0.0, continuation_score) * 0.2)
        
        # 4. Context appropriateness
        expected_trend = 'uptrend' if rising else 'downtrend'
        context_score = 1.0 if context['trend'] == expected_trend else 0.7 if context['trend'] == 'sideways' else 0.5
        confidence_factors.append(context_score * 0.2)
        
        base_confidence = sum(confidence_factors)
        sensitivity_adjustment = (sensitivity - 0.5) * 0.2
        return max(0.0, min(1.0, base_confidence + sensitivity_adjustment))
    
    def _create_multi_candlestick_pattern(self, pattern_type: PatternType, candles: List[PricePoint],
                                        start_index: int, end_index: int, confidence: float,
                                        data: PriceDataFrame, description: str) -> DetectedPattern:
        """Create a multi-candlestick pattern detection result."""
        
        # Calculate volume profile across all candles
        total_volume = sum(candle.volume for candle in candles)
        avg_volume = total_volume / len(candles)
        
        volume_profile = VolumeProfile(
            avg_volume=avg_volume,
            volume_trend="increasing" if candles[-1].volume > candles[0].volume else "decreasing",
            volume_confirmation=avg_volume > 0
        )
        
        # Calculate key levels
        all_opens = [candle.open for candle in candles]
        all_highs = [candle.high for candle in candles]
        all_lows = [candle.low for candle in candles]
        all_closes = [candle.close for candle in candles]
        
        key_levels = {
            'pattern_high': max(all_highs),
            'pattern_low': min(all_lows),
            'first_open': candles[0].open,
            'last_close': candles[-1].close,
            'candle_count': len(candles)
        }
        
        # Add individual candle data
        for i, candle in enumerate(candles):
            key_levels[f'candle_{i+1}_open'] = candle.open
            key_levels[f'candle_{i+1}_high'] = candle.high
            key_levels[f'candle_{i+1}_low'] = candle.low
            key_levels[f'candle_{i+1}_close'] = candle.close
        
        return DetectedPattern(
            pattern_type=pattern_type,
            category=PATTERN_CATEGORIES[pattern_type],
            confidence=confidence,
            start_time=candles[0].timestamp,
            end_time=candles[-1].timestamp,
            start_index=start_index,
            end_index=end_index,
            key_levels=key_levels,
            volume_profile=volume_profile,
            description=description
        )
    
    def _create_candlestick_pattern(self, pattern_type: PatternType, candle: PricePoint,
                                  index: int, confidence: float, data: PriceDataFrame,
                                  description: str) -> DetectedPattern:
        """Create a candlestick pattern detection result."""
        
        # Calculate volume profile (single candle)
        volume_profile = VolumeProfile(
            avg_volume=candle.volume,
            volume_trend="stable",
            volume_confirmation=candle.volume > 0
        )
        
        return DetectedPattern(
            pattern_type=pattern_type,
            category=PATTERN_CATEGORIES[pattern_type],
            confidence=confidence,
            start_time=candle.timestamp,
            end_time=candle.timestamp,
            start_index=index,
            end_index=index,
            key_levels={
                'open': candle.open,
                'high': candle.high,
                'low': candle.low,
                'close': candle.close,
                'body_size': abs(candle.close - candle.open),
                'total_range': candle.high - candle.low,
                'upper_wick': candle.high - max(candle.open, candle.close),
                'lower_wick': min(candle.open, candle.close) - candle.low
            },
            volume_profile=volume_profile,
            description=description
        )
    
    def _filter_overlapping_patterns(self, patterns: List[DetectedPattern]) -> List[DetectedPattern]:
        """Filter out overlapping candlestick patterns."""
        if not patterns:
            return patterns
        
        # For single candlestick patterns, remove duplicates at the same index
        # Keep the highest confidence pattern for each candle
        
        pattern_by_index = {}
        
        for pattern in patterns:
            index = pattern.start_index
            if index not in pattern_by_index or pattern.confidence > pattern_by_index[index].confidence:
                pattern_by_index[index] = pattern
        
        return list(pattern_by_index.values())