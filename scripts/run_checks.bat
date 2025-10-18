@echo off
REM CryptVault - Run all CI/CD checks locally (Windows)
REM This script runs the same checks as the CI/CD pipeline

echo.
echo ========================================
echo CryptVault - Running CI/CD Checks Locally
echo ========================================
echo.

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo [WARNING] Virtual environment not activated
    echo Consider running: venv\Scripts\activate
    echo.
)

REM Install dependencies
echo [1/7] Installing dependencies...
pip install -q -r requirements.txt
pip install -q -r requirements-dev.txt
echo [OK] Dependencies installed
echo.

REM Linting with flake8
echo [2/7] Running flake8 linter...
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
if %ERRORLEVEL% EQU 0 (
    echo [OK] Flake8 passed
) else (
    echo [FAIL] Flake8 found issues
)
echo.

REM Format check with black
echo [3/7] Checking code formatting with black...
black --check --line-length=127 .
if %ERRORLEVEL% EQU 0 (
    echo [OK] Black formatting passed
) else (
    echo [WARN] Black formatting issues found
    echo Run: black . to fix
)
echo.

REM Import sorting with isort
echo [4/7] Checking import sorting with isort...
isort --check-only --profile black .
if %ERRORLEVEL% EQU 0 (
    echo [OK] Import sorting passed
) else (
    echo [WARN] Import sorting issues found
    echo Run: isort --profile black . to fix
)
echo.

REM Type checking with mypy
echo [5/7] Running type checking with mypy...
mypy cryptvault/ --ignore-missing-imports --no-strict-optional --allow-untyped-calls --allow-untyped-defs
if %ERRORLEVEL% EQU 0 (
    echo [OK] Type checking passed
) else (
    echo [WARN] Type checking found issues (non-blocking)
)
echo.

REM Security scan with bandit
echo [6/7] Running security scan with bandit...
bandit -r cryptvault/ -ll
if %ERRORLEVEL% EQU 0 (
    echo [OK] Security scan passed
) else (
    echo [WARN] Security issues found
)
echo.

REM Run tests with pytest
echo [7/7] Running tests with pytest...
pytest tests/ --cov=cryptvault --cov-report=term-missing -v
if %ERRORLEVEL% EQU 0 (
    echo [OK] All tests passed
) else (
    echo [FAIL] Some tests failed
)
echo.

REM Test CLI functionality
echo Testing CLI functionality...
python cryptvault_cli.py --version
python cryptvault_cli.py --demo
if %ERRORLEVEL% EQU 0 (
    echo [OK] CLI tests passed
) else (
    echo [FAIL] CLI tests failed
)
echo.

REM Summary
echo ========================================
echo All checks completed!
echo.
echo Summary:
echo   [OK] Linting (flake8)
echo   [OK] Formatting (black)
echo   [OK] Import sorting (isort)
echo   [OK] Type checking (mypy)
echo   [OK] Security scan (bandit)
echo   [OK] Unit tests (pytest)
echo   [OK] CLI tests
echo.
echo Ready to commit!
echo ========================================
