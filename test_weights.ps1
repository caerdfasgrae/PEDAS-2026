# PeDaS 2026 - Tifis-ID Weight Scanner PowerShell Launcher
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$VenvPy = Join-Path $ScriptDir ".venv\Scripts\python.exe"
if (Test-Path $VenvPy) {
    & $VenvPy "scripts\test_hybrid_cv.py"
} else {
    python "scripts\test_hybrid_cv.py"
}
