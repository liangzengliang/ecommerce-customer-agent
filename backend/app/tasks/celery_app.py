"""
Celery 实例配置
使用 Redis 作为 broker 和 backend，与项目中的 Redis 共用。
"""

from celery import Celery
from app.core.config import settings

# 创建 Celery 实例
celery_app = Celery(
    "customer_service",                       # 应用名
    broker=settings.REDIS_URL,                # 消息队列（broker）
    backend=settings.REDIS_URL,               # 结果存储（backend）
    include=[
        "app.tasks.vectorize_task",           # 自动发现任务模块
        "app.tasks.import_task",
    ],
)

# Celery 配置
celery_app.conf.update(
    task_serializer="json",                   # 任务序列化格式
    result_serializer="json",                 # 结果序列化格式
    accept_content=["json"],                  # 接受的内容类型
    timezone="Asia/Shanghai",                 # 时区
    enable_utc=False,                         # 不使用 UTC
    task_track_started=True,                  # 记录任务开始状态
    task_time_limit=600,                      # 单任务硬超时（秒）
    task_soft_time_limit=540,                 # 软超时（秒）
    worker_max_tasks_per_child=100,           # 每个 worker 处理 100 个任务后重启，防内存泄漏
)