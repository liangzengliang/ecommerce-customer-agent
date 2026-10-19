#!/bin/bash
# ============================================================
# 知识库导入脚本
# 用途：清空旧数据 + 全量导入 knowledge_base/ 下的所有知识文件
# 用法：bash scripts/init_knowledge.sh
# ============================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="${PROJECT_ROOT}/backend"

MYSQL_HOST="${MYSQL_HOST:-YOUR_MYSQL_HOST}"
MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_PASSWORD="${MYSQL_PASSWORD:-YOUR_DB_PASSWORD}"
MYSQL_DATABASE="${MYSQL_DATABASE:-customer_service}"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

cd "${BACKEND_DIR}"
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate

# 1. 清空 MySQL
log_info "清空 MySQL 知识表..."
mysql -h "${MYSQL_HOST}" -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" \
    "${MYSQL_DATABASE}" -e "DELETE FROM knowledge;"

# 2. 删除 Milvus 集合
log_info "删除 Milvus 集合..."
python -c "
from pymilvus import connections, utility
from app.core.config import settings
connections.connect(host=settings.MILVUS_HOST, port=str(settings.MILVUS_PORT))
name = settings.MILVUS_COLLECTION
if utility.has_collection(name):
    utility.drop_collection(name)
    print(f'已删除集合 {name}')
else:
    print('集合不存在')
"

# 3. 全量导入
log_info "开始导入知识库..."
python -m scripts.import_knowledge

# 4. 验证
log_info "验证导入结果..."
mysql -h "${MYSQL_HOST}" -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" \
    "${MYSQL_DATABASE}" -e "SELECT category, COUNT(*) AS total FROM knowledge GROUP BY category;"

log_info "知识库导入完成"