"""
Neural Network Architectures for RL Agents

Implements state-of-the-art architectures:
- Multi-head attention transformers
- Residual connections
- Layer normalization
- Noisy networks for exploration
"""

import logging
from typing import Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger(__name__)


class NoisyLinear(nn.Module):
    """Noisy linear layer for exploration (NoisyNet)."""

    def __init__(self, in_features: int, out_features: int, std_init: float = 0.5):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.std_init = std_init

        self.weight_mu = nn.Parameter(torch.empty(out_features, in_features))
        self.weight_sigma = nn.Parameter(torch.empty(out_features, in_features))
        self.register_buffer("weight_epsilon", torch.empty(out_features, in_features))

        self.bias_mu = nn.Parameter(torch.empty(out_features))
        self.bias_sigma = nn.Parameter(torch.empty(out_features))
        self.register_buffer("bias_epsilon", torch.empty(out_features))

        self.reset_parameters()
        self.reset_noise()

    def reset_parameters(self):
        mu_range = 1 / np.sqrt(self.in_features)
        self.weight_mu.data.uniform_(-mu_range, mu_range)
        self.weight_sigma.data.fill_(self.std_init / np.sqrt(self.in_features))
        self.bias_mu.data.uniform_(-mu_range, mu_range)
        self.bias_sigma.data.fill_(self.std_init / np.sqrt(self.out_features))

    def reset_noise(self):
        epsilon_in = self._scale_noise(self.in_features)
        epsilon_out = self._scale_noise(self.out_features)
        self.weight_epsilon.copy_(epsilon_out.ger(epsilon_in))
        self.bias_epsilon.copy_(epsilon_out)

    def _scale_noise(self, size: int) -> torch.Tensor:
        x = torch.randn(size)
        return x.sign().mul_(x.abs().sqrt_())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.training:
            weight = self.weight_mu + self.weight_sigma * self.weight_epsilon
            bias = self.bias_mu + self.bias_sigma * self.bias_epsilon
        else:
            weight = self.weight_mu
            bias = self.bias_mu

        return F.linear(x, weight, bias)


class MultiHeadAttention(nn.Module):
    """Multi-head self-attention mechanism."""

    def __init__(self, d_model: int, num_heads: int = 8, dropout: float = 0.1):
        super().__init__()
        assert d_model % num_heads == 0

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        self.q_linear = nn.Linear(d_model, d_model)
        self.k_linear = nn.Linear(d_model, d_model)
        self.v_linear = nn.Linear(d_model, d_model)
        self.out_linear = nn.Linear(d_model, d_model)

        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(d_model)

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        batch_size = x.size(0)

        # Linear projections
        q = self.q_linear(x).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        k = self.k_linear(x).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        v = self.v_linear(x).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)

        # Attention scores
        scores = torch.matmul(q, k.transpose(-2, -1)) / np.sqrt(self.d_k)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        attention = F.softmax(scores, dim=-1)
        attention = self.dropout(attention)

        # Apply attention to values
        context = torch.matmul(attention, v)
        context = context.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)

        # Output projection with residual connection
        output = self.out_linear(context)
        output = self.layer_norm(x + self.dropout(output))

        return output


