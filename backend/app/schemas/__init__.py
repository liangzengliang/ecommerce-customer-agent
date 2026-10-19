# schemas 包：存放所有 Pydantic 请求/响应模型
"""
schemas 包：存放所有 Pydantic 请求/响应模型。
统一导出常用 schema，方便其他模块直接 import。
"""

# ===== 认证 =====
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
# ===== 对话 =====
from app.schemas.chat import ChatRequest, ChatResponse, Entity, NLUResult
# ===== 用户 =====
from app.schemas.user import UserCreate, UserUpdate, UserResponse
# ===== 客服Agent =====
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse
# ===== 意图 =====
from app.schemas.intent import IntentCreate, IntentUpdate, IntentResponse,IntentClassifyRequest,IntentClassifyResponse
# ===== 订单 =====
from app.schemas.order import OrderResponse, OrderItemResponse, OrderUpdate,OrderQuery
# ===== 商品 =====
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse,ProductSearchRequest

# 模型配置   → 新增
from app.schemas.model_config import (
    ModelConfigCreate, ModelConfigUpdate, ModelConfigResponse,
)
# ===== 项目管理 =====
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    ProjectMemberCreate, ProjectMemberResponse,
    ProjectTaskCreate, ProjectTaskUpdate, ProjectTaskResponse,
    ProjectRiskCreate, ProjectRiskUpdate, ProjectRiskResponse,
    ProjectMeetingCreate, ProjectMeetingUpdate, ProjectMeetingResponse,
    ProjectDocumentCreate, ProjectDocumentUpdate, ProjectDocumentResponse,
    ProjectChangeCreate, ProjectChangeUpdate, ProjectChangeResponse,
    ProjectCommentCreate, ProjectCommentResponse,
)


__all__ = [
    # auth
    "LoginRequest", "RegisterRequest", "TokenResponse",
    # chat
    "ChatRequest", "ChatResponse", "Entity", "NLUResult",
    # user
    "UserCreate", "UserUpdate", "UserResponse",
    # agent
    "AgentCreate", "AgentUpdate", "AgentResponse",
    # intent
    "IntentCreate", "IntentUpdate", "IntentResponse","IntentClassifyRequest", "IntentClassifyResponse",
    # order
    "OrderResponse", "OrderItemResponse", "OrderUpdate","OrderQuery",
    # product
    "ProductCreate", "ProductUpdate", "ProductResponse","ProductSearchRequest",
    # model
    "ModelConfigCreate", "ModelConfigUpdate", "ModelConfigResponse",
    # project
    "ProjectCreate", "ProjectUpdate", "ProjectResponse",
    "ProjectMemberCreate", "ProjectMemberResponse",
    "ProjectTaskCreate", "ProjectTaskUpdate", "ProjectTaskResponse",
    "ProjectRiskCreate", "ProjectRiskUpdate", "ProjectRiskResponse",
    "ProjectMeetingCreate", "ProjectMeetingUpdate", "ProjectMeetingResponse",
    "ProjectDocumentCreate", "ProjectDocumentUpdate", "ProjectDocumentResponse",
    "ProjectChangeCreate", "ProjectChangeUpdate", "ProjectChangeResponse",
    "ProjectCommentCreate", "ProjectCommentResponse",
]