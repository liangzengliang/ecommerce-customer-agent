# api 包：FastAPI 路由层
"""
api 包：FastAPI 路由层。
统一管理所有 API 版本（当前为 v1）。
"""

from app.api.v1 import router as v1_router

__all__ = ["v1_router"]