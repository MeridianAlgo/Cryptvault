"""
RL Agents for Cryptocurrency Trading

Implements state-of-the-art RL algorithms:
- DQN with Rainbow improvements
- PPO with clipping and GAE
- Transformer-based agent
"""

import logging
from collections import deque
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.distributions import Normal

from cryptvault.rl.networks import (
    ActorNetwork,
    CriticNetwork,
    DQNNetwork,
    TransformerNetwork,
)

logger = logging.getLogger(__name__)


class ReplayBuffer:
    """Experience replay buffer with prioritization support."""

    def __init__(self, capacity: int = 100000, alpha: float = 0.6):
        self.capacity = capacity
        self.alpha = alpha
        self.buffer = deque(maxlen=capacity)
        self.priorities = deque(maxlen=capacity)
        self.position = 0

    def push(
        self,
        state: np.ndarray,
        action: float,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        priority: Optional[float] = None,
    ):
        if priority is None:
            priority = max(self.priorities) if self.priorities else 1.0

        self.buffer.append((state, action, reward, next_state, done))
        self.priorities.append(priority)

    def sample(self, batch_size: int, beta: float = 0.4) -> Tuple:
        if len(self.buffer) < batch_size:
            batch_size = len(self.buffer)

        # Prioritized sampling
        priorities = np.array(self.priorities)
        probs = priorities**self.alpha
        probs /= probs.sum()

        indices = np.random.choice(len(self.buffer), batch_size, p=probs, replace=False)

        # Importance sampling weights
        weights = (len(self.buffer) * probs[indices]) ** (-beta)
        weights /= weights.max()

        batch = [self.buffer[idx] for idx in indices]
        states, actions, rewards, next_states, dones = zip(*batch)

        return (
            np.array(states),
            np.array(actions),
            np.array(rewards),
            np.array(next_states),
            np.array(dones),
            indices,
            weights,
        )

    def update_priorities(self, indices: np.ndarray, priorities: np.ndarray):
        for idx, priority in zip(indices, priorities):
            self.priorities[idx] = priority

    def __len__(self):
        return len(self.buffer)


