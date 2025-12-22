@echo off
cd backend
set PYTHONPATH=%~dp0backend
start "Backend API" cmd /k "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3
cd ..\frontend
start "Frontend React" cmd /k "npm run dev"
