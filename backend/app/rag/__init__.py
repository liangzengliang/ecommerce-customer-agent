"""
RAG 包：检索增强生成模块。
包含文档加载、分块、向量化、向量存储、检索。
对外暴露嵌入模型、向量库管理器、检索器。
"""

from app.rag.embedding_model import get_embeddings
from app.rag.vector_store import vector_store_manager, VectorStoreManager
from app.rag.retriever import Retriever
from app.rag.document_loader import load_document
from app.rag.text_splitter import split_documents

__all__ = [
    "get_embeddings",
    "vector_store_manager",
    "VectorStoreManager",
    "Retriever",
    "load_document",
    "split_documents",
]