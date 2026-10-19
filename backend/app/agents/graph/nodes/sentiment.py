"""
情感检查节点
根据情感分析结果标记是否需要转人工。
"""

from app.agents.graph.state import AgentState

async def check_sentiment(state: AgentState) -> AgentState:
    """
    情感检查节点：负面情绪超过阈值时标记转人工
    参数：state - 当前状态
    返回：更新后的状态
    """
    if state["sentiment"] == "negative" and state["sentiment_score"] > 0.8:
        state["need_human_transfer"] = True
    return state