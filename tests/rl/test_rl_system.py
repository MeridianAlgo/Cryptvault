"""
Test RL Trading System

Comprehensive testing and evaluation of RL agents.
"""

import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cryptvault.data.fetchers import DataFetcher
from cryptvault.ml.preprocessing import DataPreprocessor

class FeatureEngineer(DataPreprocessor):
    """Compatibility shim: maps engineer_features → create_features."""
    def engineer_features(self, df):
        return self.create_features(df)
from cryptvault.rl import (
    DQNAgent,
    PPOAgent,
    RLTrainer,
    TradingEnvironment,
    TransformerAgent,
    compare_agents,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_environment():
    """Test trading environment."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Trading Environment")
    logger.info("=" * 60 + "\n")

    # Fetch data
    fetcher = DataFetcher()
    data = fetcher.fetch("BTC", days=100)

    if data is None or len(data) < 50:
        logger.error("Failed to fetch data")
        return False

    # Create environment
    env = TradingEnvironment(data, initial_balance=100000)

    # Test reset
    state = env.reset()
    logger.info(f"State shape: {state.shape}")
    logger.info(f"Observation size: {env.observation_size}")

    # Test random actions
    total_reward = 0
    for i in range(10):
        action = np.random.uniform(-1, 1)
        next_state, reward, done, info = env.step(action)
        total_reward += reward

        if done:
            break

    logger.info(f"Random policy - Total reward: {total_reward:.2f}")
    logger.info(f"Portfolio value: ${info['portfolio_value']:,.2f}")

    # Get metrics
    metrics = env.get_metrics()
    logger.info("\nEnvironment Metrics:")
    for key, value in metrics.items():
        logger.info(f"  {key}: {value:.2f}")

    return True


def test_dqn_agent():
    """Test DQN agent."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing DQN Agent")
    logger.info("=" * 60 + "\n")

    # Fetch data
    fetcher = DataFetcher()
    data = fetcher.fetch("BTC", days=100)

    if data is None or len(data) < 50:
        logger.error("Failed to fetch data")
        return False

    # Create environment and trainer
    env = TradingEnvironment(data)
    trainer = RLTrainer(env, agent_type="dqn", hidden_dim=256)

    # Train
    logger.info("Training DQN agent...")
    train_stats = trainer.train(num_episodes=50, eval_interval=10, early_stop_patience=30)

    logger.info("\nDQN Training Results:")
    logger.info(f"  Best Return: {train_stats['best_return']:.2%}")
    logger.info(f"  Final Return: {train_stats['final_return']:.2%}")
    logger.info(f"  Final Sharpe: {train_stats['final_sharpe']:.2f}")
    logger.info(f"  Training Time: {train_stats['training_time']:.1f}s")

    return train_stats["final_return"] > 0


def test_ppo_agent():
    """Test PPO agent."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing PPO Agent")
    logger.info("=" * 60 + "\n")

    # Fetch data
    fetcher = DataFetcher()
    data = fetcher.fetch("BTC", days=100)

    if data is None or len(data) < 50:
        logger.error("Failed to fetch data")
        return False

    # Create environment and trainer
    env = TradingEnvironment(data)
    trainer = RLTrainer(env, agent_type="ppo", hidden_dim=256)

    # Train
    logger.info("Training PPO agent...")
    train_stats = trainer.train(num_episodes=50, eval_interval=10, early_stop_patience=30)

    logger.info("\nPPO Training Results:")
    logger.info(f"  Best Return: {train_stats['best_return']:.2%}")
    logger.info(f"  Final Return: {train_stats['final_return']:.2%}")
    logger.info(f"  Final Sharpe: {train_stats['final_sharpe']:.2f}")
    logger.info(f"  Training Time: {train_stats['training_time']:.1f}s")

    return train_stats["final_return"] > 0


def test_transformer_agent():
    """Test Transformer agent."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Transformer Agent")
    logger.info("=" * 60 + "\n")

    # Fetch data
    fetcher = DataFetcher()
    data = fetcher.fetch("BTC", days=100)

    if data is None or len(data) < 50:
        logger.error("Failed to fetch data")
        return False

    # Create environment and trainer
    env = TradingEnvironment(data)
    trainer = RLTrainer(env, agent_type="transformer", d_model=128, num_heads=4, num_layers=2)

    # Train
    logger.info("Training Transformer agent...")
    train_stats = trainer.train(num_episodes=50, eval_interval=10, early_stop_patience=30)

    logger.info("\nTransformer Training Results:")
    logger.info(f"  Best Return: {train_stats['best_return']:.2%}")
    logger.info(f"  Final Return: {train_stats['final_return']:.2%}")
    logger.info(f"  Final Sharpe: {train_stats['final_sharpe']:.2f}")
    logger.info(f"  Training Time: {train_stats['training_time']:.1f}s")

    return train_stats["final_return"] > 0


def test_agent_comparison():
    """Compare all agents."""
    logger.info("\n" + "=" * 60)
    logger.info("Comparing All RL Agents")
    logger.info("=" * 60 + "\n")

    # Fetch data
    fetcher = DataFetcher()
    data = fetcher.fetch("BTC", days=150)

    if data is None or len(data) < 100:
        logger.error("Failed to fetch data")
        return False

    # Compare agents
    comparison_df = compare_agents(
        data, agent_types=["dqn", "ppo", "transformer"], num_episodes=100, num_eval_episodes=10
    )

    # Find best agent
    best_agent = comparison_df.iloc[0]
    logger.info(f"\nBest Agent: {best_agent['Agent']}")
    logger.info(f"Return: {best_agent['Final Return']:.2%}")
    logger.info(f"Sharpe: {best_agent['Sharpe Ratio']:.2f}")

    return best_agent["Final Return"] > 0


