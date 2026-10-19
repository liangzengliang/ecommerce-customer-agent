"""
会话记忆服务测试
验证 Redis 中会话历史的读写、过期、清空。
"""

import pytest
from backend.app.services.memory_service import memory_service

@pytest.mark.asyncio
async def test_add_and_get_history():
    """测试添加消息后能正确读回"""
    session_id = "test_session_001"
    await memory_service.clear(session_id)

    await memory_service.add_message(session_id, "user", "你好")
    await memory_service.add_message(session_id, "bot", "您好，有什么可以帮您？")

    history = await memory_service.get_history(session_id)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "你好"
    assert history[1]["role"] == "bot"

    await memory_service.clear(session_id)

@pytest.mark.asyncio
async def test_clear_history():
    """测试清空历史"""
    session_id = "test_session_002"
    await memory_service.add_message(session_id, "user", "测试")
    await memory_service.clear(session_id)

    history = await memory_service.get_history(session_id)
    assert len(history) == 0