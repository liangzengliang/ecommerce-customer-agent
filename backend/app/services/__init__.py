"""
services 包：业务逻辑服务层。
统一导出所有服务单例，方便其他模块直接 from app.services import xxx 使用。
导入顺序按依赖深度从浅到深，避免循环导入。
"""

# ===== 基础服务 最底层：无内部依赖=====
from app.services.memory_service import memory_service        # Redis 会话记忆
from app.services.llm_service import get_llm                  # LLM 实例工厂

# ===== NLU 相关服务 =====
from app.services.intent_service import intent_service        # 意图识别
from app.services.sentiment_service import sentiment_service  # 情感分析

# ===== RAG 与 Agent =====
from app.services.rag_service import rag_service              # 知识库检索
from app.services.agent_service import agent_service          # Agent 执行

# ===== 业务服务 =====
from app.services.order_service import order_service          # 订单
from app.services.product_service import product_service      # 商品
from app.services.knowledge_service import knowledge_service  # 知识库

# ===== 对话编排服务（依赖 memory_service 和 agent_graph，放最后）=====
from app.services.chat_service import chat_service            # 对话编排

__all__ = [
    "memory_service",
    "get_llm",
    "intent_service",
    "sentiment_service",
    "rag_service",
    "agent_service",
    "order_service",
    "product_service",
    "knowledge_service",
    "chat_service",
]