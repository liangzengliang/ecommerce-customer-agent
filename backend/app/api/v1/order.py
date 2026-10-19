"""
订单接口
提供订单查询与管理。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.order import Order
from app.schemas.order import OrderResponse, OrderUpdate
# from app.services.order_service import order_service

router = APIRouter()

@router.get("/{order_no}", response_model=OrderResponse)
async def get_order(
    order_no: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    根据订单号查询订单详情
    参数：order_no - 订单号
    返回：订单信息
    """
    result = await db.execute(select(Order).where(Order.order_no == order_no))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order

@router.get("/list/all", response_model=List[OrderResponse])
async def list_orders(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    列出订单（管理员使用）
    参数：status - 可选，按订单状态过滤
    返回：订单列表
    """
    stmt = select(Order).order_by(Order.created_at.desc())
    if status:
        stmt = stmt.where(Order.status == status)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.put("/{order_no}", response_model=OrderResponse)
async def update_order(
    order_no: str,
    request: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    更新订单（管理员使用）
    参数：order_no - 订单号
          request - 待更新字段（status / tracking_no / remark）
    返回：更新后的订单
    """
    result = await db.execute(select(Order).where(Order.order_no == order_no))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(order, field, value)
    await db.commit()
    await db.refresh(order)
    return order