"""
知识库检索工具
调用 RAG 检索器查询知识库。
"""

from app.rag.retriever import Retriever

_retriever = Retriever(k=3)

async def search_knowledge(query: str) -> dict:
    """
    检索知识库
    参数：query - 查询文本
    返回：dict，含 found / docs
    """
    docs = _retriever.retrieve(query)
    return {"found": len(docs) > 0, "docs": docs}