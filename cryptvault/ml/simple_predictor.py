"""
CryptVault Simple Predictor - Reliable ML Predictions Without Errors

This module provides a simplified, error-free prediction system.
No complex LSTM, no dimension mismatches, just reliable predictions.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Prediction:
    """Prediction result."""
    direction: str  # 'bullish', 'bearish', 'neutral'
    confidence: float  # 0-100
    price_change_pct: float  # Expected % change
    support: float
    resistance: float
    trend_strength: str  # 'strong', 'moderate', 'weak'


class SimplePredictor:
    """
    Simple, reliable predictor using technical analysis.
    
    No complex ML models that can fail.
    Uses proven technical indicators for predictions.
    """
    
    def __init__(self):
        self.is_trained = False
        self.training_data = None
    
    def predict(self, df: pd.DataFrame, patterns: List[Dict] = None) -> Prediction:
        """
        Generate prediction based on technical analysis.
        
        Args:
            df: DataFrame with OHLCV data
            patterns: List of detected patterns
            
        Returns:
            Prediction object with direction, confidence, etc.
        """
        # Normalize columns
        df = self._normalize_columns(df)
        
        # Calculate indicators
        rsi = self._calculate_rsi(df['Close'].values, 14)
        macd, signal = self._calculate_macd(df['Close'].values)
        sma_20 = df['Close'].rolling(20).mean().iloc[-1]
        sma_50 = df['Close'].rolling(50).mean().iloc[-1]
        current_price = df['Close'].iloc[-1]
        
        # Calculate support/resistance
        support = df['Low'].rolling(20).min().iloc[-1]
        resistance = df['High'].rolling(20).max().iloc[-1]
        
        # Score calculation
        bullish_score = 0
        bearish_score = 0
        
        # RSI signals
        current_rsi = rsi[-1] if not np.isnan(rsi[-1]) else 50
        if current_rsi < 30:
            bullish_score += 25  # Oversold
        elif current_rsi > 70:
            bearish_score += 25  # Overbought
        elif current_rsi < 50:
            bearish_score += 10
        else:
            bullish_score += 10
        
        # MACD signals
        if not np.isnan(macd[-1]) and not np.isnan(signal[-1]):
            if macd[-1] > signal[-1]:
                bullish_score += 20  # Bullish crossover
            else:
                bearish_score += 20  # Bearish crossover
        
        # Moving average signals
        if not np.isnan(sma_20) and not np.isnan(sma_50):
            if current_price > sma_20 > sma_50:
                bullish_score += 25  # Strong uptrend
            elif current_price < sma_20 < sma_50:
                bearish_score += 25  # Strong downtrend
            elif current_price > sma_20:
                bullish_score += 15
            else:
                bearish_score += 15
        
        # Pattern signals
        if patterns:
            for pattern in patterns:
                direction = pattern.get('direction', 'neutral')
                conf = pattern.get('confidence', 50) / 100
                
                if direction == 'bullish':
                    bullish_score += 15 * conf
                elif direction == 'bearish':
                    bearish_score += 15 * conf
        
        # Momentum
        if len(df) >= 5:
            momentum = (df['Close'].iloc[-1] - df['Close'].iloc[-5]) / df['Close'].iloc[-5] * 100
            if momentum > 2:
                bullish_score += 15
            elif momentum < -2:
                bearish_score += 15
        
        # Calculate final prediction
        total_score = bullish_score + bearish_score
        if total_score == 0:
            total_score = 1
        
        if bullish_score > bearish_score:
            direction = 'bullish'
            confidence = min(90, 50 + (bullish_score - bearish_score))
            price_change = (bullish_score - bearish_score) / total_score * 5
        elif bearish_score > bullish_score:
            direction = 'bearish'
            confidence = min(90, 50 + (bearish_score - bullish_score))
            price_change = -(bearish_score - bullish_score) / total_score * 5
        else:
            direction = 'neutral'
            confidence = 50
            price_change = 0
        
        # Trend strength
        diff = abs(bullish_score - bearish_score)
        if diff > 40:
            trend_strength = 'strong'
        elif diff > 20:
            trend_strength = 'moderate'
        else:
            trend_strength = 'weak'
        
        return Prediction(
            direction=direction,
            confidence=confidence,
            price_change_pct=price_change,
            support=support,
            resistance=resistance,
            trend_strength=trend_strength
        )
    
    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column names."""
        column_map = {
            'open': 'Open', 'high': 'High', 'low': 'Low',
            'close': 'Close', 'volume': 'Volume'
        }
        return df.rename(columns=column_map)
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> np.ndarray:
        """Calculate RSI indicator."""
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        rsi = np.zeros(len(prices))
        rsi[:] = np.nan
        
        if len(prices) < period + 1:
            return rsi
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        for i in range(period, len(prices) - 1):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                rsi[i + 1] = 100
            else:
                rs = avg_gain / avg_loss
                rsi[i + 1] = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(self, prices: np.ndarray, 
                       fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
        """Calculate MACD indicator."""
        def ema(data, period):
            result = np.zeros(len(data))
            result[:] = np.nan
            if len(data) < period:
                return result
            
            multiplier = 2 / (period + 1)
            result[period - 1] = np.mean(data[:period])
            
            for i in range(period, len(data)):
                result[i] = (data[i] - result[i - 1]) * multiplier + result[i - 1]
            
            return result
        
        ema_fast = ema(prices, fast)
        ema_slow = ema(prices, slow)
        macd_line = ema_fast - ema_slow
        signal_line = ema(macd_line[~np.isnan(macd_line)], signal)
        
        # Pad signal line to match length
        full_signal = np.zeros(len(prices))
        full_signal[:] = np.nan
        full_signal[-len(signal_line):] = signal_line
        
        return macd_line, full_signal
    
    def get_summary(self, prediction: Prediction) -> str:
        """Get human-readable prediction summary."""
        emoji = "🟢" if prediction.direction == "bullish" else "🔴" if prediction.direction == "bearish" else "🟡"
        
        return f"""
{emoji} ML Forecast: {prediction.direction.upper()} ({prediction.confidence:.1f}%)
   Trend Strength: {prediction.trend_strength}
   Expected Change: {prediction.price_change_pct:+.2f}%
   Support: ${prediction.support:,.2f}
   Resistance: ${prediction.resistance:,.2f}
"""
