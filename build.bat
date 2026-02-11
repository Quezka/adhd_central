@echo off
REM Build script for ADHD Central
REM This script creates a Windows executable using PyInstaller

echo ========================================
echo   ADHD Central - Professional Builder
echo ========================================
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Clean previous builds
echo Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
echo.

REM Run PyInstaller
echo Building ADHD Central executable...
echo This may take a few minutes...
echo.
pyinstaller adhd_central.spec --distpath dist --buildpath build

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   Build Successful!
    echo ========================================
    echo.
    echo Executable Location:
    echo   dist\ADHD Central\ADHD Central.exe
    echo.
    echo Next Steps:
    echo   1. Verify the executable works by running it
    echo   2. To create an installer, download NSIS from:
    echo      https://nsis.sourceforge.io/Download
    echo   3. Then run: makensis installer.nsi
    echo.
) else (
    echo.
    echo ========================================
    echo   Build Failed!
    echo ========================================
    echo.
    echo Please check for errors above.
    echo.
)

pause
