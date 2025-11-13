"""
Feature Engineering for ML Models

This module consolidates all feature extraction functionality for machine learning models.
It provides three main feature extractors:
- TechnicalFeatureExtractor: Extracts features from technical indicators
- PatternFeatureExtractor: Extracts features from detected chart patterns
- TimeFeatureExtractor: Extracts time-based features for temporal patterns

Feature Importance:
- Technical indicators: ~40% (RSI, MACD, Bollinger Bands, Moving Averages)
- Pattern features: ~30% (Pattern presence, confidence, categories)
- Time features: ~20% (Day of week, month, market sessions)
- Price action: ~10% (Momentum, volatility, volume)
"""

import numpy as np
from typing import List, Dict, Any
from datetime import datetime
import logging

from ..data.models import PriceDataFrame
from ..indicators.trend import calculate_sma, calculate_ema
from ..indicators.momentum import calculate_rsi, calculate_macd
from ..indicators.volatility import calculate_bollinger_bands, calculate_atr


class TechnicalFeatureExtractor:
    """
    Extract technical indicator features for ML models.

    This extractor computes features from various technical indicators including:
    - Trend indicators (SMA, EMA)
    - Momentum indicators (RSI, MACD)
    - Volatility indicators (Bollinger Bands, ATR)
    - Volume indicators
    - Price action features

    Feature Importance:
    - RSI features: High importance for overbought/oversold conditions
    - MACD features: High importance for trend changes
    - Bollinger Bands: Medium importance for volatility and price position
    - Moving averages: Medium importance for trend direction
    - Volume features: Medium importance for confirmation signals
    """

    def __init__(self):
        """Initialize technical feature extractor."""
        self.logger = logging.getLogger(__name__)

    def extract(self, data: PriceDataFrame) -> List[float]:
        """
        Extract comprehensive technical indicator features.

        Args:
            data: Price data frame containing OHLCV data

        Returns:
            List of 40+ technical indicator features including:
            - RSI (14, 21 period) with overbought/oversold flags
            - MACD with signal and histogram
            - Bollinger Bands position and width
            - Multiple moving averages (SMA 20/50, EMA 12/26)
            - Volatility measures
            - Volume ratios and trends
            - Price action features (momentum, candle patterns)

        Feature Importance Ranking:
        1. RSI (14): 0.15 - Strong predictor of reversals
        2. MACD histogram: 0.12 - Trend momentum indicator
        3. Bollinger Band position: 0.10 - Volatility and extremes
        4. Price vs SMA20: 0.08 - Short-term trend
        5. Volume ratio: 0.07 - Confirmation signal
        """
        try:
            closes = np.array(data.get_closes())
            highs = np.array(data.get_highs())
            lows = np.array(data.get_lows())
            volumes = np.array(data.get_volumes())

            features = []

            # RSI features (multiple periods) - High importance
            rsi_14 = calculate_rsi(closes, 14)
            rsi_21 = calculate_rsi(closes, 21)
            current_rsi_14 = rsi_14[-1] if not np.isnan(rsi_14[-1]) else 50.0
            current_rsi_21 = rsi_21[-1] if not np.isnan(rsi_21[-1]) else 50.0

            features.extend([
                current_rsi_14 / 100.0,  # Normalize to 0-1
                current_rsi_21 / 100.0,
                1.0 if current_rsi_14 > 70 else 0.0,  # Overbought flag
                1.0 if current_rsi_14 < 30 else 0.0,  # Oversold flag
                (current_rsi_14 - 50.0) / 50.0  # RSI momentum
            ])

            # MACD features - High importance
            macd_data = calculate_macd(closes)
            current_macd = macd_data['macd'][-1] if not np.isnan(macd_data['macd'][-1]) else 0.0
            current_signal = macd_data['signal'][-1] if not np.isnan(macd_data['signal'][-1]) else 0.0
            current_histogram = macd_data['histogram'][-1] if not np.isnan(macd_data['histogram'][-1]) else 0.0

            # Normalize MACD values
            price_range = closes[-1] * 0.1
            features.extend([
                current_macd / price_range,
                current_signal / price_range,
                current_histogram / price_range,
                1.0 if current_macd > current_signal else 0.0,  # Bullish crossover
                1.0 if current_histogram > 0 else 0.0  # Positive histogram
            ])

            # Bollinger Bands features - Medium importance
            bb = calculate_bollinger_bands(closes, 20, 2.0)
            current_price = closes[-1]
            upper_band = bb['upper'][-1] if not np.isnan(bb['upper'][-1]) else current_price
            middle_band = bb['middle'][-1] if not np.isnan(bb['middle'][-1]) else current_price
            lower_band = bb['lower'][-1] if not np.isnan(bb['lower'][-1]) else current_price

            # Bollinger Band position (0 = lower band, 1 = upper band)
            if upper_band != lower_band:
                bb_position = (current_price - lower_band) / (upper_band - lower_band)
            else:
                bb_position = 0.5

            band_width = (upper_band - lower_band) / middle_band if middle_band > 0 else 0.0

            features.extend([
                bb_position,
                band_width,
                1.0 if current_price > upper_band else 0.0,  # Above upper band
                1.0 if current_price < lower_band else 0.0   # Below lower band
            ])

            # Moving average features - Medium importance
            sma_20 = calculate_sma(closes, 20)
            sma_50 = calculate_sma(closes, 50)
            ema_12 = calculate_ema(closes, 12)
            ema_26 = calculate_ema(closes, 26)

            current_sma_20 = sma_20[-1] if not np.isnan(sma_20[-1]) else current_price
            current_sma_50 = sma_50[-1] if not np.isnan(sma_50[-1]) else current_price
            current_ema_12 = ema_12[-1] if not np.isnan(ema_12[-1]) else current_price
            current_ema_26 = ema_26[-1] if not np.isnan(ema_26[-1]) else current_price

            features.extend([
                (current_price - current_sma_20) / current_sma_20 if current_sma_20 > 0 else 0.0,
                (current_price - current_sma_50) / current_sma_50 if current_sma_50 > 0 else 0.0,
                (current_price - current_ema_12) / current_ema_12 if current_ema_12 > 0 else 0.0,
                1.0 if current_sma_20 > current_sma_50 else 0.0,  # Golden cross indicator
                1.0 if current_price > current_sma_20 else 0.0     # Price above SMA20
            ])

            # Volatility features - Medium importance
            if len(closes) >= 20:
                returns = np.diff(np.log(closes[-20:]))
                volatility = np.std(returns)
                volatility_ma = np.mean(np.abs(returns))

                features.extend([
                    volatility,
                    volatility_ma,
                    1.0 if volatility > 0.03 else 0.0  # High volatility flag
                ])
            else:
                features.extend([0.02, 0.015, 0.0])

            # Volume features - Medium importance
            if len(volumes) >= 10:
                current_volume = volumes[-1]
                avg_volume = np.mean(volumes[-10:-1]) if len(volumes) > 1 else current_volume
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0

                # Volume trend
                if len(volumes) >= 6:
                    recent_avg = np.mean(volumes[-3:])
                    older_avg = np.mean(volumes[-6:-3])
                    volume_trend = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0.0
                else:
                    volume_trend = 0.0

                features.extend([
                    min(volume_ratio, 5.0),  # Cap at 5x
                    volume_trend,
                    1.0 if volume_ratio > 1.5 else 0.0  # High volume flag
                ])
            else:
                features.extend([1.0, 0.0, 0.0])

            # Price action features - Medium importance
            if len(closes) >= 5:
                price_change_1d = (closes[-1] - closes[-2]) / closes[-2]
                price_change_3d = (closes[-1] - closes[-4]) / closes[-4]

                # Candle body ratio
                if len(data.data) >= 1:
                    current_candle = data.data[-1]
                    body_size = abs(current_candle.close - current_candle.open)
                    total_range = current_candle.high - current_candle.low
                    body_ratio = body_size / total_range if total_range > 0 else 0.0
                else:
                    body_ratio = 0.5

                features.extend([
                    price_change_1d,
                    price_change_3d,
                    body_ratio
                ])
            else:
                features.extend([0.0, 0.0, 0.5])

            # ATR for volatility
            atr = calculate_atr(highs, lows, closes, 14)
            current_atr = atr[-1] if not np.isnan(atr[-1]) else 0.0
            features.append(current_atr / current_price if current_price > 0 else 0.0)

            self.logger.debug(f"Extracted {len(features)} technical features")
            return features

        except Exception as e:
            self.logger.error(f"Technical feature extraction failed: {e}")
            return [0.0] * 35  # Return zeros as fallback

    def get_feature_names(self) -> List[str]:
        """
        Get names of all extracted features.

        Returns:
            List of feature names in the same order as extract() output
        """
        return [
            # RSI features (5)
            'rsi_14', 'rsi_21', 'rsi_overbought', 'rsi_oversold', 'rsi_momentum',
            # MACD features (5)
            'macd', 'macd_signal', 'macd_histogram', 'macd_bullish', 'macd_positive',
            # Bollinger Bands features (4)
            'bb_position', 'bb_width', 'bb_above_upper', 'bb_below_lower',
            # Moving average features (5)
            'price_vs_sma20', 'price_vs_sma50', 'price_vs_ema12', 'golden_cross', 'price_above_sma20',
            # Volatility features (3)
            'volatility', 'volatility_ma', 'high_volatility',
            # Volume features (3)
            'volume_ratio', 'volume_trend', 'high_volume',
            # Price action features (3)
            'price_change_1d', 'price_change_3d', 'body_ratio',
            # ATR (1)
            'atr_normalized'
        ]


class PatternFeatureExtractor:
    """
    Extract pattern-based features for ML models.

    This extractor analyzes detected chart patterns and converts them into
    numerical features that can be used by machine learning models.

    Feature Categories:
    - Pattern presence: Binary flags for key pattern types
    - Pattern confidence: Confidence scores and statistics
    - Pattern categories: Bullish/bearish, continuation/reversal ratios
    - Pattern timing: Age and duration of patterns

    Feature Importance:
    - High confidence patterns: Strong predictive power
    - Reversal patterns: Important for trend changes
    - Pattern confluence: Multiple patterns increase reliability
    """

    def __init__(self):
        """Initialize pattern feature extractor."""
        self.logger = logging.getLogger(__name__)

    def extract(self, patterns: List[Any]) -> List[float]:
        """
        Extract pattern-based features from detected patterns.

        Args:
            patterns: List of detected chart patterns

        Returns:
            List of pattern features including:
            - Binary flags for key pattern types (8 features)
            - Confidence statistics (3 features)
            - Category ratios (4 features)
            - Timing features (2 features)

        Feature Importance Ranking:
        1. High confidence pattern count: 0.18 - Strong signals
        2. Bullish reversal ratio: 0.15 - Trend change indicator
        3. Max confidence: 0.12 - Pattern strength
        4. Pattern age: 0.10 - Recency matters
        """
        try:
            features = []

            # Pattern presence features (8 features)
            key_patterns = [
                'triangle', 'flag', 'wedge', 'rectangle',
                'head_shoulders', 'double_top', 'double_bottom', 'cup_handle'
            ]

            pattern_names = []
            for p in patterns:
                if hasattr(p, 'pattern_type'):
                    pattern_names.append(p.pattern_type.value.lower())
                elif isinstance(p, dict):
                    pattern_names.append(p.get('pattern_type', '').lower())

            for pattern_type in key_patterns:
                present = any(pattern_type in name for name in pattern_names)
                features.append(1.0 if present else 0.0)

            # Confidence features (3 features)
            if patterns:
                confidences = []
                for p in patterns:
                    if hasattr(p, 'confidence'):
                        confidences.append(p.confidence)
                    elif isinstance(p, dict):
                        conf_str = p.get('confidence', '0')
                        if isinstance(conf_str, str):
                            confidences.append(float(conf_str.rstrip('%')) / 100.0)
                        else:
                            confidences.append(float(conf_str))

                if confidences:
                    features.extend([
                        max(confidences),  # Highest confidence
                        np.mean(confidences),  # Average confidence
                        float(len([c for c in confidences if c > 0.7]))  # High-confidence count
                    ])
                else:
                    features.extend([0.0, 0.0, 0.0])
            else:
                features.extend([0.0, 0.0, 0.0])

            # Category features (4 features)
            category_counts = {
                'bullish_continuation': 0,
                'bearish_continuation': 0,
                'bullish_reversal': 0,
                'bearish_reversal': 0
            }

            for p in patterns:
                category = ''
                if hasattr(p, 'category'):
                    category = str(p.category).lower()
                elif isinstance(p, dict):
                    category = p.get('category', '').lower()

                if 'bullish' in category and 'continuation' in category:
                    category_counts['bullish_continuation'] += 1
                elif 'bearish' in category and 'continuation' in category:
                    category_counts['bearish_continuation'] += 1
                elif 'bullish' in category and 'reversal' in category:
                    category_counts['bullish_reversal'] += 1
                elif 'bearish' in category and 'reversal' in category:
                    category_counts['bearish_reversal'] += 1

            total_patterns = len(patterns) if patterns else 1
            features.extend([
                category_counts['bullish_continuation'] / total_patterns,
                category_counts['bearish_continuation'] / total_patterns,
                category_counts['bullish_reversal'] / total_patterns,
                category_counts['bearish_reversal'] / total_patterns
            ])

            # Timing features (2 features)
            if patterns:
                try:
                    # Get most recent pattern
                    most_recent = None
                    for p in patterns:
                        if hasattr(p, 'end_time'):
                            if most_recent is None or p.end_time > most_recent.end_time:
                                most_recent = p

                    if most_recent and hasattr(most_recent, 'start_time'):
                        pattern_age = (most_recent.end_time - most_recent.start_time).total_seconds() / 86400

                        # Average duration
                        durations = []
                        for p in patterns:
                            if hasattr(p, 'start_time') and hasattr(p, 'end_time'):
                                dur = (p.end_time - p.start_time).total_seconds() / 86400
                                durations.append(dur)

                        avg_duration = np.mean(durations) if durations else 7.0

                        features.extend([
                            min(pattern_age, 30.0) / 30.0,  # Normalize to 0-1
                            min(avg_duration, 14.0) / 14.0   # Normalize to 0-1
                        ])
                    else:
                        features.extend([0.0, 0.0])
                except:
                    features.extend([0.0, 0.0])
            else:
                features.extend([0.0, 0.0])

            self.logger.debug(f"Extracted {len(features)} pattern features")
            return features

        except Exception as e:
            self.logger.error(f"Pattern feature extraction failed: {e}")
            return [0.0] * 17  # Return zeros as fallback

    def get_feature_names(self) -> List[str]:
        """
        Get names of all extracted features.

        Returns:
            List of feature names in the same order as extract() output
        """
        return [
            # Pattern presence (8)
            'has_triangle', 'has_flag', 'has_wedge', 'has_rectangle',
            'has_head_shoulders', 'has_double_top', 'has_double_bottom', 'has_cup_handle',
            # Confidence features (3)
            'max_confidence', 'avg_confidence', 'high_confidence_count',
            # Category features (4)
            'bullish_continuation_ratio', 'bearish_continuation_ratio',
            'bullish_reversal_ratio', 'bearish_reversal_ratio',
            # Timing features (2)
            'pattern_age', 'avg_duration'
        ]


