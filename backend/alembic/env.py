"""
Alembic 迁移环境配置
从项目 settings 读取数据库连接串，自动检测模型变化。
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

# 导入项目配置和所有模型（必须导入，否则 autogenerate 检测不到表）
from backend.app.core.config import settings
from backend.app.core.database import Base
from backend.app.models import *  # noqa: F401,F403

# Alembic 配置对象
config = context.config

# 配置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 将项目数据库连接串注入 config（同步驱动，用于迁移）
# 注意：项目用 aiomysql，但 Alembic 迁移用同步驱动 pymysql
sync_url = settings.DATABASE_URL.replace("mysql+aiomysql://", "mysql+pymysql://")
config.set_main_option("sqlalchemy.url", sync_url)

# 目标元数据，供 autogenerate 使用
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """
    离线模式：只生成 SQL 脚本，不实际连接数据库。
    用法：alembic upgrade head --sql
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,           # 比较字段类型变化
        compare_server_default=True, # 比较默认值变化
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection) -> None:
    """在同步连接上执行迁移（由异步入口调用）"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """异步模式：创建异步引擎并执行迁移"""
    connectable = create_async_engine(sync_url, poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    """在线模式入口：执行异步迁移"""
    asyncio.run(run_async_migrations())

# 根据运行模式选择入口
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()