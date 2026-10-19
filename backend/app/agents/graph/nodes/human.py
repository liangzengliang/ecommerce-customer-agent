"""
人工转接节点
当需要转人工时，设置兜底回复内容。
"""

from app.agents.graph.state import AgentState

async def escalate_to_human(state: AgentState) -> AgentState:
    """
    转人工节点：设置转接提示语
    参数：state - 当前状态
    返回：更新后的状态
    """
    state["final_response"] = (
        "非常抱歉给您带来不便，我已为您转接人工客服，请稍等片刻。"
        "人工客服会尽快为您处理。"
    )
    return state