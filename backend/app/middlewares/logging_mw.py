"""
请求日志中间件
记录每个请求的方法、路径、耗时、状态码。
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger("request")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next):
        """
        记录请求进入和响应的耗时
        参数：request - 请求对象
              call_next - 下游处理函数
        返回：响应
        """
        start = time.time()
        response = await call_next(request)
        elapsed_ms = (time.time() - start) * 1000

        logger.info(
            f"{request.method} {request.url.path} "
            f"-> {response.status_code} "
            f"({elapsed_ms:.1f}ms)"
        )
        return response