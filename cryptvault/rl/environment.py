"""
Trading Environment for Reinforcement Learning

Implements a Gym-compatible environment for crypto trading.
"""

import logging
from typing import Dict, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class TradingEnvironment:
    """
    Advanced trading environment with realistic market simulation.

    Features:
    - Continuous action space (position sizing)
    - Transaction costs and slippage
    - Risk-adjusted rewards (Sharpe ratio)
    - Market impact modeling
    - Multi-asset support
    """

    def __init__(
        self,
        data,
        initial_balance: float = 100000.0,
        transaction_cost: float = 0.001,  # 0.1%
        slippage: float = 0.0005,  # 0.05%
        max_position_size: float = 1.0,  # 100% of portfolio
        lookback_window: int = 60,
        reward_scaling: float = 1000.0,
    ):
        # Convert PriceDataFrame to pandas DataFrame if needed
        if not isinstance(data, pd.DataFrame):
            # Assume it's a PriceDataFrame
            df_data = {
                "Open": [p.open for p in data.data],
                "High": [p.high for p in data.data],
                "Low": [p.low for p in data.data],
                "Close": [p.close for p in data.data],
                "Volume": [p.volume for p in data.data],
            }
            data = pd.DataFrame(df_data, index=[p.timestamp for p in data.data])

        self.data = data
        self.initial_balance = initial_balance
        self.transaction_cost = transaction_cost
        self.slippage = slippage
        self.max_position_size = max_position_size
        self.lookback_window = lookback_window
        self.reward_scaling = reward_scaling

        # State variables
        self.current_step = 0
        self.balance = initial_balance
        self.position = 0.0  # Current position size (-1 to 1)
        self.entry_price = 0.0
        self.total_trades = 0
        self.winning_trades = 0

        # Performance tracking
        self.portfolio_values = []
        self.returns = []
        self.actions_taken = []

        # Observation space size
        self.observation_size = self._get_observation_size()

        logger.info(f"Trading environment initialized with {len(data)} steps")

    def _get_observation_size(self) -> int:
        """Calculate observation space size."""
        # Price features + technical indicators + portfolio state
        return self.lookback_window * 5 + 10  # OHLCV + indicators + state

    def reset(self) -> np.ndarray:
        """Reset environment to initial state."""
        self.current_step = self.lookback_window
        self.balance = self.initial_balance
        self.position = 0.0
        self.entry_price = 0.0
        self.total_trades = 0
        self.winning_trades = 0

        self.portfolio_values = [self.initial_balance]
        self.returns = []
        self.actions_taken = []

        return self._get_observation()

    def _get_observation(self) -> np.ndarray:
        """Get current observation state."""
        if self.current_step < self.lookback_window:
            self.current_step = self.lookback_window

        # Get historical price data
        start_idx = self.current_step - self.lookback_window
        end_idx = self.current_step

        window_data = self.data.iloc[start_idx:end_idx]

        # Normalize prices
        close_prices = window_data["Close"].values
        price_mean = close_prices.mean()
        price_std = close_prices.std()
        if price_std == 0 or np.isnan(price_std) or price_std < 1e-8:
            price_std = 1.0
        normalized_prices = (close_prices - price_mean) / price_std

        # Volume
        volumes = window_data["Volume"].values
        vol_mean = volumes.mean()
        vol_std = volumes.std()
        if vol_std == 0 or np.isnan(vol_std) or vol_std < 1e-8:
            vol_std = 1.0
        normalized_volumes = (volumes - vol_mean) / vol_std

        # Returns
        returns = np.diff(close_prices) / close_prices[:-1]
        returns = np.concatenate([[0], returns])

        # Volatility
        volatility = pd.Series(returns).rolling(20, min_periods=1).std().values

        # Trend (simple moving average)
        sma = pd.Series(close_prices).rolling(20, min_periods=1).mean().values
        trend = (close_prices - sma) / (sma + 1e-8)

        # Combine price features
        price_features = np.column_stack(
            [normalized_prices, normalized_volumes, returns, volatility, trend]
        ).flatten()

        # Portfolio state
        current_price = close_prices[-1]
        portfolio_value = self.balance + self.position * current_price * self.balance

        portfolio_state = np.array(
            [
                self.position,  # Current position
                self.balance / self.initial_balance,  # Normalized balance
                portfolio_value / self.initial_balance,  # Normalized portfolio value
                (
                    (current_price - self.entry_price) / (self.entry_price + 1e-8)
                    if self.entry_price > 0
                    else 0
                ),  # Unrealized P&L
                self.total_trades / 100.0,  # Normalized trade count
                self.winning_trades / (self.total_trades + 1),  # Win rate
                len(self.returns) / 1000.0,  # Normalized time
                np.mean(self.returns[-20:]) if len(self.returns) > 0 else 0,  # Recent return
                np.std(self.returns[-20:]) if len(self.returns) > 0 else 0,  # Recent volatility
                self._calculate_sharpe_ratio(),  # Sharpe ratio
            ]
        )

        observation = np.concatenate([price_features, portfolio_state])

        # Replace any NaN or inf values
        observation = np.nan_to_num(observation, nan=0.0, posinf=1.0, neginf=-1.0)

        return observation.astype(np.float32)

    def step(self, action: float) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Execute one step in the environment.

        Args:
            action: Trading action (-1 to 1, where -1=full short, 0=neutral, 1=full long)

        Returns:
            observation, reward, done, info
        """
        # Clip action to valid range
        action = np.clip(action, -self.max_position_size, self.max_position_size)

        # Get current price
        current_price = self.data.iloc[self.current_step]["Close"]

        # Calculate position change
        position_change = action - self.position

        # Execute trade if position changes
        reward = 0.0
        if abs(position_change) > 0.01:  # Minimum trade size
            # Calculate costs
            trade_cost = abs(position_change) * self.transaction_cost
            slippage_cost = abs(position_change) * self.slippage
            total_cost = trade_cost + slippage_cost

            # Update position
            old_position = self.position
            self.position = action

            # Track entry price for new positions
            if old_position == 0 and self.position != 0:
                self.entry_price = current_price

            # Close position - calculate P&L
            if old_position != 0 and self.position == 0:
                pnl = old_position * (current_price - self.entry_price) / self.entry_price
                self.balance *= 1 + pnl - total_cost

                self.total_trades += 1
                if pnl > 0:
                    self.winning_trades += 1

                self.entry_price = 0.0
            else:
                # Partial close or position adjustment
                self.balance *= 1 - total_cost

        # Calculate portfolio value
        portfolio_value = self.balance + self.position * current_price * self.balance
        self.portfolio_values.append(portfolio_value)

        # Calculate return
        if len(self.portfolio_values) > 1:
            ret = (portfolio_value - self.portfolio_values[-2]) / self.portfolio_values[-2]
            self.returns.append(ret)

        # Calculate reward
        reward = self._calculate_reward(portfolio_value)

        # Move to next step
        self.current_step += 1
        self.actions_taken.append(action)

        # Check if done
        done = (
            self.current_step >= len(self.data) - 1 or portfolio_value <= self.initial_balance * 0.5
        )

        # Get next observation
        observation = self._get_observation() if not done else np.zeros(self.observation_size)

        # Info dict
        info = {
            "portfolio_value": portfolio_value,
            "position": self.position,
            "balance": self.balance,
            "total_trades": self.total_trades,
            "win_rate": self.winning_trades / (self.total_trades + 1),
            "sharpe_ratio": self._calculate_sharpe_ratio(),
        }

        return observation, reward, done, info

    def _calculate_reward(self, portfolio_value: float) -> float:
        """
        Calculate reward using risk-adjusted returns.

        Combines:
        - Portfolio return
        - Sharpe ratio
        - Win rate
        - Drawdown penalty
        """
        # Portfolio return
        portfolio_return = (portfolio_value - self.initial_balance) / self.initial_balance

        # Sharpe ratio component
        sharpe = self._calculate_sharpe_ratio()

        # Win rate component
        win_rate = self.winning_trades / (self.total_trades + 1)

        # Drawdown penalty
        max_value = max(self.portfolio_values) if self.portfolio_values else self.initial_balance
        drawdown = (max_value - portfolio_value) / max_value
        drawdown_penalty = -drawdown * 2.0

        # Combined reward
        reward = portfolio_return * 1.0 + sharpe * 0.5 + win_rate * 0.3 + drawdown_penalty

        return reward * self.reward_scaling

    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio of returns."""
        if len(self.returns) < 2:
            return 0.0

        returns_array = np.array(self.returns)
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array)

        if std_return == 0:
            return 0.0

        # Annualized Sharpe ratio (assuming daily data)
        sharpe = (mean_return / std_return) * np.sqrt(252)

        return np.clip(sharpe, -5, 5)

    def get_metrics(self) -> Dict:
        """Get performance metrics."""
        if len(self.portfolio_values) < 2:
            return {}

        final_value = self.portfolio_values[-1]
        total_return = (final_value - self.initial_balance) / self.initial_balance

        returns_array = np.array(self.returns)
        sharpe = self._calculate_sharpe_ratio()

        # Max drawdown
        cummax = np.maximum.accumulate(self.portfolio_values)
        drawdowns = (cummax - self.portfolio_values) / cummax
        max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0

        # Sortino ratio (downside deviation)
        downside_returns = returns_array[returns_array < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
        sortino = (np.mean(returns_array) / downside_std) * np.sqrt(252) if downside_std > 0 else 0

        return {
            "total_return": total_return * 100,
            "final_value": final_value,
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "max_drawdown": max_drawdown * 100,
            "total_trades": self.total_trades,
            "win_rate": self.winning_trades / (self.total_trades + 1) * 100,
            "avg_return": np.mean(returns_array) * 100 if len(returns_array) > 0 else 0,
        }
