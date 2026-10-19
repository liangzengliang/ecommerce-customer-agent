"""
tasks 包：Celery 异步任务。
用于处理耗时操作，如知识库向量化、批量导入等。
"""

from app.tasks.celery_app import celery_app
from app.tasks.vectorize_task import vectorize_knowledge
from app.tasks.import_task import import_knowledge_file

__all__ = ["celery_app", "vectorize_knowledge", "import_knowledge_file"]