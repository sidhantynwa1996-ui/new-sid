@echo off
REM ============================================================
REM  Live Stock Tracker - one-click launcher (Windows)
REM  Double-click this file to start the app and open it in
REM  your browser. Close the black window to stop the app.
REM ============================================================

REM Move into the folder this .bat lives in (works from anywhere)
cd /d "%~dp0"

title Live Stock Tracker (close this window to stop)

REM Make sure Node.js is available
where node >nul 2>nul
if errorlevel 1 (
  echo.
  echo  Node.js was not found. Install it from https://nodejs.org
  echo  then run this file again.
  echo.
  pause
  exit /b 1
)

REM Open the browser a couple seconds after the server starts
start "" cmd /c "timeout /t 2 >nul & start http://localhost:3000"

echo.
echo  Starting Live Stock Tracker...
echo  Your browser will open at http://localhost:3000
echo  Keep this window open while using the app.
echo  Press Ctrl+C or close this window to stop.
echo.

node server.js

pause
