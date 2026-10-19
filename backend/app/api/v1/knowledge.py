"""
知识库接口
提供知识库查询能力（管理端使用）。
"""

from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.services.knowledge_service import knowledge_service

router = APIRouter()

@router.get("/list")
async def list_knowledge(category: str | None = None, _=Depends(get_current_user)):
    """
    列出知识库条目
    参数：category - 分类过滤（可选）
          _ - 当前用户（仅用于认证）
    返回：dict，含 items / total
    """
    items = await knowledge_service.list_all(category)
    return {"items": items, "total": len(items)}