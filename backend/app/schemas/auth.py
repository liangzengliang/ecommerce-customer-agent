"""
认证相关的 Pydantic 模型
用于登录、注册接口的请求参数和响应结构校验。
"""

from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    """登录请求体"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")

class RegisterRequest(BaseModel):
    """注册请求体"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    email: str | None = None
    phone: str | None = None

class TokenResponse(BaseModel):
    """登录/注册成功后的响应体，含 JWT"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str