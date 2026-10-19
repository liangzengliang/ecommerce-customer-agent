"""
FastAPI 应用入口
负责：事件循环策略（Windows）、日志初始化、Redis 连接检查、CORS 配置、路由注册。
"""

# ============================================================
# Windows 兼容：必须在导入 asyncio 相关模块之前设置事件循环策略
# 否则 aiomysql / redis.asyncio 在 Windows 上会报 "Event loop is closed"
# ============================================================
import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# ============================================================
# 其他导入
# ============================================================
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import setup_logging
from app.core.redis_client import get_redis
from app.core.demo_limit import register_reset_models, demo_reset_scheduler, reset_demo_data
from app.api.v1 import router as v1_router

# 导入所有模型（确保注册到 Base.metadata）
from app.models import (
    User, Product, Order, Knowledge, Intent, Agent, ModelConfig,
    Project, ProjectMember, ProjectTask, ProjectRisk,
    ProjectMeeting, ProjectDocument, ProjectChange, ProjectComment,
)
# 注册每日重置的业务表
register_reset_models([
    Product, Order, Knowledge, Intent, Project, Agent, ModelConfig,
    ProjectMember, ProjectTask, ProjectRisk,
    ProjectMeeting, ProjectDocument, ProjectChange, ProjectComment,
])


# 初始化日志（在应用启动前调用一次）
setup_logging()


# ============================================================
# 应用生命周期：启动时检查 Redis，关闭时无需特殊处理
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    - 启动时：检查 Redis 连接；若演示模式且数据为空则注入种子数据
    - 运行中：后台任务每日凌晨 12 点自动恢复演示数据
    - 关闭时：无需特殊处理
    """
    try:
        redis = get_redis()
        await redis.ping()
        print("[OK] Redis 连接成功")
    except Exception as e:
        print(f"[WARN] Redis 连接失败: {e}")

    # ===== 演示模式：初始化种子数据 + 启动每日重置调度 =====
    from app.core.config import settings
    if settings.DEMO_MODE:
        from scripts.seed_demo import seed_all_demo_data
        try:
            await seed_all_demo_data()
            print("[OK] 演示数据初始化完成（演示账号：demo / demo123456）")
        except Exception as e:
            print(f"[WARN] 演示数据初始化失败: {e}")

        # 启动时检查一次跨天（若服务跨天重启则立即重置）
        try:
            await demo_reset_scheduler.check_once()
        except Exception as e:
            print(f"[WARN] 演示数据重置检查失败: {e}")

        # 启动后台每日重置任务
        import asyncio
        task = asyncio.create_task(demo_reset_scheduler.run())
        print("[OK] 每日零点数据重置任务已启动（演示模式）")

    yield


# ============================================================
# 创建 FastAPI 应用
# ============================================================
app = FastAPI(
    title="电商智能客服",
    version="1.0.0",
    description="基于 FastAPI + LangGraph + RAG + NLU 的电商智能客服系统",
    lifespan=lifespan,
)


# ============================================================
# CORS 中间件（开发环境放开所有来源，生产环境应指定具体域名）
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 注册 v1 版本路由
# ============================================================
app.include_router(v1_router, prefix="/api/v1")


# ============================================================
# 健康检查接口
# ============================================================
@app.get("/health")
async def health():
    """健康检查，用于负载均衡/容器探针"""
    return {"status": "ok"}


# ============================================================
# 直接运行时启动（用于调试，正式启动请用 uvicorn 命令）
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)