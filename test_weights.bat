@echo off
REM PeDaS 2026 - Tifis-ID Weight Scanner Launcher
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" scripts\test_hybrid_cv.py
) else (
    python scripts\test_hybrid_cv.py
)

pause
