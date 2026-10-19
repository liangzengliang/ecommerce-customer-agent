"""
客服坐席接口
提供客服的增删改查和会话查询。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.demo_limit import check_demo_limit
from app.models.user import User
from app.models.agent import Agent
from app.models.session import Session as SessionModel
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse

router = APIRouter()

@router.get("/list", response_model=List[AgentResponse])
async def list_agents(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    列出所有客服
    返回：客服列表
    """
    result = await db.execute(select(Agent).order_by(Agent.id))
    return result.scalars().all()

@router.post("/create", response_model=AgentResponse)
async def create_agent(
    request: AgentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    创建客服坐席
    参数：request - 客服信息
    返回：新建的客服
    """
    # 演示模式：数据上限校验
    if await check_demo_limit(db, Agent):
        raise HTTPException(status_code=400, detail="演示模式每类数据最多 10 条，已达到上限，无法继续新增。数据将在次日凌晨 12 点自动恢复。")

    agent = Agent(**request.model_dump())
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent

@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: int,
    request: AgentUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    更新客服信息
    参数：agent_id - 客服ID
          request - 待更新字段
    返回：更新后的客服
    """
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="客服不存在")

    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(agent, field, value)
    await db.commit()
    await db.refresh(agent)
    return agent

@router.get("/{agent_id}/sessions")
async def list_agent_sessions(
    agent_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    查询某客服负责的会话列表
    参数：agent_id - 客服ID
    返回：会话列表
    """
    result = await db.execute(
        select(SessionModel).where(SessionModel.agent_id == agent_id)
    )
    sessions = result.scalars().all()
    return [
        {
            "session_id": s.session_id,
            "user_id": s.user_id,
            "status": s.status,
            "created_at": s.created_at,
        }
        for s in sessions
    ]