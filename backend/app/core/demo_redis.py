"""
演示模式内存 Redis 降级客户端
当真实 Redis 不可用时，使用进程内字典模拟 Redis 常用命令，
保证演示环境（无 Redis）也能正常运行。
注意：内存数据在服务重启后丢失，仅用于演示。
"""
import json
import time
import asyncio
from typing import Any, List, Optional


class MemoryRedis:
    """用 Python dict 模拟 Redis 的常用异步接口"""

    def __init__(self):
        self._data: dict[str, list] = {}
        self._expire: dict[str, float] = {}
        self._lock = asyncio.Lock()

    # ---------- 连接 ----------
    async def ping(self) -> bool:
        return True

    async def close(self):
        return None

    # ---------- List 操作 ----------
    async def rpush(self, key: str, *values: Any) -> int:
        async with self._lock:
            if key not in self._data:
                self._data[key] = []
            self._data[key].extend(values)
            return len(self._data[key])

    async def lrange(self, key: str, start: int, end: int) -> list:
        items = self._data.get(key, [])
        if not items:
            return []
        # 支持负索引（Redis 语义）
        if start < 0:
            start = max(len(items) + start, 0)
        if end < 0:
            end = len(items) + end
        return items[start:end + 1]

    async def delete(self, *keys: str) -> int:
        deleted = 0
        for k in keys:
            if k in self._data:
                del self._data[k]
                deleted += 1
            self._expire.pop(k, None)
        return deleted

    async def expire(self, key: str, seconds: int) -> bool:
        self._expire[key] = time.time() + seconds
        return True

    # ---------- 通用 ----------
    async def get(self, key: str):
        if key in self._expire and time.time() > self._expire[key]:
            self._data.pop(key, None)
            self._expire.pop(key, None)
            return None
        val = self._data.get(key)
        if isinstance(val, list) and len(val) == 1:
            return val[0]
        return val

    async def set(self, key: str, value: Any, ex: int = None):
        self._data[key] = [value] if not isinstance(value, list) else value
        if ex:
            self._expire[key] = time.time() + ex
        return True

    async def exists(self, *keys: str) -> int:
        return sum(1 for k in keys if k in self._data)


# 全局单例
memory_redis = MemoryRedis()
