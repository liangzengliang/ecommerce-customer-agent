"""
嵌入模型模块
使用 OpenAI 兼容的嵌入 API（如硅基流动），不再依赖本地 PyTorch。
演示模式（无 API Key）时返回 None，避免启动失败。
"""

from app.core.config import settings
from functools import lru_cache
from openai import OpenAI
from typing import List, Optional

class SiliconFlowEmbeddings:
    """
    自定义 Embedding 类，直接调用 openai 库。
    兼容 LangChain 的 Embeddings 接口（embed_query / embed_documents），
    可被 langchain_milvus 等组件直接使用。
    """

    def __init__(
            self,
            model: str,
            api_key: str,
            base_url: str,
    ):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def embed_query(self, text: str) -> List[float]:
        """生成单条文本的嵌入向量"""
        resp = self.client.embeddings.create(model=self.model, input=text)
        return resp.data[0].embedding

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """批量生成文本的嵌入向量"""
        resp = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in resp.data]


@lru_cache
def get_embeddings() -> Optional[SiliconFlowEmbeddings]:
    """
    获取嵌入模型实例（单例）
    返回：SiliconFlowEmbeddings 对象，使用配置中的模型
    若未配置 API Key（演示模式），返回 None。
    """
    api_key = settings.EMBEDDING_API_KEY or settings.OPENAI_API_KEY
    if not api_key:
        return None
    return SiliconFlowEmbeddings(
        model=settings.EMBEDDING_MODEL,
        api_key=api_key,
        base_url=settings.EMBEDDING_BASE_URL or settings.OPENAI_BASE_URL,
    )
