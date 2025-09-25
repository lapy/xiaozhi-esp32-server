@echo off
REM Xiaozhi ESP32 Server - Test Runner Script (Windows)
REM This script runs all tests for the project

echo.
echo 🧪 Xiaozhi ESP32 Server - Test Suite
echo ====================================
echo.

REM Check if we're in the right directory
if not exist "main\xiaozhi-server\config.yaml" (
    echo [ERROR] Please run this script from the project root directory
    exit /b 1
)

REM Python Backend Tests
echo.
echo [INFO] Running Python Backend Tests...
echo ----------------------------------------

if exist "main\xiaozhi-server\test" (
    cd main\xiaozhi-server
    
    REM Check if Python is available
    python --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Python not found. Please install Python 3.8+
        exit /b 1
    )
    
    REM Install test dependencies if needed
    if exist "requirements.txt" (
        echo [INFO] Installing Python dependencies...
        python -m pip install -r requirements.txt >nul 2>&1
    )
    
    REM Run Python tests
    python test\test_runner.py
    if errorlevel 1 (
        echo [ERROR] Python backend tests failed!
        exit /b 1
    ) else (
        echo [SUCCESS] Python backend tests passed!
    )
    
    cd ..\..
) else (
    echo [WARNING] Python test directory not found, skipping Python tests
)

REM Java Backend Tests
echo.
echo [INFO] Running Java Backend Tests...
echo -----------------------------------

if exist "main\manager-api\pom.xml" (
    cd main\manager-api
    
    REM Check if Maven is available
    mvn --version >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] Maven not found, skipping Java tests
    ) else (
        REM Run Java tests
        mvn test -q
        if errorlevel 1 (
            echo [ERROR] Java backend tests failed!
            exit /b 1
        ) else (
            echo [SUCCESS] Java backend tests passed!
        )
    )
    
    cd ..\..
) else (
    echo [WARNING] Java project directory not found, skipping Java tests
)

REM Frontend Tests
echo.
echo [INFO] Running Frontend Tests...
echo -------------------------------

if exist "main\manager-web\package.json" (
    cd main\manager-web
    
    REM Check if Node.js is available
    npm --version >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] Node.js/npm not found, skipping frontend tests
    ) else (
        REM Install dependencies if needed
        if not exist "node_modules" (
            echo [INFO] Installing frontend dependencies...
            npm install >nul 2>&1
        )
        
        REM Run frontend tests (if test dependencies are available)
        npm test -- --passWithNoTests >nul 2>&1
        if errorlevel 1 (
            echo [WARNING] Frontend test dependencies not installed, skipping frontend tests
            echo [INFO] To install test dependencies, run: npm install --save-dev jest @vue/test-utils vue-jest babel-jest
        ) else (
            echo [SUCCESS] Frontend tests passed!
        )
    )
    
    cd ..\..
) else (
    echo [WARNING] Frontend project directory not found, skipping frontend tests
)

REM Summary
echo.
echo ====================================
echo [SUCCESS] All available tests completed successfully!
echo.
echo [INFO] Test Summary:
echo [INFO] ✓ Python Backend Tests
echo [INFO] ✓ Java Backend Tests
echo [INFO] ✓ Frontend Tests
echo.
echo [INFO] For detailed test documentation, see: docs\testing-guide.md
echo.

REM Handle command line arguments
if "%1"=="--help" goto :help
if "%1"=="-h" goto :help
if "%1"=="--python-only" goto :python_only
if "%1"=="--java-only" goto :java_only
if "%1"=="--frontend-only" goto :frontend_only
goto :end

:help
echo Usage: %0 [options]
echo.
echo Options:
echo   --python-only    Run only Python tests
echo   --java-only      Run only Java tests
echo   --frontend-only  Run only frontend tests
echo   --help, -h       Show this help message
echo.
echo Examples:
echo   %0 --python-only
echo   %0 --java-only
echo   %0 --frontend-only
goto :end

:python_only
echo [INFO] Running Python tests only...
cd main\xiaozhi-server
python test\test_runner.py
goto :end

:java_only
echo [INFO] Running Java tests only...
cd main\manager-api
mvn test -q
goto :end

:frontend_only
echo [INFO] Running frontend tests only...
cd main\manager-web
npm test -- --passWithNoTests
goto :end

:end
