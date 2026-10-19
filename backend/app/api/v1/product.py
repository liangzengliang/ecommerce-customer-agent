"""
商品接口
提供商品查询与管理。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.demo_limit import check_demo_limit
from app.models.user import User
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
# from app.services.product_service import product_service

router = APIRouter()

@router.get("/search", response_model=List[ProductResponse])
async def search_products(
    keyword: str,
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    按关键词搜索在售商品
    参数：keyword - 关键词
          limit - 返回条数
    返回：商品列表
    """
    stmt = select(Product).where(
        Product.name.like(f"%{keyword}%"),
        Product.status == "on_sale",
    ).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    获取商品详情
    参数：product_id - 商品ID
    返回：商品信息
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product

@router.post("/create", response_model=ProductResponse)
async def create_product(
    request: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    创建商品（管理员）
    参数：request - 商品信息
    返回：新建的商品
    """
    # 演示模式：数据上限校验
    if await check_demo_limit(db, Product):
        raise HTTPException(status_code=400, detail="演示模式每类数据最多 10 条，已达到上限，无法继续新增。数据将在次日凌晨 12 点自动恢复。")

    product = Product(**request.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    request: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    更新商品（管理员）
    参数：product_id - 商品ID
          request - 待更新字段
    返回：更新后的商品
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    await db.commit()
    await db.refresh(product)
    return product