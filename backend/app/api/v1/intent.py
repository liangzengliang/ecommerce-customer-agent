"""
意图接口
提供意图识别调试、意图配置的增删改查。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.demo_limit import check_demo_limit
from app.models.user import User
from app.models.intent import Intent
from app.schemas.intent import (
    IntentCreate, IntentUpdate, IntentResponse,
    IntentClassifyRequest, IntentClassifyResponse,
)
from app.services.intent_service import intent_service

router = APIRouter()

@router.post("/classify", response_model=IntentClassifyResponse)
async def classify_intent(
    request: IntentClassifyRequest,
    _: User = Depends(get_current_user),
):
    """
    意图识别调试接口
    参数：request.text - 待识别文本
    返回：意图编码、名称、置信度
    """
    result = await intent_service.classify(request.text)
    return IntentClassifyResponse(
        intent_code=result["intent_code"],
        intent_name=result["intent_name"],
        confidence=result["confidence"],
    )

@router.get("/list", response_model=List[IntentResponse])
async def list_intents(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    列出所有意图配置
    返回：意图列表
    """
    result = await db.execute(select(Intent).order_by(Intent.priority.desc()))
    return result.scalars().all()

@router.post("/create", response_model=IntentResponse)
async def create_intent(
    request: IntentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    创建意图
    参数：request - 意图信息
    返回：新建的意图
    """
    # 检查 intent_code 是否已存在
    exists = await db.execute(select(Intent).where(Intent.intent_code == request.intent_code))
    if exists.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="意图编码已存在")

    # 演示模式：数据上限校验
    if await check_demo_limit(db, Intent):
        raise HTTPException(status_code=400, detail="演示模式每类数据最多 10 条，已达到上限，无法继续新增。数据将在次日凌晨 12 点自动恢复。")

    intent = Intent(**request.model_dump())
    db.add(intent)
    await db.commit()
    await db.refresh(intent)
    return intent

@router.put("/{intent_id}", response_model=IntentResponse)
async def update_intent(
    intent_id: int,
    request: IntentUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    更新意图
    参数：intent_id - 意图ID
          request - 待更新的字段
    返回：更新后的意图
    """
    result = await db.execute(select(Intent).where(Intent.id == intent_id))
    intent = result.scalar_one_or_none()
    if not intent:
        raise HTTPException(status_code=404, detail="意图不存在")

    # 只更新传入的字段
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(intent, field, value)
    await db.commit()
    await db.refresh(intent)
    return intent

@router.delete("/{intent_id}")
async def delete_intent(
    intent_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    删除意图
    参数：intent_id - 意图ID
    返回：删除结果
    """
    result = await db.execute(select(Intent).where(Intent.id == intent_id))
    intent = result.scalar_one_or_none()
    if not intent:
        raise HTTPException(status_code=404, detail="意图不存在")
    await db.delete(intent)
    await db.commit()
    return {"success": True, "message": "已删除"}