"""
Agent 抽象基类
定义 Agent 的通用接口。
"""

from abc import ABC, abstractmethod
from app.agents.graph.state import AgentState

class BaseAgent(ABC):
    """Agent 基类，所有 Agent 需实现 run 方法"""

    @abstractmethod
    async def run(self, state: AgentState) -> AgentState:
        """执行 Agent，输入状态，返回更新后的状态"""
        ...