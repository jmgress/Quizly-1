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

# Determine script's own directory
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Initialize counters
total_suites=0
passed_suites=0
failed_suites=0

# Default behavior: run all tests
RUN_BACKEND=true
RUN_FRONTEND=true
BACKEND_SUITE_PATH="tests/backend" # Default to all backend tests

# Parse arguments
if [ "$#" -gt 0 ]; then
    RUN_BACKEND=false
    RUN_FRONTEND=false

    # Create a dummy .env file if it doesn't exist, for local runs
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        print_status "Creating dummy .env file for local test run..." "$BLUE"
        echo "LLM_PROVIDER=mock" > "$SCRIPT_DIR/.env"
        echo "OPENAI_API_KEY=test_key_local_dummy" >> "$SCRIPT_DIR/.env"
        echo "DATABASE_URL=sqlite:///./quiz_local_test.db" >> "$SCRIPT_DIR/.env"
        echo "PYTHONPATH=." >> "$SCRIPT_DIR/.env"
        # Add other necessary env vars with dummy values if tests require them
    fi

    if [ "$1" == "backend" ]; then
        RUN_BACKEND=true
        if [ "$2" == "unit" ]; then
            BACKEND_SUITE_PATH="tests/backend/unit"
        elif [ "$2" == "integration" ]; then
            BACKEND_SUITE_PATH="tests/backend/integration"
        elif [ -n "$2" ]; then
            echo "Invalid backend suite: $2. Options are 'unit' or 'integration'."
            exit 1
        fi
    elif [ "$1" == "frontend" ]; then
        RUN_FRONTEND=true
    else
        echo "Invalid argument: $1. Options are 'backend [unit|integration]' or 'frontend'."
        exit 1
    fi
fi

# Backend Tests
if [ "$RUN_BACKEND" = true ]; then
    print_status "🐍 BACKEND TESTS ($BACKEND_SUITE_PATH)" "$YELLOW"
    echo "=================="
    total_suites=$((total_suites + 1))

    print_status "Installing backend dependencies..." "$BLUE"
    if python -m pip install --upgrade pip && \
       python -m pip install -r "$SCRIPT_DIR/backend/requirements.txt" && \
       python -m pip install -r "$SCRIPT_DIR/backend/requirements-dev.txt"; then
        print_status "✅ Backend dependencies installed." "$GREEN"
    else
        print_status "❌ Failed to install backend dependencies." "$RED"
        # Optionally, exit here if backend tests cannot run without deps
        # exit 1
    fi

    # Run pytest for backend tests from project root
    # The run_test function changes directory, so call pytest from SCRIPT_DIR (project root)
    if run_test "Pytest Backend Suite" "python -m pytest ${BACKEND_SUITE_PATH} --cov=backend --cov-report=xml --cov-report=term-missing" "$SCRIPT_DIR"; then
        passed_suites=$((passed_suites + 1))
    else
        failed_suites=$((failed_suites + 1))
    fi
fi

# Frontend Tests
if [ "$RUN_FRONTEND" = true ]; then
    print_status "🌐 FRONTEND TESTS" "$YELLOW"
    echo "=================="
    total_suites=$((total_suites + 1))

    # Navigate to frontend directory relative to script location
    FRONTEND_DIR="$SCRIPT_DIR/frontend"

    if [ ! -d "$FRONTEND_DIR" ]; then
        print_status "❌ Frontend directory not found at $FRONTEND_DIR" "$RED"
        failed_suites=$((failed_suites + 1))
    else
        # Check if node_modules exists
        if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
            print_status "Installing frontend dependencies in $FRONTEND_DIR..." "$BLUE"
            (cd "$FRONTEND_DIR" && npm install)
        fi

        # Run React tests from frontend directory
        # CRA should now find tests in frontend/src/tests by default or via updated testMatch
        if run_test "Jest Frontend Suite" "npm test -- --coverage --watchAll=false" "$FRONTEND_DIR"; then
            passed_suites=$((passed_suites + 1))
        else
            failed_suites=$((failed_suites + 1))
        fi
    fi
fi

# Test Summary
echo ""
print_status "📊 TEST SUITE SUMMARY" "$YELLOW"
echo "======================"
echo "Total Suites Run: $total_suites"
print_status "Suites Passed: $passed_suites" "$GREEN"
print_status "Suites Failed: $failed_suites" "$RED"

# Overall status
if [ $failed_suites -eq 0 ] && [ $total_suites -gt 0 ]; then
    print_status "🎉 ALL TEST SUITES PASSED!" "$GREEN"
    exit 0
elif [ $total_suites -eq 0 ]; then
    print_status "🤷 No tests were run." "$YELLOW"
    exit 0
else
    print_status "❌ Some test suites failed. Please check the output above." "$RED"
    exit 1
fi

# Cleanup temporary files (if any created by run_test, ensure they are unique)
# The run_test function uses /tmp/test_output_$$.txt
rm -f /tmp/test_output_*.txt
# Consider making temp file names more specific if parallel execution is ever a goal.
# For now, $$ should be unique per script run.
