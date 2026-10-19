"""
意图识别记录模型，对应 intents 表。
存储意图分类的配置信息，供 NLU 模块使用。
"""
from sqlalchemy import Column, BigInteger, String, Enum, JSON, TEXT, Integer, Boolean, DECIMAL, DATETIME, text
from app.core.database import Base

class Intent(Base):
    """意图表 ORM 模型"""
    __tablename__ = "intents"

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # 意图ID
    intent_name = Column(String(100), nullable=False)  # 意图名称
    intent_code = Column(String(50), nullable=False, unique=True)  # 意图编码（如 ORD_001）
    confidence = Column(DECIMAL(5, 4), default=0)  # 默认置信度
    description = Column(String(255))  # 意图描述
    handler_type = Column(Enum("rag", "tool", "transfer", "fallback"), nullable=False)  # 处理类型
    handler_config = Column(JSON)  # 处理配置（工具名、参数等）
    sample_utterances = Column(TEXT)  # 示例语料
    priority = Column(Integer, default=0)  # 优先级
    is_active = Column(Boolean, default=True)  # 是否启用
    created_at = Column(DATETIME, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DATETIME, server_default=text("CURRENT_TIMESTAMP"))
