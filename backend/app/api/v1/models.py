"""
模型配置接口
提供增删改查、设为默认、启用/停用、测试连通性
"""

import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.demo_limit import check_demo_limit
from app.models.user import User
from app.models.model_config import ModelConfig
from app.schemas.model_config import (
    ModelConfigCreate, ModelConfigUpdate, ModelConfigResponse,
)

router = APIRouter()


class TestModelRequest(BaseModel):
    name: str = ""
    provider: str = ""
    type: str
    model: str
    base_url: str
    api_key: str
    temperature: float = 0.3
    max_tokens: int = 100


class ToggleRequest(BaseModel):
    is_active: bool


# ============ 测试连通性 ============
@router.post("/test")
async def test_model(
    request: TestModelRequest,
    _: User = Depends(get_current_user),
):
    start = time.time()
    try:
        if request.type == "chat":
            llm = ChatOpenAI(
                model=request.model,
                api_key=request.api_key,
                base_url=request.base_url,
                temperature=0,
                max_tokens=50,
                timeout=30,
            )
            resp = await llm.ainvoke("你好，请只回复：OK")
            elapsed = int((time.time() - start) * 1000)
            return {
                "success": True,
                "message": "连通正常",
                "response": (resp.content or "")[:100],
                "elapsed_ms": elapsed,
            }
        elif request.type == "embedding":
            emb = OpenAIEmbeddings(
                model=request.model,
                api_key=request.api_key,
                base_url=request.base_url,
                check_embedding_ctx_length=False,
            )
            vec = await emb.aembed_query("测试")
            elapsed = int((time.time() - start) * 1000)
            return {
                "success": True,
                "message": "连通正常",
                "dimension": len(vec),
                "elapsed_ms": elapsed,
            }
        else:
            raise HTTPException(status_code=400, detail="未知模型类型")
    except Exception as e:
        elapsed = int((time.time() - start) * 1000)
        return {
            "success": False,
            "message": f"测试失败：{str(e)[:200]}",
            "elapsed_ms": elapsed,
        }


# ============ 列表 ============
@router.get("/list", response_model=List[ModelConfigResponse])
async def list_models(
    type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    stmt = select(ModelConfig).order_by(
        ModelConfig.is_default.desc(),       # 默认的排前面
        ModelConfig.id.desc(),
    )
    if type:
        stmt = stmt.where(ModelConfig.type == type)
    result = await db.execute(stmt)
    return result.scalars().all()


# ============ 创建 ============
@router.post("/create", response_model=ModelConfigResponse)
async def create_model(
    request: ModelConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if request.is_default:
        await db.execute(
            update(ModelConfig)
            .where(ModelConfig.type == request.type)
            .values(is_default=False)
        )
    # 演示模式：数据上限校验
    if await check_demo_limit(db, ModelConfig):
        raise HTTPException(status_code=400, detail="演示模式每类数据最多 10 条，已达到上限，无法继续新增。数据将在次日凌晨 12 点自动恢复。")

    data = request.model_dump()
    data["is_active"] = True       # 新建时默认启用
    data["user_id"] = current_user.id
    model = ModelConfig(**data)
    db.add(model)
    await db.commit()
    await db.refresh(model)
    return model


# ============ 更新 ============
@router.put("/{model_id}", response_model=ModelConfigResponse)
async def update_model(
    model_id: int,
    request: ModelConfigUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(ModelConfig).where(ModelConfig.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="模型配置不存在")

    if request.is_default:
        await db.execute(
            update(ModelConfig)
            .where(ModelConfig.type == model.type, ModelConfig.id != model_id)
            .values(is_default=False)
        )

    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(model, field, value)
    await db.commit()
    await db.refresh(model)
    return model


# ============ 启用/停用 ============
@router.put("/{model_id}/toggle", response_model=ModelConfigResponse)
async def toggle_model(
    model_id: int,
    body: ToggleRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    启用或停用模型
    停用的模型不会被 Agent 使用（即使它是默认的）
    """
    result = await db.execute(select(ModelConfig).where(ModelConfig.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="模型配置不存在")

    model.is_active = body.is_active
    # 停用时同时取消默认
    if not body.is_active and model.is_default:
        model.is_default = False

    await db.commit()
    await db.refresh(model)
    return model


# ============ 删除 ============
@router.delete("/{model_id}")
async def delete_model(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(ModelConfig).where(ModelConfig.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    await db.delete(model)
    await db.commit()
    return {"success": True, "message": "已删除"}


# ============ 设为默认 ============
@router.post("/{model_id}/set-default", response_model=ModelConfigResponse)
async def set_default(
    model_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    result = await db.execute(select(ModelConfig).where(ModelConfig.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="模型配置不存在")

    if not model.is_active:
        raise HTTPException(status_code=400, detail="已停用的模型不能设为默认")

    await db.execute(
        update(ModelConfig)
        .where(ModelConfig.type == model.type)
        .values(is_default=False)
    )
    model.is_default = True
    await db.commit()
    await db.refresh(model)
    return model