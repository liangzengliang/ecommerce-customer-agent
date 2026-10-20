"""
models 包：统一导出所有 SQLAlchemy ORM 模型。
其他模块直接 from app.models import User 即可。
"""
from app.models.user import User
from app.models.agent import Agent
from app.models.intent import Intent
from app.models.product import Product
from app.models.session import Session
from app.models.order import Order, OrderItem
from app.models.message import Message
from app.models.knowledge import Knowledge
from app.models.rating import ConversationRating
from app.models.ticket import Ticket, TicketLog
from app.models.model_config import ModelConfig       # → 新增

__all__ = [
    # 用户与客服
    "User", "Agent",
    # 意图
    "Intent",
    # 商品
    "Product",
    # 会话与消息
    "Session", "Message",
    # 订单
    "Order", "OrderItem",
    # 知识库
    "Knowledge",
    # 评分
    "ConversationRating",
    # 工单
    "Ticket", "TicketLog",
    # 模型配置
    "ModelConfig",                                     # → 新增
]
