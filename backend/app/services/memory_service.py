"""
会话记忆服务
使用 Redis List 存储每个会话的历史消息，供多轮对话使用。
"""

import json
from app.core.redis_client import get_redis

# 历史记录过期时间：24小时
HISTORY_TTL = 86400

class MemoryService:
    """会话记忆管理器"""

    def __init__(self):
        """初始化 Redis 客户端"""
        self.redis = get_redis()

    def _key(self, session_id: str) -> str:
        """生成 Redis key"""
        return f"session:{session_id}:history"

    async def add_message(self, session_id: str, role: str, content: str):
        """
        添加一条消息到会话历史
        参数：session_id - 会话ID
              role - 角色（user / bot / agent）
              content - 消息内容
        """
        key = self._key(session_id)
        msg = json.dumps({"role": role, "content": content}, ensure_ascii=False)
        await self.redis.rpush(key, msg)   # 从右侧追加
        await self.redis.expire(key, HISTORY_TTL)  # 刷新过期时间

    async def get_history(self, session_id: str, limit: int = 10) -> list:
        """
        获取最近 N 条历史消息
        参数：session_id - 会话ID
              limit - 返回条数
        返回：消息字典列表
        """
        key = self._key(session_id)
        items = await self.redis.lrange(key, -limit, -1)   # 取最后 limit 条
        return [json.loads(i) for i in items]

    async def clear(self, session_id: str):
        """清空会话历史"""
        await self.redis.delete(self._key(session_id))

# 全局单例
memory_service = MemoryService()