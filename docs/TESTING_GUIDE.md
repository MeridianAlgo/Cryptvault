# Testing Guide

Complete guide for testing CryptVault before releases and pushes.

## Quick Start

### Run All Pre-Push Checks

**Linux/macOS:**
```bash
bash scripts/pre-push-check.sh
```

**Windows:**
```powershell
powershell -File scripts/pre-push-check.ps1
```

### Setup Automatic Pre-Push Validation

**Linux/macOS:**
```bash
bash scripts/setup-git-hooks.sh
```

**Windows:**
```powershell
powershell -File scripts/setup-git-hooks.ps1
```

## Testing Levels

### Level 1: Unit Tests

Run unit tests for specific modules:

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_parsers.py

# Specific test function
pytest tests/test_parsers.py::test_csv_parser

# With coverage
pytest tests/ --cov=cryptvault --cov-report=html

# Verbose output
pytest tests/ -v

# Stop on first failure
pytest tests/ -x
```

### Level 2: Integration Tests

Test CLI functionality:

```bash
# Help command
python cryptvault_cli.py --help

# Version check
python cryptvault_cli.py --version

# Status check
python cryptvault_cli.py --status

# Demo mode
python cryptvault_cli.py --demo

# Actual analysis (requires internet)
python cryptvault_cli.py BTC 30 1d
```

### Level 3: Code Quality

#### Formatting
```bash
# Check formatting
black --check --line-length=127 cryptvault/ generate_chart.py cryptvault_cli.py

# Auto-format
black --line-length=127 cryptvault/ generate_chart.py cryptvault_cli.py
```

#### Import Sorting
```bash
# Check imports
isort --check-only --profile black cryptvault/ generate_chart.py cryptvault_cli.py

# Auto-sort imports
isort --profile black cryptvault/ generate_chart.py cryptvault_cli.py
```

#### Linting
```bash
# Run flake8
flake8 cryptvault/ generate_chart.py cryptvault_cli.py --max-line-length=127

# With statistics
flake8 cryptvault/ --count --statistics --max-line-length=127
```

#### Type Checking
```bash
# Run mypy
mypy cryptvault/ --ignore-missing-imports
```

### Level 4: Security

#### Security Scan
```bash
# Run bandit
bandit -r cryptvault/ -ll

# Generate report
bandit -r cryptvault/ -f json -o bandit-report.json
```

#### Dependency Vulnerabilities
```bash
# Check with safety
safety check

# Check with pip-audit
pip-audit
```

### Level 5: Performance

#### Performance Testing
```bash
# Time analysis
time python cryptvault_cli.py BTC 30 1d

# Memory profiling
python -m memory_profiler cryptvault_cli.py BTC 30 1d
```

#### Load Testing
```bash
# Multiple analyses
for symbol in BTC ETH SOL; do
    python cryptvault_cli.py $symbol 30 1d
done
```

## CI/CD Pipeline

### Local CI Simulation

Run the same checks as CI:

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all checks
bash scripts/pre-push-check.sh
```

### GitHub Actions

The CI/CD pipeline runs automatically on:
- Push to main or develop branches
- Pull requests to main or develop
- Daily at 2 AM UTC
- Manual trigger via workflow_dispatch

#### Pipeline Jobs

1. **Test** - Multi-platform testing (Ubuntu, macOS, Windows) with Python 3.8-3.12
2. **Integration Test** - CLI functionality tests
3. **Security** - Bandit scan and dependency check
4. **Code Quality** - Pylint and complexity analysis
5. **Documentation** - Documentation file checks
6. **Performance** - Performance benchmarks
7. **Dependency Check** - Dependency audit
8. **Build** - Package building
9. **Summary** - Pipeline summary report

### Viewing CI Results

1. Go to GitHub repository
2. Click "Actions" tab
3. Select workflow run
4. View job results and logs

## Pre-Release Checklist

### 1. Version Update

Update version in all files:
- `setup.py`
- `cryptvault/__init__.py`
- `README.md`

```bash
# Check version consistency
grep -r "version" setup.py cryptvault/__init__.py README.md
```

### 2. Run Full Test Suite

```bash
# All tests with coverage
pytest tests/ --cov=cryptvault --cov-report=term-missing --cov-report=html

# Integration tests
python cryptvault_cli.py --demo
python cryptvault_cli.py BTC 30 1d
```

