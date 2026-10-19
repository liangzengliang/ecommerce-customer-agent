"""
初始化数据库脚本
功能：
1. 创建所有表
2. 插入初始数据（管理员用户、默认意图配置）

用法：
    cd backend
    python -m scripts.init_db
"""

import asyncio
from sqlalchemy import select
from app.core.database import engine, AsyncSessionLocal, Base
from app.core.security import hash_password
from app.models import User, Intent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_db")

# 默认意图配置
DEFAULT_INTENTS = [
    # 商品与活动咨询
    {"intent_name": "商品详情", "intent_code": "PRD_001", "handler_type": "rag", "priority": 1},
    {"intent_name": "促销活动", "intent_code": "PRD_002", "handler_type": "rag", "priority": 1},
    {"intent_name": "商品推荐", "intent_code": "PRD_003", "handler_type": "rag", "priority": 1},
    {"intent_name": "会员权益", "intent_code": "PRD_004", "handler_type": "rag", "priority": 1},
    {"intent_name": "配送时效", "intent_code": "PRD_005", "handler_type": "rag", "priority": 1},
    {"intent_name": "库存查询", "intent_code": "PRD_006", "handler_type": "tool", "priority": 2},
    # 订单与物流
    {"intent_name": "订单查询", "intent_code": "ORD_001", "handler_type": "tool", "priority": 3},
    {"intent_name": "订单修改", "intent_code": "ORD_002", "handler_type": "tool", "priority": 3},
    {"intent_name": "取消订单", "intent_code": "ORD_003", "handler_type": "tool", "priority": 3},
    {"intent_name": "物流追踪", "intent_code": "ORD_004", "handler_type": "tool", "priority": 3},
    {"intent_name": "催促发货", "intent_code": "ORD_005", "handler_type": "tool", "priority": 3},
    {"intent_name": "修改地址", "intent_code": "ORD_006", "handler_type": "tool", "priority": 3},
    # 支付与售后
    {"intent_name": "支付问题", "intent_code": "PAY_001", "handler_type": "rag", "priority": 2},
    {"intent_name": "申请退款", "intent_code": "PAY_002", "handler_type": "tool", "priority": 5},
    {"intent_name": "优惠券使用", "intent_code": "PAY_003", "handler_type": "rag", "priority": 1},
    {"intent_name": "售后政策", "intent_code": "PAY_004", "handler_type": "rag", "priority": 1},
    {"intent_name": "发票问题", "intent_code": "PAY_005", "handler_type": "rag", "priority": 1},
    # 投诉与人工
    {"intent_name": "投诉建议", "intent_code": "CMP_001", "handler_type": "tool", "priority": 5},
    {"intent_name": "退款退货", "intent_code": "CMP_002", "handler_type": "tool", "priority": 5},
    {"intent_name": "人工客服", "intent_code": "CMP_003", "handler_type": "transfer", "priority": 9},
    {"intent_name": "建议反馈", "intent_code": "CMP_004", "handler_type": "tool", "priority": 2},
    {"intent_name": "闲聊/未知", "intent_code": "FALLBACK", "handler_type": "fallback", "priority": 0},
]

async def create_tables():
    """创建所有表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ 所有表创建完成")

async def insert_admin():
    """插入默认管理员账号"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none():
            logger.info("⏭️  管理员已存在，跳过")
            return

        admin = User(
            username="admin",
            password_hash=hash_password("admin123456"),
            email="admin@example.com",
            user_type="admin",
            is_active=True,
        )
        db.add(admin)
        await db.commit()
        logger.info("✅ 管理员创建成功：admin / admin123456")

async def insert_intents():
    """插入默认意图配置"""
    async with AsyncSessionLocal() as db:
        count = 0
        for item in DEFAULT_INTENTS:
            result = await db.execute(
                select(Intent).where(Intent.intent_code == item["intent_code"])
            )
            if result.scalar_one_or_none():
                continue
            db.add(Intent(**item))
            count += 1
        await db.commit()
        logger.info(f"✅ 意图配置插入完成，新增 {count} 条")

async def main():
    """脚本主入口"""
    logger.info("=== 开始初始化数据库 ===")
    await create_tables()
    await insert_admin()
    await insert_intents()
    logger.info("=== 数据库初始化完成 ===")

    # 释放连接池，避免事件循环关闭后连接清理报错
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())