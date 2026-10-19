"""
Agent 服务
对外暴露 Agent 执行能力。
"""

from app.agents.customer_agent import customer_agent

class AgentService:
    """Agent 服务类"""

    async def run(self, state: dict) -> dict:
        """
        执行 Agent
        参数：state - 初始状态字典
        返回：最终状态字典
        """
        return await customer_agent.run(state)

agent_service = AgentService()