"""
订单相关的 Pydantic 模型
用于订单查询和订单管理接口。
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

class OrderItemResponse(BaseModel):
    """订单明细响应体"""
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    """订单信息响应体"""
    id: int
    order_no: str
    user_id: int
    status: str
    total_amount: Decimal
    pay_amount: Optional[Decimal] = None
    shipping_address: Optional[Dict[str, Any]] = None
    receiver_name: Optional[str] = None
    receiver_phone: Optional[str] = None
    tracking_no: Optional[str] = None
    remark: Optional[str] = None
    paid_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []   # 订单明细列表

    class Config:
        from_attributes = True

class OrderUpdate(BaseModel):
    """更新订单请求体（管理员使用）"""
    status: Optional[str] = Field(None, description="订单状态")
    tracking_no: Optional[str] = Field(None, max_length=50, description="物流单号")
    remark: Optional[str] = None

class OrderQuery(BaseModel):
    """订单查询请求参数（用于 GET 查询接口的 body 形式，或前端搜索条件）"""
    order_no: Optional[str] = None
    user_id: Optional[int] = None
    status: Optional[str] = None