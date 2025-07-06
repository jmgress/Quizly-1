#!/bin/bash

# Quizly Test Runner
# This script runs all tests for both backend and frontend

echo "🧪 Running Quizly Test Suite"
echo "============================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${2}${1}${NC}"
}

# Function to run command and capture result
run_test() {
    local test_name=$1
    local command=$2
    local directory=$3
    
    print_status "Running $test_name..." "$BLUE"
    
    if [ -n "$directory" ]; then
        cd "$directory"
    fi
    
    if $command > /tmp/test_output_$$.txt 2>&1; then
        print_status "✅ $test_name PASSED" "$GREEN"
        return 0
    else
        print_status "❌ $test_name FAILED" "$RED"
        echo "Error output:"
        cat /tmp/test_output_$$.txt
        rm -f /tmp/test_output_$$.txt
        return 1
    fi
}

# Initialize counters
total_tests=0
passed_tests=0
failed_tests=0

# Backend Tests
print_status "🐍 BACKEND TESTS" "$YELLOW"
echo "=================="

# Test 1: Basic Backend Functionality
total_tests=$((total_tests + 1))
if run_test "Basic Backend Test" "python test_backend.py" "/Users/james.m.gress/Reops/Quizly-1/backend"; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi

# Test 2: Logging Configuration
total_tests=$((total_tests + 1))
if run_test "Logging Configuration Test" "python test_logging_config.py" "/Users/james.m.gress/Reops/Quizly-1/backend"; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi

# Test 3: LLM Configuration
total_tests=$((total_tests + 1))
if run_test "LLM Configuration Test" "python test_llm_config.py" "/Users/james.m.gress/Reops/Quizly-1/backend"; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi

# Test 4: OpenAI Integration (if configured)
total_tests=$((total_tests + 1))
if run_test "OpenAI Integration Test" "python test_openai.py" "/Users/james.m.gress/Reops/Quizly-1/backend"; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi

# Test 5: AI Integration
total_tests=$((total_tests + 1))
if run_test "AI Integration Test" "python test_ai_integration_simple.py" "/Users/james.m.gress/Reops/Quizly-1/backend"; then
    passed_tests=$((passed_tests + 1))
else
    print_status "❌ AI Integration Test FAILED or TIMEOUT" "$RED"
    failed_tests=$((failed_tests + 1))
fi

# Test 6: Pytest (if any pytest-compatible tests exist)
total_tests=$((total_tests + 1))
if run_test "Pytest Suite" "python -m pytest test_*.py -v --tb=short" "/Users/james.m.gress/Reops/Quizly-1/backend"; then
    passed_tests=$((passed_tests + 1))
else
    failed_tests=$((failed_tests + 1))
fi

# Frontend Tests
print_status "🌐 FRONTEND TESTS" "$YELLOW"
echo "=================="

# Test 7: React Component Tests
total_tests=$((total_tests + 1))
cd /Users/james.m.gress/Reops/Quizly-1/frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    print_status "Installing frontend dependencies..." "$BLUE"
    npm install
fi

# Run React tests
if CI=true npm test -- --watchAll=false --coverage=false --verbose=false > /tmp/frontend_test_output_$$.txt 2>&1; then
    print_status "✅ Frontend Tests PASSED" "$GREEN"
    passed_tests=$((passed_tests + 1))
else
    print_status "❌ Frontend Tests FAILED" "$RED"
    echo "Frontend test output:"
    cat /tmp/frontend_test_output_$$.txt
    failed_tests=$((failed_tests + 1))
fi

# Test Summary
echo ""
print_status "📊 TEST SUMMARY" "$YELLOW"
echo "================="
echo "Total Tests: $total_tests"
print_status "Passed: $passed_tests" "$GREEN"
print_status "Failed: $failed_tests" "$RED"

if [ $failed_tests -eq 0 ]; then
    print_status "🎉 ALL TESTS PASSED!" "$GREEN"
    exit 0
else
    print_status "❌ Some tests failed. Please check the output above." "$RED"
    exit 1
fi

# Cleanup
rm -f /tmp/test_output_$$.txt /tmp/ai_test_output_$$.txt /tmp/frontend_test_output_$$.txt
