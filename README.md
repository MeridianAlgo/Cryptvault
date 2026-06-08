<div align="center">

# CryptVault

### AI-powered cryptocurrency & stock analysis — desktop, CLI, and Python API.

[![Python](https://img.shields.io/badge/python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-6.2.0-2ea44f)](https://github.com/MeridianAlgo/Cryptvault/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Tests](https://github.com/MeridianAlgo/Cryptvault/actions/workflows/tests.yml/badge.svg)](https://github.com/MeridianAlgo/Cryptvault/actions/workflows/tests.yml)
[![Lint](https://github.com/MeridianAlgo/Cryptvault/actions/workflows/lint.yml/badge.svg)](https://github.com/MeridianAlgo/Cryptvault/actions/workflows/lint.yml)
[![Coverage](https://codecov.io/gh/MeridianAlgo/Cryptvault/branch/main/graph/badge.svg)](https://codecov.io/gh/MeridianAlgo/Cryptvault)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**[Quick Start](#-quick-start)** · **[Desktop App](#-desktop-app)** · **[CLI](#-cli)** · **[Patterns](#-pattern-library)** · **[ML](#-machine-learning)** · **[Docs](#-documentation)**

</div>

---

> [!WARNING]
> **Educational and research use only.** CryptVault is **not financial advice** and must **not** be used for live trading decisions. Past performance does not guarantee future results. You are solely responsible for any investment outcomes.

---

## 🧭 What is CryptVault?

CryptVault is a research-grade analysis platform for crypto and equities that combines:

- 🖥️  A **native desktop terminal** with candlestick charts, drawn pattern overlays, and ML predictions side-by-side.
- 🧠  A **production ML ensemble** (67+ engineered features, validation-weighted stacking) achieving 1.6–2.4% MAPE on major pairs.
- 🔍  **50+ classical patterns** across 7 categories — all drawn as actual geometric shapes, not just markers.
- 🤖  **Reinforcement-learning agents** (DQN, PPO, Transformer) for trading research.
- 🛠️  A **clean Python API**, CLI, and portfolio tools.

---

## ✨ Highlights (v6.2.0)

| Area | What's new |
|---|---|
| **Reliability** | Fixed broken `DataCache` / `portfolio` imports and a phantom `--live` module — caching, portfolio, and live analysis all work again. |
| **Out-of-the-box** | Sensible CLI defaults (`days=100`) so `python cryptvault_cli.py BTC` runs with no extra args. |
| **Versioning** | Single source of truth for the version — no more drift between demo, constants, and package. |
| **Cleanup** | Removed dead shims/stubs and stray duplicate docs; consolidated docs under `docs/`. |
| **Tests** | yfinance MultiIndex handling fixed; full suite green (18/18), `cryptvault/` stays ruff-clean. |

Full history: [`docs/CHANGELOG.md`](docs/CHANGELOG.md).

---

## 🚀 Quick Start

```bash
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault
pip install -r requirements.txt
```

Verify:

```bash
python -c "import cryptvault; print(cryptvault.__version__)"
```

Run the desktop terminal:

```bash
python launch_desktop.py
```

---

## 🖥️ Desktop App

A dark-themed trading terminal with three synchronized surfaces — chart, patterns, and ML.

```
┌────────────────────────────────────────────────────────────────┐
│ CryptVault 6.1   [BTC-USD]  [Analyze]   1D 5D 1M 3M 6M 1Y YTD  │
├────────────┬──────────────────────────────────┬────────────────┤
│            │                                  │  ML PREDICTION │
│   Chart    │    📈 Candlestick + Patterns     │  ────────────  │
│            │    📊 Bollinger Bands            │                │
│  Analysis  │    📉 Volume  · RSI              │  DETECTED      │
│            │                                  │  PATTERNS      │
│  History   │    (pattern shapes drawn live)   │  (scrollable)  │
├────────────┴──────────────────────────────────┴────────────────┤
│ Status: connected · last fetch 2s · 120 candles · 12 patterns  │
└────────────────────────────────────────────────────────────────┘
```

### Patterns are drawn, not just labeled

| Pattern | Rendered as |
|---|---|
| Double Top / Bottom | Peak-to-peak line + dashed neckline |
| Head & Shoulders | LS → Head → RS connectors + neckline |
| Triple Top / Bottom | Three-pivot polyline |
| Triangles (Sym/Asc/Desc) | Fitted upper + lower trendlines |
| Rising / Falling Wedge | Converging trendlines |
| Any pattern with target | Dotted horizontal target line |
| Candlestick | `▲` bullish / `▼` bearish marker |

See [`docs/DESKTOP_APP.md`](docs/DESKTOP_APP.md).

---

## ⚡ CLI

```bash
# Analyze Bitcoin with chart
python cryptvault_cli.py BTC 60 1d

# Save chart to file
python cryptvault_cli.py ETH 120 1d --save-chart eth.png

# Text-only analysis
python cryptvault_cli.py SOL 90 1d --no-chart

# Portfolio
python cryptvault_cli.py --portfolio BTC:0.5 ETH:10 SOL:50

# Compare assets
python cryptvault_cli.py --compare BTC ETH SOL

# Interactive REPL
python cryptvault_cli.py --interactive
```

### Command reference

```
python cryptvault_cli.py SYMBOL [DAYS] [INTERVAL] [OPTIONS]
```

| Option | Description |
|---|---|
| `--no-chart` | Text-only output |
| `--save-chart FILE` | Save chart as PNG |
| `--verbose` | Detailed diagnostics |
| `--desktop` | Launch desktop app |
| `--portfolio A:X B:Y ...` | Portfolio analysis |
| `--compare S1 S2 ...` | Side-by-side comparison |
| `--interactive` | REPL mode |
| `--status` | API & data source health |
| `--demo` | Run demonstration dataset |
| `--version` / `--help` | Info |

---

## 🔍 Pattern Library

**50+ classical patterns across 7 categories.** Full reference: [`docs/PATTERNS.md`](docs/PATTERNS.md).

<details>
<summary><b>Reversal (8)</b> — Head & Shoulders, Inverse H&S, Double/Triple Top & Bottom, Rising/Falling Wedge</summary>

Detected via local pivot extraction, neckline fitting, and symmetry scoring. Drawn with the actual peak/trough connectors plus a dashed neckline and projected target.
</details>

<details>
<summary><b>Continuation</b> — Triangles (Sym/Asc/Desc), Bull/Bear Flag, Pennants, Cup & Handle</summary>

Trendline regression on swing highs and swing lows; convergence and slope tests determine the sub-type. Targets projected from breakout range.
</details>

<details>
<summary><b>Candlestick</b> — Doji (3 variants), Hammer, Hanging Man, Inverted Hammer, Shooting Star, Engulfing, Harami, Piercing, Dark Cloud, Morning/Evening Star, Three Soldiers/Crows</summary>

Body/wick ratio analysis with trend-context filters. Rendered as `▲` or `▼` above/below the candle.
</details>

<details>
<summary><b>Harmonic</b> — Gartley, Butterfly, Bat, Crab, Shark, Cypher</summary>

Fibonacci ratio validation between swing points (XABCD structure) with per-pattern tolerance bands.
</details>

<details>
<summary><b>Divergence</b> — RSI & MACD Bullish/Bearish</summary>

Peak/trough alignment between price and oscillator detects hidden and regular divergence.
</details>

---

## 🧠 Machine Learning

**Ensemble** — each base learner weighted by rolling out-of-fold validation:

| Model | Role |
|---|---|
| Random Forest | Non-linear baseline, robust to noise |
| Gradient Boosting | Sequential residual refinement |
| SVR | Small-sample non-linear regression |
| Ridge / Lasso / ElasticNet | Stable linear anchors |
| ARIMA | Explicit time-series baseline |
| XGBoost / LightGBM *(optional)* | High-capacity boosting |

Stacked via a meta-learner on validation residuals.

### Measured performance (real market data)

| Metric | Range |
|---|---|
| Average MAPE | **1.6 – 2.4 %** |
| Direction accuracy | **100 %** on tested symbols |
| Predictions within ±2 % | **80 – 100 %** |
| R² | **0.50 – 0.81** |

Tested on BTC, ETH, SOL, BNB — 120-day windows.

### Reinforcement learning research

State-of-the-art RL agents for trading research (not for live trading):

- **DQN** — dueling, noisy nets, prioritized replay
- **PPO** — with GAE
- **Transformer** — multi-head attention policy

See [`cryptvault/rl/README.md`](cryptvault/rl/README.md).

---

## 🗂️ Project Structure

```
Cryptvault/
├── cryptvault/
│   ├── desktop/         # Native Tk GUI (app, panels, theme)
│   ├── patterns/        # 50+ pattern detectors (7 categories)
│   ├── ml/              # Ensemble + feature engineering
│   ├── rl/              # DQN / PPO / Transformer agents
│   ├── data/            # Market data fetch & caching
│   ├── visualization/   # Chart rendering
│   ├── portfolio/       # Multi-asset analytics
│   └── security/        # Input validation & sanitization
├── docs/                # Full documentation
├── tests/               # pytest suite (unit + integration)
├── cryptvault_cli.py    # CLI entry point
├── launch_desktop.py    # Desktop launcher
└── pyproject.toml       # Tooling config (ruff, bandit, pytest)
```

---

## 🖥️ System Requirements

|  | Minimum | Recommended |
|---|---|---|
| Python | 3.9 | 3.11+ |
| RAM | 4 GB | 8 GB |
| Disk | 2 GB | 5 GB |
| Network | Required (data fetch) | — |

**Platforms:** Windows 10/11 · Ubuntu 20.04+ · macOS 10.15+ (including Apple Silicon).

---

## 🧪 Development

```bash
# Install dev tooling
pip install -r requirements.txt
pip install ruff bandit pytest pytest-cov pytest-xdist

# Lint (same command CI uses)
ruff check cryptvault/ cryptvault_cli.py
ruff format cryptvault/ cryptvault_cli.py

# Security scan
bandit -c pyproject.toml -r cryptvault/ -ll

# Tests (parallel)
pytest tests/ -n auto --cov=cryptvault --cov-report=term
```

The project is **ruff-clean** as of v6.1.0 — CI blocks on ruff violations.

---

## 📚 Documentation

| Doc | About |
|---|---|
| [Desktop App](docs/DESKTOP_APP.md) | Full GUI walkthrough |
| [Patterns](docs/PATTERNS.md) | Every detector, how it works |
| [Architecture](docs/ARCHITECTURE.md) | System design & data flow |
| [API Reference](docs/API_REFERENCE.md) | Python API |
| [Performance](docs/PERFORMANCE.md) | Benchmarks & tuning |
| [Deployment](docs/DEPLOYMENT.md) | Packaging & distribution |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common issues |
| [Security](docs/SECURITY.md) | Disclosure policy |
| [Changelog](docs/CHANGELOG.md) | Version history |
| [Contributing](docs/CONTRIBUTING.md) | How to contribute |
| [Code of Conduct](docs/CODE_OF_CONDUCT.md) | Community standards |

---

## 🤝 Contributing

1. Fork and branch from `main`.
2. `pip install -r requirements.txt`
3. Write tests first (pytest).
4. `ruff check` must pass.
5. Open a PR with a clear description.

See [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) and [`docs/CODE_OF_CONDUCT.md`](docs/CODE_OF_CONDUCT.md).

---

## 📝 License

MIT — see [`LICENSE`](LICENSE).

---

## 🙏 Credits

Built with: **scikit-learn** · **yfinance** · **NumPy** · **pandas** · **SciPy** · **Matplotlib** · **XGBoost** · **LightGBM**.

Maintained by **[MeridianAlgo](https://github.com/MeridianAlgo)** — a research organization focused on open-source financial ML. Not a licensed broker or financial advisor.

---

<div align="center">

**Version 6.2.0** · Last updated June 2026 · Built for researchers, by researchers.

</div>
