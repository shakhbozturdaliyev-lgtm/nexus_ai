@echo off
title NEXUS AI Launcher
echo ========================================================
echo       Starting NEXUS AI Customer Support Platform
echo ========================================================
cd /d "%~dp0\.."

echo [1/3] Starting FastAPI Backend on http://localhost:8000 ...
start "NEXUS AI - Backend API" cmd /k "set PYTHONPATH=. && backend\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"

echo [2/3] Starting React Admin Dashboard on http://localhost:5173 ...
start "NEXUS AI - Admin Dashboard" cmd /k "cd frontend && npm.cmd run dev -- --host 127.0.0.1 --port 5173"

echo [3/3] Starting Telegram Support Bot ...
start "NEXUS AI - Telegram Bot" cmd /k "set PYTHONPATH=. && backend\.venv\Scripts\python.exe -u scripts\run_bot.py"

echo ========================================================
echo All 3 services launched successfully!
echo Local Dashboard: http://localhost:5173
echo Public Website:  https://nexus-ai-sepia-two.vercel.app
echo ========================================================
pause
