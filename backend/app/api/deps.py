"""
依赖注入统一出口
方便其他模块 import 常用的 Depends。
"""

from app.core.database import get_db
from app.core.security import get_current_user

__all__ = ["get_db", "get_current_user"]