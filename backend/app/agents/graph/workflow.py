"""
LangGraph 工作流编排
定义节点、边、条件路由，并编译为可执行的 Agent。
"""

from langgraph.graph import StateGraph, END
from app.agents.graph.state import AgentState
from app.agents.graph.nodes.router import analyze_and_route, route_decision
from app.agents.graph.nodes.rag_node import retrieve_knowledge
from app.agents.graph.nodes.tool_node import call_tools
from app.agents.graph.nodes.sentiment import check_sentiment
from app.agents.graph.nodes.generate import generate_response, should_escalate
from app.agents.graph.nodes.human import escalate_to_human

def build_workflow():
    """
    构建并编译 LangGraph 工作流
    返回：编译后的图，可直接 ainvoke
    """
    workflow = StateGraph(AgentState)

    # 注册节点
    workflow.add_node("analyze", analyze_and_route)      # NLU 分析
    workflow.add_node("rag", retrieve_knowledge)          # RAG 检索
    workflow.add_node("tool", call_tools)                 # 工具调用
    workflow.add_node("sentiment", check_sentiment)       # 情感检查
    workflow.add_node("generate", generate_response)      # 回复生成
    workflow.add_node("escalate", escalate_to_human)      # 转人工

    # 设置入口
    workflow.set_entry_point("analyze")

    # 分析后条件路由
    workflow.add_conditional_edges("analyze", route_decision, {
        "rag": "rag",
        "tool": "tool",
        "generate": "generate",
    })

    # RAG 和工具调用后都进入情感检查
    workflow.add_edge("rag", "sentiment")
    workflow.add_edge("tool", "sentiment")
    workflow.add_edge("sentiment", "generate")

    # 生成后判断是否转人工
    workflow.add_conditional_edges("generate", should_escalate, {
        "escalate": "escalate",
        "end": END,
    })

    workflow.add_edge("escalate", END)

    return workflow.compile()

# 全局编译后的 Agent 图
agent_graph = build_workflow()