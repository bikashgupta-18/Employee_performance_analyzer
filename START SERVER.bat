@echo off
REM ============================================================
REM  EMPLOYEE PERFORMANCE ANALYZER - START SERVER
REM  Double-click this file to start the TCP server.
REM  It automatically switches to the correct folder first.
REM ============================================================
cd /d "%~dp0"

set "PY=C:\Users\DELL\AppData\Local\Programs\Python\Python313\python.exe"
if not exist "%PY%" set "PY=python"

echo ============================================================
echo  EMPLOYEE PERFORMANCE ANALYZER - SERVER
echo  Folder: %CD%
echo  Keep this window open. Press Ctrl+C to stop the server.
echo ============================================================
"%PY%" -u server.py
pause
