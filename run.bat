@echo off
chcp 65001 >nul
echo ========================================
echo CSDN PDFer - Launching GUI
echo ========================================
echo.

IF NOT EXIST venv (
    echo Virtual environment not found, creating...
    call setup_venv.bat
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Launching GUI application...
python gui_main.py

pause