class DQNAgent:
    """
    Deep Q-Network agent with Rainbow improvements:
    - Dueling architecture
    - Noisy networks
    - Prioritized experience replay
    - Double Q-learning
    - Multi-step returns
    """

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden_dim: int = 512,
        lr: float = 1e-4,
        gamma: float = 0.99,
        tau: float = 0.005,
        buffer_size: int = 100000,
        batch_size: int = 128,
        n_step: int = 3,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.tau = tau
        self.batch_size = batch_size
        self.n_step = n_step
        self.device = device

        # Networks
        self.q_network = DQNNetwork(state_dim, action_dim, hidden_dim).to(device)
        self.target_network = DQNNetwork(state_dim, action_dim, hidden_dim).to(device)
        self.target_network.load_state_dict(self.q_network.state_dict())

        # Optimizer
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=lr)

        # Replay buffer
        self.replay_buffer = ReplayBuffer(buffer_size)

        # N-step buffer
        self.n_step_buffer = deque(maxlen=n_step)

        # Training stats
        self.training_step = 0
        self.beta = 0.4  # Importance sampling weight

        logger.info(f"DQN Agent initialized on {device}")

    def select_action(self, state: np.ndarray, training: bool = True) -> float:
        """Select action using noisy network (no epsilon-greedy needed)."""
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)

        with torch.no_grad():
            if training:
                self.q_network.reset_noise()
            q_values = self.q_network(state_tensor)

        # Discretize continuous action space
        action_idx = q_values.argmax(1).item()
        action = (action_idx / (self.action_dim - 1)) * 2 - 1  # Map to [-1, 1]

        return action

    def store_transition(
        self, state: np.ndarray, action: float, reward: float, next_state: np.ndarray, done: bool
    ):
        """Store transition in n-step buffer and replay buffer."""
        self.n_step_buffer.append((state, action, reward, next_state, done))

        if len(self.n_step_buffer) == self.n_step:
            # Calculate n-step return
            n_step_return = 0
            for i, (_, _, r, _, _) in enumerate(self.n_step_buffer):
                n_step_return += (self.gamma**i) * r

            # Get first state and last next_state
            first_state = self.n_step_buffer[0][0]
            first_action = self.n_step_buffer[0][1]
            last_next_state = self.n_step_buffer[-1][3]
            last_done = self.n_step_buffer[-1][4]

            self.replay_buffer.push(
                first_state, first_action, n_step_return, last_next_state, last_done
            )

    def train(self) -> Dict[str, float]:
        """Train the agent on a batch of experiences."""
        if len(self.replay_buffer) < self.batch_size:
            return {}

        # Anneal beta for importance sampling
        self.beta = min(1.0, self.beta + 0.001)

        # Sample batch
        states, actions, rewards, next_states, dones, indices, weights = self.replay_buffer.sample(
            self.batch_size, self.beta
        )

        states = torch.FloatTensor(states).to(self.device)
        actions = torch.FloatTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        weights = torch.FloatTensor(weights).to(self.device)

        # Current Q values
        current_q = self.q_network(states)
        action_indices = ((actions + 1) / 2 * (self.action_dim - 1)).long()
        current_q = current_q.gather(1, action_indices.unsqueeze(1)).squeeze(1)

        # Double Q-learning: use online network to select actions
        with torch.no_grad():
            next_q_online = self.q_network(next_states)
            next_actions = next_q_online.argmax(1)

            # Use target network to evaluate actions
            next_q_target = self.target_network(next_states)
            next_q = next_q_target.gather(1, next_actions.unsqueeze(1)).squeeze(1)

            # N-step target
            target_q = rewards + (self.gamma**self.n_step) * next_q * (1 - dones)

        # TD errors for priority update
        td_errors = torch.abs(current_q - target_q).detach().cpu().numpy()
        self.replay_buffer.update_priorities(indices, td_errors + 1e-6)

        # Weighted loss
        loss = (weights * F.smooth_l1_loss(current_q, target_q, reduction="none")).mean()

        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), 10.0)
        self.optimizer.step()

        # Soft update target network
        self._soft_update()

        self.training_step += 1

        return {
            "loss": loss.item(),
            "q_value": current_q.mean().item(),
            "td_error": td_errors.mean(),
        }

    def _soft_update(self):
        """Soft update target network."""
        for target_param, param in zip(
            self.target_network.parameters(), self.q_network.parameters()
        ):
            target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)

    def save(self, path: str):
        """Save agent."""
        torch.save(
            {
                "q_network": self.q_network.state_dict(),
                "target_network": self.target_network.state_dict(),
                "optimizer": self.optimizer.state_dict(),
                "training_step": self.training_step,
            },
            path,
        )

    def load(self, path: str):
        """Load agent."""
        checkpoint = torch.load(path, map_location=self.device)
        self.q_network.load_state_dict(checkpoint["q_network"])
        self.target_network.load_state_dict(checkpoint["target_network"])
        self.optimizer.load_state_dict(checkpoint["optimizer"])
        self.training_step = checkpoint["training_step"]


