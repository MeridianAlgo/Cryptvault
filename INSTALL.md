# CryptVault Installation Guide

This guide provides detailed instructions for installing CryptVault with various configurations.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Basic Installation](#basic-installation)
- [Installation with Optional Features](#installation-with-optional-features)
- [Development Installation](#development-installation)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Disk Space**: 500 MB minimum (more for optional features)
- **RAM**: 4 GB minimum (8 GB recommended for ML features)

### Python Installation

Verify Python is installed:
```bash
python --version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/).

### Virtual Environment (Recommended)

Create a virtual environment to isolate dependencies:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

## Basic Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install cryptvault
```

This installs CryptVault with core dependencies only.

### Option 2: Install from Source

```bash
git clone https://github.com/MeridianAlgo/CryptVault.git
cd CryptVault
pip install -r requirements/base.txt
pip install -e .
```

### Option 3: Install from Requirements File

```bash
pip install -r requirements/base.txt
```

## Installation with Optional Features

CryptVault offers several optional feature sets that can be installed separately.

### Machine Learning Features

Enables LSTM neural network predictions:
```bash
pip install cryptvault[ml]
```

**Includes:**
- PyTorch for LSTM models
- Advanced prediction capabilities

**Requirements:**
- Additional 800 MB disk space
- 8 GB RAM recommended

### Visualization Features

Enables interactive web-based charts:
```bash
pip install cryptvault[viz]
```

**Includes:**
- Plotly for interactive charts
- Dash for web dashboards

### Real-time Streaming

Enables live price updates:
```bash
pip install cryptvault[streaming]
```

**Includes:**
- WebSockets for real-time data

### Performance Optimizations

Accelerates numerical computations:
```bash
pip install cryptvault[fast]
```

**Includes:**
- Numba JIT compiler

### Database Support

Enables data persistence:
```bash
pip install cryptvault[db]
```

**Includes:**
- SQLAlchemy for database operations
- Redis client for caching

**Requirements:**
- Redis server (optional, for Redis caching)

### Export Formats

Enables additional export formats:
```bash
pip install cryptvault[export]
```

**Includes:**
- openpyxl for Excel export
- Jinja2 for HTML reports

### Notification Services

Enables webhook notifications:
```bash
pip install cryptvault[notify]
```

**Includes:**
- Requests library for HTTP notifications

### Multiple Features

Install multiple feature sets:
```bash
pip install cryptvault[ml,viz,streaming]
```

### All Features

Install everything:
```bash
pip install cryptvault[full]
```

**Warning:** This installs all optional dependencies (~1.5 GB).

## Development Installation

For contributing to CryptVault:

### Step 1: Clone Repository

```bash
git clone https://github.com/MeridianAlgo/CryptVault.git
cd CryptVault
```

### Step 2: Install Development Dependencies

```bash
pip install -r requirements/dev.txt
```

This includes:
- Testing framework (pytest)
- Code quality tools (black, flake8, pylint, mypy)
- Security scanning (bandit, safety)
- Documentation tools (sphinx)

### Step 3: Install in Editable Mode

```bash
pip install -e .
```

### Step 4: Set Up Pre-commit Hooks (Optional)

```bash
pre-commit install
```

## Verification

### Verify Installation

Check if CryptVault is installed:
```bash
pip show cryptvault
```

### Check Version

```bash
python -c "import cryptvault; print(cryptvault.__version__)"
```

### Test CLI

```bash
cryptvault --help
```

### Check Optional Features

```python
from cryptvault import print_feature_status
print_feature_status()
```

Output shows which optional features are available:
```
CryptVault Optional Features
======================================================================
✓ LSTM neural network predictions
✗ Interactive web-based charts
✓ Accelerated numerical computations
...
```

### Run Tests (Development Only)

```bash
pytest tests/
```

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'cryptvault'`

**Solution:**
```bash
pip install cryptvault
```

### Version Conflicts

**Problem:** Dependency version conflicts

**Solution:** Create a fresh virtual environment:
```bash
python -m venv fresh_venv
source fresh_venv/bin/activate  # Windows: fresh_venv\Scripts\activate
pip install cryptvault
```

### PyTorch Installation Issues

**Problem:** PyTorch installation fails or is very slow

**Solution:** Install PyTorch separately first:
```bash
# CPU version (smaller, faster download)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Then install CryptVault
pip install cryptvault
```

### Permission Errors

**Problem:** `PermissionError` during installation

**Solution:** Use `--user` flag:
```bash
pip install --user cryptvault
```

Or use a virtual environment (recommended).

### SSL Certificate Errors

**Problem:** SSL certificate verification fails

**Solution:**
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org cryptvault
```

**Note:** Only use this as a last resort.

### Windows-Specific Issues

**Problem:** `error: Microsoft Visual C++ 14.0 is required`

**Solution:** Install Visual C++ Build Tools:
1. Download from [Microsoft](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Install "Desktop development with C++"
3. Retry installation

### macOS-Specific Issues

**Problem:** `xcrun: error: invalid active developer path`

**Solution:** Install Xcode Command Line Tools:
```bash
xcode-select --install
```

### Linux-Specific Issues

**Problem:** Missing system dependencies

**Solution:** Install required packages:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3-dev build-essential
```

**Fedora/RHEL:**
```bash
sudo dnf install python3-devel gcc gcc-c++
```

## Upgrade

### Upgrade to Latest Version

```bash
pip install --upgrade cryptvault
```

### Upgrade with Optional Features

```bash
pip install --upgrade cryptvault[full]
```

## Uninstall

```bash
pip uninstall cryptvault
```

## Getting Help

- **Documentation**: [GitHub Wiki](https://github.com/MeridianAlgo/CryptVault/wiki)
- **Issues**: [GitHub Issues](https://github.com/MeridianAlgo/CryptVault/issues)
- **Troubleshooting**: See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **Email**: support@meridianalgo.com

## Next Steps

After installation:

1. **Quick Start**: See [README.md](README.md) for usage examples
2. **API Reference**: See [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
3. **Examples**: Check the `examples/` directory
4. **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

## Platform-Specific Notes

### Windows

- Use PowerShell or Command Prompt
- Activate virtual environment: `venv\Scripts\activate`
- Some features may require Visual C++ Build Tools

### macOS

- Use Terminal
- Activate virtual environment: `source venv/bin/activate`
- May require Xcode Command Line Tools

### Linux

- Use Terminal
- Activate virtual environment: `source venv/bin/activate`
- May require build-essential packages

## Docker Installation

For containerized deployment:

```bash
docker pull meridianalgo/cryptvault:latest
docker run -it meridianalgo/cryptvault:latest
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for details.

## Offline Installation

For systems without internet access:

1. Download wheel file from [PyPI](https://pypi.org/project/cryptvault/)
2. Transfer to offline system
3. Install: `pip install cryptvault-4.0.0-py3-none-any.whl`

## License

CryptVault is released under the MIT License. See [LICENSE](LICENSE) for details.
