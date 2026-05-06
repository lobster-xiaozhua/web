@echo off
chcp 65001 >nul 2>&1
echo =========================================
echo   星穹书阁 v1.5.0 - 启动脚本
echo =========================================
echo.

if "%1"=="dev" goto dev
if "%1"=="lite" goto lite
if "%1"=="stop" goto stop
goto full

:full
echo 🚀 完整模式启动 (Docker Compose)...
docker compose up -d --build
echo.
echo ✅ 所有服务已启动!
echo    前端: http://localhost
echo    后端API: http://localhost/api
echo    Grafana: http://localhost:3000
goto end

:dev
echo 🔧 开发模式启动...
if not exist backend\.venv (
    echo 📦 创建 Python 虚拟环境...
    python -m venv backend\.venv
    call backend\.venv\Scripts\activate.bat
    pip install -r backend\requirements.txt
) else (
    call backend\.venv\Scripts\activate.bat
)
if not exist books mkdir books
if not exist data mkdir data

echo 🐍 启动后端服务...
cd backend
set DATABASE_TYPE=sqlite
start /b uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
cd ..

if exist frontend\node_modules (
    echo ⚛️  启动前端开发服务器...
    cd frontend
    start /b npm run dev
    cd ..
) else (
    echo 📦 安装前端依赖...
    cd frontend
    npm install
    start /b npm run dev
    cd ..
)

echo.
echo ✅ 开发服务已启动!
echo    后端: http://localhost:8000
echo    前端: http://localhost:3001
echo    API文档: http://localhost:8000/docs
goto end

:lite
echo ⚡ 精简模式启动 (仅后端 + SQLite)...
if not exist backend\.venv (
    python -m venv backend\.venv
    call backend\.venv\Scripts\activate.bat
    pip install -r backend\requirements.txt
) else (
    call backend\.venv\Scripts\activate.bat
)
if not exist books mkdir books
if not exist data mkdir data

cd backend
set DATABASE_TYPE=sqlite
set BOOKS_DIR=../books
set DATA_DIR=../data
uvicorn app.main:app --host 0.0.0.0 --port 8000
goto end

:stop
echo 🛑 停止所有服务...
docker compose down
echo ✅ 服务已停止
goto end

:end
