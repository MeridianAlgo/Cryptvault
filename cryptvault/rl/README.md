# Reinforcement Learning Trading System

State-of-the-art RL agents for cryptocurrency trading using novel deep learning techniques.

## Overview

The RL system implements three advanced agents that learn optimal trading strategies through interaction with a realistic market environment:

- **DQN Agent**: Deep Q-Network with Rainbow improvements
- **PPO Agent**: Proximal Policy Optimization with GAE
- **Transformer Agent**: Multi-head attention for sequential decision making

## Architecture

### Trading Environment

Realistic trading simulation with:
- Continuous action space (position sizing from -100% to +100%)
- Transaction costs (0.1%) and slippage (0.05%)
- Market impact modeling
- Risk-adjusted rewards (Sharpe ratio, drawdown penalty)
- Portfolio state tracking

### Neural Networks

#### DQN Network
- Dueling architecture (separate value and advantage streams)
- Noisy layers for exploration (no epsilon-greedy needed)
- Prioritized experience replay
- Double Q-learning
- N-step returns

#### PPO Networks
- Actor network with Gaussian policy
- Critic network for value estimation
- Layer normalization
- Residual connections

#### Transformer Network
- Multi-head self-attention (8 heads)
- Positional encoding
- 4 transformer blocks
- Shared actor-critic architecture

### Training Infrastructure

- Curriculum learning
- Early stopping
- Checkpointing
- Performance tracking
- Multi-agent comparison

## Usage

### Basic Training

```python
from cryptvault.rl import TradingEnvironment, RLTrainer
from cryptvault.data.fetchers import CryptoDataFetcher

# Fetch data
fetcher = CryptoDataFetcher()
data = fetcher.fetch_data("BTC", days=200)

# Create environment
env = TradingEnvironment(data, initial_balance=100000)

# Train PPO agent
trainer = RLTrainer(env, agent_type="ppo")
stats = trainer.train(num_episodes=1000)

print(f"Final Return: {stats['final_return']:.2%}")
print(f"Sharpe Ratio: {stats['final_sharpe']:.2f}")
```

### Compare Agents

```python
from cryptvault.rl import compare_agents

# Compare all agents
comparison_df = compare_agents(
    data,
    agent_types=["dqn", "ppo", "transformer"],
    num_episodes=500,
    num_eval_episodes=20
)

print(comparison_df)
```

### Train Ensemble

```python
from cryptvault.rl import train_ensemble

# Train ensemble of all agents
ensemble = train_ensemble(data, num_episodes=500)
print(f"Ensemble size: {ensemble['num_agents']}")
```

## Novel Techniques

### 1. Noisy Networks
- Parametric noise for exploration
- No epsilon-greedy needed
- Better exploration in continuous spaces

### 2. Prioritized Experience Replay
- Sample important transitions more frequently
- Importance sampling weights
- Faster learning

### 3. Multi-Head Attention
- Capture temporal dependencies
- Learn market patterns
- Attention visualization

### 4. Generalized Advantage Estimation (GAE)
- Bias-variance tradeoff
- Smoother value estimates
- Better policy gradients

### 5. Dueling Architecture
- Separate value and advantage
- Better Q-value estimates
- Faster convergence

## Performance Metrics

The system tracks:
- Total return (%)
- Sharpe ratio
- Sortino ratio
- Maximum drawdown (%)
- Win rate (%)
- Number of trades
- Average return per trade

## Hyperparameters

### DQN
- Learning rate: 1e-4
- Gamma: 0.99
- Tau (soft update): 0.005
- Buffer size: 100,000
- Batch size: 128
- N-step: 3

### PPO
- Learning rate: 3e-4
- Gamma: 0.99
- GAE lambda: 0.95
- Clip epsilon: 0.2
- Value coefficient: 0.5
- Entropy coefficient: 0.01

### Transformer
- D-model: 256
- Num heads: 8
- Num layers: 4
- Learning rate: 1e-4

## Testing

Run comprehensive tests:

```bash
python tests/rl/test_rl_system.py
```

Tests include:
- Environment functionality
- Agent training
- Multi-agent comparison
- Baseline comparison (ML predictor, buy & hold)

## Expected Performance

Target metrics (after 500-1000 episodes):
- Return: >20% (vs 2.22% MAPE baseline)
- Sharpe Ratio: >2.0
- Win Rate: >60%
- Max Drawdown: <15%

## Requirements

```
torch>=2.0.0
numpy>=1.24.0
pandas>=2.0.0
```

Optional:
```
matplotlib>=3.7.0  # For plotting
```

## Advanced Features

### Custom Reward Functions

```python
def custom_reward(portfolio_value, sharpe, win_rate, drawdown):
    return portfolio_value * 0.5 + sharpe * 0.3 + win_rate * 0.2 - drawdown * 2.0

env = TradingEnvironment(data, reward_fn=custom_reward)
```

### Save/Load Models

```python
# Save
trainer.save_agent("best_model.pt")

# Load
trainer.load_agent("best_model.pt")
```

### Visualization

```python
# Plot training progress
trainer.plot_training_progress(save_path="training_plot.png")
```

## Architecture Comparison

| Feature | DQN | PPO | Transformer |
|---------|-----|-----|-------------|
| Action Space | Discrete | Continuous | Continuous |
| Memory | Replay Buffer | On-Policy | On-Policy |
| Exploration | Noisy Nets | Gaussian | Gaussian |
| Complexity | Medium | Low | High |
| Training Speed | Fast | Medium | Slow |
| Sample Efficiency | High | Medium | Low |

## Best Practices

1. **Start with PPO**: Most stable and reliable
2. **Use Transformer for long sequences**: Better temporal modeling
3. **DQN for discrete actions**: Fast and sample efficient
4. **Train for 500+ episodes**: RL needs time to learn
5. **Monitor Sharpe ratio**: Better than raw returns
6. **Use early stopping**: Prevent overfitting
7. **Ensemble multiple agents**: Reduce variance

## Troubleshooting

### Low Returns
- Increase training episodes
- Adjust reward function
- Tune hyperparameters
- Check data quality

### High Variance
- Reduce learning rate
- Increase batch size
- Use ensemble
- Add regularization

### Slow Training
- Reduce network size
- Use GPU
- Decrease batch size
- Simplify environment

## Future Improvements

- [ ] Hierarchical RL (multi-timeframe)
- [ ] Meta-learning (adapt to new markets)
- [ ] Multi-asset portfolio optimization
- [ ] Risk-aware RL (CVaR, VaR)
- [ ] Offline RL (learn from historical data)
- [ ] Model-based RL (world models)

## References

- Rainbow DQN: Hessel et al., 2017
- PPO: Schulman et al., 2017
- Attention is All You Need: Vaswani et al., 2017
- Noisy Networks: Fortunato et al., 2017
- GAE: Schulman et al., 2015

## Contact

For questions or issues, contact: contact@meridianalgo.org
