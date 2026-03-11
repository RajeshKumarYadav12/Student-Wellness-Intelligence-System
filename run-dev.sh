#!/bin/bash
# AURA Local Development Runner (macOS/Linux)
# Run this script to start both backend and frontend

echo "🚀 Starting AURA Development Environment..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run: python -m venv .venv"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Frontend dependencies not installed!"
    echo "Run: cd frontend && npm install"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found! Creating from template..."
    cp .env.example .env
    echo "✅ Please edit .env with your MongoDB URI and secrets"
    echo ""
fi

echo "Starting Backend API..."
echo "URL: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
echo ""

# Start backend in background
cd backend
source ../.venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait 3 seconds for backend to start
sleep 3

echo "Starting Frontend Dashboard..."
echo "URL: http://localhost:3000"
echo ""

# Start frontend in background
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ AURA Development Environment Started!"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Trap Ctrl+C and kill both processes
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Wait for both processes
wait
