"""
模型配置服务
从数据库读取默认模型配置，供 LLM / Embedding 使用
"""

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.model_config import ModelConfig
import logging

logger = logging.getLogger(__name__)


class ModelConfigService:

    async def get_default_chat_model(self) -> dict | None:
        """获取默认的对话模型配置（只查启用的）"""
        async with AsyncSessionLocal() as db:
            stmt = (
                select(ModelConfig)
                .where(ModelConfig.type == "chat")
                .where(ModelConfig.is_default == True)   # noqa: E712
                .where(ModelConfig.is_active == True)    # ★ 只查启用的
                .where(ModelConfig.status == "正常")
                .where(ModelConfig.api_key != "")       # ★ 只选有 API Key 的
                .limit(1)
            )
            result = await db.execute(stmt)
            config = result.scalar_one_or_none()
            if not config:
                return None
            return {
                "name": config.name,
                "provider": config.provider,
                "model": config.model,
                "base_url": config.base_url,
                "api_key": config.api_key,
                "temperature": float(config.temperature) if config.temperature else 0.3,
                "max_tokens": config.max_tokens or 2048,
            }

    async def get_default_embedding_model(self) -> dict | None:
        """获取默认的嵌入模型配置（只查启用的）"""
        async with AsyncSessionLocal() as db:
            stmt = (
                select(ModelConfig)
                .where(ModelConfig.type == "embedding")
                .where(ModelConfig.is_default == True)   # noqa: E712
                .where(ModelConfig.is_active == True)    # ★ 只查启用的
                .where(ModelConfig.status == "正常")
                .limit(1)
            )
            result = await db.execute(stmt)
            config = result.scalar_one_or_none()
            if not config:
                return None
            return {
                "name": config.name,
                "provider": config.provider,
                "model": config.model,
                "base_url": config.base_url,
                "api_key": config.api_key,
            }


model_config_service = ModelConfigService()