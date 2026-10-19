"""
转人工工具
将会话状态更新为 transferred。
"""

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.session import Session

async def transfer_human(session_id: str) -> dict:
    """
    将会话转接给人工客服
    参数：session_id - 会话ID
    返回：dict，含 success / message
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Session).where(Session.session_id == session_id))
        session = result.scalar_one_or_none()
        if not session:
            return {"success": False, "message": "会话不存在"}
        session.status = "transferred"
        await db.commit()
        return {"success": True, "message": "已转接人工客服"}