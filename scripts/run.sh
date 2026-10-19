#!/bin/bash
# ============================================================
# 一键启动脚本
# 用法：
#   bash scripts/run.sh backend    # 只启动后端
#   bash scripts/run.sh frontend   # 只启动前端
#   bash scripts/run.sh all        # 同时启动前后端
# ============================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ============ 启动后端 ============
start_backend() {
    log_info "启动后端..."
    cd "${BACKEND_DIR}"
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate

    uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload
}

# ============ 启动前端 ============
start_frontend() {
    log_info "启动前端..."
    cd "${FRONTEND_DIR}"
    npm run dev
}

# ============ 同时启动 ============
start_all() {
    log_info "同时启动前后端..."

    # 后端放后台，日志写文件
    cd "${BACKEND_DIR}"
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload \
        > "${PROJECT_ROOT}/logs/backend.log" 2>&1 &
    BACKEND_PID=$!
    log_info "后端已启动，PID=${BACKEND_PID}，日志：logs/backend.log"

    # 前端放后台
    cd "${FRONTEND_DIR}"
    npm run dev > "${PROJECT_ROOT}/logs/frontend.log" 2>&1 &
    FRONTEND_PID=$!
    log_info "前端已启动，PID=${FRONTEND_PID}，日志：logs/frontend.log"

    log_info "按 Ctrl+C 停止所有服务"

    # 捕获退出信号，关闭子进程
    trap "kill ${BACKEND_PID} ${FRONTEND_PID} 2>/dev/null; exit 0" INT TERM
    wait
}

# ============ 主入口 ============
case "$1" in
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    all)
        start_all
        ;;
    *)
        echo "用法：$0 {backend|frontend|all}"
        exit 1
        ;;
esac