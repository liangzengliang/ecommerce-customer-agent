"""
知识库服务
封装知识库的增查业务逻辑。
"""

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.knowledge import Knowledge

class KnowledgeService:
    """知识库服务类"""

    async def list_all(self, category: str | None = None) -> list:
        """
        列出知识库条目
        参数：category - 分类过滤（可选）
        返回：知识字典列表
        """
        async with AsyncSessionLocal() as db:
            stmt = select(Knowledge).where(Knowledge.is_active == True)
            if category:
                stmt = stmt.where(Knowledge.category == category)
            result = await db.execute(stmt)
            return [
                {"id": k.id, "category": k.category, "question": k.question,
                 "answer": k.answer, "vector_id": k.vector_id}
                for k in result.scalars().all()
            ]

    async def create(self, category: str, question: str, answer: str) -> dict:
        """
        创建一条知识
        参数：category - 分类
              question - 问题
              answer - 答案
        返回：新建知识的字典
        """
        async with AsyncSessionLocal() as db:
            k = Knowledge(category=category, question=question, answer=answer)
            db.add(k)
            await db.commit()
            await db.refresh(k)
            return {"id": k.id, "question": k.question}

knowledge_service = KnowledgeService()