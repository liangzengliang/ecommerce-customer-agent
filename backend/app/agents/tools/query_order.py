"""
订单查询工具
返回完整订单信息，供 LLM 直接展示给用户
"""

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import AsyncSessionLocal
from app.models.order import Order, OrderItem
from app.models.product import Product


async def query_order(order_no: str) -> dict:
    """
    根据订单号查询订单完整信息
    参数：order_no - 订单号
    返回：dict，包含状态、金额、收货、物流、商品明细等
    """
    async with AsyncSessionLocal() as db:
        # 1. 查订单
        stmt = select(Order).where(Order.order_no == order_no)
        result = await db.execute(stmt)
        order = result.scalar_one_or_none()

        if not order:
            return {"found": False, "message": f"未找到订单 {order_no}"}

        # 2. 查订单明细 + 商品
        item_stmt = (
            select(OrderItem, Product)
            .join(Product, OrderItem.product_id == Product.id)
            .where(OrderItem.order_id == order.id)
        )
        item_result = await db.execute(item_stmt)
        items = []
        for oi, p in item_result.all():
            items.append({
                "商品名称": p.name,
                "单价": float(oi.unit_price),
                "数量": oi.quantity,
                "小计": round(float(oi.unit_price) * oi.quantity, 2),
            })

        # 3. 地址
        addr = order.shipping_address or {}
        addr_str = addr.get("full") if isinstance(addr, dict) else str(addr) if addr else "无"

        # 4. 状态中文映射
        status_map = {
            "pending": "待付款",
            "paid": "待发货",
            "shipped": "已发货",
            "delivered": "已收货",
            "completed": "已完成",
            "cancelled": "已取消",
            "refunding": "退款中",
            "refunded": "已退款",
        }
        status_cn = status_map.get(order.status, order.status)

        # 5. 格式化时间
        def fmt(dt):
            return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "无"

        return {
            "found": True,
            "订单号": order.order_no,
            "订单状态": status_cn,
            "订单总金额": float(order.total_amount),
            "实付金额": float(order.pay_amount) if order.pay_amount else float(order.total_amount),
            "收货人": order.receiver_name or "无",
            "联系电话": order.receiver_phone or "无",
            "收货地址": addr_str,
            "物流单号": order.tracking_no or "无",
            "下单时间": fmt(order.created_at),
            "支付时间": fmt(order.paid_at),
            "发货时间": fmt(order.shipped_at),
            "收货时间": fmt(order.delivered_at),
            "订单备注": order.remark or "无",
            "商品明细": items,
        }