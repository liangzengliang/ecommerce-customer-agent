"""
会话模型，对应 sessions 表。
"""

from sqlalchemy import (
    Column, BigInteger, String, Enum, TIMESTAMP, DATETIME,
    Integer, SmallInteger, Boolean, text, ForeignKey,
)
from app.core.database import Base


class Session(Base):
    """会话表 ORM 模型"""

    __tablename__ = "sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(String(64), nullable=False, unique=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(BigInteger, ForeignKey("agents.id"))
    status = Column(Enum("active", "waiting", "transferred", "closed"), default="active")
    channel = Column(String(20), default="web")

    custom_title = Column(String(100), nullable=True)
    is_pinned = Column(Boolean, default=False)

    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    ended_at = Column(DATETIME)
    last_message_at = Column(DATETIME)
    message_count = Column(Integer, default=0)
    satisfaction_score = Column(SmallInteger)