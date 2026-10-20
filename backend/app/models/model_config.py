"""
模型配置模型
"""

from sqlalchemy import (
    Column, BigInteger, String, Enum, DECIMAL, Integer,
    Boolean, DATETIME, TEXT, text,
)
from app.core.database import Base


class ModelConfig(Base):
    """模型配置表 ORM 模型"""

    __tablename__ = "model_configs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, default=0, index=True)   # owner user id (demo: deleted on logout)
    name = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)
    type = Column(Enum("chat", "embedding"), nullable=False)
    model = Column(String(200), nullable=False)
    base_url = Column(String(255), nullable=False)
    api_key = Column(String(500), nullable=False)
    temperature = Column(DECIMAL(3, 2), default=0.7)
    max_tokens = Column(Integer, default=2048)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)         # ★ 新增：是否启用
    status = Column(Enum("正常", "异常"), default="正常")
    description = Column(String(500))
    created_at = Column(DATETIME, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DATETIME, server_default=text("CURRENT_TIMESTAMP"))