"""
回复生成节点
"""

from langchain_core.prompts import ChatPromptTemplate
from app.services.llm_service import get_llm_async, is_llm_available
from app.agents.graph.state import AgentState
import logging
import json

logger = logging.getLogger(__name__)

# ============ 模板 A：有工具结果 ============
_SYSTEM_WITH_TOOLS = """你是电商智能客服助手，负责把工具调用结果完整、清晰地告诉用户。

【规则】
1. 工具返回 found=true 时，逐项列出所有字段：订单号、订单状态、总金额、实付金额、收货人、联系电话、收货地址、物流单号、下单时间、支付时间、发货时间、收货时间、订单备注、商品明细、物流轨迹。
2. 商品明细逐条列出：商品名称 × 数量 = 小计。
3. 物流轨迹按时间顺序逐条列出。
4. 工具返回 found=false 时，只回复一句"未找到该订单，请核对订单号后重试"。

【格式】
您好，订单 **{{订单号}}** 的详细信息如下：

📦 订单状态：{{订单状态}}
💰 订单总金额：¥{{订单总金额}}
💳 实付金额：¥{{实付金额}}

**收货信息**
- 收货人：{{收货人}}
- 联系电话：{{联系电话}}
- 收货地址：{{收货地址}}

**物流信息**
- 物流单号：{{物流单号}}
- 发货时间：{{发货时间}}

**物流轨迹**
（有就按时间顺序列出，没有写"暂无物流轨迹"）

**商品明细**
- {{商品名称}} × {{数量}} = ¥{{小计}}

**时间线**
- 下单时间：{{下单时间}}
- 支付时间：{{支付时间}}"""

_PROMPT_WITH_TOOLS = ChatPromptTemplate.from_messages([
    ("system", _SYSTEM_WITH_TOOLS),
    ("human",
     "用户问题：{user_message}\n\n"
     "工具调用结果：\n{tool_results}\n\n"
     "请严格根据工具结果生成完整回复。"),
])


# ============ 模板 B：无工具结果（只走 RAG）============
_SYSTEM_NO_TOOLS = """你是电商智能客服助手。根据用户问题和知识库内容生成回复。

【规则】
1. 如果知识库上下文包含相关内容，就基于它回答，可以整理、改写，但要保证信息准确。
2. 如果知识库上下文为空，或与问题完全无关，就基于你的电商常识给出通用回答，不要说"抱歉无法回答"。
3. 回答要简洁、分点清晰，控制在 300 字以内。
4. 不要说"未找到该订单"，除非用户明确提供了订单号且需要查询。

【回答风格】
- 用户问流程 → 用有序列表
- 用户问政策 → 直接说明
- 用户问概念 → 简短定义 + 举例"""

_PROMPT_NO_TOOLS = ChatPromptTemplate.from_messages([
    ("system", _SYSTEM_NO_TOOLS),
    ("human",
     "用户问题：{user_message}\n\n"
     "知识库上下文：\n{rag_context}\n\n"
     "请生成回复。"),
])


def _format_tool_result(result) -> str:
    """将工具结果格式化为可读文本（降级方案）"""
    if isinstance(result, dict):
        lines = []
        for k, v in result.items():
            if v is None or v == "":
                continue
            if isinstance(v, (dict, list)):
                lines.append(f"{k}: {v}")
            else:
                lines.append(f"{k}: {v}")
        return "\n".join(lines)
    return str(result)


def _offline_reply_with_tools(state: AgentState) -> str:
    """无 LLM 时，基于工具结果生成结构化回复"""
    results = [
        r for r in (state.get("tool_results") or [])
        if isinstance(r, dict) and r.get("result")
    ]
    if not results:
        return "抱歉，我暂时无法处理该请求，请稍后再试。"

    lines = []
    for item in results:
        tool = item.get("tool", "")
        result = item.get("result", {})
        lines.append(_format_tool_result(result))

    # 查询订单场景：格式化订单详情
    order = None
    for item in results:
        res = item.get("result", {})
        if isinstance(res, dict) and res.get("found") and res.get("order"):
            order = res.get("order") or res
            break
    if order:
        out = [f"您好，订单 **{order.get('order_no', '')}** 的详细信息如下："]
        out.append(f"\n📦 订单状态：{order.get('status', '未知')}")
        out.append(f"💰 订单总金额：¥{order.get('total_amount', '')}")
        out.append(f"💳 实付金额：¥{order.get('pay_amount', '')}")
        receiver = order.get("receiver_name")
        phone = order.get("receiver_phone")
        addr = order.get("shipping_address")
        if receiver or phone or addr:
            out.append("\n**收货信息**")
            if receiver:
                out.append(f"- 收货人：{receiver}")
            if phone:
                out.append(f"- 联系电话：{phone}")
            if addr:
                if isinstance(addr, dict):
                    out.append(f"- 收货地址：{addr.get('full', addr)}")
                else:
                    out.append(f"- 收货地址：{addr}")
        tracking = order.get("tracking_no")
        if tracking:
            out.append("\n**物流信息**")
            out.append(f"- 物流单号：{tracking}")
        items = order.get("items") or order.get("order_items") or []
        if items:
            out.append("\n**商品明细**")
            for it in items:
                name = it.get("product_name") or it.get("name") or "商品"
                qty = it.get("quantity") or it.get("qty") or 1
                price = it.get("unit_price") or it.get("price") or ""
                out.append(f"- {name} × {qty} = ¥{float(price or 0) * int(qty)}")
        return "\n".join(out)

    return "\n".join(lines)


def _offline_reply_no_tools(state: AgentState) -> str:
    """无 LLM 时，基于 RAG 上下文生成回复"""
    rag_ctx = state.get("rag_context") or ""
    if rag_ctx:
        # 提取第一条知识问答
        import re
        m = re.search(r"【知识】Q: (.*?)\nA: (.*?)(?:\n\n|$)", rag_ctx, re.S)
        if m:
            return f"{m.group(2)}"
        return rag_ctx[:300]
    return "您好，我是电商智能客服助手，可以帮您查询订单、了解退换货政策、咨询商品信息。请问有什么可以帮您？"


async def generate_response(state: AgentState) -> AgentState:
    tool_results_list = state.get("tool_results", [])
    valid_tools = [
        r for r in (tool_results_list or [])
        if isinstance(r, dict) and r.get("result")
    ]

    # ===== 演示模式/LLM 不可用：走离线规则回复 =====
    if not await is_llm_available():
        if valid_tools:
            state["final_response"] = _offline_reply_with_tools(state)
        else:
            state["final_response"] = _offline_reply_no_tools(state)
        return state

    llm = await get_llm_async(streaming=True, temperature=0.3)

    if valid_tools:
        tool_results_str = json.dumps(
            valid_tools, ensure_ascii=False, indent=2, default=str,
        )
        chain = _PROMPT_WITH_TOOLS | llm
        response = await chain.ainvoke({
            "user_message": state["user_message"],
            "tool_results": tool_results_str,
        })
    else:
        rag_ctx = state.get("rag_context", "") or "无相关内容"
        chain = _PROMPT_NO_TOOLS | llm
        response = await chain.ainvoke({
            "user_message": state["user_message"],
            "rag_context": rag_ctx,
        })

    state["final_response"] = response.content
    return state


def should_escalate(state: AgentState) -> str:
    if state.get("need_human_transfer"):
        return "escalate"
    return "end"