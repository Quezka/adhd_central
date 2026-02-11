@echo off
REM Complete build script for ADHD Central with Installer
REM This script builds both the executable and the Windows installer

echo ========================================
echo   ADHD Central - Complete Build
echo ========================================
echo.
echo This script will:
echo   1. Build the executable
echo   2. Create the Windows installer
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
echo.

REM Run PyInstaller
echo ========================================
echo   Step 1: Building Executable
echo ========================================
echo.
pyinstaller adhd_central.spec --distpath dist --workpath build

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo   Build Failed!
    echo ========================================
    echo.
    pause
    exit /b 1
)

echo.
echo Executable built successfully!
echo.

REM Check if NSIS is installed
echo ========================================
echo   Step 2: Creating Windows Installer
echo ========================================
echo.

set NSIS_PATH="C:\Program Files (x86)\NSIS\makensis.exe"

if not exist "%NSIS_PATH%" (
    echo NSIS not found at: %NSIS_PATH%
    echo.
    echo Please install NSIS from: https://nsis.sourceforge.io/Download
    echo.
    pause
    exit /b 1
)

REM Build the installer
echo Building Windows installer...
"%NSIS_PATH%" installer.nsi

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo   Installer Build Failed!
    echo ========================================
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Build Complete!
echo ========================================
echo.
echo Files created:
echo   1. Executable:
echo      dist\ADHD Central\ADHD Central.exe
echo.
echo   2. Windows Installer:
echo      dist\ADHD Central Installer.exe (Ready to distribute!)
echo.
echo Next Steps:
echo   - Test the executable: dist\ADHD Central\ADHD Central.exe
echo   - Distribute the installer: dist\ADHD Central Installer.exe
echo.

pause
