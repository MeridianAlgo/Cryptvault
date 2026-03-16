"""
Shared pytest fixtures for CryptVault test suite.
"""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def symbol():
    """Default test symbol."""
    return "BTC"


@pytest.fixture
def test_days():
    return 5


@pytest.fixture
def synthetic_price_df():
    """Generate a 200-bar synthetic OHLCV DataFrame."""
    np.random.seed(42)
    n = 200
    dates = pd.date_range("2023-01-01", periods=n, freq="D")
    prices = 30000 + np.cumsum(np.random.randn(n) * 300)
    prices = np.maximum(prices, 100)

    df = pd.DataFrame(
        {
            "Open":   prices * (1 + np.random.randn(n) * 0.003),
            "High":   prices * (1 + np.abs(np.random.randn(n) * 0.006)),
            "Low":    prices * (1 - np.abs(np.random.randn(n) * 0.006)),
            "Close":  prices,
            "Volume": np.random.randint(5_000, 50_000, n).astype(float),
        },
        index=dates,
    )
    return df


def _make_features(n=500, trend="bullish"):
    """Generate synthetic feature arrays for ML tests."""
    np.random.seed(42)
    t = np.linspace(0, 10, n)

    if trend == "bullish":
        base = 100 + 5 * t
    elif trend == "bearish":
        base = 150 - 3 * t
    else:
        base = 100 + np.sin(t) * 2

    prices = base + np.random.normal(0, 2, n)
    prices = np.maximum(prices, 1.0)

    X = []
    for i in range(n):
        window = prices[max(0, i - 20): i + 1]
        X.append(
            [
                prices[i],
                np.mean(window),
                np.std(window) if len(window) > 1 else 0.01,
                (prices[i] - prices[i - 1]) / prices[i - 1] if i > 0 else 0.0,
                i / n,
            ]
        )

    return np.array(X), prices


@pytest.fixture
def X_train():
    X, _ = _make_features(400)
    return X[:300]


@pytest.fixture
def y_train():
    _, y = _make_features(400)
    return y[:300]


@pytest.fixture
def X_test():
    X, _ = _make_features(400)
    return X[300:]


@pytest.fixture
def y_test():
    _, y = _make_features(400)
    return y[300:]


@pytest.fixture
def y_train_only():
    """For ARIMA-style tests that only need 1-D series."""
    _, y = _make_features(400)
    return y[:300]


@pytest.fixture
def y_test_only():
    _, y = _make_features(400)
    return y[300:]
