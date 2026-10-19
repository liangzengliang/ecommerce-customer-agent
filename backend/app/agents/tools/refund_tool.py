"""
退款申请工具
将订单状态改为 refunding 并记录退款原因。
"""

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.order import Order

async def request_refund(order_no: str, reason: str) -> dict:
    """
    提交退款申请
    参数：order_no - 订单号
          reason - 退款原因
    返回：dict，含 success / message
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Order).where(Order.order_no == order_no))
        order = result.scalar_one_or_none()
        if not order:
            return {"success": False, "message": f"未找到订单 {order_no}"}
        order.status = "refunding"
        order.remark = (order.remark or "") + f"\n退款原因：{reason}"
        await db.commit()
        return {"success": True, "message": "退款申请已提交，等待审核"}