"""
CORS 中间件配置
统一处理跨域请求，开发环境放开所有来源。
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app: FastAPI, allow_origins: list[str] | None = None):
    """
    为 FastAPI 应用添加 CORS 中间件
    参数：app - FastAPI 实例
          allow_origins - 允许的来源列表，默认 ["*"]
    """
    origins = allow_origins or ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )