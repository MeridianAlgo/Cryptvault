# Setup Git hooks for pre-push validation (Windows)

Write-Host "Setting up Git hooks for CryptVault..." -ForegroundColor Cyan

# Create hooks directory if it doesn't exist
if (-not (Test-Path ".git/hooks")) {
    New-Item -ItemType Directory -Path ".git/hooks" -Force | Out-Null
}

# Create pre-push hook
$hookContent = @'
#!/bin/bash
# Pre-push hook to run validation checks

echo "Running pre-push validation..."
echo ""

# Run the pre-push check script
if [ -f "scripts/pre-push-check.sh" ]; then
    bash scripts/pre-push-check.sh
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -ne 0 ]; then
        echo ""
        echo "Pre-push validation failed!"
        echo "Fix the issues or use 'git push --no-verify' to skip checks."
        exit 1
    fi
elif [ -f "scripts/pre-push-check.ps1" ]; then
    powershell -ExecutionPolicy Bypass -File scripts/pre-push-check.ps1
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -ne 0 ]; then
        echo ""
        echo "Pre-push validation failed!"
        echo "Fix the issues or use 'git push --no-verify' to skip checks."
        exit 1
    fi
else
    echo "Warning: pre-push check script not found, skipping validation"
fi

echo ""
echo "Pre-push validation passed! Pushing..."
exit 0
'@

Set-Content -Path ".git/hooks/pre-push" -Value $hookContent -Encoding UTF8

Write-Host "✓ Pre-push hook installed" -ForegroundColor Green
Write-Host ""
Write-Host "The hook will run automatically before each push."
Write-Host "To skip the hook, use: git push --no-verify"
Write-Host ""
Write-Host "To run validation manually: powershell -File scripts/pre-push-check.ps1"
