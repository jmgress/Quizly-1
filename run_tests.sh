#!/bin/bash
# Centralized Quizly Test Runner
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEST_DIR="$ROOT_DIR/tests"

category=${1:-all}
suite=${2:-all}

run_backend() {
    local subdir="$TEST_DIR/backend"
    if [ "$1" = "unit" ]; then
        subdir="$subdir/unit"
    elif [ "$1" = "integration" ]; then
        subdir="$subdir/integration"
    fi
    echo "Running backend tests in $subdir"
    pytest "$subdir"
}

run_frontend() {
    local pattern="$TEST_DIR/frontend"
    if [ "$1" = "unit" ]; then
        pattern="$pattern/unit"
    elif [ "$1" = "integration" ]; then
        pattern="$pattern/integration"
    fi
    echo "Running frontend tests in $pattern"
    cd "$ROOT_DIR/frontend"
    if [ ! -d node_modules ]; then
        npm install
    fi
    CI=true npm test -- --watchAll=false --testPathPattern="$pattern"
    cd "$ROOT_DIR"
}

case "$category" in
    backend)
        run_backend "$suite"
        ;;
    frontend)
        run_frontend "$suite"
        ;;
    *)
        run_backend "$suite"
        run_frontend "$suite"
        ;;
esac
