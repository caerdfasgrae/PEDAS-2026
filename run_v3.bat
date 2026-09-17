@echo off
REM PeDaS 2026 - Launcher: Submisi 3 (Data-Centric & Adaptive Hedge)
REM Jalankan dari folder repo manapun, otomatis pakai .venv jika ada.

cd /d "%~dp0"

IF EXIST ".venv\Scripts\python.exe" (
    echo [INFO] Menggunakan virtual environment: .venv
    ".venv\Scripts\python.exe" scripts\alternatives\run_v3_adaptive_hedge.py %*
) ELSE (
    echo [INFO] .venv tidak ditemukan, menggunakan Python sistem
    python scripts\alternatives\run_v3_adaptive_hedge.py %*
)
pause
