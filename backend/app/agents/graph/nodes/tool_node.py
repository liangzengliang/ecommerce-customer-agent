"""
工具调用节点
根据意图编码和槽位，调用具体的业务工具（订单查询、工单、转人工等）。
"""

from app.agents.graph.state import AgentState
from app.agents.tools.query_order import query_order
from app.agents.tools.query_product import query_product
from app.agents.tools.create_ticket import create_ticket
from app.agents.tools.transfer_human import transfer_human
from app.agents.tools.refund_tool import request_refund   # ← 补上这行
import logging

logger = logging.getLogger(__name__)

async def call_tools(state: AgentState) -> AgentState:
    """
    工具调用节点
    参数：state - 当前状态
    返回：更新后的状态（填充 tool_results / missing_slots）
    """
    code = state["intent_code"]
    slots = state["slots"]
    results = []

    try:
        # 订单相关意图 → 查询订单
        if code in ("ORD_001", "ORD_003", "ORD_004", "ORD_005"):
            order_no = slots.get("order_no")
            if order_no:
                result = await query_order(order_no)
                results.append({"tool": "query_order", "result": result})
            else:
                state["missing_slots"] = ["order_no"]

        # 库存查询 → 查询商品
        elif code == "PRD_006":
            product_name = slots.get("product_name") or state["user_message"]
            result = await query_product(product_name)
            results.append({"tool": "query_product", "result": result})

        # 申请退款 → 调用退款工具（新增分支）
        elif code == "PAY_002":
            order_no = slots.get("order_no")
            if order_no:
                result = await request_refund(order_no, state["user_message"])
                results.append({"tool": "request_refund", "result": result})
            else:
                state["missing_slots"] = ["order_no"]

        # 投诉/退款/建议 → 创建工单
        elif code in ("CMP_001", "CMP_002", "CMP_004"):
            result = await create_ticket(
                user_id=state["user_id"],
                session_id=state["session_id"],
                ticket_type="complaint" if code == "CMP_001" else "refund",
                title=state["user_message"][:50],
                content=state["user_message"],
            )
            results.append({"tool": "create_ticket", "result": result})

        # 人工客服 → 转人工
        elif code == "CMP_003":
            result = await transfer_human(state["session_id"])
            state["need_human_transfer"] = True
            results.append({"tool": "transfer_human", "result": result})

    except Exception as e:
        logger.error(f"工具调用失败: {e}")
        state["error"] = str(e)

    state["tool_results"] = results
    return state