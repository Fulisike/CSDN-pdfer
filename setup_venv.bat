@echo off
chcp 65001 >nul
echo ========================================
echo CSDN PDFer - Virtual Environment Setup
echo ========================================
echo.

IF EXIST venv (
    echo Removing old virtual environment...
    rmdir /s /q venv
)

echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat

echo.
echo Installing project dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Usage:
echo 1. Activate: venv\Scripts\activate.bat
echo 2. Run GUI: python gui_main.py
echo 3. Build EXE: build_exe_simple.bat
echo.

pause