class PPOAgent:
    """
    Proximal Policy Optimization agent with:
    - Clipped surrogate objective
    - Generalized Advantage Estimation (GAE)
    - Value function clipping
    - Entropy bonus
    """

    def __init__(
        self,
        state_dim: int,
        action_dim: int = 1,
        hidden_dim: int = 512,
        lr: float = 3e-4,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        clip_epsilon: float = 0.2,
        value_coef: float = 0.5,
        entropy_coef: float = 0.01,
        max_grad_norm: float = 0.5,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_epsilon = clip_epsilon
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef
        self.max_grad_norm = max_grad_norm
        self.device = device

        # Networks
        self.actor = ActorNetwork(state_dim, action_dim, hidden_dim).to(device)
        self.critic = CriticNetwork(state_dim, hidden_dim).to(device)

        # Optimizer
        self.optimizer = optim.Adam(
            list(self.actor.parameters()) + list(self.critic.parameters()), lr=lr
        )

        # Storage
        self.states = []
        self.actions = []
        self.rewards = []
        self.values = []
        self.log_probs = []
        self.dones = []

        logger.info(f"PPO Agent initialized on {device}")

    def select_action(self, state: np.ndarray, training: bool = True) -> Tuple[float, float, float]:
        """Select action from policy."""
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)

        with torch.no_grad():
            mean, std = self.actor(state_tensor)
            value = self.critic(state_tensor)

        # Sample action from Gaussian policy
        dist = Normal(mean, std)

        if training:
            action = dist.sample()
        else:
            action = mean

        log_prob = dist.log_prob(action).sum(dim=-1)

        action = action.cpu().numpy()[0, 0]
        log_prob = log_prob.cpu().numpy()[0]
        value = value.cpu().numpy()[0, 0]

        return action, log_prob, value

    def store_transition(
        self,
        state: np.ndarray,
        action: float,
        reward: float,
        log_prob: float,
        value: float,
        done: bool,
    ):
        """Store transition."""
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.log_probs.append(log_prob)
        self.values.append(value)
        self.dones.append(done)

    def train(self, next_value: float = 0.0) -> Dict[str, float]:
        """Train using collected trajectories."""
        if len(self.states) == 0:
            return {}

        # Convert to tensors
        states = torch.FloatTensor(np.array(self.states)).to(self.device)
        actions = torch.FloatTensor(np.array(self.actions)).unsqueeze(1).to(self.device)
        old_log_probs = torch.FloatTensor(np.array(self.log_probs)).to(self.device)

        # Calculate advantages using GAE
        advantages, returns = self._calculate_gae(next_value)
        advantages = torch.FloatTensor(advantages).to(self.device)
        returns = torch.FloatTensor(returns).to(self.device)

        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        # PPO update
        total_loss = 0
        actor_loss_sum = 0
        critic_loss_sum = 0
        entropy_sum = 0

        # Multiple epochs
        for _ in range(10):
            # Forward pass
            mean, std = self.actor(states)
            values = self.critic(states).squeeze()

            # Policy distribution
            dist = Normal(mean, std)
            new_log_probs = dist.log_prob(actions).sum(dim=-1)
            entropy = dist.entropy().sum(dim=-1).mean()

            # Ratio for PPO
            ratio = torch.exp(new_log_probs - old_log_probs)

            # Clipped surrogate objective
            surr1 = ratio * advantages
            surr2 = torch.clamp(ratio, 1 - self.clip_epsilon, 1 + self.clip_epsilon) * advantages
            actor_loss = -torch.min(surr1, surr2).mean()

            # Value loss with clipping
            value_pred_clipped = torch.FloatTensor(self.values).to(self.device) + torch.clamp(
                values - torch.FloatTensor(self.values).to(self.device),
                -self.clip_epsilon,
                self.clip_epsilon,
            )
            value_loss1 = F.mse_loss(values, returns)
            value_loss2 = F.mse_loss(value_pred_clipped, returns)
            critic_loss = torch.max(value_loss1, value_loss2)

            # Total loss
            loss = actor_loss + self.value_coef * critic_loss - self.entropy_coef * entropy

            # Optimize
            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(
                list(self.actor.parameters()) + list(self.critic.parameters()), self.max_grad_norm
            )
            self.optimizer.step()

            total_loss += loss.item()
            actor_loss_sum += actor_loss.item()
            critic_loss_sum += critic_loss.item()
            entropy_sum += entropy.item()

        # Clear storage
        self.states.clear()
        self.actions.clear()
        self.rewards.clear()
        self.log_probs.clear()
        self.values.clear()
        self.dones.clear()

        return {
            "loss": total_loss / 10,
            "actor_loss": actor_loss_sum / 10,
            "critic_loss": critic_loss_sum / 10,
            "entropy": entropy_sum / 10,
        }

    def _calculate_gae(self, next_value: float) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate Generalized Advantage Estimation."""
        values = self.values + [next_value]
        advantages = []
        gae = 0

        for t in reversed(range(len(self.rewards))):
            delta = self.rewards[t] + self.gamma * values[t + 1] * (1 - self.dones[t]) - values[t]
            gae = delta + self.gamma * self.gae_lambda * (1 - self.dones[t]) * gae
            advantages.insert(0, gae)

        returns = [adv + val for adv, val in zip(advantages, self.values)]

        return np.array(advantages), np.array(returns)

    def save(self, path: str):
        """Save agent."""
        torch.save(
            {
                "actor": self.actor.state_dict(),
                "critic": self.critic.state_dict(),
                "optimizer": self.optimizer.state_dict(),
            },
            path,
        )

    def load(self, path: str):
        """Load agent."""
        checkpoint = torch.load(path, map_location=self.device)
        self.actor.load_state_dict(checkpoint["actor"])
        self.critic.load_state_dict(checkpoint["critic"])
        self.optimizer.load_state_dict(checkpoint["optimizer"])


class TransformerAgent:
    """
    Transformer-based agent with multi-head attention.

    Processes sequential market data with temporal dependencies.
    """

    def __init__(
        self,
        state_dim: int,
        action_dim: int = 1,
        d_model: int = 256,
        num_heads: int = 8,
        num_layers: int = 4,
        lr: float = 1e-4,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        clip_epsilon: float = 0.2,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_epsilon = clip_epsilon
        self.device = device

        # Transformer network
        self.network = TransformerNetwork(state_dim, action_dim, d_model, num_heads, num_layers).to(
            device
        )

        # Optimizer
        self.optimizer = optim.Adam(self.network.parameters(), lr=lr)

        # Storage
        self.states = []
        self.actions = []
        self.rewards = []
        self.values = []
        self.log_probs = []
        self.dones = []

        logger.info(f"Transformer Agent initialized on {device}")

    def select_action(self, state: np.ndarray, training: bool = True) -> Tuple[float, float, float]:
        """Select action using transformer."""
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)

        with torch.no_grad():
            mean, std, value = self.network(state_tensor)

        dist = Normal(mean, std)

        if training:
            action = dist.sample()
        else:
            action = mean

        log_prob = dist.log_prob(action).sum(dim=-1)

        action = action.cpu().numpy()[0, 0]
        log_prob = log_prob.cpu().numpy()[0]
        value = value.cpu().numpy()[0, 0]

        return action, log_prob, value

    def store_transition(
        self,
        state: np.ndarray,
        action: float,
        reward: float,
        log_prob: float,
        value: float,
        done: bool,
    ):
        """Store transition."""
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.log_probs.append(log_prob)
        self.values.append(value)
        self.dones.append(done)

    def train(self, next_value: float = 0.0) -> Dict[str, float]:
        """Train using PPO with transformer."""
        if len(self.states) == 0:
            return {}

        states = torch.FloatTensor(np.array(self.states)).to(self.device)
        actions = torch.FloatTensor(np.array(self.actions)).unsqueeze(1).to(self.device)
        old_log_probs = torch.FloatTensor(np.array(self.log_probs)).to(self.device)

        # Calculate advantages
        advantages, returns = self._calculate_gae(next_value)
        advantages = torch.FloatTensor(advantages).to(self.device)
        returns = torch.FloatTensor(returns).to(self.device)
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        total_loss = 0

        for _ in range(10):
            mean, std, values = self.network(states)
            values = values.squeeze()

            dist = Normal(mean, std)
            new_log_probs = dist.log_prob(actions).sum(dim=-1)
            entropy = dist.entropy().sum(dim=-1).mean()

            ratio = torch.exp(new_log_probs - old_log_probs)
            surr1 = ratio * advantages
            surr2 = torch.clamp(ratio, 1 - self.clip_epsilon, 1 + self.clip_epsilon) * advantages
            actor_loss = -torch.min(surr1, surr2).mean()

            critic_loss = F.mse_loss(values, returns)

            loss = actor_loss + 0.5 * critic_loss - 0.01 * entropy

            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.network.parameters(), 0.5)
            self.optimizer.step()

            total_loss += loss.item()

        self.states.clear()
        self.actions.clear()
        self.rewards.clear()
        self.log_probs.clear()
        self.values.clear()
        self.dones.clear()

        return {"loss": total_loss / 10}

    def _calculate_gae(self, next_value: float) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate GAE."""
        values = self.values + [next_value]
        advantages = []
        gae = 0

        for t in reversed(range(len(self.rewards))):
            delta = self.rewards[t] + self.gamma * values[t + 1] * (1 - self.dones[t]) - values[t]
            gae = delta + self.gamma * self.gae_lambda * (1 - self.dones[t]) * gae
            advantages.insert(0, gae)

        returns = [adv + val for adv, val in zip(advantages, self.values)]

        return np.array(advantages), np.array(returns)

    def save(self, path: str):
        """Save agent."""
        torch.save(
            {"network": self.network.state_dict(), "optimizer": self.optimizer.state_dict()}, path
        )

    def load(self, path: str):
        """Load agent."""
        checkpoint = torch.load(path, map_location=self.device)
        self.network.load_state_dict(checkpoint["network"])
        self.optimizer.load_state_dict(checkpoint["optimizer"])
