@echo off
chcp 65001 >nul
echo ========================================
echo CSDN PDFer - Build with Dependencies
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
echo Cleaning old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Building executable...

pyinstaller --onefile --windowed --name "CSDN-PDFer" gui_main.py

if %ERRORLEVEL% NEQ 0 (
    echo ========================================
    echo Build Failed!
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo Copying wkhtmltopdf dependencies...
echo ========================================

set WKHTML_DIR=wkhtmltox-0.12.6-1.mxe-cross-win64\wkhtmltox\bin

if not exist "%WKHTML_DIR%\wkhtmltopdf.exe" (
    echo Warning: wkhtmltopdf.exe not found in %WKHTML_DIR%
    echo Please ensure wkhtmltopdf is in the correct location
    echo.
    echo You can manually copy wkhtmltopdf.exe and wkhtmltox.dll to dist folder
) else (
    echo Copying wkhtmltopdf.exe...
    copy "%WKHTML_DIR%\wkhtmltopdf.exe" "dist\"

    echo Copying wkhtmltox.dll...
    copy "%WKHTML_DIR%\wkhtmltox.dll" "dist\"

    echo.
    echo ========================================
    echo Build Complete!
    echo ========================================
    echo.
    echo Generated files in dist folder:
    echo - CSDN-PDFer.exe (main application)
    echo - wkhtmltopdf.exe (PDF engine)
    echo - wkhtmltox.dll (required library)
    echo.
    echo Distribution: Copy all 3 files to distribute
    echo.
)

pause
