# Quick test of pre-push validation script

Write-Host "Testing pre-push validation script..." -ForegroundColor Cyan
Write-Host ""

# Test if script exists
if (Test-Path "scripts\pre-push-check.ps1") {
    Write-Host "[OK] Pre-push check script found" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Pre-push check script not found" -ForegroundColor Red
    exit 1
}

# Test Python
Write-Host ""
Write-Host "Testing Python..." -ForegroundColor Cyan
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Python not found" -ForegroundColor Red
    exit 1
}

# Test Git
Write-Host ""
Write-Host "Testing Git..." -ForegroundColor Cyan
$gitVersion = git --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Git found: $gitVersion" -ForegroundColor Green
} else {
    Write-Host "[FAIL] Git not found" -ForegroundColor Red
    exit 1
}

# Test required files
Write-Host ""
Write-Host "Testing required files..." -ForegroundColor Cyan
$requiredFiles = @(
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "LICENSE",
    "requirements.txt"
)

$allFound = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] $file" -ForegroundColor Red
        $allFound = $false
    }
}

Write-Host ""
if ($allFound) {
    Write-Host "[OK] All tests passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run the full pre-push check:" -ForegroundColor Cyan
    Write-Host "  powershell -File scripts\pre-push-check.ps1" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "[FAIL] Some tests failed" -ForegroundColor Red
    exit 1
}
