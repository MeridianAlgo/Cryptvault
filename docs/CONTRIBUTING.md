# Contributing to CryptVault

Thank you for your interest in contributing to CryptVault! This project is an educational tool for cryptocurrency and stock analysis using AI/ML, pattern recognition, and technical analysis. We welcome contributions that improve functionality, documentation, testing, and code quality.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Code Style Guidelines](#code-style-guidelines)
5. [Testing Requirements](#testing-requirements)
6. [Pull Request Process](#pull-request-process)
7. [Issue Reporting](#issue-reporting)
8. [Documentation](#documentation)
9. [Recognition](#recognition)

## Code of Conduct

### Our Standards

- Be respectful and inclusive to all contributors
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members
- Follow the MIT License terms

### Educational Purpose

CryptVault is designed for educational and research purposes only. Contributions should:
- Avoid promoting financial advice or trading recommendations
- Focus on technical analysis and pattern recognition
- Maintain educational value
- Include proper disclaimers where appropriate

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of cryptocurrency/stock analysis
- Familiarity with Python development

### Quick Start

1. **Fork the Repository**
   ```bash
   # Fork via GitHub UI, then clone your fork
   git clone https://github.com/YOUR_USERNAME/cryptvault.git
   cd cryptvault
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Configure Environment**
   ```bash
   # Copy example configuration
   cp config/.env.example .env
   
   # Edit .env with your settings (optional for development)
   ```

4. **Verify Setup**
   ```bash
   # Run tests
   python -m pytest tests/
   
   # Run basic analysis
   python cryptvault_cli.py analyze BTC --days 30
   ```

## Development Setup

### Project Structure

```
cryptvault/
├── cryptvault/          # Main package
│   ├── cli/            # Command-line interface
│   ├── core/           # Core analysis logic
│   ├── data/           # Data fetching and models
│   ├── indicators/     # Technical indicators
│   ├── patterns/       # Pattern detection
│   ├── ml/             # Machine learning
│   ├── visualization/  # Charting
│   └── utils/          # Utilities
├── tests/              # Test suite
├── docs/               # Documentation
├── config/             # Configuration files
└── scripts/            # Utility scripts
```

### Development Tools

Install development tools:
```bash
pip install pylint mypy flake8 black pytest pytest-cov
```

### IDE Setup

**VS Code** (recommended):
- Install Python extension
- Configure linting (pylint, flake8)
- Enable type checking (mypy)
- Set up auto-formatting (black)

**PyCharm**:
- Configure Python interpreter
- Enable code inspections
- Set up pytest as test runner

## Code Style Guidelines

### Python Style (PEP 8)

We follow PEP 8 with some specific guidelines:

**Formatting**:
- Line length: 100 characters maximum
- Indentation: 4 spaces (no tabs)
- Blank lines: 2 between top-level definitions, 1 between methods
- Imports: Grouped (standard library, third-party, local)

**Naming Conventions**:
- Classes: `PascalCase` (e.g., `PatternAnalyzer`)
- Functions/Methods: `snake_case` (e.g., `analyze_ticker`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_DATA_POINTS`)
- Private members: Leading underscore (e.g., `_internal_method`)

**Example**:
```python
from typing import List, Optional
import numpy as np

from ..data.models import PriceDataFrame
from ..exceptions import AnalysisError


class PatternDetector:
    """Detect chart patterns in price data."""
    
    MAX_PATTERN_LENGTH = 100
    
    def __init__(self, sensitivity: float = 0.5):
        """Initialize pattern detector."""
        self.sensitivity = sensitivity
        self._cache = {}
    
    def detect_patterns(
        self,
        data: PriceDataFrame,
        min_confidence: float = 0.6
    ) -> List[DetectedPattern]:
        """
        Detect patterns in price data.
        
        Args:
            data: Price data to analyze
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of detected patterns
            
        Raises:
            AnalysisError: If detection fails
        """
        if len(data) < 10:
            raise AnalysisError("Insufficient data")
        
        patterns = self._find_patterns(data)
        return [p for p in patterns if p.confidence >= min_confidence]
    
    def _find_patterns(self, data: PriceDataFrame) -> List:
        """Internal pattern finding logic."""
        # Implementation
        pass
```

### Documentation Standards

**Docstrings** (Google Style):
```python
def analyze_ticker(
    ticker: str,
    days: int = 60,
    interval: str = '1d'
) -> AnalysisResult:
    """
    Analyze cryptocurrency by ticker symbol.
    
    This function fetches historical data and performs comprehensive
    analysis including pattern detection and technical indicators.
    
    Args:
        ticker: Ticker symbol (e.g., 'BTC', 'ETH', 'AAPL')
        days: Number of days of historical data (default: 60)
        interval: Data interval - '1m', '1h', '1d', '1wk' (default: '1d')
        
    Returns:
        AnalysisResult containing patterns, indicators, and predictions
        
    Raises:
        InvalidTickerError: If ticker symbol is invalid
        DataFetchError: If data cannot be fetched
        
    Example:
        >>> analyzer = PatternAnalyzer()
        >>> result = analyzer.analyze_ticker('BTC', days=60)
        >>> print(f"Found {len(result.patterns)} patterns")
        Found 5 patterns
    """
```

**Type Hints**:
- Use type hints for all function signatures
- Import from `typing` module
- Use `Optional` for nullable types
- Use `List`, `Dict`, `Tuple` for collections

**Comments**:
- Explain "why", not "what"
- Document complex algorithms
- Reference sources for formulas
- Note performance considerations

### Code Quality Standards

**Complexity**:
- Maximum cyclomatic complexity: 10 per function
- Break down complex functions into smaller ones
- Use helper functions for repeated logic

**Error Handling**:
- Use custom exceptions from `cryptvault.exceptions`
- Provide meaningful error messages
- Include context in exception details
- Log errors appropriately

**Performance**:
- Use NumPy for array operations
- Avoid unnecessary loops
- Cache expensive computations
- Document time complexity

## Testing Requirements

### Test Coverage

- Minimum 85% code coverage required
- All new features must include tests
- Bug fixes must include regression tests

### Test Structure

```
tests/
├── unit/              # Unit tests
│   ├── test_indicators.py
│   ├── test_patterns.py
│   └── test_ml.py
├── integration/       # Integration tests
│   └── test_analyzer.py
└── fixtures/          # Test data
    └── sample_data.py
```

### Writing Tests

**Unit Test Example**:
```python
import pytest
from cryptvault.indicators.momentum import calculate_rsi


class TestRSI:
    """Test RSI calculation."""
    
    def test_rsi_calculation(self):
        """Test RSI with known values."""
        prices = [44, 44.34, 44.09, 43.61, 44.33, 44.83, 45.10]
        rsi = calculate_rsi(prices, period=6)
        
        # RSI should be between 0 and 100
        assert 0 <= rsi[-1] <= 100
        
        # Test specific value (with tolerance)
        assert rsi[-1] == pytest.approx(66.67, rel=0.01)
    
    def test_rsi_edge_cases(self):
        """Test RSI edge cases."""
        # Insufficient data
        with pytest.raises(ValueError):
            calculate_rsi([1, 2, 3], period=14)
        
        # All same values (should return 50)
        prices = [100] * 20
        rsi = calculate_rsi(prices, period=14)
        assert rsi[-1] == pytest.approx(50.0, rel=0.01)
```

**Integration Test Example**:
```python
from cryptvault.core.analyzer import PatternAnalyzer


class TestAnalyzerIntegration:
    """Integration tests for analyzer."""
    
    def test_complete_analysis_workflow(self):
        """Test complete analysis from ticker to results."""
        analyzer = PatternAnalyzer()
        result = analyzer.analyze_ticker('BTC', days=30)
        
        assert result.success
        assert result.symbol == 'BTC'
        assert len(result.patterns) >= 0
        assert result.analysis_time > 0
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=cryptvault --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_indicators.py

# Run specific test
python -m pytest tests/unit/test_indicators.py::TestRSI::test_rsi_calculation

# Run with verbose output
python -m pytest tests/ -v

# Run only fast tests (skip slow integration tests)
python -m pytest tests/ -m "not slow"
```

### Test Markers

Use pytest markers to categorize tests:
```python
@pytest.mark.slow
def test_with_real_api():
    """Test that makes real API calls."""
    pass

@pytest.mark.unit
def test_calculation():
    """Fast unit test."""
    pass
```

## Pull Request Process

### Before Submitting

1. **Update Your Branch**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run Quality Checks**
   ```bash
   # Format code
   black cryptvault/
   
   # Run linters
   pylint cryptvault/
   flake8 cryptvault/
   mypy cryptvault/
   
   # Run tests
   python -m pytest tests/ --cov=cryptvault
   ```

3. **Update Documentation**
   - Update docstrings
   - Update README if needed
   - Update CHANGELOG.md
   - Add examples if applicable

### Commit Guidelines

**Commit Message Format**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(patterns): Add harmonic pattern detection

Implement Gartley, Butterfly, Bat, and Crab patterns using
Fibonacci ratios. Includes comprehensive tests and documentation.

Closes #123
```

```
fix(indicators): Correct RSI calculation for edge cases

Fix RSI calculation when all prices are identical. Now correctly
returns 50.0 instead of NaN.

Fixes #456
```

### Pull Request Template

When creating a PR, include:

**Title**: Clear, descriptive title

**Description**:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing
- [ ] Code coverage maintained/improved

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests added for new functionality

## Related Issues
Closes #123
```

### Review Process

1. **Automated Checks**: CI/CD runs tests and linters
2. **Code Review**: Maintainers review code quality
3. **Testing**: Reviewers test functionality
4. **Approval**: At least one maintainer approval required
5. **Merge**: Squash and merge to main branch

### Review Criteria

- Code quality and style
- Test coverage
- Documentation completeness
- Performance impact
- Security considerations
- Backward compatibility

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Describe the Bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. With parameters '...'
3. See error

**Expected Behavior**
What you expected to happen

**Actual Behavior**
What actually happened

**Environment**
- OS: [e.g., Windows 10, macOS 12, Ubuntu 20.04]
- Python Version: [e.g., 3.9.7]
- CryptVault Version: [e.g., 4.0.0]

**Logs**
```
Paste relevant logs from logs/cryptvault.log
```

**Additional Context**
Any other relevant information
```

### Feature Requests

Use the feature request template:

```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other approaches you've considered

**Additional Context**
Any other relevant information
```

### Questions

For questions:
- Check existing documentation
- Search closed issues
- Use GitHub Discussions
- Tag with `question` label

## Documentation

### Documentation Types

1. **Code Documentation**: Docstrings in code
2. **API Reference**: `docs/API_REFERENCE.md`
3. **Architecture**: `docs/ARCHITECTURE.md`
4. **User Guide**: `README.md`
5. **Examples**: `examples/` directory

### Documentation Standards

- Clear and concise
- Include examples
- Keep up-to-date with code
- Use proper markdown formatting
- Add diagrams where helpful

### Building Documentation

```bash
# Generate API documentation
python scripts/generate_docs.py

# View documentation locally
cd docs
python -m http.server 8000
# Open http://localhost:8000
```

## Recognition

### Contributors

All contributors are recognized in:
- `CHANGELOG.md` for each release
- GitHub contributors page
- Release notes

### Significant Contributions

Major contributions may be highlighted in:
- Project README
- Documentation credits
- Blog posts or announcements

## Getting Help

### Resources

- **Documentation**: `docs/` directory
- **Examples**: `examples/` directory
- **API Reference**: `docs/API_REFERENCE.md`
- **Architecture**: `docs/ARCHITECTURE.md`

### Communication

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Pull Requests**: Code contributions

### Maintainers

Current maintainers:
- Review pull requests
- Triage issues
- Maintain documentation
- Release new versions

## License

By contributing to CryptVault, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to CryptVault! Your efforts help make this project better for everyone.
