"""
会话列表接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy import select, desc, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.session import Session
from app.models.message import Message

router = APIRouter()


# ============ 请求体 ============
class RenameRequest(BaseModel):
    title: str


class PinRequest(BaseModel):
    pinned: bool


# ============ 工具函数 ============
def _build_title(content: str, max_len: int = 20) -> str:
    """从消息内容生成标题"""
    if not content:
        return "新会话"
    text = content.replace("\n", " ").strip()
    return text if len(text) <= max_len else text[:max_len] + "..."


# ============ 会话列表 ============
@router.get("/list")
async def list_sessions(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """列出最近 N 天的会话（置顶优先）"""
    since = datetime.now() - timedelta(days=days)

    stmt = (
        select(Session)
        .where(Session.user_id == current_user.id)
        .where(Session.created_at >= since)
        .where(Session.message_count > 0)          # 过滤空会话
        .order_by(
            desc(Session.is_pinned),               # 置顶优先
            desc(Session.updated_at),
            desc(Session.created_at),
        )
        .limit(50)
    )
    result = await db.execute(stmt)
    sessions = result.scalars().all()

    items = []
    for s in sessions:
        # 首条用户消息（作为默认标题）
        first_stmt = (
            select(Message)
            .where(Message.session_id == s.session_id, Message.sender_type == "user")
            .order_by(Message.created_at)
            .limit(1)
        )
        first_msg = (await db.execute(first_stmt)).scalar_one_or_none()

        # 最后一条消息（作为预览）
        last_stmt = (
            select(Message)
            .where(Message.session_id == s.session_id)
            .order_by(desc(Message.created_at))
            .limit(1)
        )
        last_msg = (await db.execute(last_stmt)).scalar_one_or_none()

        # 标题优先级：自定义 > 首条用户消息 > 默认
        if s.custom_title:
            title = s.custom_title
        elif first_msg and first_msg.content:
            title = _build_title(first_msg.content, max_len=16)
        else:
            title = "新会话"

        preview = _build_title(last_msg.content, max_len=24) if last_msg and last_msg.content else "点击开始对话"

        items.append({
            "session_id": s.session_id,
            "title": title,
            "preview": preview,
            "status": "active" if s.status in ("active", "bot") else "completed",
            "message_count": s.message_count or 0,
            "is_pinned": bool(s.is_pinned),
            "custom_title": s.custom_title,
            "created_at": s.created_at.strftime("%m-%d %H:%M") if s.created_at else "",
            "updated_at": (s.updated_at or s.created_at).strftime("%m-%d %H:%M")
                          if (s.updated_at or s.created_at) else "",
        })

    return {"items": items, "total": len(items)}


# ============ 历史消息 ============
@router.get("/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """拉取会话的所有历史消息"""
    s_stmt = select(Session).where(Session.session_id == session_id)
    session = (await db.execute(s_stmt)).scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问")

    msg_stmt = (
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at)
    )
    messages = (await db.execute(msg_stmt)).scalars().all()

    return {
        "session_id": session_id,
        "messages": [
            {
                "id": str(m.id),
                "role": "user" if m.sender_type == "user" else "bot",
                "content": m.content,
                "sentiment": m.sentiment,
                "created_at": m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else "",
            }
            for m in messages
        ],
    }


# ============ 重命名 ============
@router.put("/{session_id}/rename")
async def rename_session(
    session_id: str,
    body: RenameRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """重命名会话"""
    s_stmt = select(Session).where(Session.session_id == session_id)
    session = (await db.execute(s_stmt)).scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")

    title = (body.title or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="标题不能为空")
    if len(title) > 100:
        raise HTTPException(status_code=400, detail="标题过长")

    session.custom_title = title
    await db.commit()

    return {"success": True, "custom_title": title}


# ============ 置顶/取消置顶 ============
@router.put("/{session_id}/pin")
async def pin_session(
    session_id: str,
    body: PinRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """置顶或取消置顶"""
    s_stmt = select(Session).where(Session.session_id == session_id)
    session = (await db.execute(s_stmt)).scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")

    session.is_pinned = body.pinned
    await db.commit()

    return {"success": True, "is_pinned": body.pinned}


# ============ 删除 ============
@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除会话及其所有消息"""
    s_stmt = select(Session).where(Session.session_id == session_id)
    session = (await db.execute(s_stmt)).scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除")

    await db.execute(sql_delete(Message).where(Message.session_id == session_id))
    await db.delete(session)
    await db.commit()

    return {"success": True, "message": "已删除"}