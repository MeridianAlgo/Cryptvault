#!/bin/bash
# Setup Git hooks for pre-push validation

echo "Setting up Git hooks for CryptVault..."

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Create pre-push hook
cat > .git/hooks/pre-push << 'EOF'
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
else
    echo "Warning: pre-push-check.sh not found, skipping validation"
fi

echo ""
echo "Pre-push validation passed! Pushing..."
exit 0
EOF

# Make hook executable
chmod +x .git/hooks/pre-push

echo "✓ Pre-push hook installed"
echo ""
echo "The hook will run automatically before each push."
echo "To skip the hook, use: git push --no-verify"
echo ""
echo "To run validation manually: bash scripts/pre-push-check.sh"
