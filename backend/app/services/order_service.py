"""
订单服务
封装订单相关的业务逻辑。
"""

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.order import Order

class OrderService:
    """订单服务类"""

    async def get_by_no(self, order_no: str) -> dict | None:
        """
        根据订单号获取订单
        参数：order_no - 订单号
        返回：订单字典，不存在返回 None
        """
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Order).where(Order.order_no == order_no))
            order = result.scalar_one_or_none()
            if not order:
                return None
            return {
                "order_no": order.order_no,
                "status": order.status,
                "total_amount": float(order.total_amount),
                "tracking_no": order.tracking_no,
            }

order_service = OrderService()