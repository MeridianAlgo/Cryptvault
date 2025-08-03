"""Technical indicator feature extraction for ML models."""

import numpy as np
from typing import List, Dict, Any
import logging

from ...data.models import PriceDataFrame
from ...indicators.technical import TechnicalIndicators
from ...indicators.moving_averages import MovingAverages


class TechnicalFeatureExtractor:
    """Extract technical indicator features for ML models."""
    
    def __init__(self):
        """Initialize technical feature extractor."""
        self.technical_indicators = TechnicalIndicators()
        self.moving_averages = MovingAverages()
        self.logger = logging.getLogger(__name__)
    
    def extract(self, data: PriceDataFrame) -> List[float]:
        """
        Extract technical indicator features.
        
        Args:
            data: Price data frame
            
        Returns:
            List of technical indicator features
        """
        try:
            features = []
            
            # RSI features (multiple periods)
            rsi_features = self._extract_rsi_features(data)
            features.extend(rsi_features)
            
            # MACD features
            macd_features = self._extract_macd_features(data)
            features.extend(macd_features)
            
            # Bollinger Bands features
            bb_features = self._extract_bollinger_features(data)
            features.extend(bb_features)
            
            # Moving average features
            ma_features = self._extract_moving_average_features(data)
            features.extend(ma_features)
            
            # Volatility features
            vol_features = self._extract_volatility_features(data)
            features.extend(vol_features)
            
            # Volume features
            volume_features = self._extract_volume_features(data)
            features.extend(volume_features)
            
            # Price action features
            price_features = self._extract_price_action_features(data)
            features.extend(price_features)
            
            self.logger.debug(f"Extracted {len(features)} technical features")
            return features
            
        except Exception as e:
            self.logger.error(f"Technical feature extraction failed: {e}")
            return [0.0] * 25  # Return zeros as fallback
    
    def _extract_rsi_features(self, data: PriceDataFrame) -> List[float]:
        """Extract RSI-based features."""
        features = []
        
        try:
            # RSI with different periods
            rsi_14 = self.technical_indicators.calculate_rsi(data, period=14)
            rsi_21 = self.technical_indicators.calculate_rsi(data, period=21)
            
            # Current RSI values
            current_rsi_14 = rsi_14[-1] if rsi_14 and rsi_14[-1] is not None else 50.0
            current_rsi_21 = rsi_21[-1] if rsi_21 and rsi_21[-1] is not None else 50.0
            
            features.extend([
                current_rsi_14 / 100.0,  # Normalize to 0-1
                current_rsi_21 / 100.0,
                1.0 if current_rsi_14 > 70 else 0.0,  # Overbought flag
                1.0 if current_rsi_14 < 30 else 0.0,  # Oversold flag
                (current_rsi_14 - 50.0) / 50.0  # RSI momentum
            ])
            
        except Exception as e:
            self.logger.warning(f"RSI feature extraction failed: {e}")
            features.extend([0.5, 0.5, 0.0, 0.0, 0.0])
        
        return features
    
    def _extract_macd_features(self, data: PriceDataFrame) -> List[float]:
        """Extract MACD-based features."""
        features = []
        
        try:
            macd_data = self.technical_indicators.calculate_macd(data)
            
            if macd_data and len(macd_data['macd']) > 0:
                current_macd = macd_data['macd'][-1] or 0.0
                current_signal = macd_data['signal'][-1] or 0.0
                current_histogram = macd_data['histogram'][-1] or 0.0
                
                # Normalize MACD values
                price_range = data.data[-1].close * 0.1  # Use 10% of price as normalization
                
                features.extend([
                    current_macd / price_range,
                    current_signal / price_range,
                    current_histogram / price_range,
                    1.0 if current_macd > current_signal else 0.0,  # Bullish crossover
                    1.0 if current_histogram > 0 else 0.0  # Positive histogram
                ])
            else:
                features.extend([0.0, 0.0, 0.0, 0.0, 0.0])
                
        except Exception as e:
            self.logger.warning(f"MACD feature extraction failed: {e}")
            features.extend([0.0, 0.0, 0.0, 0.0, 0.0])
        
        return features
    
    def _extract_bollinger_features(self, data: PriceDataFrame) -> List[float]:
        """Extract Bollinger Bands features."""
        features = []
        
        try:
            bb_data = self.technical_indicators.calculate_bollinger_bands(data)
            
            if bb_data and len(bb_data['middle']) > 0:
                current_price = data.data[-1].close
                upper_band = bb_data['upper'][-1] or current_price
                middle_band = bb_data['middle'][-1] or current_price
                lower_band = bb_data['lower'][-1] or current_price
                
                # Bollinger Band position (0 = lower band, 1 = upper band)
                if upper_band != lower_band:
                    bb_position = (current_price - lower_band) / (upper_band - lower_band)
                else:
                    bb_position = 0.5
                
                # Band width (volatility measure)
                band_width = (upper_band - lower_band) / middle_band if middle_band > 0 else 0.0
                
                features.extend([
                    bb_position,
                    band_width,
                    1.0 if current_price > upper_band else 0.0,  # Above upper band
                    1.0 if current_price < lower_band else 0.0   # Below lower band
                ])
            else:
                features.extend([0.5, 0.02, 0.0, 0.0])
                
        except Exception as e:
            self.logger.warning(f"Bollinger Bands feature extraction failed: {e}")
            features.extend([0.5, 0.02, 0.0, 0.0])
        
        return features
    
    def _extract_moving_average_features(self, data: PriceDataFrame) -> List[float]:
        """Extract moving average features."""
        features = []
        
        try:
            current_price = data.data[-1].close
            
            # Calculate different moving averages
            prices = [point.close for point in data.data]
            sma_20 = self.moving_averages.simple_moving_average(prices, 20)
            sma_50 = self.moving_averages.simple_moving_average(prices, 50)
            ema_12 = self.moving_averages.exponential_moving_average(prices, 12)
            
            # Get current values
            current_sma_20 = sma_20[-1] if sma_20 else current_price
            current_sma_50 = sma_50[-1] if sma_50 else current_price
            current_ema_12 = ema_12[-1] if ema_12 else current_price
            
            features.extend([
                (current_price - current_sma_20) / current_sma_20 if current_sma_20 > 0 else 0.0,
                (current_price - current_sma_50) / current_sma_50 if current_sma_50 > 0 else 0.0,
                (current_price - current_ema_12) / current_ema_12 if current_ema_12 > 0 else 0.0,
                1.0 if current_sma_20 > current_sma_50 else 0.0,  # Golden cross indicator
                1.0 if current_price > current_sma_20 else 0.0     # Price above SMA20
            ])
            
        except Exception as e:
            self.logger.warning(f"Moving average feature extraction failed: {e}")
            features.extend([0.0, 0.0, 0.0, 0.0, 0.0])
        
        return features
    
    def _extract_volatility_features(self, data: PriceDataFrame) -> List[float]:
        """Extract volatility-based features."""
        features = []
        
        try:
            if len(data) >= 20:
                # Calculate realized volatility
                prices = [point.close for point in data.data[-20:]]
                returns = [np.log(prices[i]/prices[i-1]) for i in range(1, len(prices))]
                
                if returns:
                    volatility = np.std(returns)
                    volatility_ma = np.mean([abs(r) for r in returns])
                    
                    features.extend([
                        volatility,
                        volatility_ma,
                        1.0 if volatility > 0.03 else 0.0  # High volatility flag
                    ])
                else:
                    features.extend([0.02, 0.015, 0.0])
            else:
                features.extend([0.02, 0.015, 0.0])
                
        except Exception as e:
            self.logger.warning(f"Volatility feature extraction failed: {e}")
            features.extend([0.02, 0.015, 0.0])
        
        return features
    
    def _extract_volume_features(self, data: PriceDataFrame) -> List[float]:
        """Extract volume-based features."""
        features = []
        
        try:
            if len(data) >= 10:
                volumes = [point.volume for point in data.data[-10:]]
                current_volume = volumes[-1]
                avg_volume = np.mean(volumes[:-1]) if len(volumes) > 1 else current_volume
                
                # Volume ratio
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
                
                # Volume trend
                if len(volumes) >= 5:
                    recent_avg = np.mean(volumes[-3:])
                    older_avg = np.mean(volumes[-6:-3])
                    volume_trend = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0.0
                else:
                    volume_trend = 0.0
                
                features.extend([
                    min(volume_ratio, 5.0),  # Cap at 5x to avoid outliers
                    volume_trend,
                    1.0 if volume_ratio > 1.5 else 0.0  # High volume flag
                ])
            else:
                features.extend([1.0, 0.0, 0.0])
                
        except Exception as e:
            self.logger.warning(f"Volume feature extraction failed: {e}")
            features.extend([1.0, 0.0, 0.0])
        
        return features
    
    def _extract_price_action_features(self, data: PriceDataFrame) -> List[float]:
        """Extract price action features."""
        features = []
        
        try:
            if len(data) >= 5:
                recent_candles = data.data[-5:]
                
                # Price momentum
                price_change_1d = (recent_candles[-1].close - recent_candles[-2].close) / recent_candles[-2].close
                price_change_3d = (recent_candles[-1].close - recent_candles[-4].close) / recent_candles[-4].close
                
                # Candle patterns
                current_candle = recent_candles[-1]
                body_size = abs(current_candle.close - current_candle.open)
                total_range = current_candle.high - current_candle.low
                body_ratio = body_size / total_range if total_range > 0 else 0.0
                
                # Upper and lower wicks
                if current_candle.close >= current_candle.open:  # Bullish candle
                    upper_wick = current_candle.high - current_candle.close
                    lower_wick = current_candle.open - current_candle.low
                else:  # Bearish candle
                    upper_wick = current_candle.high - current_candle.open
                    lower_wick = current_candle.close - current_candle.low
                
                upper_wick_ratio = upper_wick / total_range if total_range > 0 else 0.0
                lower_wick_ratio = lower_wick / total_range if total_range > 0 else 0.0
                
                features.extend([
                    price_change_1d,
                    price_change_3d,
                    body_ratio,
                    upper_wick_ratio,
                    lower_wick_ratio
                ])
            else:
                features.extend([0.0, 0.0, 0.5, 0.1, 0.1])
                
        except Exception as e:
            self.logger.warning(f"Price action feature extraction failed: {e}")
            features.extend([0.0, 0.0, 0.5, 0.1, 0.1])
        
        return features
    
    def get_feature_names(self) -> List[str]:
        """Get names of all extracted features."""
        return [
            # RSI features
            'rsi_14', 'rsi_21', 'rsi_overbought', 'rsi_oversold', 'rsi_momentum',
            # MACD features
            'macd', 'macd_signal', 'macd_histogram', 'macd_bullish', 'macd_positive',
            # Bollinger Bands features
            'bb_position', 'bb_width', 'bb_above_upper', 'bb_below_lower',
            # Moving average features
            'price_vs_sma20', 'price_vs_sma50', 'price_vs_ema12', 'golden_cross', 'price_above_sma20',
            # Volatility features
            'volatility', 'volatility_ma', 'high_volatility',
            # Volume features
            'volume_ratio', 'volume_trend', 'high_volume',
            # Price action features
            'price_change_1d', 'price_change_3d', 'body_ratio', 'upper_wick_ratio', 'lower_wick_ratio'
        ]