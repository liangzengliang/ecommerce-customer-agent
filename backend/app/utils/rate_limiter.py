"""
限流工具（函数级别）
供业务代码主动调用，比如限制 LLM 调用频率。
"""

import time
from app.core.redis_client import get_redis
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """基于 Redis 的滑动窗口限流器"""

    def __init__(self, name: str, max_calls: int = 10, window: int = 60):
        """
        参数：name - 限流器名称（用于隔离不同的限流规则）
              max_calls - 窗口内最大调用次数
              window - 窗口大小（秒）
        """
        self.redis = get_redis()
        self.name = name
        self.max_calls = max_calls
        self.window = window

    def _key(self, identity: str) -> str:
        """生成限流 key"""
        window_bucket = int(time.time() // self.window)
        return f"rl:{self.name}:{identity}:{window_bucket}"

    async def is_allowed(self, identity: str) -> bool:
        """
        判断是否允许本次调用
        参数：identity - 调用方标识（如 user_id、IP）
        返回：True 表示允许，False 表示超限
        """
        key = self._key(identity)
        try:
            current = await self.redis.incr(key)
            if current == 1:
                await self.redis.expire(key, self.window)
            return current <= self.max_calls
        except Exception as e:
            # Redis 故障时放行
            logger.error(f"限流器异常: {e}")
            return True

    async def remaining(self, identity: str) -> int:
        """
        查询剩余可用次数
        参数：identity - 调用方标识
        返回：剩余次数
        """
        key = self._key(identity)
        try:
            current = await self.redis.get(key)
            used = int(current) if current else 0
            return max(0, self.max_calls - used)
        except Exception as e:
            logger.error(f"限流器查询异常: {e}")
            return self.max_calls