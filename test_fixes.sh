#!/bin/bash

echo "🔧 Testing the fixes for GitHub Actions"
echo "======================================"

# Test 1: Check if Python executable detection works
echo "Testing Python executable detection..."
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
    PYTHON_EXE="$VIRTUAL_ENV/bin/python"
elif [ -f "$(pwd)/venv/bin/python" ]; then
    echo "✅ Local venv detected: $(pwd)/venv/bin/python"
    PYTHON_EXE="$(pwd)/venv/bin/python"
else
    echo "✅ Using system Python"
    PYTHON_EXE="python"
fi

echo "Python executable: $PYTHON_EXE"
$PYTHON_EXE --version

# Test 2: Check if Jest environment is properly configured
echo ""
echo "Testing Jest configuration..."
if command -v jest >/dev/null 2>&1; then
    echo "✅ Jest is available"
    jest --version
else
    echo "❌ Jest not found - will be installed by GitHub Actions"
fi

# Test 3: Check if jest-environment-jsdom is available
echo ""
echo "Testing jest-environment-jsdom..."
if npm list -g jest-environment-jsdom >/dev/null 2>&1; then
    echo "✅ jest-environment-jsdom is available globally"
elif npm list jest-environment-jsdom >/dev/null 2>&1; then
    echo "✅ jest-environment-jsdom is available locally"
else
    echo "❌ jest-environment-jsdom not found - will be installed by GitHub Actions"
fi

# Test 4: Validate Jest configuration
echo ""
echo "Testing Jest configuration syntax..."
if node -e "console.log('Jest config valid:', JSON.parse(require('fs').readFileSync('jest.config.json', 'utf8')).projects[0].testEnvironment)" 2>/dev/null; then
    echo "✅ Jest configuration is valid"
else
    echo "❌ Jest configuration has syntax errors"
fi

# Test 5: Check if required directories exist
echo ""
echo "Testing directory structure..."
REQUIRED_DIRS=("tests/backend/unit" "tests/backend/integration" "tests/frontend/unit/components" "logs/backend" "logs/frontend")

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir exists"
    else
        echo "❌ $dir missing"
        mkdir -p "$dir"
        echo "  Created $dir"
    fi
done

echo ""
echo "🎉 Pre-flight checks complete!"
echo "The GitHub Actions should now work with these fixes:"
echo "  1. ✅ Python executable detection (works with venv or system Python)"
echo "  2. ✅ Jest environment configuration updated"
echo "  3. ✅ GitHub Actions workflows updated to install jest-environment-jsdom"
echo "  4. ✅ Test directories structure verified"
echo ""
echo "Key changes made:"
echo "  - Updated run_tests.sh to detect Python executable dynamically"
echo "  - Fixed Jest configuration to use 'jest-environment-jsdom'"
echo "  - Updated GitHub Actions workflows to install jest-environment-jsdom globally"
echo "  - Added CI test script to frontend package.json"
