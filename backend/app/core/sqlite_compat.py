"""
SQLite 兼容建表层
用途：演示模式使用 SQLite 时，在不修改任何 MySQL ORM 模型的前提下，
生成 SQLite 兼容的建表 DDL（自动移除 MySQL 特有的
`ON UPDATE CURRENT_TIMESTAMP` 等语法）。

MySQL 生产环境不受影响：本模块只在 SQLite 模式下被调用。
"""
import logging
from sqlalchemy import text
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import sqlite

from app.core.database import Base

logger = logging.getLogger(__name__)


def build_sqlite_ddl() -> list:
    """使用 SQLite 方言编译所有表的建表 SQL，并清理 MySQL 特有语法"""
    import re
    dialect = sqlite.dialect()
    ddl_list = []
    for table in Base.metadata.sorted_tables:
        ddl = str(CreateTable(table).compile(dialect=dialect))
        # 移除 MySQL 特有的 ON UPDATE CURRENT_TIMESTAMP（SQLite 不支持）
        ddl = ddl.replace("ON UPDATE CURRENT_TIMESTAMP", "")
        # 清理可能产生的双空格 / 尾部逗号等问题
        ddl = ddl.replace("DEFAULT CURRENT_TIMESTAMP  ", "DEFAULT CURRENT_TIMESTAMP")
        # SQLite 中只有 INTEGER PRIMARY KEY 才会自增（rowid 别名）。
        # ORM 模型统一使用 BigInteger 主键，编译为 BIGINT 后 SQLite 不会自增，
        # 插入时 id 为 NULL 会报 NOT NULL constraint failed。
        # 这里将单列 id 主键转换为 SQLite 自增主键。
        if re.search(r"^\s*id BIGINT NOT NULL,?\s*$", ddl, re.M) and re.search(
            r"^\s*PRIMARY KEY \(id\),?\s*$", ddl, re.M
        ):
            ddl = re.sub(
                r"^\s*id BIGINT NOT NULL,?\s*$",
                "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,",
                ddl,
                flags=re.M,
            )
            ddl = re.sub(
                r"^\s*PRIMARY KEY \(id\),?\s*$",
                "",
                ddl,
                flags=re.M,
            )
        # 清理移除 PRIMARY KEY 行后可能残留的尾部逗号（如 "...,\n)"）
        ddl = re.sub(r",\s*\)", ")", ddl)
        ddl_list.append(ddl)
    return ddl_list


async def create_all_sqlite(engine) -> None:
    """在 SQLite 引擎上执行兼容建表 DDL"""
    ddl_list = build_sqlite_ddl()
    async with engine.begin() as conn:
        for ddl in ddl_list:
            try:
                await conn.execute(text(ddl))
            except Exception as e:  # 表已存在等错误忽略
                logger.warning(f"SQLite 建表跳过: {e}")
    logger.info(f"SQLite 兼容建表完成（{len(ddl_list)} 张表）")
