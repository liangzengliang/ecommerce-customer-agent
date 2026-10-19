"""
消息模型，对应 messages 表。
记录会话中的每一条用户/机器人/客服消息。
"""

from sqlalchemy import (
    Column, BigInteger, String, Enum, TEXT, JSON,
    DATETIME, DECIMAL, Boolean, ForeignKey, Index, text,
)
from app.core.database import Base


class Message(Base):
    """消息表 ORM 模型"""

    __tablename__ = "messages"

    id = Column(BigInteger, primary_key=True, autoincrement=True)                # 消息ID
    session_id = Column(
        String(64),
        ForeignKey("sessions.session_id", ondelete="CASCADE"),
        nullable=False,
    )                                                                            # 会话ID
    sender_type = Column(Enum("user", "bot", "agent"), nullable=False)           # 发送方类型
    sender_id = Column(BigInteger)                                               # 发送方ID
    content = Column(TEXT, nullable=False)                                       # 消息内容
    content_type = Column(
        Enum("text", "image", "voice", "file", "quick_reply"),
        default="text",
    )                                                                            # 内容类型
    intent_id = Column(BigInteger, ForeignKey("intents.id", ondelete="SET NULL")) # 意图ID
    intent_confidence = Column(DECIMAL(5, 4))                                    # 意图置信度
    sentiment = Column(Enum("positive", "neutral", "negative"))                  # 情感倾向
    sentiment_score = Column(DECIMAL(3, 2))                                      # 情感得分
    is_human_transfer = Column(Boolean, default=False)                           # 是否已转人工
    is_generated = Column(Boolean, default=False)                                # 是否AI生成
    metadata_ = Column("metadata", JSON)                                         # 元数据
    created_at = Column(DATETIME, server_default=text("CURRENT_TIMESTAMP"))      # 创建时间

    __table_args__ = (
        Index("idx_session_created", "session_id", "created_at"),
    )