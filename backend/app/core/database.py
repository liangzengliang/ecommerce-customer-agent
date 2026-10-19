"""
数据库连接模块
支持 MySQL（生产）与 SQLite（演示模式）两种数据库。
演示模式默认使用 SQLite（sqlite+aiosqlite），无需安装 MySQL。
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# 判断是否 SQLite 演示模式
IS_SQLITE = settings.DATABASE_URL.startswith("sqlite")

if IS_SQLITE:
    # SQLite 演示模式：无需连接池参数
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
    )
else:
    # MySQL 生产模式
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,   # 每次用连接前先 ping 一下
        pool_recycle=300,     # 5 分钟回收一次
        pool_size=10,
        max_overflow=20,
    )

# 异步会话工厂，expire_on_commit=False 避免 commit 后对象属性过期
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# 所有 ORM 模型的基类
Base = declarative_base()

async def get_db():
    """
    FastAPI 依赖注入函数，为每个请求提供一个独立的数据库会话。
    请求结束后自动关闭会话。
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
