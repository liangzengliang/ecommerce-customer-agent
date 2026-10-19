"""
Agent 工具测试
验证订单查询、工单创建等工具函数。
"""

import pytest
from backend.app.agents.tools.query_order import query_order
from backend.app.agents.tools.create_ticket import create_ticket

@pytest.mark.asyncio
async def test_query_order_not_found():
    """测试查询不存在的订单"""
    result = await query_order("NOT_EXIST_ORDER_NO")
    assert result["found"] is False
    assert "未找到" in result["message"]

@pytest.mark.asyncio
async def test_create_ticket():
    """测试创建工单"""
    result = await create_ticket(
        user_id=1,
        session_id="test_session_003",
        ticket_type="complaint",
        title="测试工单",
        content="这是一条测试工单",
    )
    assert result["status"] == "pending"
    assert result["ticket_no"].startswith("TK")