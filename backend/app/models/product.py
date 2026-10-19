"""
商品模型，对应 products 表。
存储电商商品信息。
"""
from sqlalchemy import Column, BigInteger, String, Enum, JSON, TEXT, Integer, DECIMAL, TIMESTAMP, text
from app.core.database import Base

class Product(Base):
    """商品表 ORM 模型"""
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # 商品ID
    name = Column(String(200), nullable=False)  # 商品名称
    category = Column(String(50))  # 分类
    price = Column(DECIMAL(10, 2), nullable=False)  # 价格
    description = Column(TEXT)  # 描述
    stock = Column(Integer, default=0)  # 库存
    images = Column(JSON)  # 图片列表（JSON数组）
    status = Column(Enum("on_sale", "off_sale"), default="on_sale")  # 状态：上架/下架
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))