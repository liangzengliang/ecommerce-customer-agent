"""
对话相关的 Pydantic 模型
定义聊天请求/响应、NLU 识别结果、实体等结构。
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    """对话请求体"""
    message: str = Field(..., min_length=1, max_length=2000, description="用户消息")
    session_id: Optional[str] = Field(None, description="会话ID，首次为空")

class ChatResponse(BaseModel):
    """对话响应体"""
    session_id: str
    content: str
    intent_code: Optional[str] = None
    sentiment: Optional[str] = None

class Entity(BaseModel):
    """实体抽取结果"""
    type: str                              # 实体类型（order_no / phone 等）
    value: str                             # 原始值
    normalized: Optional[str] = None       # 归一化后的值
    start: Optional[int] = None            # 在原文中的起始位置
    end: Optional[int] = None              # 结束位置
    confidence: float = 0.0                # 置信度
    slot: Optional[str] = None             # 对应的槽位名

class NLUResult(BaseModel):
    """NLU 整体识别结果"""
    intent_code: str                       # 意图编码
    intent_name: str                       # 意图名称
    confidence: float                      # 意图置信度
    sentiment: str                         # 情感倾向
    sentiment_score: float                 # 情感得分
    entities: List[Entity] = []            # 实体列表
    slots: Dict[str, Any] = {}             # 槽位字典
    missing_slots: List[str] = []          # 缺失的槽位
    need_clarification: bool = False       # 是否需要澄清
    clarification_question: Optional[str] = None  # 澄清问题