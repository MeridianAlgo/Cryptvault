# Contributing to CryptVault

Thank you for your interest in contributing to CryptVault! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow project standards

## Getting Started

### Prerequisites

```bash
# Python 3.8+
python --version

# Install dependencies
pip install -r requirements.txt
pip install -r requirements/dev.txt  # Development dependencies
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/cryptvault.git
cd cryptvault

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Run tests
pytest tests/
```

## How to Contribute

### Reporting Bugs

1. Check if the bug already exists in [Issues](https://github.com/yourusername/cryptvault/issues)
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Error messages and logs

### Suggesting Features

1. Check existing feature requests
2. Create an issue with:
   - Clear use case
   - Proposed solution
   - Alternative approaches considered
   - Impact on existing functionality

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow code style guidelines
   - Add tests for new functionality
   - Update documentation

4. **Test your changes**
   ```bash
   pytest tests/
   python -m pylint cryptvault/
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "feat: add new pattern detection algorithm"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use docstrings for all public functions/classes

### Example

```python
def calculate_rsi(prices: np.ndarray, period: int = 14) -> np.ndarray:
    """
    Calculate Relative Strength Index.
    
    Args:
        prices: Array of closing prices
        period: RSI period (default: 14)
    
    Returns:
        Array of RSI values (0-100)
    
    Raises:
        ValueError: If period < 1 or prices array is empty
    """
    if period < 1:
        raise ValueError("Period must be >= 1")
    
    # Implementation...
    return rsi_values
```

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Example:**
```
feat: add LSTM model to ensemble predictor

- Implemented 2-layer LSTM with dropout
- Added adaptive weight adjustment
- Improved accuracy from 65% to 75%

Closes #123
```

## Testing

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_indicators.py

# With coverage
pytest --cov=cryptvault tests/
```

### Writing Tests

```python
import pytest
from cryptvault.indicators import calculate_rsi

def test_rsi_calculation():
    """Test RSI calculation with known values."""
    prices = np.array([44, 44.34, 44.09, 43.61, 44.33])
    rsi = calculate_rsi(prices, period=14)
    
    assert len(rsi) == len(prices)
    assert 0 <= rsi[-1] <= 100

def test_rsi_invalid_period():
    """Test RSI raises error for invalid period."""
    prices = np.array([44, 44.34, 44.09])
    
    with pytest.raises(ValueError):
        calculate_rsi(prices, period=0)
```

## Documentation

### Updating Documentation

- Update relevant `.md` files in `docs/`
- Add docstrings to new functions/classes
- Update `README.md` if adding major features
- Include code examples where helpful

### Documentation Structure

```
docs/
├── API_REFERENCE.md      # API documentation
├── ARCHITECTURE.md       # System architecture
├── CHANGELOG.md          # Version history
├── CONTRIBUTING.md       # This file
├── DEPLOYMENT.md         # Deployment guide
├── PERFORMANCE.md        # Performance optimization
├── SECURITY.md           # Security guidelines
└── TROUBLESHOOTING.md    # Common issues
```

## Project Structure

```
cryptvault/
├── cli/              # Command-line interface
├── core/             # Core analysis engine
├── data/             # Data models and fetching
├── indicators/       # Technical indicators
├── ml/               # Machine learning models
├── patterns/         # Pattern detection
├── security/         # Security features
├── storage/          # Data persistence
├── utils/            # Utility functions
└── visualization/    # Chart generation
```

## Review Process

1. **Automated Checks**
   - Tests must pass
   - Code coverage > 80%
   - Linting passes
   - No security vulnerabilities

2. **Code Review**
   - At least one maintainer approval
   - Address all review comments
   - Ensure documentation is updated

3. **Merge**
   - Squash commits if needed
   - Update CHANGELOG.md
   - Tag release if applicable

## Release Process

1. Update version in `__version__.py`
2. Update `CHANGELOG.md`
3. Create release branch
4. Run full test suite
5. Create GitHub release
6. Publish to PyPI (maintainers only)

## Getting Help

- **Documentation**: Check `docs/` folder
- **Issues**: Search existing issues
- **Discussions**: Use GitHub Discussions
- **Email**: contact@cryptvault.dev

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors are recognized in:
- `CHANGELOG.md` for each release
- GitHub contributors page
- Project README

Thank you for contributing to CryptVault! 🚀
