"""
订单与订单明细模型，对应 orders 和 order_items 表。
"""
from sqlalchemy import Column, BigInteger, String, Enum, JSON, TEXT, DATETIME, DECIMAL, ForeignKey, Integer, text
from app.core.database import Base

class Order(Base):
    """订单表 ORM 模型"""
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # 订单ID
    order_no = Column(String(32), nullable=False, unique=True)  # 订单号
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # 用户ID
    status = Column(Enum("pending", "paid", "shipped", "delivered", "completed",
                         "cancelled", "refunding", "refunded"), default="pending")  # 订单状态
    total_amount = Column(DECIMAL(10, 2), nullable=False)  # 订单总金额
    pay_amount = Column(DECIMAL(10, 2))  # 实付金额
    shipping_address = Column(JSON)  # 收货地址（JSON）
    receiver_name = Column(String(50))  # 收货人
    receiver_phone = Column(String(20))  # 联系电话
    tracking_no = Column(String(50))  # 物流单号
    remark = Column(TEXT)  # 订单备注
    paid_at = Column(DATETIME)  # 支付时间
    shipped_at = Column(DATETIME)  # 发货时间
    delivered_at = Column(DATETIME)  # 收货时间
    created_at = Column(DATETIME, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DATETIME, server_default=text("CURRENT_TIMESTAMP"))


class OrderItem(Base):
    """订单明细表 ORM 模型，一个订单包含多个商品"""
    __tablename__ = "order_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # 明细ID
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False)  # 订单ID
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)  # 商品ID
    quantity = Column(Integer, nullable=False)  # 数量
    unit_price = Column(DECIMAL(10, 2), nullable=False)  # 单价