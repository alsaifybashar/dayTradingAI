#!/bin/bash
echo "Starting Day Trading AI System..."

# Function to kill processes on exit
cleanup() {
    echo "Shutting down..."
    kill $(jobs -p)
}
trap cleanup EXIT

# Start Backend
echo "Starting Backend on port 8000..."
source backend/venv/bin/activate
export PYTHONUNBUFFERED=1
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to be ready (simple sleep)
sleep 2

# Start Frontend
echo "Starting Frontend..."
cd frontend
npm run dev -- --host --clearScreen false &
FRONTEND_PID=$!

wait
