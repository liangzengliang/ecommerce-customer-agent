"""
数据分析接口
提供看板统计数据：会话量、意图分布、情感分布、满意度等。
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.session import Session as SessionModel
from app.models.message import Message
from app.models.ticket import Ticket
from app.models.rating import ConversationRating

router = APIRouter()

@router.get("/overview")
async def overview(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    总览统计：会话总数、消息总数、工单总数、平均评分
    返回：统计字典
    """
    session_count = (await db.execute(select(func.count(SessionModel.id)))).scalar() or 0
    message_count = (await db.execute(select(func.count(Message.id)))).scalar() or 0
    ticket_count = (await db.execute(select(func.count(Ticket.id)))).scalar() or 0
    avg_score = (await db.execute(select(func.avg(ConversationRating.rating_score)))).scalar()

    return {
        "session_count": session_count,
        "message_count": message_count,
        "ticket_count": ticket_count,
        "avg_rating": float(avg_score) if avg_score else None,
    }

@router.get("/sentiment")
async def sentiment_distribution(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    情感分布统计
    返回：{positive: n, neutral: n, negative: n}
    """
    stmt = select(Message.sentiment, func.count(Message.id)).group_by(Message.sentiment)
    result = await db.execute(stmt)
    return {row[0] or "unknown": row[1] for row in result.all()}

@router.get("/intents")
async def intent_distribution(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    意图分布统计（按 intent_id 分组）
    返回：意图ID → 消息数
    """
    stmt = select(Message.intent_id, func.count(Message.id)).group_by(Message.intent_id)
    result = await db.execute(stmt)
    return {str(row[0]) if row[0] else "unknown": row[1] for row in result.all()}

@router.get("/sessions/recent")
async def recent_sessions(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    最近的会话列表
    参数：limit - 返回条数
    返回：会话列表
    """
    stmt = select(SessionModel).order_by(SessionModel.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    return [
        {
            "session_id": s.session_id,
            "user_id": s.user_id,
            "status": s.status,
            "message_count": s.message_count,
            "created_at": s.created_at,
        }
        for s in sessions
    ]