# CryptVault Dependencies

This directory contains organized dependency files for different use cases.

## Files

### `base.txt`
Core dependencies required for basic CryptVault functionality:
- Data processing (NumPy, Pandas)
- Machine learning (scikit-learn)
- Data sources (yfinance, ccxt, cryptocompare)
- Visualization (matplotlib)
- CLI interface (colorama)

**Install:** `pip install -r requirements/base.txt`

### `dev.txt`
Development dependencies including testing, linting, and documentation tools:
- Testing framework (pytest, pytest-cov)
- Code quality (black, flake8, isort, pylint)
- Type checking (mypy)
- Security scanning (bandit, safety)
- Documentation (sphinx)
- Development tools (ipython, pre-commit)

**Install:** `pip install -r requirements/dev.txt`

Note: This automatically includes base.txt dependencies.

### `test.txt`
Testing-specific dependencies for running the test suite:
- Core testing (pytest, pytest-cov, pytest-mock)
- Parallel execution (pytest-xdist)
- Test data generation (faker, freezegun)
- HTTP mocking (responses, requests-mock)
- Performance testing (pytest-benchmark)
- Coverage reporting (coverage)

**Install:** `pip install -r requirements/test.txt`

Note: This automatically includes base.txt dependencies.

### `optional.txt`
Optional dependencies that enable additional features:
- **Deep Learning** (`torch`, `tensorflow`) - LSTM neural networks
- **Advanced Visualization** (`plotly`, `dash`) - Interactive charts
- **Real-time Streaming** (`websockets`) - Live price updates
- **Performance** (`numba`) - Accelerated computations
- **Database** (`sqlalchemy`, `redis`) - Data persistence
- **Export** (`openpyxl`, `jinja2`) - Excel and HTML reports
- **Notifications** (`requests`) - Webhook alerts

**Install:** `pip install -r requirements/optional.txt`

Note: This automatically includes base.txt dependencies.

## Installation Scenarios

### Basic Installation (Minimal)
For core functionality only:
```bash
pip install -r requirements/base.txt
```

### Development Setup
For contributing to CryptVault:
```bash
pip install -r requirements/dev.txt
```

### Testing Setup
For running tests:
```bash
pip install -r requirements/test.txt
```

### Full Installation
For all features including optional dependencies:
```bash
pip install -r requirements/base.txt -r requirements/optional.txt
```

### Custom Installation
Install specific feature sets using setup.py extras:
```bash
# Machine learning features
pip install cryptvault[ml]

# Visualization features
pip install cryptvault[viz]

# Real-time streaming
pip install cryptvault[streaming]

# Performance optimizations
pip install cryptvault[fast]

# Database support
pip install cryptvault[db]

# Export formats
pip install cryptvault[export]

# Notifications
pip install cryptvault[notify]

# Everything
pip install cryptvault[full]
```

## Dependency Management

### Version Constraints
All dependencies use version ranges to balance stability and security:
- **Lower bound**: Minimum version with required features
- **Upper bound**: Major version to prevent breaking changes

Example: `numpy>=1.19.0,<2.0.0`
- Requires at least 1.19.0 for specific features
- Excludes 2.x to avoid breaking changes

### Updating Dependencies
To update dependencies to latest compatible versions:
```bash
pip install --upgrade -r requirements/base.txt
```

To check for outdated packages:
```bash
pip list --outdated
```

### Security Updates
Run security checks on dependencies:
```bash
pip install safety
safety check -r requirements/base.txt
```

## Optional Dependency Handling

CryptVault gracefully handles missing optional dependencies. If you try to use a feature that requires an optional package, you'll get a helpful error message:

```python
from cryptvault.utils.optional_deps import require_optional

# This will raise a helpful error if torch is not installed
torch = require_optional('torch', feature='LSTM predictions')
```

To check which optional features are available:
```python
from cryptvault import print_feature_status

print_feature_status()
```

Output:
```
CryptVault Optional Features
======================================================================
✓ LSTM neural network predictions
✗ Interactive web-based charts
✓ Accelerated numerical computations
...
```

## Troubleshooting

### Import Errors
If you encounter import errors, ensure you've installed the correct requirements file:
```bash
pip install -r requirements/base.txt
```

### Conflicting Dependencies
If you have conflicting dependencies, create a fresh virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements/base.txt
```

### Platform-Specific Issues
Some optional dependencies may have platform-specific requirements:
- **TA-Lib**: Requires C library installation
- **PyTorch**: Different versions for CPU vs GPU
- **TensorFlow**: May require specific system libraries

Refer to the package documentation for platform-specific installation instructions.

## Contributing

When adding new dependencies:
1. Add to the appropriate requirements file
2. Include version constraints
3. Add comments explaining the purpose
4. Update this README
5. Test installation in a clean environment
6. Update setup.py extras_require if optional

## Support

For dependency-related issues:
- Check [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)
- Review [GitHub Issues](https://github.com/MeridianAlgo/CryptVault/issues)
- Consult package documentation
