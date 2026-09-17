@echo off
REM PeDaS 2026 - Launcher: Evaluate All Alternatives (Benchmark Suite)
REM Jalankan dari folder repo manapun, otomatis pakai .venv jika ada.

cd /d "%~dp0"

IF EXIST ".venv\Scripts\python.exe" (
    echo [INFO] Menggunakan virtual environment: .venv
    ".venv\Scripts\python.exe" scripts\alternatives\evaluate_alternatives.py %*
) ELSE (
    echo [INFO] .venv tidak ditemukan, menggunakan Python sistem
    python scripts\alternatives\evaluate_alternatives.py %*
)
pause
