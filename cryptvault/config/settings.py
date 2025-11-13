"""Configuration settings classes."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class SensitivityLevel(Enum):
    """Predefined sensitivity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CUSTOM = "custom"


@dataclass
class SensitivitySettings:
    """Sensitivity settings for pattern detection."""

    # Overall sensitivity level
    level: SensitivityLevel = SensitivityLevel.MEDIUM

    # Pattern-specific sensitivity values (0.0 to 1.0)
    geometric_patterns: float = 0.5
    reversal_patterns: float = 0.5
    harmonic_patterns: float = 0.6  # Harmonic patterns need higher precision
    candlestick_patterns: float = 0.4  # Candlestick patterns can be more lenient
    divergence_patterns: float = 0.5

    # Minimum confidence thresholds for reporting
    min_confidence_geometric: float = 0.3
    min_confidence_reversal: float = 0.4
    min_confidence_harmonic: float = 0.5
    min_confidence_candlestick: float = 0.3
    min_confidence_divergence: float = 0.4

    # Volume analysis settings
    volume_confirmation_weight: float = 0.2
    require_volume_confirmation: bool = False

    # Time frame considerations
    min_pattern_duration: int = 5  # Minimum candles for pattern
    max_pattern_duration: int = 100  # Maximum candles for pattern

    @classmethod
    def get_preset(cls, level: SensitivityLevel) -> 'SensitivitySettings':
        """Get preset sensitivity settings."""
        if level == SensitivityLevel.LOW:
            return cls(
                level=level,
                geometric_patterns=0.3,
                reversal_patterns=0.3,
                harmonic_patterns=0.4,
                candlestick_patterns=0.2,
                divergence_patterns=0.3,
                min_confidence_geometric=0.2,
                min_confidence_reversal=0.3,
                min_confidence_harmonic=0.4,
                min_confidence_candlestick=0.2,
                min_confidence_divergence=0.3,
                volume_confirmation_weight=0.1,
                require_volume_confirmation=False,
                min_pattern_duration=3,
                max_pattern_duration=150
            )
        elif level == SensitivityLevel.HIGH:
            return cls(
                level=level,
                geometric_patterns=0.7,
                reversal_patterns=0.7,
                harmonic_patterns=0.8,
                candlestick_patterns=0.6,
                divergence_patterns=0.7,
                min_confidence_geometric=0.5,
                min_confidence_reversal=0.6,
                min_confidence_harmonic=0.7,
                min_confidence_candlestick=0.4,
                min_confidence_divergence=0.5,
                volume_confirmation_weight=0.3,
                require_volume_confirmation=True,
                min_pattern_duration=8,
                max_pattern_duration=50
            )
        else:  # MEDIUM (default)
            return cls(level=level)

    def get_pattern_sensitivity(self, pattern_category: str) -> float:
        """Get sensitivity for specific pattern category."""
        category_map = {
            'geometric': self.geometric_patterns,
            'reversal': self.reversal_patterns,
            'harmonic': self.harmonic_patterns,
            'candlestick': self.candlestick_patterns,
            'divergence': self.divergence_patterns
        }
        return category_map.get(pattern_category.lower(), self.geometric_patterns)

    def get_min_confidence(self, pattern_category: str) -> float:
        """Get minimum confidence threshold for pattern category."""
        category_map = {
            'geometric': self.min_confidence_geometric,
            'reversal': self.min_confidence_reversal,
            'harmonic': self.min_confidence_harmonic,
            'candlestick': self.min_confidence_candlestick,
            'divergence': self.min_confidence_divergence
        }
        return category_map.get(pattern_category.lower(), self.min_confidence_geometric)


@dataclass
class DisplaySettings:
    """Display and visualization settings."""

    # Terminal chart settings
    chart_width: int = 80
    chart_height: int = 24
    enable_colors: bool = True
    enable_unicode: bool = True

    # Pattern display settings
    show_pattern_overlays: bool = True
    show_support_resistance: bool = True
    show_fibonacci_levels: bool = True
    show_volume_profile: bool = True

    # Legend and info settings
    max_patterns_in_legend: int = 8
    show_confidence_bars: bool = True
    show_pattern_details: bool = True
    show_key_levels: bool = True

    # Color scheme
    bullish_color: str = "green"
    bearish_color: str = "red"
    neutral_color: str = "yellow"
    harmonic_color: str = "magenta"
    candlestick_color: str = "cyan"
    divergence_color: str = "blue"

    # Output format settings
    timestamp_format: str = "%Y-%m-%d %H:%M"
    price_decimal_places: int = 2
    percentage_decimal_places: int = 1

    def get_terminal_size(self) -> tuple:
        """Get terminal size as (width, height)."""
        return (self.chart_width, self.chart_height)

    def get_color_for_category(self, category: str) -> str:
        """Get color for pattern category."""
        color_map = {
            'bullish_continuation': self.bullish_color,
            'bullish_reversal': self.bullish_color,
            'bearish_continuation': self.bearish_color,
            'bearish_reversal': self.bearish_color,
            'bilateral_neutral': self.neutral_color,
            'harmonic_pattern': self.harmonic_color,
            'candlestick_pattern': self.candlestick_color,
            'divergence_pattern': self.divergence_color
        }
        return color_map.get(category.lower(), self.neutral_color)


