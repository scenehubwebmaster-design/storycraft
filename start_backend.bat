@echo off
echo Starting StoryCraft Backend Server...
echo.
cd /d "%~dp0backend"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
