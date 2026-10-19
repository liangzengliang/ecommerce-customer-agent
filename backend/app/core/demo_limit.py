"""
演示模式数据限制与每日重置
功能：
1. 演示模式下每个业务表最多 10 条数据，超出后创建接口返回 400 提示。
2. 每天凌晨 12 点自动恢复种子数据（网友的增删改次日失效）。
"""
import asyncio
import logging
from datetime import datetime
from sqlalchemy import select, func, delete

from app.core.config import settings
from app.core.database import AsyncSessionLocal, Base

logger = logging.getLogger(__name__)

# 演示模式每表数据上限
DEMO_TABLE_LIMIT = 10

# 参与每日重置的业务表（ORM 模型类）
# 注意：User 表保留（登录需要），但新增注册用户也限制在 10 条以内
RESET_MODELS = []


def register_reset_models(models: list):
    """注册需要参与每日重置的模型（避免循环导入）"""
    global RESET_MODELS
    RESET_MODELS = models


async def check_demo_limit(db, model, limit: int = DEMO_TABLE_LIMIT) -> bool:
    """
    检查演示模式下某表是否已达到上限。
    返回 True 表示已达上限（应拒绝新增）。
    """
    if not settings.DEMO_MODE:
        return False
    result = await db.execute(select(func.count(model.id)))
    count = result.scalar() or 0
    return count >= limit


async def get_demo_limit_info(db, model) -> dict:
    """返回演示模式的限制信息（供接口提示）"""
    result = await db.execute(select(func.count(model.id)))
    count = result.scalar() or 0
    return {
        "demo_mode": settings.DEMO_MODE,
        "limit": DEMO_TABLE_LIMIT,
        "current_count": count,
        "message": f"演示模式每类数据最多 {DEMO_TABLE_LIMIT} 条，已达到上限，无法继续新增。数据将在次日凌晨 12 点自动恢复。",
    }


# ============================================================
# 每日零点重置
# ============================================================

async def reset_demo_data() -> bool:
    """
    重置所有业务数据为种子数据。
    在每天凌晨 12 点调用。
    """
    if not settings.DEMO_MODE:
        return False
    from scripts.seed_demo import seed_all_demo_data  # 延迟导入避免循环

    logger.info("===== 每日零点重置：开始恢复演示数据 =====")
    async with AsyncSessionLocal() as db:
        # 清空所有注册的业务表
        for model in RESET_MODELS:
            try:
                await db.execute(delete(model))
                logger.info(f"清空表: {model.__tablename__}")
            except Exception as e:
                logger.warning(f"清空表 {model.__tablename__} 失败: {e}")
        await db.commit()

    # 重新注入种子数据
    try:
        await seed_all_demo_data()
        logger.info("===== 每日零点重置：演示数据已恢复 =====")
        return True
    except Exception as e:
        logger.error(f"每日零点重置失败: {e}")
        return False


class DemoResetScheduler:
    """后台任务：检测跨天并触发数据重置"""

    def __init__(self):
        self._last_date = datetime.now().date()

    async def run(self):
        """持续运行的后台任务"""
        while True:
            try:
                now = datetime.now()
                if now.date() != self._last_date:
                    logger.info(f"检测到日期变化: {self._last_date} -> {now.date()}，开始重置")
                    self._last_date = now.date()
                    await reset_demo_data()
            except Exception as e:
                logger.error(f"DemoResetScheduler 异常: {e}")
            # 每 30 秒检查一次
            await asyncio.sleep(30)

    async def check_once(self):
        """启动时检查一次（用于服务刚启动时若已跨天则立即重置）"""
        now = datetime.now()
        if now.date() != self._last_date:
            self._last_date = now.date()
            await reset_demo_data()


# 全局调度器实例
demo_reset_scheduler = DemoResetScheduler()
