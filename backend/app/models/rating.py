"""
会话评分模型，对应 conversation_ratings 表。
用户对会话进行 1-5 星评分。
"""
from sqlalchemy import Column, BigInteger, String, SmallInteger, TEXT, TIMESTAMP, ForeignKey, text
from app.core.database import Base

class ConversationRating(Base):
    """会话评分表 ORM 模型"""
    __tablename__ = "conversation_ratings"

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # 评分ID
    session_id = Column(String(64), ForeignKey("sessions.session_id"), nullable=False)  # 会话ID
    rating_score = Column(SmallInteger, nullable=False)  # 评分 1-5
    rating_comment = Column(TEXT)  # 评价内容
    rating_time = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))  # 评分时间