"""
检索器模块
"""

from app.rag.vector_store import vector_store_manager
from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.models.knowledge import Knowledge
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)


class Retriever:
    """RAG 检索器"""

    def __init__(self, k: int = 10):
        self.k = k

    def retrieve(self, query: str) -> list:
        """向量检索（top_k=10）"""
        # 演示模式：跳过向量检索，直接返回空（走数据库兜底）
        if settings.DEMO_MODE:
            return []
        try:
            docs = vector_store_manager.similarity_search(query, k=self.k)
            result = [
                {"content": d.page_content, "metadata": d.metadata}
                for d in docs
            ]
            if result:
                return result
        except Exception as e:
            logger.error(f"RAG 向量检索失败: {e}")

        # 向量检索失败或空结果，返回空
        return []

    async def retrieve_with_db_fallback(self, query: str) -> str:
        """向量检索 + 数据库关键词兜底"""
        docs = self.retrieve(query)

        if docs:
            return self._format(docs)

        # 兜底：数据库关键词匹配
        try:
            async with AsyncSessionLocal() as db:
                stmt = (
                    select(Knowledge)
                    .where(Knowledge.is_active == True)
                    .where(
                        Knowledge.question.like(f"%{query[:10]}%")
                        | Knowledge.answer.like(f"%{query[:10]}%")
                    )
                    .limit(5)
                )
                result = await db.execute(stmt)
                items = result.scalars().all()
                if items:
                    return "\n\n".join([
                        f"【知识】Q: {k.question}\nA: {k.answer}"
                        for k in items
                    ])
        except Exception as e:
            logger.error(f"DB 兜底检索失败: {e}")

        return ""

    def retrieve_as_context(self, query: str) -> str:
        """同步版：只走向量检索"""
        docs = self.retrieve(query)
        if not docs:
            return ""
        return self._format(docs)

    def _format(self, docs: list) -> str:
        return "\n\n".join([
            f"【知识{i+1}】{d['content']}"
            for i, d in enumerate(docs)
        ])