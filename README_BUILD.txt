@echo off
REM Quick guide to building ADHD Central
REM
REM This file explains the different build options.
REM Choose one of the scripts below:

echo.
echo ========================================
echo   ADHD Central - Build Guide
echo ========================================
echo.
echo Choose what you want to build:
echo.
echo [1] build.bat
echo     - Fast build of executable only
echo     - Creates: dist\ADHD Central\ADHD Central.exe
echo     - No installer, portable/standalone
echo     - Best for: Testing, portable distribution
echo.
echo [2] build-installer.bat (RECOMMENDED)
echo     - Full build with professional installer
echo     - Creates: ADHD Central.exe + Installer.exe
echo     - Auto-detects NSIS installation
echo     - Best for: Professional distribution to end users
echo.
echo [3] Manual installer (requires NSIS)
echo     - Use if build-installer.bat fails
echo     - Command: makensis installer.nsi
echo     - Requires NSIS to be installed
echo.
echo ========================================
echo.
echo For detailed instructions, see: BUILD_GUIDE.md
echo.