### 3. Code Quality Checks

```bash
# Format code
black --line-length=127 cryptvault/ generate_chart.py cryptvault_cli.py

# Sort imports
isort --profile black cryptvault/ generate_chart.py cryptvault_cli.py

# Lint
flake8 cryptvault/ generate_chart.py cryptvault_cli.py --max-line-length=127

# Type check
mypy cryptvault/ --ignore-missing-imports
```

### 4. Security Scan

```bash
# Security scan
bandit -r cryptvault/ -ll

# Dependency check
safety check
pip-audit
```

### 5. Documentation Update

- Update CHANGELOG.md
- Update version in README.md
- Review all documentation links
- Check for broken links

### 6. Build and Test Package

```bash
# Build package
python -m build

# Check package
twine check dist/*

# Test installation
pip install dist/*.whl
python -c "import cryptvault; print(cryptvault.__version__)"
```

### 7. Create Release

```bash
# Tag release
git tag -a v3.3.0 -m "Release v3.3.0"

# Push tag
git push origin v3.3.0
```

## Continuous Testing

### Daily Testing

Set up cron job for daily testing:

```bash
# Add to crontab
0 2 * * * cd /path/to/cryptvault && bash scripts/pre-push-check.sh
```

### Pre-Commit Hook

Install pre-commit hook for automatic checks:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Troubleshooting

### Tests Failing

1. Check Python version (3.8+)
2. Update dependencies: `pip install -r requirements.txt`
3. Clear cache: `pytest --cache-clear`
4. Run specific test: `pytest tests/test_file.py -v`

### Import Errors

1. Check PYTHONPATH
2. Reinstall package: `pip install -e .`
3. Check for circular imports

### Coverage Issues

1. Run with verbose: `pytest --cov=cryptvault --cov-report=term-missing -v`
2. Check .coveragerc configuration
3. Exclude test files from coverage

### CI/CD Failures

1. Check GitHub Actions logs
2. Run same commands locally
3. Check for platform-specific issues
4. Review recent changes

## Best Practices

### Before Every Commit

1. Run unit tests: `pytest tests/`
2. Check formatting: `black --check cryptvault/`
3. Run linter: `flake8 cryptvault/`

### Before Every Push

1. Run full pre-push check: `bash scripts/pre-push-check.sh`
2. Review changes: `git diff`
3. Check commit messages

### Before Every Release

1. Complete pre-release checklist
2. Run full test suite on all platforms
3. Update documentation
4. Create release notes
5. Tag release

## Testing Tools

### Required Tools

- pytest - Unit testing
- pytest-cov - Coverage reporting
- black - Code formatting
- flake8 - Linting
- isort - Import sorting
- mypy - Type checking
- bandit - Security scanning
- safety - Dependency checking

### Optional Tools

- pytest-xdist - Parallel testing
- pytest-benchmark - Performance testing
- memory-profiler - Memory profiling
- coverage - Coverage analysis
- pylint - Advanced linting
- radon - Complexity analysis

### Installation

```bash
# Required tools
pip install pytest pytest-cov black flake8 isort mypy bandit safety

# Optional tools
pip install pytest-xdist pytest-benchmark memory-profiler coverage pylint radon
```

## Resources

### Documentation
- [pytest documentation](https://docs.pytest.org/)
- [black documentation](https://black.readthedocs.io/)
- [flake8 documentation](https://flake8.pycqa.org/)
- [mypy documentation](https://mypy.readthedocs.io/)

### Internal Docs
- [Developer Guide](DEVELOPER_GUIDE.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
- [CI/CD Pipeline](.github/workflows/ci.yml)

---

## Related Documentation

### Development
- [Developer Guide](DEVELOPER_GUIDE.md) - Complete development guide
- [Contributing](../CONTRIBUTING.md) - Contribution guidelines
- [Code of Conduct](policies/CODE_OF_CONDUCT.md) - Community guidelines

### CI/CD
- [CI Workflow](../.github/workflows/ci.yml) - CI/CD pipeline
- [Release Workflow](../.github/workflows/release.yml) - Release process

### Reference
- [Documentation Index](INDEX.md) - Complete documentation index
- [Main README](../README.md) - Project overview

---

[Documentation Index](INDEX.md) | [Main README](../README.md) | [Developer Guide](DEVELOPER_GUIDE.md)
