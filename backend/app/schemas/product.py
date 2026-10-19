"""
商品相关的 Pydantic 模型
用于商品查询、创建、更新接口。
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ProductCreate(BaseModel):
    """创建商品请求体"""
    name: str = Field(..., max_length=200, description="商品名称")
    category: Optional[str] = Field(None, max_length=50, description="分类")
    price: Decimal = Field(..., ge=0, description="价格")
    description: Optional[str] = Field(None, description="描述")
    stock: int = Field(0, ge=0, description="库存")
    images: Optional[List[str]] = Field(None, description="图片URL列表")
    status: str = Field("on_sale", description="on_sale/off_sale")

class ProductUpdate(BaseModel):
    """更新商品请求体"""
    name: Optional[str] = Field(None, max_length=200)
    category: Optional[str] = Field(None, max_length=50)
    price: Optional[Decimal] = Field(None, ge=0)
    description: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)
    images: Optional[List[str]] = None
    status: Optional[str] = None

class ProductResponse(BaseModel):
    """商品信息响应体"""
    id: int
    name: str
    category: Optional[str] = None
    price: Decimal
    description: Optional[str] = None
    stock: int
    images: Optional[List[str]] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProductSearchRequest(BaseModel):
    """商品搜索请求体"""
    keyword: str = Field(..., min_length=1, max_length=100, description="搜索关键词")
    limit: int = Field(5, ge=1, le=50, description="返回条数上限")