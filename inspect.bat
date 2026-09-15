@echo off
REM Tifis-ID Domain Inspector Launcher
setlocal
cd /d "%~dp0"

if "%~1"=="" (
    set /p TARGET_URL="Masukkan URL/Domain yang ingin diuji (misal: klikbca-promo.id): "
) else (
    set TARGET_URL=%~1
)

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" scripts\inspect_domain.py "%TARGET_URL%"
) else (
    python scripts\inspect_domain.py "%TARGET_URL%"
)

pause
