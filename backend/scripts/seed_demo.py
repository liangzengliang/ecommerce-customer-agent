"""
演示模式种子数据脚本
用途：为 GitHub Demo 注入 10 条演示数据（商品/订单/知识库等）。
演示账号：demo / demo123456
说明：演示模式下每天凌晨 12 点会自动调用本脚本恢复数据。
用法：
    cd backend
    python -m scripts.seed_demo
"""
import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy import select, func

from app.core.database import AsyncSessionLocal, engine, Base
from app.core.security import hash_password
from app.models import (
    User, Product, Order, OrderItem, Knowledge, Intent,
    Agent, ModelConfig,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_demo")

# ============ 演示商品（10 条） ============
DEMO_PRODUCTS = [
    {"name": "无线蓝牙耳机 Pro", "category": "耳机", "price": 399.00, "stock": 500, "description": "主动降噪，30 小时续航，支持无线充电。", "status": "on_sale"},
    {"name": "头戴式降噪耳机 X1", "category": "耳机", "price": 899.00, "stock": 300, "description": "沉浸式降噪，Hi-Res 音质，佩戴舒适。", "status": "on_sale"},
    {"name": "真无线耳机 Air", "category": "耳机", "price": 599.00, "stock": 400, "description": "轻巧便携，通话清晰，IPX5 防水。", "status": "on_sale"},
    {"name": "旗舰手机 Mate 60", "category": "手机", "price": 5999.00, "stock": 100, "description": "麒麟芯片，超强影像，卫星通信。", "status": "on_sale"},
    {"name": "折叠屏手机 Fold 5", "category": "手机", "price": 12999.00, "stock": 50, "description": "折叠大屏，多任务处理，轻薄机身。", "status": "on_sale"},
    {"name": "轻薄笔记本 Air 14", "category": "电脑", "price": 4999.00, "stock": 80, "description": "14 英寸 2.8K 屏，16G 内存，长续航。", "status": "on_sale"},
    {"name": "游戏笔记本 ROG", "category": "电脑", "price": 9999.00, "stock": 40, "description": "高性能独显，电竞屏，散热强劲。", "status": "on_sale"},
    {"name": "平板电脑 Pad 6", "category": "平板", "price": 2499.00, "stock": 200, "description": "2K 全面屏，四扬声器，学习娱乐好帮手。", "status": "on_sale"},
    {"name": "智能手表 Watch 4", "category": "穿戴", "price": 1499.00, "stock": 150, "description": "血氧监测，运动记录，消息提醒。", "status": "on_sale"},
    {"name": "无线充电器 15W", "category": "配件", "price": 99.00, "stock": 1000, "description": "兼容多设备，轻薄便携，安全快充。", "status": "on_sale"},
]

# ============ 演示订单（10 条） ============
DEMO_ORDERS = [
    {"order_no": "ORDER20261001001", "status": "delivered", "total": 399.00, "pay": 379.00, "receiver": "张三", "phone": "13800138001", "addr": {"province": "北京市", "city": "朝阳区", "detail": "建国路 88 号 SOHO 现代城", "full": "北京市朝阳区建国路 88 号 SOHO 现代城"}, "tracking": "SF1000000001", "remark": "请尽快发货"},
    {"order_no": "ORDER20261001002", "status": "shipped", "total": 599.00, "pay": 599.00, "receiver": "李四", "phone": "13800138002", "addr": {"province": "上海市", "city": "浦东新区", "detail": "陆家嘴环路 1000 号", "full": "上海市浦东新区陆家嘴环路 1000 号"}, "tracking": "SF1000000002", "remark": None},
    {"order_no": "ORDER20261001003", "status": "paid", "total": 5999.00, "pay": 5699.00, "receiver": "王五", "phone": "13800138003", "addr": {"province": "广东省", "city": "深圳市", "detail": "南山区科技园南区", "full": "广东省深圳市南山区科技园南区"}, "tracking": None, "remark": "需要发票"},
    {"order_no": "ORDER20261001004", "status": "completed", "total": 899.00, "pay": 899.00, "receiver": "赵六", "phone": "13800138004", "addr": {"province": "浙江省", "city": "杭州市", "detail": "西湖区文三路 100 号", "full": "浙江省杭州市西湖区文三路 100 号"}, "tracking": "SF1000000004", "remark": None},
    {"order_no": "ORDER20261001005", "status": "pending", "total": 99.00, "pay": 99.00, "receiver": "钱七", "phone": "13800138005", "addr": {"province": "江苏省", "city": "南京市", "detail": "鼓楼区中山路 200 号", "full": "江苏省南京市鼓楼区中山路 200 号"}, "tracking": None, "remark": None},
    {"order_no": "ORDER20261001006", "status": "refunding", "total": 12999.00, "pay": 12349.00, "receiver": "张三", "phone": "13800138001", "addr": {"province": "北京市", "city": "朝阳区", "detail": "建国路 88 号 SOHO 现代城", "full": "北京市朝阳区建国路 88 号 SOHO 现代城"}, "tracking": "SF1000000006", "remark": "申请退款"},
    {"order_no": "ORDER20261001007", "status": "cancelled", "total": 2499.00, "pay": 0.00, "receiver": "李四", "phone": "13800138002", "addr": {"province": "上海市", "city": "浦东新区", "detail": "陆家嘴环路 1000 号", "full": "上海市浦东新区陆家嘴环路 1000 号"}, "tracking": None, "remark": "取消订单"},
    {"order_no": "ORDER20261001008", "status": "delivered", "total": 1499.00, "pay": 1424.00, "receiver": "王五", "phone": "13800138003", "addr": {"province": "广东省", "city": "深圳市", "detail": "南山区科技园南区", "full": "广东省深圳市南山区科技园南区"}, "tracking": "SF1000000008", "remark": None},
    {"order_no": "ORDER20261001009", "status": "shipped", "total": 4999.00, "pay": 4999.00, "receiver": "赵六", "phone": "13800138004", "addr": {"province": "浙江省", "city": "杭州市", "detail": "西湖区文三路 100 号", "full": "浙江省杭州市西湖区文三路 100 号"}, "tracking": "SF1000000009", "remark": "工作日配送"},
    {"order_no": "ORDER20261001010", "status": "completed", "total": 1198.00, "pay": 1138.00, "receiver": "钱七", "phone": "13800138005", "addr": {"province": "四川省", "city": "成都市", "detail": "武侯区天府大道 500 号", "full": "四川省成都市武侯区天府大道 500 号"}, "tracking": "SF1000000010", "remark": None},
]

# ============ 演示知识（10 条） ============
DEMO_KNOWLEDGE = [
    {"category": "订单", "question": "如何查询我的订单？", "answer": "您可以在对话中直接输入订单号（如 ORDER20261001001），我会为您查询订单状态、物流信息等。", "keywords": "查订单,订单查询,订单号"},
    {"category": "订单", "question": "订单多久能发货？", "answer": "一般情况下，现货商品在支付成功后 24 小时内发货，预售商品以页面提示为准。", "keywords": "发货,发货时间,多久发货"},
    {"category": "售后", "question": "如何申请退款？", "answer": "您可以在对话中提供订单号并说明退款原因，系统会自动创建退款工单。退款将在 1-3 个工作日内原路退回。", "keywords": "退款,退货,申请退款"},
    {"category": "售后", "question": "退换货政策是什么？", "answer": "签收后 7 天内支持无理由退换货（商品完好、不影响二次销售），15 天内质量问题可免费退换。", "keywords": "退换货,售后,政策"},
    {"category": "支付", "question": "支持哪些支付方式？", "answer": "我们支持支付宝、微信支付、银联云闪付等多种支付方式。", "keywords": "支付方式,付款,支付宝,微信"},
    {"category": "支付", "question": "退款多久到账？", "answer": "退款一般在审核通过后 1-3 个工作日内原路退回，具体到账时间以支付渠道为准。", "keywords": "退款到账,多久到账"},
    {"category": "物流", "question": "如何修改收货地址？", "answer": "订单未发货前，您可以联系在线客服修改收货地址；已发货订单需联系物流公司处理。", "keywords": "修改地址,收货地址"},
    {"category": "商品", "question": "耳机支持保修吗？", "answer": "耳机类商品享受 1 年官方保修，非人为损坏可免费维修。", "keywords": "保修,耳机,售后"},
    {"category": "商品", "question": "电脑的配置如何？", "answer": "轻薄笔记本 Air 14 搭载最新处理器，16GB 内存，512GB 固态硬盘，2.8K 高清屏，适合办公与学习。", "keywords": "电脑,配置,笔记本"},
    {"category": "优惠", "question": "有什么优惠活动？", "answer": "目前正在进行新品首发促销，部分商品可享受 95 折优惠，具体以商品页面为准。", "keywords": "优惠,活动,促销,打折"},
]

# ============ 演示意图（系统配置，不占演示限额） ============
DEMO_INTENTS = [
    {"intent_name": "商品详情", "intent_code": "PRD_001", "handler_type": "rag", "priority": 1},
    {"intent_name": "促销活动", "intent_code": "PRD_002", "handler_type": "rag", "priority": 1},
    {"intent_name": "商品推荐", "intent_code": "PRD_003", "handler_type": "rag", "priority": 1},
    {"intent_name": "会员权益", "intent_code": "PRD_004", "handler_type": "rag", "priority": 1},
    {"intent_name": "配送时效", "intent_code": "PRD_005", "handler_type": "rag", "priority": 1},
    {"intent_name": "库存查询", "intent_code": "PRD_006", "handler_type": "tool", "priority": 2},
    {"intent_name": "订单查询", "intent_code": "ORD_001", "handler_type": "tool", "priority": 3},
    {"intent_name": "订单修改", "intent_code": "ORD_002", "handler_type": "tool", "priority": 3},
    {"intent_name": "取消订单", "intent_code": "ORD_003", "handler_type": "tool", "priority": 3},
    {"intent_name": "物流追踪", "intent_code": "ORD_004", "handler_type": "tool", "priority": 3},
    {"intent_name": "催促发货", "intent_code": "ORD_005", "handler_type": "tool", "priority": 3},
    {"intent_name": "修改地址", "intent_code": "ORD_006", "handler_type": "tool", "priority": 3},
    {"intent_name": "支付问题", "intent_code": "PAY_001", "handler_type": "rag", "priority": 2},
    {"intent_name": "申请退款", "intent_code": "PAY_002", "handler_type": "tool", "priority": 5},
    {"intent_name": "优惠券使用", "intent_code": "PAY_003", "handler_type": "rag", "priority": 1},
    {"intent_name": "售后政策", "intent_code": "PAY_004", "handler_type": "rag", "priority": 1},
    {"intent_name": "发票问题", "intent_code": "PAY_005", "handler_type": "rag", "priority": 1},
    {"intent_name": "投诉建议", "intent_code": "CMP_001", "handler_type": "tool", "priority": 5},
    {"intent_name": "退款退货", "intent_code": "CMP_002", "handler_type": "tool", "priority": 5},
    {"intent_name": "人工客服", "intent_code": "CMP_003", "handler_type": "transfer", "priority": 9},
    {"intent_name": "建议反馈", "intent_code": "CMP_004", "handler_type": "tool", "priority": 2},
    {"intent_name": "闲聊/未知", "intent_code": "FALLBACK", "handler_type": "fallback", "priority": 0},
]



async def create_tables_if_not_exists():
    """建表（演示模式 SQLite 自动建表）"""
    from app.core.config import settings
    if settings.DATABASE_URL.startswith("sqlite"):
        from app.core.sqlite_compat import create_all_sqlite
        await create_all_sqlite(engine)
    else:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ 数据表已就绪")



async def seed_users(db):
    """演示用户（demo 账号 + 普通用户）"""
    users = [
        {"username": "demo", "password": "demo123456", "email": "demo@example.com", "phone": "13800000001", "user_type": "admin"},
        {"username": "demo2", "password": "demo123456", "email": "demo2@example.com", "phone": "13800000002", "user_type": "customer"},
        {"username": "demo3", "password": "demo123456", "email": "demo3@example.com", "phone": "13800000003", "user_type": "customer"},
        {"username": "demo4", "password": "demo123456", "email": "demo4@example.com", "phone": "13800000004", "user_type": "customer"},
        {"username": "demo5", "password": "demo123456", "email": "demo5@example.com", "phone": "13800000005", "user_type": "customer"},
        {"username": "alice", "password": "demo123456", "email": "alice@example.com", "phone": "13800000006", "user_type": "customer"},
        {"username": "bob", "password": "demo123456", "email": "bob@example.com", "phone": "13800000007", "user_type": "customer"},
        {"username": "carol", "password": "demo123456", "email": "carol@example.com", "phone": "13800000008", "user_type": "customer"},
    ]
    created = 0
    for u in users:
        exists = (await db.execute(select(User).where(User.username == u["username"]))).scalar_one_or_none()
        if not exists:
            db.add(User(
                username=u["username"],
                password_hash=hash_password(u["password"]),
                email=u["email"],
                phone=u["phone"],
                user_type=u["user_type"],
                is_active=True,
            ))
            created += 1
    await db.commit()
    logger.info(f"✅ 演示用户就绪（新增 {created}）")


async def seed_products(db):
    for p in DEMO_PRODUCTS:
        exists = (await db.execute(select(Product).where(Product.name == p["name"]))).scalar_one_or_none()
        if not exists:
            db.add(Product(**p))
    await db.commit()
    logger.info("✅ 演示商品就绪（10 条）")


async def seed_orders(db):
    """订单 + 明细"""
    demo_user = (await db.execute(select(User).where(User.username == "demo"))).scalar_one_or_none()
    user_id = demo_user.id if demo_user else 1
    products = (await db.execute(select(Product).limit(10))).scalars().all()
    for idx, o in enumerate(DEMO_ORDERS):
        exists = (await db.execute(select(Order).where(Order.order_no == o["order_no"]))).scalar_one_or_none()
        if exists:
            continue
        now = datetime.now() - timedelta(days=idx % 7, hours=idx)
        order = Order(
            order_no=o["order_no"],
            user_id=user_id,
            status=o["status"],
            total_amount=o["total"],
            pay_amount=o["pay"],
            shipping_address=o["addr"],
            receiver_name=o["receiver"],
            receiver_phone=o["phone"],
            tracking_no=o["tracking"],
            remark=o["remark"],
            paid_at=now if o["status"] not in ("pending", "cancelled") else None,
            shipped_at=now if o["status"] in ("shipped", "delivered", "completed", "refunding") else None,
            delivered_at=now if o["status"] in ("delivered", "completed") else None,
            created_at=now,
            updated_at=now,
        )
        db.add(order)
        await db.flush()
        # 明细：关联一个商品
        if products:
            product = products[idx % len(products)]
            db.add(OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=1,
                unit_price=o["total"],
            ))
    await db.commit()
    logger.info("✅ 演示订单就绪（10 条）")


