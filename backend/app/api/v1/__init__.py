"""
v1 版本路由注册
把所有子路由统一挂载到 router 上，方便 main.py 一次性注册。
"""

from fastapi import APIRouter
from app.api.v1 import (
    auth,
    chat,
    intent,
    agent,
    knowledge,
    order,
    product,
    analytics,
    models,  # → 新增
    memory,  # → 新增
    sessions,       # → 新增
)

router = APIRouter()

# 认证：注册、登录
router.include_router(auth.router, prefix="/auth", tags=["认证"])
# 对话：同步 + SSE 流式
router.include_router(chat.router, tags=["对话"])
# 意图：分类调谐 + 意图配置 CRUD
router.include_router(intent.router, prefix="/intent", tags=["意图"])
# 客服：客服坐席管理
router.include_router(agent.router, prefix="/agent", tags=["客服"])
# 知识库：知识条目管理
router.include_router(knowledge.router, prefix="/knowledge", tags=["知识库"])
# 订单：订单查询与管理
router.include_router(order.router, prefix="/order", tags=["订单"])
# 商品：商品查询与管理
router.include_router(product.router, prefix="/product", tags=["商品"])
# 数据分析：看板统计
router.include_router(analytics.router, prefix="/analytics", tags=["数据分析"])
# 模型配置
router.include_router(models.router, prefix="/models", tags=["模型配置"])    # → 新增
# 记忆库
router.include_router(memory.router, prefix="/memory", tags=["记忆库"])      # → 新增
# 会话列表
router.include_router(sessions.router, prefix="/sessions", tags=["会话列表"])  # → 新增
