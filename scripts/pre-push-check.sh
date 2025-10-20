#!/bin/bash
# Pre-push validation script
# Run this before pushing to ensure code quality

set -e

echo "========================================="
echo "CryptVault Pre-Push Validation"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track failures
FAILURES=0

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
        FAILURES=$((FAILURES + 1))
    fi
}

# 1. Check Python version
echo "1. Checking Python version..."
python --version
PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [[ "$PYTHON_VERSION" < "3.8" ]]; then
    print_status 1 "Python version must be 3.8 or higher"
else
    print_status 0 "Python version OK ($PYTHON_VERSION)"
fi
echo ""

# 2. Install dependencies
echo "2. Installing dependencies..."
pip install -q -r requirements.txt
pip install -q -r requirements-dev.txt 2>/dev/null || pip install -q pytest pytest-cov black flake8 isort mypy bandit safety
print_status $? "Dependencies installed"
echo ""

# 3. Code formatting check
echo "3. Checking code formatting (black)..."
black --check --line-length=127 cryptvault/ generate_chart.py cryptvault_cli.py 2>/dev/null
print_status $? "Code formatting check"
echo ""

# 4. Import sorting check
echo "4. Checking import sorting (isort)..."
isort --check-only --profile black cryptvault/ generate_chart.py cryptvault_cli.py 2>/dev/null
print_status $? "Import sorting check"
echo ""

# 5. Linting
echo "5. Running linter (flake8)..."
flake8 cryptvault/ generate_chart.py cryptvault_cli.py --count --max-complexity=10 --max-line-length=127 --statistics --exit-zero
print_status $? "Linting check"
echo ""

# 6. Type checking
echo "6. Running type checker (mypy)..."
mypy cryptvault/ --ignore-missing-imports --no-strict-optional --allow-untyped-calls --allow-untyped-defs 2>/dev/null
print_status $? "Type checking"
echo ""

# 7. Security scan
echo "7. Running security scan (bandit)..."
bandit -r cryptvault/ -ll -q 2>/dev/null
print_status $? "Security scan"
echo ""

# 8. Dependency vulnerabilities
echo "8. Checking dependency vulnerabilities (safety)..."
safety check --json 2>/dev/null || safety check 2>/dev/null
print_status $? "Dependency vulnerability check"
echo ""

# 9. Run tests
echo "9. Running tests (pytest)..."
pytest tests/ -v --maxfail=3 --tb=short -q
TEST_RESULT=$?
print_status $TEST_RESULT "Unit tests"
echo ""

# 10. Test coverage
echo "10. Checking test coverage..."
pytest tests/ --cov=cryptvault --cov-report=term-missing --cov-fail-under=50 -q 2>/dev/null
print_status $? "Test coverage (minimum 50%)"
echo ""

# 11. Integration tests
echo "11. Running integration tests..."
python cryptvault_cli.py --help > /dev/null 2>&1
CLI_HELP=$?
python cryptvault_cli.py --version > /dev/null 2>&1
CLI_VERSION=$?
python cryptvault_cli.py --status > /dev/null 2>&1
CLI_STATUS=$?

if [ $CLI_HELP -eq 0 ] && [ $CLI_VERSION -eq 0 ] && [ $CLI_STATUS -eq 0 ]; then
    print_status 0 "CLI integration tests"
else
    print_status 1 "CLI integration tests"
fi
echo ""

# 12. Documentation check
echo "12. Checking documentation..."
DOC_ERRORS=0
[ ! -f README.md ] && DOC_ERRORS=$((DOC_ERRORS + 1))
[ ! -f CONTRIBUTING.md ] && DOC_ERRORS=$((DOC_ERRORS + 1))
[ ! -f SECURITY.md ] && DOC_ERRORS=$((DOC_ERRORS + 1))
[ ! -f LICENSE ] && DOC_ERRORS=$((DOC_ERRORS + 1))
[ ! -d docs ] && DOC_ERRORS=$((DOC_ERRORS + 1))
print_status $DOC_ERRORS "Documentation files"
echo ""

# 13. Check for large files
echo "13. Checking for large files..."
LARGE_FILES=$(find . -type f -size +1M -not -path "./.git/*" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./node_modules/*" 2>/dev/null | wc -l)
if [ $LARGE_FILES -gt 0 ]; then
    echo "Warning: Found $LARGE_FILES files larger than 1MB"
    find . -type f -size +1M -not -path "./.git/*" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./node_modules/*" 2>/dev/null
    print_status 1 "Large files check"
else
    print_status 0 "No large files found"
fi
echo ""

# 14. Check for sensitive data
echo "14. Checking for sensitive data..."
SENSITIVE_PATTERNS="password|secret|api_key|private_key|token"
SENSITIVE_FILES=$(grep -r -i -E "$SENSITIVE_PATTERNS" --include="*.py" --include="*.yml" --include="*.yaml" --exclude-dir=".git" --exclude-dir="venv" --exclude-dir=".venv" . 2>/dev/null | grep -v "# " | wc -l)
if [ $SENSITIVE_FILES -gt 0 ]; then
    echo "Warning: Found potential sensitive data patterns"
    print_status 1 "Sensitive data check"
else
    print_status 0 "No sensitive data patterns found"
fi
echo ""

# 15. Check git status
echo "15. Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
    echo "Warning: You have uncommitted changes"
    git status --short
    print_status 1 "Git status clean"
else
    print_status 0 "Git status clean"
fi
echo ""

# Summary
echo "========================================="
echo "Validation Summary"
echo "========================================="
if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo "You can safely push your changes."
    exit 0
else
    echo -e "${RED}✗ $FAILURES check(s) failed${NC}"
    echo "Please fix the issues before pushing."
    exit 1
fi
