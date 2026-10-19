"""
知识向量化任务
将 MySQL 中的知识条目向量化后写入 Milvus。
"""

import asyncio
from sqlalchemy import select
from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.models.knowledge import Knowledge
from app.rag.vector_store import vector_store_manager
import logging

logger = logging.getLogger(__name__)

async def _do_vectorize(knowledge_id: int | None = None):
    """
    实际执行向量化的异步函数
    参数：knowledge_id - 指定知识ID则只向量化该条，为 None 则处理所有未向量化的
    返回：处理条数
    """
    async with AsyncSessionLocal() as db:
        stmt = select(Knowledge).where(Knowledge.is_active == True)
        if knowledge_id:
            stmt = stmt.where(Knowledge.id == knowledge_id)
        else:
            # 只处理还没有 vector_id 的条目
            stmt = stmt.where(Knowledge.vector_id.is_(None))

        result = await db.execute(stmt)
        items = result.scalars().all()

        if not items:
            logger.info("没有需要向量化的知识条目")
            return 0

        # 批量写入 Milvus
        texts = [f"{item.question}\n{item.answer}" for item in items]
        metadatas = [
            {"knowledge_id": item.id, "category": item.category}
            for item in items
        ]
        ids = vector_store_manager.add_texts(texts, metadatas)

        # 回写 vector_id 到 MySQL
        for item, vid in zip(items, ids):
            item.vector_id = str(vid)
        await db.commit()

        logger.info(f"向量化完成，共处理 {len(items)} 条")
        return len(items)

@celery_app.task(name="tasks.vectorize_knowledge", bind=True)
def vectorize_knowledge(self, knowledge_id: int | None = None):
    """
    Celery 任务入口：向量化知识库条目
    参数：knowledge_id - 指定知识ID则只处理该条，为空则处理所有未向量化的
    返回：处理条数
    """
    logger.info(f"[Task {self.request.id}] 开始向量化 knowledge_id={knowledge_id}")
    try:
        count = asyncio.run(_do_vectorize(knowledge_id))
        return {"success": True, "count": count}
    except Exception as e:
        logger.error(f"向量化任务失败: {e}", exc_info=True)
        return {"success": False, "error": str(e)}