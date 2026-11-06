@echo off
echo ========================================================
echo   Khoi dong RedLamp Web Demo (Chay tren CPU)
echo ========================================================
py -3.12 run_demo.py
if %ERRORLEVEL% NEQ 0 (
    python run_demo.py
)
pause

