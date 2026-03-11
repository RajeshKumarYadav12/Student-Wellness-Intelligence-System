#!/usr/bin/env pwsh
# AURA Local Development Runner
# Run this script to start both backend and frontend

Write-Host "🚀 Starting AURA Development Environment..." -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "Run: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# Check if node_modules exists
if (-not (Test-Path "frontend/node_modules")) {
    Write-Host "❌ Frontend dependencies not installed!" -ForegroundColor Red
    Write-Host "Run: cd frontend && npm install" -ForegroundColor Yellow
    exit 1
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found! Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Please edit .env with your MongoDB URI and secrets" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Starting Backend API..." -ForegroundColor Green
Write-Host "URL: http://localhost:8000" -ForegroundColor Gray
Write-Host "Docs: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""

# Start backend in new terminal
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "& { cd '$PWD\backend'; & '..\\.venv\Scripts\Activate.ps1'; uvicorn main:app --reload --host 0.0.0.0 --port 8000 }"

# Wait 3 seconds for backend to start
Start-Sleep -Seconds 3

Write-Host "Starting Frontend Dashboard..." -ForegroundColor Green
Write-Host "URL: http://localhost:3000" -ForegroundColor Gray
Write-Host ""

# Start frontend in new terminal
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "& { cd '$PWD\frontend'; npm start }"

Write-Host "✅ AURA Development Environment Started!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in each terminal to stop" -ForegroundColor Yellow
