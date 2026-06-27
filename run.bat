@echo off
REM ============================================================
REM  CFA Level I Tutor - one-click launcher (Windows)
REM  Starts a local web server and opens the app in your browser.
REM ============================================================

cd /d "%~dp0"

REM --- Find a Python launcher ---
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)

if not defined PY (
    echo.
    echo Python was not found on this PC.
    echo Install it from https://www.python.org/downloads/ ^(tick "Add to PATH"^),
    echo then double-click run.bat again.
    echo.
    pause
    exit /b 1
)

REM --- Start the server in its own window (close that window to stop) ---
start "CFA Tutor Server (close to stop)" cmd /k "%PY% -m http.server 8000"

REM --- Give the server a moment, then open the browser ---
timeout /t 2 >nul
start "" http://localhost:8000

echo.
echo CFA Tutor is running at http://localhost:8000
echo A "CFA Tutor Server" window has opened - close it to stop the app.
echo If the page looks stale, press Ctrl+Shift+R to hard-refresh.
echo.
exit /b 0