def compare_with_baseline():
    """Compare RL agents with baseline ML predictor."""
    logger.info("\n" + "=" * 60)
    logger.info("Comparing RL Agents with Baseline ML System")
    logger.info("=" * 60 + "\n")

    # Fetch data
    fetcher = DataFetcher()
    data = fetcher.fetch("BTC", days=200)

    if data is None or len(data) < 150:
        logger.error("Failed to fetch data")
        return False

    # Split data
    train_size = int(len(data) * 0.7)
    train_data = data[:train_size]
    test_data = data[train_size:]

    logger.info(f"Train size: {len(train_data)}, Test size: {len(test_data)}")

    # Baseline: Buy and Hold
    buy_hold_return = (test_data["Close"].iloc[-1] - test_data["Close"].iloc[0]) / test_data[
        "Close"
    ].iloc[0]
    logger.info(f"\nBuy & Hold Return: {buy_hold_return:.2%}")

    # Baseline: ML Predictor (from production system)
    try:
        from cryptvault.ml.production_predictor import ProductionPredictor

        # Engineer features
        engineer = FeatureEngineer()
        train_features = engineer.engineer_features(train_data)
        test_features = engineer.engineer_features(test_data)

        if train_features is None or test_features is None:
            logger.warning("Feature engineering failed")
        else:
            # Prepare data
            X_train = train_features.drop(columns=["Close"], errors="ignore").values
            y_train = train_features["Close"].values
            X_test = test_features.drop(columns=["Close"], errors="ignore").values
            y_test = test_features["Close"].values

            # Train predictor
            predictor = ProductionPredictor()
            predictor.train(X_train, y_train)

            # Evaluate
            metrics = predictor.evaluate(X_test, y_test)
            logger.info(f"\nML Predictor (Baseline):")
            logger.info(f"  MAPE: {metrics['MAPE']:.2f}%")
            logger.info(f"  Direction Accuracy: {metrics['Direction_Accuracy']:.1f}%")

            # Simulate trading with predictions
            predictions = predictor.predict(X_test)
            ml_returns = []
            for i in range(1, len(predictions)):
                pred_direction = np.sign(predictions[i] - predictions[i - 1])
                actual_return = (y_test[i] - y_test[i - 1]) / y_test[i - 1]
                ml_returns.append(pred_direction * actual_return)

            ml_total_return = np.sum(ml_returns)
            logger.info(f"  Trading Return: {ml_total_return:.2%}")

    except Exception as e:
        logger.warning(f"ML baseline failed: {e}")
        ml_total_return = 0

    # RL Agents
    rl_results = {}

    for agent_type in ["ppo", "transformer"]:
        logger.info(f"\nTraining {agent_type.upper()} agent...")

        env = TradingEnvironment(train_data)
        trainer = RLTrainer(env, agent_type=agent_type)

        # Train on training data
        trainer.train(num_episodes=100, eval_interval=20)

        # Evaluate on test data
        test_env = TradingEnvironment(test_data)
        test_trainer = RLTrainer(test_env, agent_type=agent_type)
        test_trainer.agent = trainer.agent  # Use trained agent

        eval_stats = test_trainer.evaluate(num_episodes=10)

        rl_results[agent_type] = eval_stats["avg_return"]

        logger.info(f"{agent_type.upper()} Test Results:")
        logger.info(f"  Return: {eval_stats['avg_return']:.2%}")
        logger.info(f"  Sharpe: {eval_stats['avg_sharpe']:.2f}")
        logger.info(f"  Win Rate: {eval_stats['avg_win_rate']:.1f}%")

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("FINAL COMPARISON")
    logger.info("=" * 60)
    logger.info(f"\nBuy & Hold:        {buy_hold_return:>8.2%}")
    logger.info(f"ML Predictor:      {ml_total_return:>8.2%}")

    for agent_type, return_val in rl_results.items():
        logger.info(f"{agent_type.upper():15s}    {return_val:>8.2%}")

    # Check if RL beats baseline
    best_rl_return = max(rl_results.values())
    beats_baseline = best_rl_return > max(buy_hold_return, ml_total_return)

    if beats_baseline:
        logger.info(
            f"\n✓ RL agents beat baseline by {(best_rl_return - max(buy_hold_return, ml_total_return)):.2%}"
        )
    else:
        logger.info(f"\n✗ RL agents underperformed baseline")

    return beats_baseline


def main():
    """Run all tests."""
    logger.info("\n" + "=" * 60)
    logger.info("RL TRADING SYSTEM - COMPREHENSIVE TEST SUITE")
    logger.info("=" * 60 + "\n")

    tests = [
        ("Environment", test_environment),
        ("DQN Agent", test_dqn_agent),
        ("PPO Agent", test_ppo_agent),
        ("Transformer Agent", test_transformer_agent),
        ("Agent Comparison", test_agent_comparison),
        ("Baseline Comparison", compare_with_baseline),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            logger.info(f"\nRunning: {test_name}")
            result = test_func()
            results[test_name] = "PASS" if result else "FAIL"
        except Exception as e:
            logger.error(f"Test {test_name} failed with error: {e}", exc_info=True)
            results[test_name] = "ERROR"

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60 + "\n")

    for test_name, result in results.items():
        status_symbol = "✓" if result == "PASS" else "✗"
        logger.info(f"{status_symbol} {test_name:30s} {result}")

    passed = sum(1 for r in results.values() if r == "PASS")
    total = len(results)

    logger.info(f"\nPassed: {passed}/{total}")

    if passed == total:
        logger.info("\n🎉 All tests passed! RL system is ready for production.")
    else:
        logger.info("\n⚠️  Some tests failed. Review logs above.")


if __name__ == "__main__":
    main()
