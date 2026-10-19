"""
创建工单工具
在数据库中创建工单并写入日志。
"""

import uuid
from app.core.database import AsyncSessionLocal
from app.models.ticket import Ticket, TicketLog

async def create_ticket(user_id: int, session_id: str, ticket_type: str,
                        title: str, content: str) -> dict:
    """
    创建工单
    参数：user_id - 用户ID
          session_id - 会话ID
          ticket_type - 工单类型（complaint/refund/consult/suggestion/other）
          title - 标题
          content - 内容
    返回：dict，含 ticket_no / status
    """
    async with AsyncSessionLocal() as db:
        # 生成工单号：TK + 12 位随机十六进制
        ticket_no = f"TK{uuid.uuid4().hex[:12].upper()}"
        ticket = Ticket(
            ticket_no=ticket_no,
            session_id=session_id,
            user_id=user_id,
            type=ticket_type,
            title=title,
            content=content,
            status="pending",
            priority="normal",
        )
        db.add(ticket)
        await db.flush()   # 拿到 ticket.id

        # 写入工单日志
        log = TicketLog(
            ticket_id=ticket.id,
            operator_type="system",
            action="创建",
            content=f"系统自动创建工单：{title}",
        )
        db.add(log)
        await db.commit()
        return {"ticket_no": ticket_no, "status": "pending"}