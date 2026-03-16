"""
RL Training Infrastructure

Handles training, evaluation, and comparison of RL agents.
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from cryptvault.rl.agents import DQNAgent, PPOAgent, TransformerAgent
from cryptvault.rl.environment import TradingEnvironment

logger = logging.getLogger(__name__)


class RLTrainer:
    """
    Training infrastructure for RL agents.

    Features:
    - Multi-agent training and comparison
    - Curriculum learning
    - Early stopping
    - Checkpointing
    - Performance tracking
    """

    def __init__(
        self,
        env: TradingEnvironment,
        agent_type: str = "ppo",
        save_dir: str = "models/rl",
        **agent_kwargs,
    ):
        self.env = env
        self.agent_type = agent_type
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

        # Initialize agent
        state_dim = env.observation_size
        action_dim = 21  # Discretize [-1, 1] into 21 actions for DQN

        if agent_type == "dqn":
            self.agent = DQNAgent(state_dim, action_dim, **agent_kwargs)
        elif agent_type == "ppo":
            self.agent = PPOAgent(state_dim, **agent_kwargs)
        elif agent_type == "transformer":
            self.agent = TransformerAgent(state_dim, **agent_kwargs)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

        # Training stats
        self.episode_rewards = []
        self.episode_returns = []
        self.episode_sharpes = []
        self.training_losses = []

        logger.info(f"Initialized {agent_type.upper()} trainer")

    def train(
        self,
        num_episodes: int = 1000,
        eval_interval: int = 10,
        save_interval: int = 50,
        early_stop_patience: int = 50,
        target_return: float = 0.20,  # 20% return target
    ) -> Dict:
        """
        Train the agent.

        Args:
            num_episodes: Number of training episodes
            eval_interval: Episodes between evaluations
            save_interval: Episodes between checkpoints
            early_stop_patience: Episodes without improvement before stopping
            target_return: Target return for early stopping

        Returns:
            Training statistics
        """
        best_return = -np.inf
        episodes_without_improvement = 0

        logger.info(f"Starting training for {num_episodes} episodes")
        start_time = time.time()

        for episode in range(num_episodes):
            episode_start = time.time()

            # Run episode
            stats = self._run_episode(training=True)

            # Track stats
            self.episode_rewards.append(stats["total_reward"])
            self.episode_returns.append(stats["total_return"])
            self.episode_sharpes.append(stats["sharpe_ratio"])

            if "loss" in stats:
                self.training_losses.append(stats["loss"])

            # Logging
            if (episode + 1) % 10 == 0:
                avg_return = np.mean(self.episode_returns[-10:])
                avg_sharpe = np.mean(self.episode_sharpes[-10:])
                episode_time = time.time() - episode_start

                logger.info(
                    f"Episode {episode + 1}/{num_episodes} | "
                    f"Return: {stats['total_return']:.2%} | "
                    f"Sharpe: {stats['sharpe_ratio']:.2f} | "
                    f"Avg Return (10): {avg_return:.2%} | "
                    f"Avg Sharpe (10): {avg_sharpe:.2f} | "
                    f"Time: {episode_time:.1f}s"
                )

            # Evaluation
            if (episode + 1) % eval_interval == 0:
                eval_stats = self.evaluate(num_episodes=5)
                eval_return = eval_stats["avg_return"]

                logger.info(
                    f"Evaluation | "
                    f"Return: {eval_return:.2%} | "
                    f"Sharpe: {eval_stats['avg_sharpe']:.2f} | "
                    f"Win Rate: {eval_stats['avg_win_rate']:.1f}%"
                )

                # Check for improvement
                if eval_return > best_return:
                    best_return = eval_return
                    episodes_without_improvement = 0

                    # Save best model
                    self.save_agent("best_model.pt")
                    logger.info(f"New best model saved with return: {best_return:.2%}")
                else:
                    episodes_without_improvement += eval_interval

                # Early stopping
                if episodes_without_improvement >= early_stop_patience:
                    logger.info(f"Early stopping after {episode + 1} episodes")
                    break

                # Target reached
                if eval_return >= target_return:
                    logger.info(f"Target return {target_return:.2%} reached!")
                    break

            # Save checkpoint
            if (episode + 1) % save_interval == 0:
                self.save_agent(f"checkpoint_ep{episode + 1}.pt")

        training_time = time.time() - start_time

        # Final evaluation
        final_stats = self.evaluate(num_episodes=10)

        logger.info(
            f"Training completed in {training_time:.1f}s | "
            f"Best Return: {best_return:.2%} | "
            f"Final Return: {final_stats['avg_return']:.2%}"
        )

        return {
            "best_return": best_return,
            "final_return": final_stats["avg_return"],
            "final_sharpe": final_stats["avg_sharpe"],
            "training_time": training_time,
            "episodes_trained": episode + 1,
            "episode_rewards": self.episode_rewards,
            "episode_returns": self.episode_returns,
            "episode_sharpes": self.episode_sharpes,
        }

    def _run_episode(self, training: bool = True) -> Dict:
        """Run a single episode."""
        state = self.env.reset()
        done = False
        total_reward = 0
        steps = 0

        while not done:
            # Select action
            if self.agent_type == "dqn":
                action = self.agent.select_action(state, training)
                log_prob = 0
                value = 0
            else:
                action, log_prob, value = self.agent.select_action(state, training)

            # Step environment
            next_state, reward, done, info = self.env.step(action)

            # Store transition
            if training:
                if self.agent_type == "dqn":
                    self.agent.store_transition(state, action, reward, next_state, done)
                else:
                    self.agent.store_transition(state, action, reward, log_prob, value, done)

            state = next_state
            total_reward += reward
            steps += 1

        # Train agent
        train_stats = {}
        if training:
            if self.agent_type == "dqn":
                # Train DQN multiple times per episode
                for _ in range(steps // 4):
                    train_stats = self.agent.train()
            else:
                # Train PPO/Transformer at end of episode
                next_value = 0.0
                train_stats = self.agent.train(next_value)

        # Get environment metrics
        env_metrics = self.env.get_metrics()

        return {
            "total_reward": total_reward,
            "total_return": env_metrics.get("total_return", 0) / 100,
            "sharpe_ratio": env_metrics.get("sharpe_ratio", 0),
            "win_rate": env_metrics.get("win_rate", 0),
            "max_drawdown": env_metrics.get("max_drawdown", 0),
            "steps": steps,
            **train_stats,
        }

    def evaluate(self, num_episodes: int = 10) -> Dict:
        """Evaluate agent performance."""
        returns = []
        sharpes = []
        win_rates = []
        max_drawdowns = []

        for _ in range(num_episodes):
            stats = self._run_episode(training=False)
            returns.append(stats["total_return"])
            sharpes.append(stats["sharpe_ratio"])
            win_rates.append(stats["win_rate"])
            max_drawdowns.append(stats["max_drawdown"])

        return {
            "avg_return": np.mean(returns),
            "std_return": np.std(returns),
            "avg_sharpe": np.mean(sharpes),
            "avg_win_rate": np.mean(win_rates),
            "avg_max_drawdown": np.mean(max_drawdowns),
            "min_return": np.min(returns),
            "max_return": np.max(returns),
        }

    def save_agent(self, filename: str):
        """Save agent to file."""
        path = self.save_dir / filename
        self.agent.save(str(path))
        logger.info(f"Agent saved to {path}")

    def load_agent(self, filename: str):
        """Load agent from file."""
        path = self.save_dir / filename
        self.agent.load(str(path))
        logger.info(f"Agent loaded from {path}")

    def plot_training_progress(self, save_path: Optional[str] = None):
        """Plot training progress."""
        try:
            import matplotlib.pyplot as plt

            fig, axes = plt.subplots(2, 2, figsize=(15, 10))

            # Returns
            axes[0, 0].plot(self.episode_returns)
            axes[0, 0].set_title("Episode Returns")
            axes[0, 0].set_xlabel("Episode")
            axes[0, 0].set_ylabel("Return")
            axes[0, 0].grid(True)

            # Sharpe ratios
            axes[0, 1].plot(self.episode_sharpes)
            axes[0, 1].set_title("Episode Sharpe Ratios")
            axes[0, 1].set_xlabel("Episode")
            axes[0, 1].set_ylabel("Sharpe Ratio")
            axes[0, 1].grid(True)

            # Rewards
            axes[1, 0].plot(self.episode_rewards)
            axes[1, 0].set_title("Episode Rewards")
            axes[1, 0].set_xlabel("Episode")
            axes[1, 0].set_ylabel("Reward")
            axes[1, 0].grid(True)

            # Training loss
            if self.training_losses:
                axes[1, 1].plot(self.training_losses)
                axes[1, 1].set_title("Training Loss")
                axes[1, 1].set_xlabel("Training Step")
                axes[1, 1].set_ylabel("Loss")
                axes[1, 1].grid(True)

            plt.tight_layout()

            if save_path:
                plt.savefig(save_path)
                logger.info(f"Training plot saved to {save_path}")
            else:
                plt.show()

            plt.close()

        except ImportError:
            logger.warning("Matplotlib not available for plotting")


def compare_agents(
    data: pd.DataFrame,
    agent_types: List[str] = ["dqn", "ppo", "transformer"],
    num_episodes: int = 500,
    num_eval_episodes: int = 20,
) -> pd.DataFrame:
    """
    Compare multiple RL agents.

    Args:
        data: Market data
        agent_types: List of agent types to compare
        num_episodes: Training episodes per agent
        num_eval_episodes: Evaluation episodes per agent

    Returns:
        Comparison DataFrame
    """
    results = []

    for agent_type in agent_types:
        logger.info(f"\n{'='*60}")
        logger.info(f"Training {agent_type.upper()} agent")
        logger.info(f"{'='*60}\n")

        # Create environment
        env = TradingEnvironment(data)

        # Create trainer
        trainer = RLTrainer(env, agent_type=agent_type)

        # Train
        train_stats = trainer.train(num_episodes=num_episodes)

        # Evaluate
        eval_stats = trainer.evaluate(num_episodes=num_eval_episodes)

        # Store results
        results.append(
            {
                "Agent": agent_type.upper(),
                "Final Return": eval_stats["avg_return"],
                "Std Return": eval_stats["std_return"],
                "Sharpe Ratio": eval_stats["avg_sharpe"],
                "Win Rate": eval_stats["avg_win_rate"],
                "Max Drawdown": eval_stats["avg_max_drawdown"],
                "Training Time": train_stats["training_time"],
                "Episodes": train_stats["episodes_trained"],
            }
        )

        logger.info(f"\n{agent_type.upper()} Results:")
        logger.info(f"Return: {eval_stats['avg_return']:.2%} ± {eval_stats['std_return']:.2%}")
        logger.info(f"Sharpe: {eval_stats['avg_sharpe']:.2f}")
        logger.info(f"Win Rate: {eval_stats['avg_win_rate']:.1f}%")

    # Create comparison DataFrame
    df = pd.DataFrame(results)
    df = df.sort_values("Final Return", ascending=False)

    logger.info(f"\n{'='*60}")
    logger.info("AGENT COMPARISON")
    logger.info(f"{'='*60}\n")
    logger.info(df.to_string(index=False))

    return df


def train_ensemble(
    data: pd.DataFrame, num_episodes: int = 500, save_dir: str = "models/rl/ensemble"
) -> Dict:
    """
    Train an ensemble of all agent types.

    Args:
        data: Market data
        num_episodes: Training episodes per agent
        save_dir: Directory to save models

    Returns:
        Ensemble statistics
    """
    agent_types = ["dqn", "ppo", "transformer"]
    agents = []

    for agent_type in agent_types:
        logger.info(f"Training {agent_type.upper()} for ensemble")

        env = TradingEnvironment(data)
        trainer = RLTrainer(env, agent_type=agent_type, save_dir=save_dir)
        trainer.train(num_episodes=num_episodes)

        agents.append(trainer.agent)

    logger.info("Ensemble training completed")

    return {"agents": agents, "agent_types": agent_types, "num_agents": len(agents)}
