"""
agents 包：LangGraph Agent 编排核心。
对外暴露客服 Agent 单例，内部工作流和工具按需直接导入。
"""

from app.agents.base_agent import BaseAgent
from app.agents.customer_agent import CustomerAgent, customer_agent
from app.agents.graph.workflow import agent_graph

__all__ = [
    "BaseAgent",
    "CustomerAgent",
    "customer_agent",
    "agent_graph",
]