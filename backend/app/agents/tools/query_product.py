"""
商品查询工具
按关键词模糊查询在售商品。
"""

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.product import Product

async def query_product(keyword: str) -> dict:
    """
    按关键词查询商品
    参数：keyword - 商品名关键词
    返回：dict，含 found / products
    """
    async with AsyncSessionLocal() as db:
        stmt = select(Product).where(
            Product.name.like(f"%{keyword}%"),
            Product.status == "on_sale",
        ).limit(5)
        result = await db.execute(stmt)
        products = result.scalars().all()
        if not products:
            return {"found": False, "message": f"未找到相关商品：{keyword}"}
        return {
            "found": True,
            "products": [
                {"id": p.id, "name": p.name, "price": float(p.price), "stock": p.stock}
                for p in products
            ],
        }