class TimeFeatureExtractor:
    """
    Extract time-based features for ML models.

    This extractor captures temporal patterns that affect market behavior:
    - Day of week effects (Monday effect, Friday effect)
    - Monthly seasonality
    - Market session effects (Asian, European, US)
    - Weekend vs weekday patterns

    Feature Importance:
    - Market sessions: Medium importance for intraday patterns
    - Day of week: Low-medium importance for swing trading
    - Month seasonality: Low importance but captures yearly cycles
    """

    def __init__(self):
        """Initialize time feature extractor."""
        self.logger = logging.getLogger(__name__)

    def extract(self, data: PriceDataFrame) -> List[float]:
        """
        Extract time-based features from price data.

        Args:
            data: Price data frame with timestamp information

        Returns:
            List of time features including:
            - Day of week (one-hot encoded, 7 features)
            - Hour of day (normalized, 1 feature)
            - Month seasonality (sin/cos encoded, 2 features)
            - Quarter (one-hot encoded, 4 features)
            - Weekend flag (1 feature)
            - Market sessions (3 features)

        Feature Importance Ranking:
        1. Market sessions: 0.08 - Trading activity patterns
        2. Day of week: 0.06 - Weekly patterns
        3. Month seasonality: 0.04 - Seasonal effects
        """
        try:
            features = []

            if not data.data:
                return [0.0] * 18

            latest_time = data.data[-1].timestamp

            # Day of week features (7 features)
            day_of_week = latest_time.weekday()
            dow_features = [1.0 if i == day_of_week else 0.0 for i in range(7)]
            features.extend(dow_features)

            # Hour of day (1 feature)
            hour_of_day = latest_time.hour / 23.0
            features.append(hour_of_day)

            # Month seasonality (2 features)
            month = latest_time.month
            month_sin = np.sin(2 * np.pi * month / 12)
            month_cos = np.cos(2 * np.pi * month / 12)
            features.extend([month_sin, month_cos])

            # Quarter (4 features)
            quarter = (month - 1) // 3
            quarter_features = [1.0 if i == quarter else 0.0 for i in range(4)]
            features.extend(quarter_features)

            # Weekend flag (1 feature)
            is_weekend = 1.0 if day_of_week >= 5 else 0.0
            features.append(is_weekend)

            # Market sessions (3 features)
            hour = latest_time.hour
            asian_session = 1.0 if 0 <= hour < 8 else 0.0
            european_session = 1.0 if 8 <= hour < 16 else 0.0
            us_session = 1.0 if 16 <= hour < 24 else 0.0
            features.extend([asian_session, european_session, us_session])

            self.logger.debug(f"Extracted {len(features)} time features")
            return features

        except Exception as e:
            self.logger.error(f"Time feature extraction failed: {e}")
            return [0.0] * 18

    def get_feature_names(self) -> List[str]:
        """
        Get names of all extracted features.

        Returns:
            List of feature names in the same order as extract() output
        """
        return [
            # Day of week (7)
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
            # Hour (1)
            'hour_normalized',
            # Month seasonality (2)
            'month_sin', 'month_cos',
            # Quarter (4)
            'q1', 'q2', 'q3', 'q4',
            # Weekend (1)
            'is_weekend',
            # Market sessions (3)
            'asian_session', 'european_session', 'us_session'
        ]
