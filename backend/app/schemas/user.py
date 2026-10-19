"""
用户相关的 Pydantic 模型
用于用户管理接口的请求参数校验和响应序列化。
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """创建用户请求体（管理员在后台创建用户时使用）"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="明文密码")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    user_type: str = Field("customer", description="用户类型：customer/agent/admin")

class UserUpdate(BaseModel):
    """更新用户信息请求体，所有字段可选，只更新传入的字段"""
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    avatar_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    status: Optional[int] = Field(None, ge=0, le=1, description="1正常 0禁用")

class UserResponse(BaseModel):
    """用户信息响应体（不包含密码哈希）"""
    id: int
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    user_type: str
    avatar_url: Optional[str] = None
    is_active: bool
    status: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True   # 允许从 ORM 对象直接转换