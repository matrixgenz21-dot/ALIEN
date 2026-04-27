@echo off
echo =======================================
echo   HMS - Hospital Management System
echo   Matrix Tech Solutions, Lahore
echo =======================================
echo.
echo Installing dependencies...
pip install matplotlib openpyxl >nul 2>&1
echo.
echo Loading demo data...
python demo_data.py
echo.
echo Starting HMS...
python hospital_mgmt.py
pause
