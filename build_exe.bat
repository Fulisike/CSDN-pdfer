@echo off
chcp 65001 >nul
echo ========================================
echo CSDN PDFer - Advanced Build Script
echo ========================================
echo.

IF NOT EXIST venv (
    echo Error: Virtual environment not found!
    echo Please run setup_venv.bat first
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Building with PyInstaller...

pyinstaller --onefile ^
    --windowed ^
    --name "CSDN-PDFer" ^
    --add-data "main.py;." ^
    --hidden-import=requests ^
    --hidden-import=bs4 ^
    --hidden-import=markdownify ^
    --hidden-import=markdown ^
    --hidden-import=pdfkit ^
    --hidden-import=tkinter ^
    --collect-all pdfkit ^
    gui_main.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo ========================================
    echo Build Complete!
    echo ========================================
    echo.
    echo Executable: dist\CSDN-PDFer.exe
    echo.
    echo Note: Users must install wkhtmltopdf
    echo Download: https://wkhtmltopdf.org/downloads.html
    echo.
) else (
    echo ========================================
    echo Build Failed!
    echo ========================================
    echo.
)

pause
