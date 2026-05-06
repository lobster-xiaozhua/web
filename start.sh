#!/usr/bin/env bash
set -e

echo "========================================="
echo "  星穹书阁 v1.5.0 - 启动脚本"
echo "========================================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "⚠️  未找到 $1，正在检查替代方案..."
        return 1
    fi
    return 0
}

MODE="${1:-full}"

case "$MODE" in
  full)
    echo "🚀 完整模式启动 (Docker Compose)..."
    if check_command docker; then
      if docker compose version &> /dev/null 2>&1; then
        docker compose up -d --build
      elif check_command docker-compose; then
        docker-compose up -d --build
      else
        echo "❌ 未找到 docker compose 或 docker-compose"
        exit 1
      fi
      echo ""
      echo "✅ 所有服务已启动!"
      echo "   前端: http://localhost"
      echo "   后端API: http://localhost/api"
      echo "   Grafana: http://localhost:3000"
    else
      echo "❌ 未找到 Docker，请先安装 Docker"
      exit 1
    fi
    ;;

  dev)
    echo "🔧 开发模式启动 (本地运行)..."
    echo ""

    if check_command python3; then
      PYTHON=python3
    elif check_command python; then
      PYTHON=python
    else
      echo "❌ 未找到 Python"
      exit 1
    fi

    if [ ! -d "backend/.venv" ]; then
      echo "📦 创建 Python 虚拟环境..."
      $PYTHON -m venv backend/.venv
      source backend/.venv/bin/activate
      echo "📦 安装后端依赖..."
      pip install -r backend/requirements.txt
    else
      source backend/.venv/bin/activate
    fi

    mkdir -p books data

    echo "🐍 启动后端服务..."
    cd backend
    DATABASE_TYPE=sqlite uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd "$SCRIPT_DIR"

    if check_command node; then
      if [ ! -d "frontend/node_modules" ]; then
        echo "📦 安装前端依赖..."
        cd frontend && npm install && cd "$SCRIPT_DIR"
      fi
      echo "⚛️  启动前端开发服务器..."
      cd frontend && npm run dev &
      FRONTEND_PID=$!
      cd "$SCRIPT_DIR"
    else
      echo "⚠️  未找到 Node.js，跳过前端启动"
    fi

    echo ""
    echo "✅ 开发服务已启动!"
    echo "   后端: http://localhost:8000"
    echo "   前端: http://localhost:3001"
    echo "   API文档: http://localhost:8000/docs"
    echo ""
    echo "按 Ctrl+C 停止所有服务"

    cleanup() {
      echo ""
      echo "🛑 正在停止服务..."
      [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null
      [ -n "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null
      echo "✅ 服务已停止"
      exit 0
    }
    trap cleanup INT TERM

    wait
    ;;

  lite)
    echo "⚡ 精简模式启动 (仅后端 + SQLite)..."
    echo ""

    if check_command python3; then
      PYTHON=python3
    elif check_command python; then
      PYTHON=python
    else
      echo "❌ 未找到 Python"
      exit 1
    fi

    if [ ! -d "backend/.venv" ]; then
      $PYTHON -m venv backend/.venv
      source backend/.venv/bin/activate
      pip install -r backend/requirements.txt
    else
      source backend/.venv/bin/activate
    fi

    mkdir -p books data

    cd backend
    DATABASE_TYPE=sqlite BOOKS_DIR=../books DATA_DIR=../data \
      uvicorn app.main:app --host 0.0.0.0 --port 8000
    ;;

  stop)
    echo "🛑 停止所有服务..."
    if check_command docker; then
      if docker compose version &> /dev/null 2>&1; then
        docker compose down
      elif check_command docker-compose; then
        docker-compose down
      fi
    fi
    echo "✅ 服务已停止"
    ;;

  *)
    echo "用法: $0 {full|dev|lite|stop}"
    echo ""
    echo "  full  - Docker Compose 完整模式 (默认)"
    echo "  dev   - 本地开发模式 (后端+前端)"
    echo "  lite  - 精简模式 (仅后端+SQLite，零依赖)"
    echo "  stop  - 停止所有服务"
    ;;
esac
