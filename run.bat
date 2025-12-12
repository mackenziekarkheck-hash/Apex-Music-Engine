@echo off
REM =============================================================================
REM APEX Engine - Startup Script (Windows)
REM =============================================================================
REM Usage:
REM   run.bat          - Start the web UI (default)
REM   run.bat --cli    - Run CLI mode  
REM   run.bat --demo   - Run demonstration mode
REM   run.bat --help   - Show all options
REM =============================================================================

setlocal EnableDelayedExpansion

cd /d "%~dp0"

echo.
echo ================================================================
echo     APEX Engine - Autonomous Aural Architectures
echo     for Algorithmic Rap Composition
echo ================================================================
echo.

REM Check for Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.11+
    echo Download from: https://python.org/downloads
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=*" %%i in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PYVER=%%i
echo [OK] Python %PYVER% detected

REM Check for virtual environment
if exist "venv\Scripts\activate.bat" (
    echo [OK] Virtual environment found
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo [OK] Virtual environment found
    call .venv\Scripts\activate.bat
) else (
    echo [INFO] No virtual environment found. Using system Python.
    echo [TIP] Create one with: python -m venv venv
)

REM Load .env file if it exists
if exist ".env" (
    echo [OK] Loading .env configuration
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        set "line=%%a"
        if not "!line:~0,1!"=="#" (
            if not "%%b"=="" (
                set "%%a=%%b"
            )
        )
    )
) else (
    echo [INFO] No .env file found
    if exist ".env.example" (
        echo [TIP] Copy .env.example to .env and add your API keys
    )
)

REM Check API keys
echo.
echo [Environment Check]
if defined FAL_KEY (
    echo   [OK] FAL_KEY configured
) else (
    echo   [!] FAL_KEY not set - audio generation disabled
)

if defined OPENAI_API_KEY (
    echo   [OK] OPENAI_API_KEY configured
) else (
    echo   [!] OPENAI_API_KEY not set - using simulation mode
)
echo.

REM Check dependencies
echo [Checking Dependencies]
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo   [!] Some dependencies missing
    echo.
    set /p INSTALL="Install dependencies now? (y/n): "
    if /i "!INSTALL!"=="y" (
        pip install -r requirements.txt
    ) else (
        echo [ERROR] Cannot continue without dependencies
        pause
        exit /b 1
    )
) else (
    echo   [OK] Core dependencies installed
)
echo.

REM Parse command line arguments
set MODE=web
if "%1"=="--cli" set MODE=cli
if "%1"=="-c" set MODE=cli
if "%1"=="--demo" set MODE=demo
if "%1"=="-d" set MODE=demo
if "%1"=="--help" set MODE=help
if "%1"=="-h" set MODE=help
if "%1"=="--check" set MODE=check

if "%MODE%"=="help" (
    echo APEX Engine - Startup Options
    echo.
    echo Usage: run.bat [option]
    echo.
    echo Options:
    echo   (default)     Start the web UI on http://localhost:5000
    echo   --cli, -c     Start interactive CLI mode
    echo   --demo, -d    Run demonstration mode
    echo   --check       Check environment only
    echo   --help, -h    Show this help message
    echo.
    echo Environment Variables:
    echo   FAL_KEY           Sonauto API key for audio generation
    echo   OPENAI_API_KEY    OpenAI API key for GPT-4o
    echo   PORT              Server port (default: 5000)
    echo.
    pause
    exit /b 0
)

if "%MODE%"=="check" (
    echo [OK] Environment check complete
    pause
    exit /b 0
)

if "%MODE%"=="cli" (
    echo Starting APEX Engine CLI...
    echo.
    python apex_engine\main.py --interactive
    pause
    exit /b 0
)

if "%MODE%"=="demo" (
    echo Running APEX Engine Demo...
    echo.
    python apex_engine\main.py --demo
    pause
    exit /b 0
)

REM Default: Start web UI
if not defined PORT set PORT=5000
echo Starting APEX Engine Web UI...
echo   URL: http://localhost:%PORT%
echo   Press Ctrl+C to stop
echo.
cd apex_engine
python -m web.app

pause
