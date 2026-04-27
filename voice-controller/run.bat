@echo off
echo ========================================
echo   VOICE CONTROLLER BOT
echo   Starting...
echo ========================================
echo.

cd /d "%~dp0"

python main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Kuch gadbad ho gayi!
    echo Pehle setup.bat run karo agar nahi kiya.
    echo.
)

pause