@dataclass
class PatternSettings:
    """Pattern-specific detection settings."""

    # Enabled pattern types
    enabled_geometric: bool = True
    enabled_reversal: bool = True
    enabled_harmonic: bool = True
    enabled_candlestick: bool = True
    enabled_divergence: bool = True

    # Specific pattern toggles
    enabled_patterns: Dict[str, bool] = field(default_factory=lambda: {
        # Geometric patterns
        'ascending_triangle': True,
        'descending_triangle': True,
        'symmetrical_triangle': True,
        'bull_flag': True,
        'bear_flag': True,
        'cup_and_handle': True,
        'rising_wedge': True,
        'falling_wedge': True,
        'rectangle': True,
        'channel': True,

        # Reversal patterns
        'double_top': True,
        'double_bottom': True,
        'triple_top': True,
        'triple_bottom': True,
        'head_shoulders': True,
        'inverse_head_shoulders': True,

        # Advanced patterns
        'diamond': True,
        'expanding_triangle': True,

        # Harmonic patterns
        'gartley': True,
        'butterfly': True,
        'bat': True,
        'crab': True,
        'abcd': True,
        'cypher': True,

        # Candlestick patterns
        'hammer': True,
        'shooting_star': True,
        'doji': True,
        'spinning_top': True,
        'marubozu': True,
        'engulfing': True,
        'harami': True,
        'piercing_line': True,
        'dark_cloud_cover': True,
        'morning_star': True,
        'evening_star': True,
        'three_soldiers': True,
        'three_crows': True,

        # Divergence patterns
        'bullish_divergence': True,
        'bearish_divergence': True,
        'hidden_divergence': True
    })

    # Pattern filtering settings
    max_patterns_per_type: int = 10
    max_total_patterns: int = 50
    filter_overlapping: bool = True
    overlap_threshold: float = 0.5  # Percentage overlap to consider as overlapping

    # Pattern validation settings
    require_volume_confirmation: bool = False
    min_volume_ratio: float = 1.0  # Minimum volume ratio for confirmation
    validate_breakouts: bool = True
    breakout_confirmation_candles: int = 2

    def is_pattern_enabled(self, pattern_name: str) -> bool:
        """Check if a specific pattern is enabled."""
        return self.enabled_patterns.get(pattern_name.lower(), True)

    def enable_pattern(self, pattern_name: str, enabled: bool = True):
        """Enable or disable a specific pattern."""
        self.enabled_patterns[pattern_name.lower()] = enabled

    def get_enabled_patterns(self) -> List[str]:
        """Get list of enabled pattern names."""
        return [name for name, enabled in self.enabled_patterns.items() if enabled]

    def disable_all_patterns(self):
        """Disable all patterns."""
        for pattern_name in self.enabled_patterns:
            self.enabled_patterns[pattern_name] = False

    def enable_all_patterns(self):
        """Enable all patterns."""
        for pattern_name in self.enabled_patterns:
            self.enabled_patterns[pattern_name] = True


@dataclass
class AnalysisSettings:
    """General analysis settings."""

    # Data processing settings
    min_data_points: int = 50
    max_data_points: int = 1000
    data_validation_strict: bool = True

    # Performance settings
    enable_parallel_processing: bool = False
    max_worker_threads: int = 4

    # Caching settings
    enable_caching: bool = True
    cache_size_mb: int = 100
    cache_expiry_hours: int = 24

    # Output settings
    save_results: bool = False
    output_format: str = "json"  # json, csv, txt
    output_directory: str = "./analysis_results"

    # Logging settings
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    log_to_file: bool = False
    log_file_path: str = "./crypto_analyzer.log"

    def get_log_level_numeric(self) -> int:
        """Get numeric log level."""
        levels = {
            'DEBUG': 10,
            'INFO': 20,
            'WARNING': 30,
            'ERROR': 40
        }
        return levels.get(self.log_level.upper(), 20)
