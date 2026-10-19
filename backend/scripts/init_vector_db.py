"""
初始化向量数据库脚本
功能：
1. 检查 Milvus 连接
2. 创建集合（如果不存在）
3. 打印集合信息

用法：
    cd backend
    python -m scripts.init_vector_db
"""

import asyncio
from pymilvus import connections, utility, Collection
from backend.app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_vector_db")

def check_milvus():
    """连接 Milvus 并打印状态"""
    logger.info(f"连接 Milvus: {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
    connections.connect(
        alias="default",
        host=settings.MILVUS_HOST,
        port=str(settings.MILVUS_PORT),
    )

    # 版本信息
    version = utility.get_server_version()
    logger.info(f"✅ Milvus 服务端版本：{version}")

    # 已有集合列表
    collections = utility.list_collections()
    logger.info(f"📋 已有集合：{collections}")

    # 检查目标集合
    name = settings.MILVUS_COLLECTION
    if utility.has_collection(name):
        col = Collection(name)
        logger.info(f"✅ 集合 '{name}' 已存在，行数：{col.num_entities}")
    else:
        logger.info(f"⚠️  集合 '{name}' 不存在，将在首次写入时自动创建")

def main():
    """脚本主入口"""
    logger.info("=== 开始检查向量数据库 ===")
    try:
        check_milvus()
        logger.info("=== 检查完成 ===")
    except Exception as e:
        logger.error(f"❌ 连接失败：{e}")
        logger.error("请确认 Milvus 已启动，且 .env 中 MILVUS_HOST / MILVUS_PORT 正确")

if __name__ == "__main__":
    main()