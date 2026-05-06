@echo off
chcp 936 >nul 2>&1
title XingQiongShuGe v1.5.0
echo =========================================
echo   XingQiongShuGe v1.5.0
echo =========================================
echo.

if "%1"=="" goto usage
if "%1"=="dev" goto dev
if "%1"=="lite" goto lite
if "%1"=="full" goto full
if "%1"=="stop" goto stop
goto usage

:usage
echo Usage: start-lab.bat [mode]
echo.
echo   lite  - Backend only (SQLite, no Docker needed)
echo   dev   - Backend + Frontend (local dev servers)
echo   full  - All services (Docker Compose)
echo   stop  - Stop all Docker services
echo.
echo Example:
echo   start-lab.bat lite
echo   start-lab.bat dev
echo.
pause
exit /b 0

:check_python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.10+
    echo         https://www.python.org/downloads/
    goto fail
)
goto :eof

:check_node
where node >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found! Please install Node.js 18+
    echo         https://nodejs.org/
    goto fail
)
goto :eof

:check_docker
where docker >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker not found! Please install Docker Desktop
    echo         https://www.docker.com/products/docker-desktop
    goto fail
)
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running! Please start Docker Desktop first.
    goto fail
)
goto :eof

:setup_venv
if not exist backend\.venv (
    echo [INFO] Creating Python virtual environment...
    python -m venv backend\.venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        goto fail
    )
)
call backend\.venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    goto fail
)
if not exist backend\.venv\Lib\site-packages\uvicorn (
    echo [INFO] Installing Python dependencies (first run only)...
    pip install -r backend\requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install Python dependencies!
        goto fail
    )
)
goto :eof

:full
echo [FULL] Starting with Docker Compose...
call :check_docker
echo [INFO] Building and starting containers...
docker compose up -d --build
if errorlevel 1 (
    echo [ERROR] Docker Compose failed!
    goto fail
)
echo.
echo [OK] All services started!
echo     Frontend : http://localhost
echo     Backend  : http://localhost/api
echo     Grafana  : http://localhost:3000
echo.
echo Press any key to view logs, or close this window...
pause >nul
docker compose logs -f
goto end

:dev
echo [DEV] Starting development mode...
call :check_python
call :check_node
call :setup_venv
if not exist books mkdir books
if not exist data mkdir data

echo [INFO] Starting backend on port 8000...
start "XQSG-Backend" cmd /k "cd /d %~dp0backend && call ..\backend\.venv\Scripts\activate.bat && set DATABASE_TYPE=sqlite && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo [INFO] Waiting for backend to start (3s)...
timeout /t 3 /nobreak >nul

if exist frontend\node_modules (
    echo [INFO] Starting frontend dev server...
) else (
    echo [INFO] Installing frontend dependencies (first run only)...
    cd frontend
    call npm install
    if errorlevel 1 (
        echo [ERROR] npm install failed!
        goto fail
    )
    cd ..
)
cd frontend
start "XQSG-Frontend" cmd /k "npm run dev"
cd ..

echo.
echo [OK] Development services started!
echo     Backend  : http://localhost:8000
echo     Frontend : http://localhost:3001
echo     API Docs : http://localhost:8000/docs
echo.
echo Two new windows opened for backend and frontend.
echo Close them or press Ctrl+C in each to stop.
echo.
pause
goto end

:lite
echo [LITE] Starting backend only (SQLite)...
call :check_python
call :setup_venv
if not exist books mkdir books
if not exist data mkdir data

cd backend
set DATABASE_TYPE=sqlite
set BOOKS_DIR=../books
set DATA_DIR=../data
echo [INFO] Starting backend on port 8000...
echo [INFO] Press Ctrl+C to stop
echo.
uvicorn app.main:app --host 0.0.0.0 --port 8000
if errorlevel 1 (
    echo.
    echo [ERROR] Backend crashed! See error above.
    cd ..
    goto fail
)
cd ..
goto end

:stop
echo [STOP] Stopping all services...
docker compose down 2>nul
echo [OK] Docker services stopped.
echo.
pause
goto end

:fail
echo.
echo =========================================
echo   An error occurred. See above for details.
echo =========================================
echo.
pause
exit /b 1

:end
exit /b 0
