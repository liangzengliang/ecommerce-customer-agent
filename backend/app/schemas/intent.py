"""
意图相关的 Pydantic 模型
用于意图配置接口（管理后台维护意图体系）。
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class IntentCreate(BaseModel):
    """创建意图请求体"""
    intent_name: str = Field(..., max_length=100, description="意图名称")
    intent_code: str = Field(..., max_length=50, description="意图编码，如 ORD_001")
    description: Optional[str] = Field(None, max_length=255)
    handler_type: str = Field(..., description="处理类型：rag/tool/transfer/fallback")
    handler_config: Optional[Dict[str, Any]] = Field(None, description="处理配置")
    sample_utterances: Optional[str] = Field(None, description="示例语料")
    priority: int = Field(0, description="优先级，数值越大越优先")
    is_active: bool = True

class IntentUpdate(BaseModel):
    """更新意图请求体"""
    intent_name: Optional[str] = None
    description: Optional[str] = None
    handler_type: Optional[str] = None
    handler_config: Optional[Dict[str, Any]] = None
    sample_utterances: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None

class IntentResponse(BaseModel):
    """意图信息响应体"""
    id: int
    intent_name: str
    intent_code: str
    confidence: float
    description: Optional[str] = None
    handler_type: str
    handler_config: Optional[Dict[str, Any]] = None
    sample_utterances: Optional[str] = None
    priority: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IntentClassifyRequest(BaseModel):
    """意图识别请求体（供调试接口使用）"""
    text: str = Field(..., min_length=1, max_length=2000, description="待识别的文本")

class IntentClassifyResponse(BaseModel):
    """意图识别响应体"""
    intent_code: str
    intent_name: str
    confidence: float
    entities: List[Dict[str, Any]] = []
    slots: Dict[str, Any] = {}