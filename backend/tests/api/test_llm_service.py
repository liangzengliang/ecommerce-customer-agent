"""
LLM 可用性测试
验证：网友在模型配置页面配置了默认对话模型后，is_llm_available() 应返回 True（聊天会使用该 LLM）
"""
import pytest
from app.services.llm_service import is_llm_available
from app.services.model_config_service import model_config_service
from app.core.database import AsyncSessionLocal
from app.models.model_config import ModelConfig


@pytest.mark.asyncio
async def test_llm_available_with_db_config(client):
    """数据库存在默认对话模型配置时，is_llm_available() 返回 True"""
    # 确保 .env 没有 OPENAI_API_KEY 时也能通过数据库配置判断
    # 先确认初始状态：无数据库配置时（可能 .env 无 key）不可用
    # 创建默认对话模型配置
    async with AsyncSessionLocal() as db:
        cfg = ModelConfig(
            name="测试默认模型",
            provider="openai",
            type="chat",
            model="gpt-4o-mini",
            base_url="https://api.openai.com/v1",
            api_key="sk-test-key",
            temperature=0.3,
            max_tokens=2048,
            is_default=True,
            is_active=True,
            status="正常",
        )
        db.add(cfg)
        await db.commit()

    # 数据库有默认配置 → LLM 可用
    available = await is_llm_available()
    assert available is True