class TransformerBlock(nn.Module):
    """Transformer block with attention and feed-forward."""

    def __init__(self, d_model: int, num_heads: int = 8, d_ff: int = 2048, dropout: float = 0.1):
        super().__init__()

        self.attention = MultiHeadAttention(d_model, num_heads, dropout)

        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout),
        )

        self.layer_norm = nn.LayerNorm(d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Attention with residual
        x = self.attention(x)

        # Feed-forward with residual
        ff_output = self.feed_forward(x)
        x = self.layer_norm(x + ff_output)

        return x


class DQNNetwork(nn.Module):
    """Deep Q-Network with dueling architecture and noisy layers."""

    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 512):
        super().__init__()

        # Shared feature extraction
        self.feature_layer = nn.Sequential(
            NoisyLinear(state_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            NoisyLinear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
        )

        # Dueling architecture
        # Value stream
        self.value_stream = nn.Sequential(
            NoisyLinear(hidden_dim, hidden_dim // 2), nn.ReLU(), NoisyLinear(hidden_dim // 2, 1)
        )

        # Advantage stream
        self.advantage_stream = nn.Sequential(
            NoisyLinear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            NoisyLinear(hidden_dim // 2, action_dim),
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        features = self.feature_layer(state)

        value = self.value_stream(features)
        advantage = self.advantage_stream(features)

        # Combine value and advantage (dueling architecture)
        q_values = value + (advantage - advantage.mean(dim=1, keepdim=True))

        return q_values

    def reset_noise(self):
        """Reset noise for all noisy layers."""
        for module in self.modules():
            if isinstance(module, NoisyLinear):
                module.reset_noise()


class ActorNetwork(nn.Module):
    """Actor network for PPO (continuous actions)."""

    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 512):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.Tanh(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.Tanh(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, action_dim),
        )

        # Log std for Gaussian policy
        self.log_std = nn.Parameter(torch.zeros(action_dim))

    def forward(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        out = self.network(state)
        # Guard against NaN from exploding gradients
        out = torch.nan_to_num(out, nan=0.0, posinf=1.0, neginf=-1.0)
        mean = torch.tanh(out)  # Bounded to [-1, 1]
        # nan_to_num BEFORE clamp — clamp(NaN) = NaN in PyTorch
        log_std_clean = torch.nan_to_num(self.log_std, nan=0.0, posinf=2.0, neginf=-4.0)
        log_std_clamped = torch.clamp(log_std_clean, -4.0, 2.0)
        std = torch.exp(log_std_clamped).expand_as(mean)
        return mean, std


class CriticNetwork(nn.Module):
    """Critic network for PPO (value function)."""

    def __init__(self, state_dim: int, hidden_dim: int = 512):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.Tanh(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.Tanh(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, 1),
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        return self.network(state)


class TransformerNetwork(nn.Module):
    """Transformer-based network for sequential decision making."""

    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        d_model: int = 256,
        num_heads: int = 8,
        num_layers: int = 4,
        dropout: float = 0.1,
    ):
        super().__init__()

        self.state_dim = state_dim
        self.d_model = d_model

        # Input embedding
        self.input_embedding = nn.Sequential(
            nn.Linear(state_dim, d_model), nn.LayerNorm(d_model), nn.ReLU(), nn.Dropout(dropout)
        )

        # Positional encoding
        self.positional_encoding = nn.Parameter(torch.randn(1, 100, d_model))

        # Transformer blocks
        self.transformer_blocks = nn.ModuleList(
            [TransformerBlock(d_model, num_heads, d_model * 4, dropout) for _ in range(num_layers)]
        )

        # Output heads
        self.actor_head = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Linear(d_model // 2, action_dim),
            nn.Tanh(),
        )

        self.critic_head = nn.Sequential(
            nn.Linear(d_model, d_model // 2), nn.ReLU(), nn.Linear(d_model // 2, 1)
        )

        # Log std for policy
        self.log_std = nn.Parameter(torch.zeros(action_dim))

    def forward(
        self, state: torch.Tensor, sequence_length: int = 1
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        batch_size = state.size(0)

        # Embed input
        x = self.input_embedding(state)

        # Add positional encoding
        if sequence_length > 1:
            x = x.view(batch_size, sequence_length, -1)
            x = x + self.positional_encoding[:, :sequence_length, :]
        else:
            x = x.unsqueeze(1)
            x = x + self.positional_encoding[:, :1, :]

        # Apply transformer blocks
        for block in self.transformer_blocks:
            x = block(x)

        # Take last sequence element
        x = x[:, -1, :]

        # Actor output (mean)
        action_mean = torch.nan_to_num(self.actor_head(x), nan=0.0)
        # nan_to_num BEFORE clamp — clamp(NaN) = NaN in PyTorch
        log_std_clean = torch.nan_to_num(self.log_std, nan=0.0, posinf=2.0, neginf=-4.0)
        log_std_clamped = torch.clamp(log_std_clean, -4.0, 2.0)
        action_std = torch.exp(log_std_clamped).expand_as(action_mean)

        # Critic output (value)
        value = torch.nan_to_num(self.critic_head(x), nan=0.0)

        return action_mean, action_std, value


class EnsembleNetwork(nn.Module):
    """Ensemble of networks for uncertainty estimation."""

    def __init__(
        self, state_dim: int, action_dim: int, num_networks: int = 5, hidden_dim: int = 512
    ):
        super().__init__()

        self.networks = nn.ModuleList(
            [
                nn.Sequential(
                    nn.Linear(state_dim, hidden_dim),
                    nn.LayerNorm(hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(hidden_dim, hidden_dim),
                    nn.LayerNorm(hidden_dim),
                    nn.ReLU(),
                    nn.Dropout(0.2),
                    nn.Linear(hidden_dim, action_dim),
                    nn.Tanh(),
                )
                for _ in range(num_networks)
            ]
        )

    def forward(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        outputs = [net(state) for net in self.networks]
        outputs = torch.stack(outputs, dim=0)

        mean = torch.nan_to_num(outputs.mean(dim=0), nan=0.0)
        # std can be NaN when only 1 network; clamp to ensure valid distribution
        std = torch.nan_to_num(outputs.std(dim=0), nan=0.1).clamp(min=1e-6)

        return mean, std
