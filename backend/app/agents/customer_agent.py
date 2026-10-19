"""
客服 Agent 实现
封装 LangGraph 工作流的调用。
"""

from app.agents.graph.workflow import agent_graph
from app.agents.graph.state import AgentState
from app.agents.base_agent import BaseAgent

class CustomerAgent(BaseAgent):
    """客服 Agent：调用 LangGraph 工作流"""

    async def run(self, state: AgentState) -> AgentState:
        """
        执行 Agent
        参数：state - 初始状态
        返回：最终状态
        """
        return await agent_graph.ainvoke(state)

# 全局单例
customer_agent = CustomerAgent()