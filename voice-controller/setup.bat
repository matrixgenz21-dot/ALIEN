@echo off
echo ========================================
echo   VOICE CONTROLLER - SETUP
echo   Sab kuch install ho raha hai...
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python nahi mila!
    echo Python install karo: https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Install karte waqt "Add Python to PATH" checkbox check karo!
    echo.
    pause
    exit /b 1
)

echo [1/3] Python found!
python --version
echo.

echo [2/3] Installing required packages...
echo.
pip install SpeechRecognition pyautogui pyttsx3 pyperclip
echo.

echo [3/3] Installing PyAudio...
echo (Agar error aaye to neeche instructions follow karo)
echo.
pip install PyAudio
if errorlevel 1 (
    echo.
    echo [NOTE] PyAudio install nahi hua. Ye try karo:
    echo   pip install pipwin
    echo   pipwin install pyaudio
    echo.
    echo Ya download karo: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
    echo.
)

echo.
echo ========================================
echo   SETUP COMPLETE!
echo   Ab 'run.bat' double-click karo
echo   ya CMD mein type karo: python main.py
echo ========================================
echo.
pause
