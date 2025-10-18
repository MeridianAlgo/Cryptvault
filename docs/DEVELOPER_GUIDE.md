# CryptVault Developer Guide

Complete guide for developers contributing to CryptVault.

## Table of Contents
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [CI/CD Pipeline](#cicd-pipeline)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Contributing](#contributing)

---

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- pip (Python package manager)

### Quick Setup
```bash
# Clone repository
git clone https://github.com/MeridianAlgo/Cryptvault.git
cd Cryptvault

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run application
python cryptvault_cli.py --demo
```

---

## Development Setup

### Virtual Environment
Always use a virtual environment:
```bash
# Create
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Deactivate
deactivate
```

### Install Development Dependencies
```bash
pip install -r requirements-dev.txt
```

**Development dependencies include:**
- pytest - Testing framework
- pytest-cov - Code coverage
- black - Code formatter
- flake8 - Linter
- isort - Import sorter
- mypy - Type checker
- bandit - Security scanner

---

## CI/CD Pipeline

### Overview
CryptVault uses GitHub Actions for comprehensive CI/CD with **15 test configurations**.

### Pipeline Jobs

#### 1. **Test** (15 configurations)
- **Platforms:** Ubuntu, macOS, Windows
- **Python Versions:** 3.8, 3.9, 3.10, 3.11, 3.12
- **Total:** 3 OS × 5 Python = 15 configurations

**What it does:**
- Installs dependencies
- Runs linters (flake8, black, isort)
- Type checking (mypy)
- Unit tests (pytest)
- Code coverage

#### 2. **Integration Tests**
- Tests CLI functionality
- Verifies analysis features
- Checks all commands work

#### 3. **Security Scan**
- Bandit security analysis
- Dependency vulnerability check
- Safety audit

#### 4. **Code Quality**
- Pylint analysis
- Code complexity (radon)
- Maintainability index

#### 5. **Documentation Check**
- Verifies all docs exist
- Checks for broken links
- Validates structure

#### 6. **Performance Tests**
- Analysis speed tests
- Memory profiling
- Performance benchmarks

#### 7. **Dependency Analysis**
- Audit dependencies
- Check for vulnerabilities
- Show dependency tree

#### 8. **Build**
- Package building
- Distribution creation
- PyPI preparation

#### 9. **Release** (on tags)
- GitHub release creation
- PyPI publishing
- Artifact distribution

### Triggering CI/CD

**Automatic triggers:**
- Push to `main` or `develop` branch
- Pull requests to `main`
- Daily at 2 AM UTC (scheduled)

**Manual trigger:**
```bash
# Go to GitHub Actions tab
# Click "Run workflow"
```

### Local CI/CD Simulation

Run the same checks locally before pushing:

```bash
# Linting
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127

# Formatting
black --check --line-length=127 .

# Import sorting
isort --check-only --profile black .

# Type checking
mypy cryptvault/ --ignore-missing-imports

# Tests
pytest tests/ --cov=cryptvault --cov-report=term-missing

# Security
bandit -r cryptvault/

# All at once
./scripts/run_checks.sh  # (create this script)
```

---

## Testing

### Running Tests

**All tests:**
```bash
pytest tests/
```

**With coverage:**
```bash
pytest tests/ --cov=cryptvault --cov-report=html
```

**Specific test:**
```bash
pytest tests/test_analyzer.py
```

**Verbose output:**
```bash
pytest tests/ -v
```

### Writing Tests

**Test structure:**
```python
# tests/test_feature.py
import pytest
from cryptvault.feature import FeatureClass

def test_feature_functionality():
    """Test feature works correctly."""
    feature = FeatureClass()
    result = feature.do_something()
    assert result == expected_value

def test_feature_error_handling():
    """Test feature handles errors."""
    feature = FeatureClass()
    with pytest.raises(ValueError):
        feature.do_invalid_thing()
```

**Test fixtures:**
```python
@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {
        'symbol': 'BTC',
        'price': 50000
    }

def test_with_fixture(sample_data):
    """Test using fixture."""
    assert sample_data['symbol'] == 'BTC'
```

---

## Code Quality

### Code Formatting

**Black (automatic formatting):**
```bash
# Check
black --check .

# Format
black .
```

**Configuration:** Uses 127 character line length

### Linting

**Flake8:**
```bash
flake8 . --max-line-length=127
```

**Common issues:**
- E501: Line too long
- F401: Unused import
- E302: Expected 2 blank lines

### Import Sorting

**isort:**
```bash
# Check
isort --check-only --profile black .

# Fix
isort --profile black .
```

### Type Checking

**mypy:**
```bash
mypy cryptvault/ --ignore-missing-imports
```

**Type hints example:**
```python
def analyze_data(symbol: str, days: int) -> Dict[str, Any]:
    """Analyze data with type hints."""
    return {'symbol': symbol, 'days': days}
```

---

## Contributing

### Workflow

1. **Fork the repository**
2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature
   ```

3. **Make changes**
   - Write code
   - Add tests
   - Update docs

4. **Run checks locally**
   ```bash
   pytest tests/
   black .
   flake8 .
   ```

5. **Commit changes**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature
   ```

### Commit Messages

**Format:**
```
type: Short description

Longer description if needed.

- Bullet points for details
- More details
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `style:` Formatting
- `chore:` Maintenance

**Examples:**
```
feat: Add support for new cryptocurrency

Added support for analyzing Solana (SOL) with full
pattern detection and ML predictions.

- Added SOL to supported tickers
- Updated documentation
- Added tests
```

### Pull Request Guidelines

**PR Title:**
```
[Type] Short description
```

**PR Description:**
```markdown
## Description
What does this PR do?

## Changes
- Change 1
- Change 2

## Testing
How was this tested?

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code formatted
- [ ] No linting errors
```

---

## Project Structure

```
CryptVault/
├── .github/
│   └── workflows/
│       └── ci.yml          # CI/CD pipeline
├── cryptvault/             # Main package
│   ├── data/              # Data handling
│   ├── patterns/          # Pattern detection
│   ├── ml/                # Machine learning
│   ├── indicators/        # Technical indicators
│   ├── visualization/     # Charts
│   ├── portfolio/         # Portfolio analysis
│   ├── storage/           # Result storage
│   └── config/            # Configuration
├── docs/                  # Documentation
├── tests/                 # Test suite
├── config/                # Config files
├── cryptvault_cli.py      # CLI application
├── cryptvault.py          # Core charts
├── setup.py               # Package setup
├── requirements.txt       # Dependencies
└── requirements-dev.txt   # Dev dependencies
```

---

## Common Tasks

### Adding a New Feature

1. **Create feature file**
   ```bash
   touch cryptvault/new_feature.py
   ```

2. **Write code with tests**
   ```python
   # cryptvault/new_feature.py
   def new_function():
       """New feature."""
       return "result"
   ```

3. **Add tests**
   ```python
   # tests/test_new_feature.py
   def test_new_function():
       from cryptvault.new_feature import new_function
       assert new_function() == "result"
   ```

4. **Update documentation**
   ```markdown
   # docs/NEW_FEATURE.md
   # New Feature Documentation
   ```

5. **Run checks**
   ```bash
   pytest tests/
   black .
   flake8 .
   ```

### Adding a New Cryptocurrency

1. **Update package_fetcher.py**
   ```python
   crypto_symbols = {
       # ... existing ...
       'NEW': 'New Coin',
   }
   ```

2. **Add to supported list**
   ```python
   def get_supported_tickers(self):
       return ['BTC', 'ETH', ..., 'NEW']
   ```

3. **Test**
   ```bash
   python cryptvault_cli.py NEW 60 1d
   ```

4. **Update docs**
   - README.md
   - docs/main_README.md

---

## Debugging

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Debug Mode

```bash
python cryptvault_cli.py BTC 60 1d --verbose
```

### Common Issues

**Import errors:**
```bash
pip install -r requirements.txt
```

**Test failures:**
```bash
pytest tests/ -v  # Verbose output
pytest tests/ -s  # Show print statements
```

**Type errors:**
```bash
mypy cryptvault/ --ignore-missing-imports
```

---

## Performance Optimization

### Profiling

```bash
# Time profiling
python -m cProfile -o profile.stats cryptvault_cli.py BTC 60 1d

# Memory profiling
python -m memory_profiler cryptvault_cli.py BTC 60 1d
```

### Optimization Tips

1. **Cache expensive operations**
2. **Use numpy for calculations**
3. **Minimize API calls**
4. **Lazy load modules**
5. **Profile before optimizing**

---

## Release Process

### Version Bumping

1. **Update version** in:
   - `setup.py`
   - `cryptvault/__init__.py`
   - `cryptvault_cli.py`
   - `README.md`

2. **Update CHANGELOG**
   ```markdown
   ## [3.2.2] - 2025-10-18
   ### Added
   - New feature
   ### Fixed
   - Bug fix
   ```

3. **Commit and tag**
   ```bash
   git add .
   git commit -m "Release v3.2.2"
   git tag -a v3.2.2 -m "Release v3.2.2"
   git push origin main
   git push origin v3.2.2
   ```

4. **CI/CD will:**
   - Run all tests
   - Build package
   - Create GitHub release
   - Publish to PyPI (if configured)

---

## Resources

### Documentation
- [Main README](../README.md)
- [CLI vs Core](CLI_VS_CORE.md)
- [Platform Support](PLATFORM_SUPPORT.md)
- [Contributing](../CONTRIBUTING.md)

### External Resources
- [Python Packaging](https://packaging.python.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [PEP 8 Style Guide](https://pep8.org/)

---

## Getting Help

### Community
- **GitHub Issues:** Report bugs or request features
- **Discussions:** Ask questions
- **Pull Requests:** Contribute code

### Contact
- **Email:** meridianalgo@gmail.com
- **GitHub:** [@MeridianAlgo](https://github.com/MeridianAlgo)

---

**Happy Coding! 🚀**

*Last Updated: October 18, 2025*
