@echo off
REM ============================================================
REM  EMPLOYEE PERFORMANCE ANALYZER - START CLIENT
REM  Double-click AFTER starting the server (START SERVER.bat).
REM  It automatically switches to the correct folder first.
REM ============================================================
cd /d "%~dp0"

set "PY=C:\Users\DELL\AppData\Local\Programs\Python\Python313\python.exe"
if not exist "%PY%" set "PY=python"

echo ============================================================
echo  EMPLOYEE PERFORMANCE ANALYZER - CLIENT
echo  Folder: %CD%
echo ============================================================
"%PY%" -u client.py
echo.
echo ============================================================
echo  Report generated. Take your screenshot now, then press
echo  any key to close this window.
echo ============================================================
pause > nul
