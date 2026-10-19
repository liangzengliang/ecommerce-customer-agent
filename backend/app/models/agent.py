"""
客服坐席模型，对应 agents 表。
存储人工客服的基本信息和在线状态。
"""
from sqlalchemy import Column, BigInteger, String, Boolean, Enum, TIMESTAMP, text
from app.core.database import Base

class Agent(Base):
    """客服坐席表 ORM 模型"""
    __tablename__ = "agents"

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # 客服ID
    name = Column(String(50), nullable=False)  # 客服姓名
    email = Column(String(100))  # 邮箱
    description = Column(String(255))  # 描述
    is_active = Column(Boolean, default=True)  # 是否启用
    status = Column(Enum("online", "busy", "offline"), default="offline")  # 在线状态
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))  # 创建时间