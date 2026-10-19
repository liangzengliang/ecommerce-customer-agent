# """
# 向量库管理模块
# 封装 Milvus 向量库的连接、写入、检索操作。
# """
#
# import logging
# from langchain_milvus import Milvus
# from pymilvus import connections
# from app.core.config import settings
# from app.rag.embedding_model import get_embeddings
#
# logger = logging.getLogger(__name__)
#
# class VectorStoreManager:
#     """向量库管理器，懒加载 Milvus 连接"""
#
#     def __init__(self):
#         """初始化嵌入模型、连接参数、集合名"""
#         self.embeddings = get_embeddings()
#         self.connection_args = {
#             "host": settings.MILVUS_HOST,
#             "port": str(settings.MILVUS_PORT),
#         }
#         self.collection_name = settings.MILVUS_COLLECTION
#         self._store = None
#
#     @property
#     def store(self) -> Milvus:
#         """懒加载 Milvus 实例，避免启动时连接失败"""
#         if self._store is None:
#             # 1. 先手动建立连接（使用默认别名 "default"）
#             if not connections.has_connection("default"):
#                 connections.connect(
#                     alias="default",
#                     host=settings.MILVUS_HOST,
#                     port=str(settings.MILVUS_PORT),
#                 )
#                 logger.info("Milvus 连接已建立: %s:%s", settings.MILVUS_HOST, settings.MILVUS_PORT)
#
#                 # 2. 再创建 Milvus 实例
#             self._store = Milvus(
#                 embedding_function=self.embeddings,
#                 collection_name=self.collection_name,
#                 connection_args={
#                     "uri": f"http://{settings.MILVUS_HOST}:{settings.MILVUS_PORT}",
#                 },
#                 auto_id=True,  # 自动生成主键
#                 drop_old=False,  # 不删除已有集合
#             )
#             return self._store
#
#
#     def add_texts(self, texts, metadatas=None):
#             """
#             向向量库添加文本
#             参数：texts - 文本列表
#                   metadatas - 元数据列表（可选）
#             返回：添加的向量ID列表
#             """
#             return self.store.add_texts(texts=texts, metadatas=metadatas)
#
#     def similarity_search(self, query: str, k: int = 5):
#         """
#         相似度检索
#         参数：query - 查询文本
#               k - 返回条数
#         返回：Document 列表
#         """
#         return self.store.similarity_search(query, k=k)
#
# # 全局单例
# vector_store_manager = VectorStoreManager()

"""
向量库管理模块
封装 Milvus 向量库的连接、写入、检索操作。
"""

#
# import logging
# from typing import List, Optional
#
# from langchain_core.documents import Document
# from pymilvus import DataType, MilvusClient
#
# from app.core.config import settings
# from app.rag.embedding_model import get_embeddings
#
# logger = logging.getLogger(__name__)
#
#
# class VectorStoreManager:
#     """向量库管理器，懒加载 MilvusClient"""
#
#     def __init__(self):
#         self.embeddings = get_embeddings()
#         self.collection_name = settings.MILVUS_COLLECTION
#         self.uri = f"http://{settings.MILVUS_HOST}:{settings.MILVUS_PORT}"
#         self._client: Optional[MilvusClient] = None
#
#     @property
#     def client(self) -> MilvusClient:
#         if self._client is None:
#             self._client = MilvusClient(uri=self.uri)
#             self._ensure_collection()
#         return self._client
#
#     def _ensure_collection(self) -> None:
#         """如果集合不存在，按预定义 schema 创建"""
#         if self.client.has_collection(self.collection_name):
#             return
#
#         schema = MilvusClient.create_schema(auto_id=True, enable_dynamic_field=True)
#         schema.add_field(field_name="pk", datatype=DataType.INT64, is_primary=True)
#         schema.add_field(
#             field_name="vector",
#             datatype=DataType.FLOAT_VECTOR,
#             dim=settings.EMBEDDING_DIM,
#         )
#         schema.add_field(
#             field_name="text",
#             datatype=DataType.VARCHAR,
#             max_length=65535,
#         )
#
#         index_params = self.client.prepare_index_params()
#         index_params.add_index(
#             field_name="vector",
#             index_type="AUTOINDEX",
#             metric_type="COSINE",
#         )
#
#         self.client.create_collection(
#             collection_name=self.collection_name,
#             schema=schema,
#             index_params=index_params,
#         )
#         logger.info("Milvus 集合已创建: %s", self.collection_name)
#
#     def add_texts(
#         self,
#         texts: List[str],
#         metadatas: Optional[List[dict]] = None,
#     ) -> List[int]:
#         """写入文本，返回主键列表"""
#         vectors = self.embeddings.embed_documents(texts)
#         rows = []
#         for i, (vec, text) in enumerate(zip(vectors, texts)):
#             row = {"vector": vec, "text": text}
#             if metadatas and i < len(metadatas):
#                 row.update(metadatas[i])
#             rows.append(row)
#
#         result = self.client.insert(
#             collection_name=self.collection_name,
#             data=rows,
#         )
#         return result.get("ids", [])
#
#     def similarity_search(self, query: str, k: int = 5) -> List[Document]:
#         """相似度检索，返回 Document 列表"""
#         query_vector = self.embeddings.embed_query(query)
#         results = self.client.search(
#             collection_name=self.collection_name,
#             data=[query_vector],
#             limit=k,
#             output_fields=["text"],
#         )
#         docs: List[Document] = []
#         for hits in results:
#             for hit in hits:
#                 entity = hit.get("entity", {}) or {}
#                 docs.append(
#                     Document(
#                         page_content=entity.get("text", ""),
#                         metadata={"score": hit.get("distance"), **entity},
#                     )
#                 )
#         return docs

