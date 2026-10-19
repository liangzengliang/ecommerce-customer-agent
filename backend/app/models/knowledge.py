"""
知识库模型，对应 knowledge 表。
存储问答对，向量存 Milvus，MySQL 只存元数据。
"""
from sqlalchemy import Column, BigInteger, String, TEXT, Integer, Boolean, DECIMAL, DATETIME, text
from app.core.database import Base

class Knowledge(Base):
    """知识库表 ORM 模型"""
    __tablename__ = "knowledge"

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # 知识ID
    category = Column(String(50), nullable=False)  # 分类（商品/政策/FAQ）
    question = Column(TEXT, nullable=False)  # 问题
    answer = Column(TEXT, nullable=False)  # 答案
    keywords = Column(String(500))  # 关键词
    vector_id = Column(String(100))  # Milvus 中的向量ID
    embedding_model = Column(String(50), default="BAAI/bge-m3")  # 使用的嵌入模型
    hit_count = Column(Integer, default=0)  # 命中次数
    satisfaction_rate = Column(DECIMAL(5, 2))  # 满意度
    is_active = Column(Boolean, default=True)  # 是否启用
    created_at = Column(DATETIME, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DATETIME, server_default=text("CURRENT_TIMESTAMP"))