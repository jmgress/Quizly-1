#!/bin/bash

# Quizly Application Launcher
# This script starts both the backend and frontend servers

echo "🧠 Starting Quizly Application..."
echo "=================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Pick a Python interpreter that the pinned dependencies support.
# The pinned requirements (pydantic-core, etc.) do not yet ship wheels for
# very new Python versions, so prefer a known-good interpreter when creating
# the virtual environment.
select_python() {
    for candidate in python3.12 python3.11 python3.10 python3; do
        if command -v "$candidate" &> /dev/null; then
            echo "$candidate"
            return 0
        fi
    done
    return 1
}

# Ensure a Python virtual environment exists (create one if needed)
if [ ! -d ".venv" ]; then
    PYTHON_BIN="$(select_python)"
    echo "🐍 No virtual environment found. Creating one at .venv using $PYTHON_BIN..."
    if ! "$PYTHON_BIN" -m venv .venv; then
        echo "❌ Failed to create Python virtual environment."
        exit 1
    fi
    echo "✅ Virtual environment created."
fi

# Activate the virtual environment
echo "🐍 Activating virtual environment..."
# shellcheck disable=SC1091
source .venv/bin/activate

# Verify the application is running inside a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Failed to activate the virtual environment. The application must not run outside a virtual env."
    exit 1
fi
echo "✅ Using virtual environment: $VIRTUAL_ENV"

# Check for required Python packages
echo "🔍 Checking Python dependencies..."
cd backend
if ! python -c "import dotenv" &> /dev/null; then
    echo "📦 Installing required Python packages..."
    python -m pip install -r requirements.txt || python -m pip install python-dotenv fastapi uvicorn sqlalchemy
fi
cd ..

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed."
    exit 1
fi

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check if backend port is already in use
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use. Trying to stop existing backend..."
    pkill -f "python.*main.py" 2>/dev/null || true
    sleep 2
fi

# Check if frontend port is already in use
if check_port 3000; then
    echo "⚠️  Port 3000 is already in use. Trying to stop existing frontend..."
    pkill -f "react-scripts.*start" 2>/dev/null || true
    pkill -f "node.*start" 2>/dev/null || true
    sleep 2
fi

# Start backend server
echo "🚀 Starting FastAPI backend on http://localhost:8000..."
cd backend
python main.py > ../backend_log.txt 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start (up to 20s)
BACKEND_TIMEOUT=20
BACKEND_WAITED=0
while ! check_port 8000; do
    sleep 1
    BACKEND_WAITED=$((BACKEND_WAITED+1))
    if [ $BACKEND_WAITED -ge $BACKEND_TIMEOUT ]; then
        echo "❌ Backend failed to start after $BACKEND_TIMEOUT seconds."
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    echo "⏳ Waiting for backend to start... ($BACKEND_WAITED s)"
done

# Check if backend started successfully
if check_port 8000; then
    echo "✅ Backend server started successfully!"
else
    echo "❌ Failed to start backend server"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Start frontend server
echo "🌐 Starting React frontend on http://localhost:3000..."
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

npm start &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start (up to 30s)
FRONTEND_TIMEOUT=30
FRONTEND_WAITED=0
while ! check_port 3000; do
    sleep 1
    FRONTEND_WAITED=$((FRONTEND_WAITED+1))
    if [ $FRONTEND_WAITED -ge $FRONTEND_TIMEOUT ]; then
        echo "❌ Frontend failed to start after $FRONTEND_TIMEOUT seconds."
        kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
        exit 1
    fi
    echo "⏳ Waiting for frontend to start... ($FRONTEND_WAITED s)"
done

# Check if frontend started successfully
if check_port 3000; then
    echo "✅ Frontend server started successfully!"
else
    echo "❌ Failed to start frontend server"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "🎉 Quizly is now running!"
echo "=================================="
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    echo "✅ Servers stopped. Goodbye!"
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Wait for user to stop
wait