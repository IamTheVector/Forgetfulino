@echo off
REM Build standalone Forgetfulino Watcher app (Windows)
REM Run from anywhere; the script finds the library root.

set SCRIPT_DIR=%~dp0
set ROOT=%SCRIPT_DIR%..
cd /d "%ROOT%"

echo Building Forgetfulino Watcher...
pip install pyinstaller -q
pip install -r tools/requirements-watcher.txt -q

pyinstaller -y tools/forgetfulino_watcher.spec

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: App built at:
    echo   %ROOT%\dist\ForgetfulinoWatcher\ForgetfulinoWatcher.exe
    echo.
    start "" "%ROOT%\dist\ForgetfulinoWatcher"
) else (
    echo Build failed.
    exit /b 1
)
