#!/bin/bash
# ============================================================
# 一键安装脚本
# 用途：初始化后端 venv、安装依赖、初始化数据库
# 用法：bash scripts/setup.sh
# ============================================================

set -e  # 遇错退出

# ============ 配置 ============
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"
FRONTEND_DIR="${PROJECT_ROOT}/frontend"

MYSQL_HOST="${MYSQL_HOST:-YOUR_MYSQL_HOST}"
MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_PASSWORD="${MYSQL_PASSWORD:-YOUR_DB_PASSWORD}"
MYSQL_DATABASE="${MYSQL_DATABASE:-customer_service}"

# ============ 颜色 ============
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ============ 检查 Python ============
check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "未找到 python3，请先安装 Python 3.11+"
        exit 1
    fi
    PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    log_info "Python 版本：${PY_VERSION}"
}

# ============ 检查 Node ============
check_node() {
    if ! command -v node &> /dev/null; then
        log_warn "未找到 node，跳过前端依赖安装"
        return 1
    fi
    NODE_VERSION=$(node -v)
    log_info "Node 版本：${NODE_VERSION}"
    return 0
}

# ============ 后端 venv ============
setup_backend() {
    log_info "开始配置后端..."
    cd "${BACKEND_DIR}"

    # 在 backend 下创建 venv（规范位置）
    if [ ! -d "venv" ]; then
        log_info "创建虚拟环境 backend/venv"
        python3 -m venv venv
    else
        log_info "虚拟环境已存在，跳过创建"
    fi

    # 激活
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate

    # 升级 pip
    pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

    # 装依赖
    log_info "安装 Python 依赖..."
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

    # 检查 .env
    if [ ! -f ".env" ]; then
        log_warn "backend/.env 不存在，从 .env.example 复制"
        cp .env.example .env
        log_warn "请编辑 backend/.env，填入实际配置后重新运行"
        exit 0
    fi

    log_info "后端配置完成"
}

# ============ 前端依赖 ============
setup_frontend() {
    if ! check_node; then
        return
    fi
    log_info "开始配置前端..."
    cd "${FRONTEND_DIR}"

    if [ ! -d "node_modules" ]; then
        log_info "安装 npm 依赖..."
        npm config set registry https://registry.npmmirror.com
        npm install
    else
        log_info "node_modules 已存在，跳过安装"
    fi

    log_info "前端配置完成"
}

# ============ 初始化数据库 ============
init_database() {
    log_info "检查数据库 ${MYSQL_DATABASE}..."

    # 创建数据库（如果不存在）
    mysql -h "${MYSQL_HOST}" -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" \
        -e "CREATE DATABASE IF NOT EXISTS ${MYSQL_DATABASE} DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;" \
        2>/dev/null && log_info "数据库已就绪" || {
        log_warn "无法连接 MySQL，跳过数据库初始化"
        return
    }

    # 建表
    if [ -f "${PROJECT_ROOT}/schema.sql" ]; then
        log_info "执行建表脚本..."
        mysql -h "${MYSQL_HOST}" -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" \
            "${MYSQL_DATABASE}" < "${PROJECT_ROOT}/schema.sql"
        log_info "建表完成"
    else
        log_warn "schema.sql 不存在，跳过建表"
    fi
}

# ============ 初始化数据 ============
init_data() {
    log_info "初始化基础数据..."
    cd "${BACKEND_DIR}"
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate

    python -m scripts.init_db || log_warn "init_db 执行失败，可稍后手动执行"
}

# ============ 主流程 ============
main() {
    log_info "========== 开始安装 =========="
    check_python
    setup_backend
    setup_frontend
    init_database
    init_data
    log_info "========== 安装完成 =========="
    log_info "启动后端：bash scripts/run.sh backend"
    log_info "启动前端：bash scripts/run.sh frontend"
}

main