"""Pattern type definitions and data structures."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class PatternType(Enum):
    """Enumeration of all supported chart patterns."""

    # Continuation Patterns - Bullish
    ASCENDING_TRIANGLE = "ascending_triangle"
    BULL_FLAG = "bull_flag"
    BULL_PENNANT = "bull_pennant"
    CUP_AND_HANDLE = "cup_and_handle"
    RISING_CHANNEL = "rising_channel"
    RISING_WEDGE_CONTINUATION = "rising_wedge_continuation"
    RECTANGLE_BULLISH = "rectangle_bullish"

    # Continuation Patterns - Bearish
    DESCENDING_TRIANGLE = "descending_triangle"
    BEAR_FLAG = "bear_flag"
    BEAR_PENNANT = "bear_pennant"
    INVERTED_CUP_HANDLE = "inverted_cup_handle"
    FALLING_CHANNEL = "falling_channel"
    FALLING_WEDGE_CONTINUATION = "falling_wedge_continuation"
    RECTANGLE_BEARISH = "rectangle_bearish"

    # Reversal Patterns - Bullish
    DOUBLE_BOTTOM = "double_bottom"
    TRIPLE_BOTTOM = "triple_bottom"
    INVERSE_HEAD_SHOULDERS = "inverse_head_shoulders"
    FALLING_WEDGE_REVERSAL = "falling_wedge_reversal"
    HAMMER = "hammer"
    MORNING_STAR = "morning_star"
    BULLISH_ENGULFING = "bullish_engulfing"

    # Reversal Patterns - Bearish
    DOUBLE_TOP = "double_top"
    TRIPLE_TOP = "triple_top"
    HEAD_SHOULDERS = "head_shoulders"
    RISING_WEDGE_REVERSAL = "rising_wedge_reversal"
    SHOOTING_STAR = "shooting_star"
    EVENING_STAR = "evening_star"
    BEARISH_ENGULFING = "bearish_engulfing"

    # Bilateral Patterns
    SYMMETRICAL_TRIANGLE = "symmetrical_triangle"
    DIAMOND = "diamond"
    RECTANGLE_NEUTRAL = "rectangle_neutral"
    EXPANDING_TRIANGLE = "expanding_triangle"
    PENNANT_NEUTRAL = "pennant_neutral"

    # Harmonic Patterns
    GARTLEY = "gartley"
    BUTTERFLY = "butterfly"
    BAT = "bat"
    CRAB = "crab"
    ABCD = "abcd"
    CYPHER = "cypher"

    # Candlestick Patterns - Single
    DOJI = "doji"
    SPINNING_TOP = "spinning_top"
    MARUBOZU = "marubozu"
    GRAVESTONE_DOJI = "gravestone_doji"

    # Candlestick Patterns - Multi
    BULLISH_HARAMI = "bullish_harami"
    BEARISH_HARAMI = "bearish_harami"
    PIERCING_LINE = "piercing_line"
    DARK_CLOUD_COVER = "dark_cloud_cover"
    THREE_WHITE_SOLDIERS = "three_white_soldiers"
    THREE_BLACK_CROWS = "three_black_crows"
    TWEEZER_TOPS = "tweezer_tops"
    TWEEZER_BOTTOMS = "tweezer_bottoms"
    RISING_THREE_METHODS = "rising_three_methods"
    FALLING_THREE_METHODS = "falling_three_methods"

    # Divergence Patterns
    BULLISH_DIVERGENCE = "bullish_divergence"
    BEARISH_DIVERGENCE = "bearish_divergence"
    HIDDEN_BULLISH_DIVERGENCE = "hidden_bullish_divergence"
    HIDDEN_BEARISH_DIVERGENCE = "hidden_bearish_divergence"


class PatternCategory(Enum):
    """Pattern categories for classification."""
    BULLISH_CONTINUATION = "Bullish Continuation"
    BEARISH_CONTINUATION = "Bearish Continuation"
    BULLISH_REVERSAL = "Bullish Reversal"
    BEARISH_REVERSAL = "Bearish Reversal"
    BILATERAL_NEUTRAL = "Bilateral/Neutral"
    HARMONIC_PATTERN = "Harmonic Pattern"
    CANDLESTICK_PATTERN = "Candlestick Pattern"
    DIVERGENCE_PATTERN = "Divergence Pattern"


@dataclass
class VolumeProfile:
    """Volume analysis for pattern validation."""
    avg_volume: float
    volume_trend: str  # "increasing", "decreasing", "stable"
    volume_confirmation: bool
    breakout_volume: Optional[float] = None


@dataclass
class DetectedPattern:
    """Represents a detected chart pattern with all relevant information."""
    pattern_type: PatternType
    category: PatternCategory
    confidence: float  # 0.0 to 1.0
    start_time: datetime
    end_time: datetime
    start_index: int
    end_index: int
    key_levels: Dict[str, float]  # support, resistance, target levels
    volume_profile: VolumeProfile
    description: str
    fibonacci_levels: Optional[Dict[str, float]] = None  # For harmonic patterns

    def get_duration_days(self) -> float:
        """Get pattern duration in days."""
        return (self.end_time - self.start_time).total_seconds() / 86400

    def is_bullish(self) -> bool:
        """Check if pattern is bullish."""
        return self.category in [
            PatternCategory.BULLISH_CONTINUATION,
            PatternCategory.BULLISH_REVERSAL
        ]

    def is_bearish(self) -> bool:
        """Check if pattern is bearish."""
        return self.category in [
            PatternCategory.BEARISH_CONTINUATION,
            PatternCategory.BEARISH_REVERSAL
        ]

    def is_reversal(self) -> bool:
        """Check if pattern is a reversal pattern."""
        return self.category in [
            PatternCategory.BULLISH_REVERSAL,
            PatternCategory.BEARISH_REVERSAL
        ]


# Pattern type to category mapping
PATTERN_CATEGORIES = {
    # Bullish Continuation
    PatternType.ASCENDING_TRIANGLE: PatternCategory.BULLISH_CONTINUATION,
    PatternType.BULL_FLAG: PatternCategory.BULLISH_CONTINUATION,
    PatternType.BULL_PENNANT: PatternCategory.BULLISH_CONTINUATION,
    PatternType.CUP_AND_HANDLE: PatternCategory.BULLISH_CONTINUATION,
    PatternType.RISING_CHANNEL: PatternCategory.BULLISH_CONTINUATION,
    PatternType.RISING_WEDGE_CONTINUATION: PatternCategory.BULLISH_CONTINUATION,
    PatternType.RECTANGLE_BULLISH: PatternCategory.BULLISH_CONTINUATION,

    # Bearish Continuation
    PatternType.DESCENDING_TRIANGLE: PatternCategory.BEARISH_CONTINUATION,
    PatternType.BEAR_FLAG: PatternCategory.BEARISH_CONTINUATION,
    PatternType.BEAR_PENNANT: PatternCategory.BEARISH_CONTINUATION,
    PatternType.INVERTED_CUP_HANDLE: PatternCategory.BEARISH_CONTINUATION,
    PatternType.FALLING_CHANNEL: PatternCategory.BEARISH_CONTINUATION,
    PatternType.FALLING_WEDGE_CONTINUATION: PatternCategory.BEARISH_CONTINUATION,
    PatternType.RECTANGLE_BEARISH: PatternCategory.BEARISH_CONTINUATION,
    PatternType.RISING_CHANNEL: PatternCategory.BULLISH_CONTINUATION,
    PatternType.FALLING_CHANNEL: PatternCategory.BEARISH_CONTINUATION,

    # Bullish Reversal
    PatternType.DOUBLE_BOTTOM: PatternCategory.BULLISH_REVERSAL,
    PatternType.TRIPLE_BOTTOM: PatternCategory.BULLISH_REVERSAL,
    PatternType.INVERSE_HEAD_SHOULDERS: PatternCategory.BULLISH_REVERSAL,
    PatternType.FALLING_WEDGE_REVERSAL: PatternCategory.BULLISH_REVERSAL,
    PatternType.HAMMER: PatternCategory.BULLISH_REVERSAL,
    PatternType.MORNING_STAR: PatternCategory.BULLISH_REVERSAL,
    PatternType.BULLISH_ENGULFING: PatternCategory.BULLISH_REVERSAL,

    # Bearish Reversal
    PatternType.DOUBLE_TOP: PatternCategory.BEARISH_REVERSAL,
    PatternType.TRIPLE_TOP: PatternCategory.BEARISH_REVERSAL,
    PatternType.HEAD_SHOULDERS: PatternCategory.BEARISH_REVERSAL,
    PatternType.RISING_WEDGE_REVERSAL: PatternCategory.BEARISH_REVERSAL,
    PatternType.SHOOTING_STAR: PatternCategory.BEARISH_REVERSAL,
    PatternType.EVENING_STAR: PatternCategory.BEARISH_REVERSAL,
    PatternType.BEARISH_ENGULFING: PatternCategory.BEARISH_REVERSAL,

    # Bilateral/Neutral
    PatternType.SYMMETRICAL_TRIANGLE: PatternCategory.BILATERAL_NEUTRAL,
    PatternType.DIAMOND: PatternCategory.BILATERAL_NEUTRAL,
    PatternType.RECTANGLE_NEUTRAL: PatternCategory.BILATERAL_NEUTRAL,
    PatternType.EXPANDING_TRIANGLE: PatternCategory.BILATERAL_NEUTRAL,
    PatternType.PENNANT_NEUTRAL: PatternCategory.BILATERAL_NEUTRAL,

    # Harmonic Patterns
    PatternType.GARTLEY: PatternCategory.HARMONIC_PATTERN,
    PatternType.BUTTERFLY: PatternCategory.HARMONIC_PATTERN,
    PatternType.BAT: PatternCategory.HARMONIC_PATTERN,
    PatternType.CRAB: PatternCategory.HARMONIC_PATTERN,
    PatternType.ABCD: PatternCategory.HARMONIC_PATTERN,
    PatternType.CYPHER: PatternCategory.HARMONIC_PATTERN,

    # Candlestick Patterns
    PatternType.DOJI: PatternCategory.CANDLESTICK_PATTERN,
    PatternType.SPINNING_TOP: PatternCategory.CANDLESTICK_PATTERN,
    PatternType.MARUBOZU: PatternCategory.CANDLESTICK_PATTERN,
    PatternType.GRAVESTONE_DOJI: PatternCategory.CANDLESTICK_PATTERN,
    PatternType.HAMMER: PatternCategory.CANDLESTICK_PATTERN,
    PatternType.SHOOTING_STAR: PatternCategory.CANDLESTICK_PATTERN,
    PatternType.BULLISH_HARAMI: PatternCategory.CANDLESTICK_PATTERN,
    PatternType.BEARISH_HARAMI: PatternCategory.CANDLESTICK_PATTERN,
    PatternType.PIERCING_LINE: PatternCategory.CANDLESTICK_PATTERN,
    PatternType.DARK_CLOUD_COVER: PatternCategory.CANDLESTICK_PATTERN,
    PatternType.THREE_WHITE_SOLDIERS: PatternCategory.CANDLESTICK_PATTERN,
    PatternType.THREE_BLACK_CROWS: PatternCategory.CANDLESTICK_PATTERN,
    PatternType.MORNING_STAR: PatternCategory.CANDLESTICK_PATTERN,
    PatternType.EVENING_STAR: PatternCategory.CANDLESTICK_PATTERN,
    PatternType.BULLISH_ENGULFING: PatternCategory.CANDLESTICK_PATTERN,
    PatternType.BEARISH_ENGULFING: PatternCategory.CANDLESTICK_PATTERN,
    PatternType.TWEEZER_TOPS: PatternCategory.CANDLESTICK_PATTERN,
    PatternType.TWEEZER_BOTTOMS: PatternCategory.CANDLESTICK_PATTERN,
    PatternType.RISING_THREE_METHODS: PatternCategory.CANDLESTICK_PATTERN,
    PatternType.FALLING_THREE_METHODS: PatternCategory.CANDLESTICK_PATTERN,

    # Divergence Patterns
    PatternType.BULLISH_DIVERGENCE: PatternCategory.DIVERGENCE_PATTERN,
    PatternType.BEARISH_DIVERGENCE: PatternCategory.DIVERGENCE_PATTERN,
    PatternType.HIDDEN_BULLISH_DIVERGENCE: PatternCategory.DIVERGENCE_PATTERN,
    PatternType.HIDDEN_BEARISH_DIVERGENCE: PatternCategory.DIVERGENCE_PATTERN,
}