async def seed_knowledge(db):
    for k in DEMO_KNOWLEDGE:
        exists = (await db.execute(select(Knowledge).where(Knowledge.question == k["question"]))).scalar_one_or_none()
        if not exists:
            db.add(Knowledge(**k, is_active=True))
    await db.commit()
    logger.info("✅ 演示知识就绪（10 条）")


async def seed_intents(db):
    for item in DEMO_INTENTS:
        exists = (await db.execute(select(Intent).where(Intent.intent_code == item["intent_code"]))).scalar_one_or_none()
        if not exists:
            db.add(Intent(**item))
    await db.commit()
    logger.info(f"✅ 演示意图就绪（{len(DEMO_INTENTS)} 条）")


async def seed_agents(db):
    agents = [
        {"name": "小智", "status": "online", "description": "电商智能客服助手", "is_active": True},
        {"name": "售后专员", "status": "offline", "description": "售后问题处理专员", "is_active": True},
    ]
    for a in agents:
        exists = (await db.execute(select(Agent).where(Agent.name == a["name"]))).scalar_one_or_none()
        if not exists:
            db.add(Agent(**a))
    await db.commit()
    logger.info("✅ 演示客服就绪（2 条）")


async def seed_model_configs(db):
    """模型配置（演示用占位，API Key 为空）"""
    configs = [
        {"name": "演示默认对话模型", "provider": "siliconflow", "type": "chat", "model": "Qwen/Qwen2.5-7B-Instruct", "base_url": "https://api.siliconflow.cn/v1", "api_key": "", "temperature": 0.3, "max_tokens": 2048, "is_default": True, "is_active": True, "status": "正常"},
        {"name": "演示默认嵌入模型", "provider": "siliconflow", "type": "embedding", "model": "BAAI/bge-m3", "base_url": "https://api.siliconflow.cn/v1", "api_key": "", "temperature": 0.0, "max_tokens": 1024, "is_default": True, "is_active": True, "status": "正常"},
    ]
    for c in configs:
        exists = (await db.execute(select(ModelConfig).where(ModelConfig.name == c["name"]))).scalar_one_or_none()
        if not exists:
            db.add(ModelConfig(**c))
    await db.commit()
    logger.info("✅ 演示模型配置就绪（2 条）")


async def seed_all_demo_data():
    """主入口：注入全部演示数据"""
    await create_tables_if_not_exists()
    async with AsyncSessionLocal() as db:
        await seed_users(db)
        await seed_products(db)
        await seed_orders(db)
        await seed_knowledge(db)
        await seed_intents(db)
        await seed_agents(db)
        await seed_model_configs(db)
    logger.info("===== 演示数据初始化完成 =====")


async def main():
    logger.info("=== 开始初始化演示数据 ===")
    await seed_all_demo_data()
    await engine.dispose()
    logger.info("=== 完成 ===")
    logger.info("演示账号：demo / demo123456")


if __name__ == "__main__":
    asyncio.run(main())
