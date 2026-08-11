@echo off
cd /d "%~dp0"
".venv\Scripts\python.exe" scripts\run_pipeline.py
pause
