"""
工单与工单日志模型，对应 tickets 和 ticket_logs 表。
用于记录需要人工跟进的售后、投诉等任务。
"""
from sqlalchemy import Column, BigInteger, String, Enum, TEXT, DATETIME, ForeignKey, text, TIMESTAMP
from app.core.database import Base

class Ticket(Base):
    """工单表 ORM 模型"""
    __tablename__ = "tickets"

    id = Column(BigInteger, primary_key=True, autoincrement=True)                    # 工单ID
    ticket_no = Column(String(32), nullable=False, unique=True)                       # 工单号
    session_id = Column(String(64))                                                   # 关联会话ID
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # 提交用户
    order_id = Column(BigInteger, ForeignKey("orders.id"))                            # 关联订单
    type = Column(Enum("complaint", "refund", "consult", "suggestion", "other"), nullable=False)  # 工单类型
    title = Column(String(200), nullable=False)                                       # 标题
    content = Column(TEXT, nullable=False)                                            # 内容
    status = Column(Enum("pending", "processing", "resolved", "closed"), default="pending")  # 状态
    priority = Column(Enum("low", "normal", "high", "urgent"), default="normal")      # 优先级
    assigned_to = Column(BigInteger, ForeignKey("agents.id", ondelete="SET NULL"))    # 处理客服
    resolution = Column(TEXT)                                                         # 处理结果
    resolved_at = Column(DATETIME)                                                    # 解决时间
    created_at = Column(DATETIME, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DATETIME, server_default=text("CURRENT_TIMESTAMP"))


class TicketLog(Base):
    """工单处理日志表 ORM 模型，记录工单的每一次操作"""
    __tablename__ = "ticket_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)   # 日志ID
    ticket_id = Column(BigInteger, ForeignKey("tickets.id"), nullable=False)  # 工单ID
    operator_type = Column(Enum("user", "agent", "system"), nullable=False)   # 操作方
    operator_id = Column(BigInteger)                                          # 操作人ID
    action = Column(String(50), nullable=False)                               # 操作类型
    content = Column(TEXT)                                                    # 操作内容
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))