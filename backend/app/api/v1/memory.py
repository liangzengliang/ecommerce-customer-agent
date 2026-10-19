"""
记忆库接口
基于 messages 表，提供"对话记忆"的查询、删除、统计
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.message import Message

router = APIRouter()


@router.get("/list")
async def list_memory(
    title: Optional[str] = None,
    type: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    分页查询记忆列表（基于 messages 表）
    参数：title - 标题模糊匹配
          type - 类型过滤（暂用 sender_type）
          page / size - 分页
    """
    # 基础查询
    stmt = select(Message).order_by(Message.id.desc())
    count_stmt = select(func.count(Message.id))

    if title:
        stmt = stmt.where(Message.content.like(f"%{title}%"))
        count_stmt = count_stmt.where(Message.content.like(f"%{title}%"))

    if type:
        stmt = stmt.where(Message.sender_type == type)
        count_stmt = count_stmt.where(Message.sender_type == type)

    # 总数
    total = (await db.execute(count_stmt)).scalar() or 0

    # 分页
    stmt = stmt.offset((page - 1) * size).limit(size)
    result = await db.execute(stmt)
    items = result.scalars().all()

    return {
        "items": [
            {
                "id": m.id,
                "title": f"对话记忆：{m.content[:50]}" if m.content else "",
                "type": "对话",
                "tag": "对话",
                "source": f"message-{m.id}",
                "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else "",
            }
            for m in items
        ],
        "total": total,
        "page": page,
        "size": size,
    }


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """删除单条记忆"""
    result = await db.execute(select(Message).where(Message.id == memory_id))
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="记忆不存在")
    await db.delete(msg)
    await db.commit()
    return {"success": True, "message": "已删除"}


@router.post("/batch-delete")
async def batch_delete(
    ids: List[int],
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """批量删除记忆"""
    if not ids:
        raise HTTPException(status_code=400, detail="未选择记录")
    await db.execute(delete(Message).where(Message.id.in_(ids)))
    await db.commit()
    return {"success": True, "deleted": len(ids)}


@router.delete("/clear/all")
async def clear_all(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """清空所有记忆"""
    result = await db.execute(delete(Message))
    await db.commit()
    return {"success": True, "message": "已清空"}


@router.get("/stats")
async def memory_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """记忆统计"""
    total = (await db.execute(select(func.count(Message.id)))).scalar() or 0
    user_count = (await db.execute(
        select(func.count(Message.id)).where(Message.sender_type == "user")
    )).scalar() or 0
    bot_count = (await db.execute(
        select(func.count(Message.id)).where(Message.sender_type == "bot")
    )).scalar() or 0

    return {
        "total": total,
        "user_count": user_count,
        "bot_count": bot_count,
    }


@router.post("/semantic-search")
async def semantic_search(
    keyword: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """语义检索（当前用关键词匹配模拟，后续可接入 Milvus）"""
    stmt = select(Message).where(
        Message.content.like(f"%{keyword}%")
    ).order_by(Message.id.desc()).limit(limit)
    result = await db.execute(stmt)
    items = result.scalars().all()

    return {
        "keyword": keyword,
        "items": [
            {
                "id": m.id,
                "content": m.content,
                "sender_type": m.sender_type,
                "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else "",
            }
            for m in items
        ],
    }