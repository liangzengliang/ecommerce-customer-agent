"""
生成测试订单数据
用途：为开发/测试环境快速生成 100 条订单及明细
用法：
    cd backend
    python -m scripts.seed_orders
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy import select, delete
from app.core.database import AsyncSessionLocal
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_orders")

# ============ 测试商品 ============
PRODUCTS = [
    {"name": "无线蓝牙耳机 Pro", "category": "耳机", "price": 399.00, "stock": 500},
    {"name": "头戴式降噪耳机 X1", "category": "耳机", "price": 899.00, "stock": 300},
    {"name": "真无线耳机 Air", "category": "耳机", "price": 599.00, "stock": 400},
    {"name": "旗舰手机 Mate 60", "category": "手机", "price": 5999.00, "stock": 100},
    {"name": "折叠屏手机 Fold 5", "category": "手机", "price": 12999.00, "stock": 50},
    {"name": "轻薄笔记本 Air 14", "category": "电脑", "price": 4999.00, "stock": 80},
    {"name": "游戏笔记本 ROG", "category": "电脑", "price": 9999.00, "stock": 40},
    {"name": "平板电脑 Pad 6", "category": "平板", "price": 2499.00, "stock": 200},
    {"name": "智能手表 Watch 4", "category": "穿戴", "price": 1499.00, "stock": 150},
    {"name": "无线充电器 15W", "category": "配件", "price": 99.00, "stock": 1000},
]

# ============ 测试用户 ============
TEST_USERS = [
    {"username": "张三", "phone": "13800138001"},
    {"username": "李四", "phone": "13800138002"},
    {"username": "王五", "phone": "13800138003"},
]

# ============ 订单状态分布 ============
STATUS_POOL = (
    ["completed"] * 30 +      # 30% 已完成
    ["delivered"] * 15 +      # 15% 已收货
    ["shipped"] * 15 +        # 15% 已发货
    ["paid"] * 15 +           # 15% 已支付待发货
    ["pending"] * 10 +        # 10% 待付款
    ["cancelled"] * 5 +       # 5% 已取消
    ["refunding"] * 5 +       # 5% 退款中
    ["refunded"] * 5          # 5% 已退款
)

# ============ 收货地址池 ============
ADDRESSES = [
    {"province": "北京市", "city": "朝阳区", "detail": "建国路 88 号 SOHO 现代城"},
    {"province": "上海市", "city": "浦东新区", "detail": "陆家嘴环路 1000 号"},
    {"province": "广东省", "city": "深圳市", "detail": "南山区科技园南区"},
    {"province": "广东省", "city": "广州市", "detail": "天河区珠江新城"},
    {"province": "浙江省", "city": "杭州市", "detail": "西湖区文三路 100 号"},
    {"province": "江苏省", "city": "南京市", "detail": "鼓楼区中山路 200 号"},
    {"province": "四川省", "city": "成都市", "detail": "武侯区天府大道 500 号"},
    {"province": "湖北省", "city": "武汉市", "detail": "洪山区光谷广场"},
]


async def ensure_users(db) -> list:
    """确保测试用户存在，返回用户ID列表"""
    user_ids = []
    for u in TEST_USERS:
        result = await db.execute(select(User).where(User.username == u["username"]))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                username=u["username"],
                password_hash="test_hash_placeholder",
                phone=u["phone"],
                user_type="customer",
                is_active=True,
            )
            db.add(user)
            await db.flush()
            logger.info(f"创建用户：{u['username']} (id={user.id})")
        user_ids.append(user.id)
    await db.commit()
    return user_ids


async def ensure_products(db) -> list:
    """确保测试商品存在，返回商品列表"""
    products = []
    for p in PRODUCTS:
        result = await db.execute(select(Product).where(Product.name == p["name"]))
        product = result.scalar_one_or_none()
        if not product:
            product = Product(
                name=p["name"],
                category=p["category"],
                price=p["price"],
                stock=p["stock"],
                status="on_sale",
            )
            db.add(product)
            await db.flush()
            logger.info(f"创建商品：{p['name']} (id={product.id})")
        products.append(product)
    await db.commit()
    return products


async def clear_old_orders(db):
    """清空旧订单（可选）"""
    result = await db.execute(select(Order))
    count = len(result.scalars().all())
    if count > 0:
        logger.warning(f"检测到已有 {count} 条订单")
        # 不主动删除，避免误操作
    return count


async def generate_orders(db, user_ids: list, products: list, count: int = 100):
    """生成订单和明细"""
    today = datetime.now()

    for i in range(1, count + 1):
        # 订单号：ORDER20260926001 ~ ORDER20260926100
        order_no = f"ORDER20260926{i:03d}"

        # 随机用户
        user_id = random.choice(user_ids)

        # 随机状态
        status = random.choice(STATUS_POOL)

        # 随机时间（过去 90 天内）
        created_at = today - timedelta(days=random.randint(0, 90),
                                        hours=random.randint(0, 23),
                                        minutes=random.randint(0, 59))

        # 随机商品 1~3 个
        selected = random.sample(products, random.randint(1, 3))

        total = 0
        items_data = []
        for p in selected:
            qty = random.randint(1, 2)
            price = float(p.price)
            total += price * qty
            items_data.append({"product_id": p.id, "quantity": qty, "unit_price": price})

        # 实付金额（可能有优惠）
        discount = random.choice([1.0, 1.0, 1.0, 0.95, 0.9])
        pay_amount = round(total * discount, 2)

        # 随机收货地址
        addr = random.choice(ADDRESSES)
        shipping_address = {
            "province": addr["province"],
            "city": addr["city"],
            "detail": addr["detail"],
            "full": f"{addr['province']}{addr['city']}{addr['detail']}",
        }

        # 根据状态决定各时间戳
        paid_at = None
        shipped_at = None
        delivered_at = None

        if status not in ("pending", "cancelled"):
            paid_at = created_at + timedelta(minutes=random.randint(1, 30))
        if status in ("shipped", "delivered", "completed"):
            shipped_at = (paid_at or created_at) + timedelta(hours=random.randint(6, 48))
        if status in ("delivered", "completed"):
            delivered_at = (shipped_at or created_at) + timedelta(days=random.randint(1, 5))

        # 物流单号
        tracking_no = None
        if shipped_at:
            tracking_no = f"SF{random.randint(1000000000, 9999999999)}"

        # 创建订单
        order = Order(
            order_no=order_no,
            user_id=user_id,
            status=status,
            total_amount=round(total, 2),
            pay_amount=pay_amount,
            shipping_address=shipping_address,
            receiver_name=random.choice(["张三", "李四", "王五", "赵六", "钱七"]),
            receiver_phone=f"138{random.randint(10000000, 99999999)}",
            tracking_no=tracking_no,
            remark=random.choice([None, None, "请尽快发货", "需要发票", "工作日配送"]),
            paid_at=paid_at,
            shipped_at=shipped_at,
            delivered_at=delivered_at,
            created_at=created_at,
            updated_at=created_at,
        )
        db.add(order)
        await db.flush()

        # 创建明细
        for item in items_data:
            db.add(OrderItem(
                order_id=order.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
            ))

        if i % 20 == 0:
            await db.commit()
            logger.info(f"已生成 {i} 条订单")

    await db.commit()
    logger.info(f"✅ 共生成 {count} 条订单")


async def main():
    logger.info("=== 开始生成测试订单数据 ===")

    async with AsyncSessionLocal() as db:
        await clear_old_orders(db)
        user_ids = await ensure_users(db)
        logger.info(f"用户数量：{len(user_ids)}")
        products = await ensure_products(db)
        logger.info(f"商品数量：{len(products)}")
        await generate_orders(db, user_ids, products, count=100)

    # 关闭数据库连接池（修复 Windows 上的 Event loop is closed）
    from app.core.database import engine
    await engine.dispose()

    logger.info("=== 完成 ===")
    logger.info("测试订单号示例：ORDER20260926001 ~ ORDER20260926100")

if __name__ == "__main__":
    asyncio.run(main())