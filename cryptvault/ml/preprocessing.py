"""
Production-Grade Data Preprocessing Pipeline

Handles NaN values, outliers, scaling, and feature engineering.
"""

import logging
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Robust data preprocessing pipeline."""

    def __init__(self):
        self.scaler = RobustScaler()
        self.imputer = SimpleImputer(strategy="mean")
        self.is_fitted = False
        self.feature_names = []

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create comprehensive technical features from OHLCV data."""
        # Flatten multi-level columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        features = pd.DataFrame(index=df.index)

        # Price features
        features["close"] = df["Close"].values
        features["high"] = df["High"].values
        features["low"] = df["Low"].values
        features["open"] = df["Open"].values
        features["volume"] = df["Volume"].values

        # Returns
        features["returns"] = df["Close"].pct_change().values
        features["log_returns"] = np.log(df["Close"] / df["Close"].shift(1)).values

        # Moving averages
        for period in [5, 10, 20, 50]:
            features[f"sma_{period}"] = df["Close"].rolling(period).mean().values
            features[f"ema_{period}"] = df["Close"].ewm(span=period).mean().values

        # Price relative to MAs
        features["price_to_sma20"] = (df["Close"] / features["sma_20"]).values
        features["price_to_sma50"] = (df["Close"] / features["sma_50"]).values

        # Volatility
        features["volatility_20"] = df["Close"].rolling(20).std().values
        features["volatility_50"] = df["Close"].rolling(50).std().values

        # RSI
        delta = df["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        features["rsi"] = (100 - (100 / (1 + rs))).values

        # MACD
        exp1 = df["Close"].ewm(span=12, adjust=False).mean()
        exp2 = df["Close"].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        features["macd"] = macd.values
        features["macd_signal"] = macd.ewm(span=9, adjust=False).mean().values
        features["macd_diff"] = (macd - features["macd_signal"]).values

        # Bollinger Bands
        bb_middle = df["Close"].rolling(20).mean()
        bb_std = df["Close"].rolling(20).std()
        features["bb_middle"] = bb_middle.values
        features["bb_upper"] = (bb_middle + (bb_std * 2)).values
        features["bb_lower"] = (bb_middle - (bb_std * 2)).values
        features["bb_width"] = (
            (features["bb_upper"] - features["bb_lower"]) / features["bb_middle"]
        ).values
        features["bb_position"] = (
            (df["Close"] - features["bb_lower"]) / (features["bb_upper"] - features["bb_lower"])
        ).values

        # Momentum
        features["momentum_5"] = (df["Close"] / df["Close"].shift(5) - 1).values
        features["momentum_10"] = (df["Close"] / df["Close"].shift(10) - 1).values
        features["momentum_20"] = (df["Close"] / df["Close"].shift(20) - 1).values

        # Volume features
        volume_sma_20 = df["Volume"].rolling(20).mean()
        features["volume_sma_20"] = volume_sma_20.values
        features["volume_ratio"] = (df["Volume"] / volume_sma_20).values

        # Price range
        features["high_low_ratio"] = (df["High"] / df["Low"]).values
        features["close_open_ratio"] = (df["Close"] / df["Open"]).values

        # ATR (Average True Range)
        high_low = df["High"] - df["Low"]
        high_close = np.abs(df["High"] - df["Close"].shift())
        low_close = np.abs(df["Low"] - df["Close"].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        features["atr"] = true_range.rolling(14).mean().values

        # Lag features
        for lag in [1, 2, 3, 5, 10]:
            features[f"close_lag_{lag}"] = df["Close"].shift(lag).values
            features[f"returns_lag_{lag}"] = features["returns"].shift(lag).values

        # Time features (cyclical encoding)
        features["day_of_week_sin"] = np.sin(2 * np.pi * df.index.dayofweek / 7)
        features["day_of_week_cos"] = np.cos(2 * np.pi * df.index.dayofweek / 7)
        features["day_of_month_sin"] = np.sin(2 * np.pi * df.index.day / 31)
        features["day_of_month_cos"] = np.cos(2 * np.pi * df.index.day / 31)
        features["month_sin"] = np.sin(2 * np.pi * df.index.month / 12)
        features["month_cos"] = np.cos(2 * np.pi * df.index.month / 12)

        # Advanced features
        # Rate of change
        features["roc_5"] = (df["Close"] - df["Close"].shift(5)) / df["Close"].shift(5) * 100
        features["roc_10"] = (df["Close"] - df["Close"].shift(10)) / df["Close"].shift(10) * 100

        # Williams %R
        high_14 = df["High"].rolling(14).max()
        low_14 = df["Low"].rolling(14).min()
        features["williams_r"] = ((high_14 - df["Close"]) / (high_14 - low_14) * -100).values

        # Stochastic Oscillator
        features["stoch_k"] = ((df["Close"] - low_14) / (high_14 - low_14) * 100).values
        features["stoch_d"] = features["stoch_k"].rolling(3).mean().values

        # Money Flow Index (MFI)
        typical_price = (df["High"] + df["Low"] + df["Close"]) / 3
        money_flow = typical_price * df["Volume"]

        positive_flow = (
            money_flow.where(typical_price > typical_price.shift(1), 0).rolling(14).sum()
        )
        negative_flow = (
            money_flow.where(typical_price < typical_price.shift(1), 0).rolling(14).sum()
        )

        mfi_ratio = positive_flow / negative_flow
        features["mfi"] = (100 - (100 / (1 + mfi_ratio))).values

        # Commodity Channel Index (CCI)
        mad = typical_price.rolling(20).apply(lambda x: np.abs(x - x.mean()).mean())
        features["cci"] = (
            (typical_price - typical_price.rolling(20).mean()) / (0.015 * mad)
        ).values

        # Donchian Channels
        features["donchian_high"] = df["High"].rolling(20).max().values
        features["donchian_low"] = df["Low"].rolling(20).min().values
        features["donchian_mid"] = (
            (features["donchian_high"] + features["donchian_low"]) / 2
        ).values

        # Keltner Channels
        keltner_mid = df["Close"].ewm(span=20).mean()
        keltner_atr = features["atr"]
        features["keltner_upper"] = (keltner_mid + 2 * keltner_atr).values
        features["keltner_lower"] = (keltner_mid - 2 * keltner_atr).values

        # Price momentum oscillator
        features["pmo"] = (df["Close"].ewm(span=35).mean() - df["Close"].ewm(span=20).mean()).values

        # Volume-weighted features
        features["vwap"] = (
            (df["Close"] * df["Volume"]).rolling(20).sum() / df["Volume"].rolling(20).sum()
        ).values
        features["price_to_vwap"] = (df["Close"] / features["vwap"]).values

        return features

    def fit(self, X: pd.DataFrame) -> "DataPreprocessor":
        """Fit the preprocessor on training data."""
        # Store feature names
        self.feature_names = X.columns.tolist()

        # Fit imputer
        X_imputed = self.imputer.fit_transform(X)

        # Fit scaler
        self.scaler.fit(X_imputed)

        self.is_fitted = True
        logger.info(f"Preprocessor fitted on {len(self.feature_names)} features")

        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """Transform data using fitted preprocessor."""
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted before transform")

        # Ensure same features
        X = X[self.feature_names]

        # Impute missing values
        X_imputed = self.imputer.transform(X)

        # Scale features
        X_scaled = self.scaler.transform(X_imputed)

        return X_scaled

    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        """Fit and transform in one step."""
        return self.fit(X).transform(X)

    def inverse_transform_target(
        self, y_scaled: np.ndarray, original_prices: np.ndarray
    ) -> np.ndarray:
        """Convert scaled predictions back to original price scale."""
        # Simple approach: use the scale from original prices
        if len(original_prices) > 0:
            scale = np.mean(original_prices)
            return y_scaled * scale
        return y_scaled


def prepare_sequences(
    X: np.ndarray, y: np.ndarray, sequence_length: int = 10
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Prepare sequences for time series prediction.

    Args:
        X: Feature matrix
        y: Target values
        sequence_length: Length of input sequences

    Returns:
        X_sequences, y_sequences
    """
    X_seq = []
    y_seq = []

    for i in range(sequence_length, len(X)):
        X_seq.append(X[i - sequence_length : i])
        y_seq.append(y[i])

    return np.array(X_seq), np.array(y_seq)


def split_train_val_test(
    X: np.ndarray, y: np.ndarray, train_ratio: float = 0.7, val_ratio: float = 0.15
) -> Tuple:
    """
    Split data into train, validation, and test sets.

    Maintains temporal order for time series.
    """
    n = len(X)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))

    X_train = X[:train_end]
    y_train = y[:train_end]

    X_val = X[train_end:val_end]
    y_val = y[train_end:val_end]

    X_test = X[val_end:]
    y_test = y[val_end:]

    return X_train, y_train, X_val, y_val, X_test, y_test
