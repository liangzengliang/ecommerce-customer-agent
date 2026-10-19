"""
Redis 客户端模块
提供异步 Redis 连接池，用于会话记忆、缓存等。
当 Redis 不可用时（演示环境），自动降级为进程内内存客户端。
"""
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.demo_redis import memory_redis
import logging

logger = logging.getLogger(__name__)

# 创建 Redis 连接池，decode_responses=True 让返回值自动解码为字符串
try:
    redis_pool = aioredis.ConnectionPool.from_url(
        settings.REDIS_URL,
        max_connections=20,
        decode_responses=True,
    )
    _redis_available = True
except Exception as e:
    logger.warning(f"Redis 连接池创建失败，降级为内存模式: {e}")
    redis_pool = None
    _redis_available = False

def get_redis():
    """
    获取 Redis 客户端实例（从连接池中取）
    如果 Redis 不可用，返回内存降级客户端。
    """
    # 演示模式：直接使用进程内内存客户端，避免依赖真实 Redis 服务
    if settings.DEMO_MODE:
        return memory_redis
    if redis_pool is not None:
        try:
            return aioredis.Redis(connection_pool=redis_pool)
        except Exception as e:
            logger.warning(f"获取 Redis 客户端失败，降级为内存模式: {e}")
    return memory_redis


# 供其他模块判断 Redis 是否可用
def is_redis_available() -> bool:
    """Redis 是否可用"""
    return redis_pool is not None
