"""
模型配置 Pydantic Schema
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ModelConfigCreate(BaseModel):
    name: str = Field(..., max_length=100)
    provider: str = Field(..., max_length=50)
    type: str
    model: str = Field(..., max_length=200)
    base_url: str = Field(..., max_length=255)
    api_key: str = Field(..., max_length=500)
    temperature: Decimal = Field(0.7, ge=0, le=2)
    max_tokens: int = Field(2048, ge=1, le=128000)
    is_default: bool = False
    is_active: bool = True
    description: Optional[str] = Field(None, max_length=500)


class ModelConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    provider: Optional[str] = Field(None, max_length=50)
    type: Optional[str] = None
    model: Optional[str] = Field(None, max_length=200)
    base_url: Optional[str] = Field(None, max_length=255)
    api_key: Optional[str] = Field(None, max_length=500)
    temperature: Optional[Decimal] = Field(None, ge=0, le=2)
    max_tokens: Optional[int] = Field(None, ge=1, le=128000)
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=500)


class ModelConfigResponse(BaseModel):
    id: int
    name: str
    provider: str
    type: str
    model: str
    base_url: str
    api_key: str
    temperature: Decimal
    max_tokens: int
    is_default: bool
    is_active: bool
    status: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True