#     # def close(self) -> None:
#         if self._client is not None:
#             self._client.close()
#             self._client = None
#
# # 全局单例
# vector_store_manager = VectorStoreManager()
"""
向量库管理模块
直接使用 pymilvus.MilvusClient，不依赖 langchain_milvus。
"""
import logging
from typing import List, Optional
from langchain_core.documents import Document
from pymilvus import DataType, MilvusClient
from app.core.config import settings
from app.rag.embedding_model import get_embeddings

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """向量库管理器，懒加载 MilvusClient"""

    def __init__(self):
        self.embeddings = get_embeddings()
        self.collection_name = settings.MILVUS_COLLECTION
        self.uri = f"http://{settings.MILVUS_HOST}:{settings.MILVUS_PORT}"
        self._client: Optional[MilvusClient] = None

    # ==================== 连接与集合 ====================

    @property
    def client(self) -> MilvusClient:
        """懒加载 MilvusClient，并确保集合已创建、已加载"""
        if self._client is None:
            self._client = MilvusClient(uri=self.uri)
            self._ensure_collection()
        return self._client

    def _ensure_collection(self) -> None:
        """确保集合存在且已加载到内存"""
        # 1. 集合不存在 → 创建
        if not self._client.has_collection(self.collection_name):
            schema = MilvusClient.create_schema(
                auto_id=True,
                enable_dynamic_field=True,
            )
            schema.add_field(
                field_name="pk",
                datatype=DataType.INT64,
                is_primary=True,
            )
            schema.add_field(
                field_name="vector",
                datatype=DataType.FLOAT_VECTOR,
                dim=settings.EMBEDDING_DIM,
            )
            schema.add_field(
                field_name="text",
                datatype=DataType.VARCHAR,
                max_length=65535,
            )

            index_params = self._client.prepare_index_params()
            index_params.add_index(
                field_name="vector",
                index_type="AUTOINDEX",
                metric_type="COSINE",
            )

            self._client.create_collection(
                collection_name=self.collection_name,
                schema=schema,
                index_params=index_params,
            )
            logger.info("Milvus 集合已创建: %s", self.collection_name)

        # 2. 集合已存在 → 确保已加载到内存（搜索必需）
        try:
            self._client.load_collection(self.collection_name)
            logger.info("Milvus 集合已加载: %s", self.collection_name)
        except Exception as e:
            logger.warning("加载 Milvus 集合失败: %s", e)

    # ==================== 写入 ====================

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
    ) -> List[int]:
        """
        向向量库添加文本
        参数：texts - 文本列表
              metadatas - 元数据列表（可选）
        返回：写入的主键 ID 列表
        """
        if not texts:
            return []

        # 1. 生成向量
        vectors = self.embeddings.embed_documents(texts)

        # 2. 组装数据
        rows = []
        for i, (vec, text) in enumerate(zip(vectors, texts)):
            row = {"vector": vec, "text": text}
            if metadatas and i < len(metadatas) and metadatas[i]:
                row.update(metadatas[i])
            rows.append(row)

        # 3. 写入
        result = self.client.insert(
            collection_name=self.collection_name,
            data=rows,
        )

        # 4. 写入后确保集合处于加载状态（新数据要能立即被搜索到）
        try:
            self.client.load_collection(self.collection_name)
        except Exception as e:
            logger.warning("写入后加载集合失败: %s", e)

        ids = result.get("ids", []) if isinstance(result, dict) else []
        logger.info("向量写入成功，共 %d 条", len(ids))
        return ids

    # ==================== 检索 ====================

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """
        相似度检索
        参数：query - 查询文本
              k - 返回条数
        返回：Document 列表
        """
        # 1. 检索前确保集合已加载
        try:
            self.client.load_collection(self.collection_name)
        except Exception as e:
            logger.warning("检索前加载集合失败: %s", e)

        # 2. 生成查询向量
        query_vector = self.embeddings.embed_query(query)

        # 3. 执行检索
        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_vector],
            limit=k,
            output_fields=["text"],
        )

        # 4. 转换为 Document
        docs: List[Document] = []
        for hits in results:
            for hit in hits:
                entity = hit.get("entity", {}) or {}
                docs.append(
                    Document(
                        page_content=entity.get("text", ""),
                        metadata={
                            "score": hit.get("distance"),
                            "pk": hit.get("id"),
                            **entity,
                        },
                    )
                )
        return docs

    # ==================== 资源清理 ====================

    def close(self) -> None:
        """关闭 MilvusClient，释放连接"""
        if self._client is not None:
            try:
                self._client.close()
            except Exception as e:
                logger.warning("关闭 MilvusClient 失败: %s", e)
            finally:
                self._client = None

# 全局单例
vector_store_manager = VectorStoreManager()