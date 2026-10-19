"""
缓存工具
封装 Redis 的常见缓存操作，支持 JSON 序列化。
"""

import json
from typing import Any
from app.core.redis_client import get_redis
import logging

logger = logging.getLogger(__name__)

class CacheHelper:
    """Redis 缓存辅助类"""

    def __init__(self, prefix: str = "cache"):
        """
        参数：prefix - 缓存 key 前缀，用于隔离不同业务
        """
        self.redis = get_redis()
        self.prefix = prefix

    def _key(self, key: str) -> str:
        """生成带前缀的完整 key"""
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> Any | None:
        """
        读取缓存
        参数：key - 缓存键
        返回：反序列化后的值，不存在返回 None
        """
        try:
            raw = await self.redis.get(self._key(key))
            return json.loads(raw) if raw else None
        except Exception as e:
            logger.error(f"缓存读取失败: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        """
        写入缓存
        参数：key - 缓存键
              value - 任意可 JSON 序列化的值
              ttl - 过期时间（秒），默认 300
        """
        try:
            await self.redis.set(
                self._key(key),
                json.dumps(value, ensure_ascii=False, default=str),
                ex=ttl,
            )
        except Exception as e:
            logger.error(f"缓存写入失败: {e}")

    async def delete(self, key: str):
        """删除缓存"""
        try:
            await self.redis.delete(self._key(key))
        except Exception as e:
            logger.error(f"缓存删除失败: {e}")