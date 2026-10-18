@echo off
REM ============================================================
REM  EMPLOYEE PERFORMANCE ANALYZER - RUN THE 3 TEST CASES
REM  Double-click to run Test Case 1, 2 and 3 one after another.
REM  No server needs to be running (Test Case 3 starts its own).
REM ============================================================
cd /d "%~dp0"

set "PY=C:\Users\DELL\AppData\Local\Programs\Python\Python313\python.exe"
if not exist "%PY%" set "PY=python"

echo ============================================================
echo  RUNNING ALL THREE TEST CASES (folder: %CD%)
echo ============================================================

echo.
echo ################ TEST CASE 1 ################
"%PY%" -u test_cases.py 1

echo.
echo ################ TEST CASE 2 ################
"%PY%" -u test_cases.py 2

echo.
echo ################ TEST CASE 3 ################
"%PY%" -u test_cases.py 3

echo.
echo ============================================================
echo  ALL TEST CASES FINISHED. Take your screenshots now, then
echo  press any key to close this window.
echo ============================================================
pause > nul
