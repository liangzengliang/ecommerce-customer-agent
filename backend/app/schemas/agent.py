"""
客服坐席相关的 Pydantic 模型
用于客服管理接口（后台管理端）的请求和响应。
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class AgentCreate(BaseModel):
    """创建客服请求体"""
    name: str = Field(..., min_length=1, max_length=50, description="客服姓名")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    description: Optional[str] = Field(None, max_length=255, description="描述")

class AgentUpdate(BaseModel):
    """更新客服信息请求体"""
    name: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    status: Optional[str] = Field(None, description="online/busy/offline")

class AgentResponse(BaseModel):
    """客服信息响应体"""
    id: int
    name: str
    email: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    status: str
    created_at: datetime

    class Config:
        from_attributes = True