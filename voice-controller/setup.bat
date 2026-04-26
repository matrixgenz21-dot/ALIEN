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

echo [2/4] Installing required packages...
echo.
pip install SpeechRecognition pyautogui pyttsx3 pyperclip groq
echo.

echo [3/4] Installing PyAudio...
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
echo [4/4] Groq AI Setup...
echo.
echo Groq API key chahiye AI mode ke liye (FREE hai):
echo   1. Jao: https://console.groq.com/keys
echo   2. Sign up karo (Google se bhi ho jata hai)
echo   3. "Create API Key" click karo
echo   4. Key copy karo
echo   5. config.py kholke GROQ_API_KEY mein paste karo
echo.

echo ========================================
echo   SETUP COMPLETE!
echo   config.py mein GROQ_API_KEY set karo
echo   Phir 'run.bat' double-click karo
echo ========================================
echo.
pause
