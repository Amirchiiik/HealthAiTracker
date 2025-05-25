@echo off
REM AI Health Tracker - Development Starter (Windows)

echo Starting AI Health Tracker Development Environment...

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start both services with concurrently
concurrently --prefix "[{name}]" --names "BACKEND,FRONTEND" --prefix-colors "blue,green" --kill-others "cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" "cd frontend && npm start"

pause 