"""
RAG 服务
对外暴露知识库检索能力。
"""

from app.rag.retriever import Retriever

class RAGService:
    """RAG 服务类"""

    def __init__(self):
        """初始化检索器"""
        self.retriever = Retriever(k=5)

    def retrieve(self, query: str):
        """
        检索相关文档
        参数：query - 查询文本
        返回：文档字典列表
        """
        return self.retriever.retrieve(query)

    def retrieve_as_context(self, query: str) -> str:
        """
        检索并拼接为上下文字符串
        参数：query - 查询文本
        返回：拼接后的上下文
        """
        return self.retriever.retrieve_as_context(query)

rag_service = RAGService()