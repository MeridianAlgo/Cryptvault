# Contributing to CryptVault

We love your input! We want to make contributing to CryptVault as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## Pull Requests

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issue tracker](https://github.com/MeridianAlgo/CryptVault/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/MeridianAlgo/CryptVault/issues/new); it's that easy!

## Write bug reports with detail, background, and sample code

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/CryptVault.git
cd CryptVault

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run linting
flake8 cryptvault/
black cryptvault/
```

## Code Style

We use [Black](https://black.readthedocs.io/) for code formatting and [flake8](https://flake8.pycqa.org/) for linting.

- Use meaningful variable names
- Add docstrings to all functions and classes
- Keep functions focused and small
- Add type hints where appropriate
- Write tests for new functionality

## Areas for Contribution

### 🔍 Pattern Recognition
- Add new technical analysis patterns
- Improve pattern detection algorithms
- Enhance pattern confidence scoring

### 🧠 Machine Learning
- Implement new ML models
- Optimize existing ensemble methods
- Add feature engineering techniques

### 📊 Visualization
- Enhance ASCII chart rendering
- Add new chart types
- Improve pattern overlay visualization

### 🔧 Performance
- Optimize analysis speed
- Reduce memory usage
- Improve data fetching efficiency

### 📚 Documentation
- Improve code documentation
- Add usage examples
- Create tutorials and guides

## Testing

We use pytest for testing. Please add tests for any new functionality:

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_patterns.py

# Run with coverage
python -m pytest --cov=cryptvault tests/
```

## Commit Messages

Use clear and meaningful commit messages:

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

## License

By contributing, you agree that your contributions will be licensed under its MIT License.

## References

This document was adapted from the open-source contribution guidelines for [Facebook's Draft](https://github.com/facebook/draft-js/blob/a9316a723f9e918afde44dea68b5f9f39b7d9b00/CONTRIBUTING.md).