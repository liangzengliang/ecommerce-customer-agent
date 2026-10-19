"""
商品服务
封装商品查询业务逻辑。
"""

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.product import Product

class ProductService:
    """商品服务类"""

    async def search(self, keyword: str, limit: int = 5) -> list:
        """
        按关键词搜索商品
        参数：keyword - 关键词
              limit - 返回条数上限
        返回：商品字典列表
        """
        async with AsyncSessionLocal() as db:
            stmt = select(Product).where(
                Product.name.like(f"%{keyword}%"),
                Product.status == "on_sale",
            ).limit(limit)
            result = await db.execute(stmt)
            return [
                {"id": p.id, "name": p.name, "price": float(p.price), "stock": p.stock}
                for p in result.scalars().all()
            ]

product_service = ProductService()