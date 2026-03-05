@echo off
title FORGETFULINO WATCHER
color 0A
cls

echo ========================================
echo    FORGETFULINO WATCHER - SETUP
echo ========================================
echo.
echo This script starts the automatic monitoring
echo of your Arduino sketches.
echo.
pause

cls
echo [1/6] Searching for a valid Python installation...

set PYTHON_CMD=

REM Search for Python in AppData (preferred location)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
    echo Found Python 3.12 in AppData
) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe
    echo Found Python 3.11 in AppData
) else if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" (
    set PYTHON_CMD=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe
    echo Found Python 3.12 in Users
) else (
    echo Python not found in AppData.
    echo.
    echo Use the path that previously worked for you:
    echo C:\Users\Vector_len\AppData\Local\Programs\Python\Python312\python.exe
    echo.
    set /p PYTHON_CMD="Enter the full path to python.exe: "
)

if not exist "%PYTHON_CMD%" (
    echo ERROR: Python not found in the specified path!
    pause
    exit /b
)

echo Python OK: %PYTHON_CMD%
pause

cls
echo [2/6] Checking pip...
%PYTHON_CMD% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Pip not found. Using get-pip.py...
    
    REM Download get-pip.py
    powershell -Command "Invoke-WebRequest https://bootstrap.pypa.io/get-pip.py -OutFile %TEMP%\get-pip.py"
    
    if exist "%TEMP%\get-pip.py" (
        %PYTHON_CMD% "%TEMP%\get-pip.py"
    ) else (
        echo ERROR: Unable to download get-pip.py
        pause
        exit /b
    )
)
echo Pip OK
pause

cls
echo [3/6] Checking watchdog...
%PYTHON_CMD% -c "from watchdog.observers import Observer" 2>nul
if %errorlevel% neq 0 (
    echo Watchdog not found. Installing...
    %PYTHON_CMD% -m pip install watchdog --user
    if %errorlevel% neq 0 (
        echo ERROR: Unable to install watchdog
        pause
        exit /b
    )
    echo Watchdog installed successfully!
) else (
    echo Watchdog already installed
)
pause

cls
echo [4/6] Calculating sketch path...
set SKETCH_PATH=%~dp0..\..
echo Sketch folder: %SKETCH_PATH%

if not exist "%SKETCH_PATH%" (
    echo ERROR: Sketch folder not found!
    pause
    exit /b
)
echo OK
pause

cls
echo [5/6] Checking generator...
set GENERATOR=%~dp0tools\forgetfulino_generator.py
if not exist "%GENERATOR%" (
    echo ERROR: Generator not found!
    pause
    exit /b
)
echo OK
pause

cls
echo [6/6] Starting watcher...
echo.
echo ========================================
echo    FORGETFULINO WATCHER - RUNNING
echo ========================================
echo.
echo Monitored folder: %SKETCH_PATH%
echo.
echo You can now edit your sketches normally.
echo Every time you save, the .h file will be generated.
echo.
echo To stop, close this window or press Ctrl+C
echo.
echo ========================================
echo.

%PYTHON_CMD% "%~dp0tools\watch_auto.py" "%SKETCH_PATH%"

echo.
echo Watcher stopped.
pause