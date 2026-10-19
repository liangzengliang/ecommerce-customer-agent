"""
RAG 检索节点
"""

from app.agents.graph.state import AgentState
from app.rag.retriever import Retriever
import logging

logger = logging.getLogger(__name__)

_retriever = Retriever(k=10)


async def retrieve_knowledge(state: AgentState) -> AgentState:
    """
    RAG 检索节点：向量检索 + 数据库兜底
    """
    query = state["user_message"]

    # 先向量检索，空则 DB 兜底
    context = await _retriever.retrieve_with_db_fallback(query)

    state["rag_context"] = context

    # 清空工具结果，防止残留污染
    state["tool_results"] = []
    state["error"] = None

    logger.info(f"RAG 检索到 {len(context)} 字上下文")
    return state