"""
限流中间件
基于 Redis 实现固定窗口限流：每个 IP 每分钟最多 N 次请求。
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.redis_client import get_redis
import time
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """基于 Redis 的限流中间件"""

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        """
        参数：app - ASGI 应用
              max_requests - 窗口内最大请求数
              window_seconds - 窗口大小（秒）
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.redis = get_redis()

    async def dispatch(self, request: Request, call_next):
        """对每个请求做限流判断"""
        # 获取客户端 IP
        client_ip = request.client.host if request.client else "unknown"

        # 计算当前窗口的 key
        window = int(time.time() // self.window_seconds)
        key = f"rate_limit:{client_ip}:{window}"

        try:
            # 计数 +1，并设置过期时间
            current = await self.redis.incr(key)
            if current == 1:
                await self.redis.expire(key, self.window_seconds)

            # 超过阈值则拒绝
            if current > self.max_requests:
                logger.warning(f"限流触发: {client_ip} 请求数 {current}")
                raise HTTPException(
                    status_code=429,
                    detail=f"请求过于频繁，请 {self.window_seconds} 秒后再试",
                )
        except HTTPException:
            raise
        except Exception as e:
            # Redis 故障时放行，避免影响主流程
            logger.error(f"限流中间件异常: {e}")

        return await call_next(request)