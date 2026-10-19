"""
Agent 状态定义
LangGraph 在各节点之间传递的共享状态。
"""
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """Agent 工作流的全局状态"""

    # ===== 会话信息 =====
    session_id: str           # 会话ID
    user_id: int              # 用户ID

    # ===== 输入 =====
    user_message: str         # 用户当前消息
    messages: Annotated[List[BaseMessage], add_messages]  # 历史消息（自动累加）

    # ===== NLU 结果 =====
    intent_code: str          # 意图编码
    intent_name: str          # 意图名称
    intent_confidence: float  # 意图置信度
    sentiment: str            # 情感倾向
    sentiment_score: float    # 情感得分
    entities: List[Dict[str, Any]]   # 实体列表
    slots: Dict[str, Any]     # 槽位字典
    missing_slots: List[str]  # 缺失槽位

    # ===== RAG 结果 =====
    rag_context: str          # RAG 检索到的上下文

    # ===== 工具调用结果 =====
    tool_results: List[Dict[str, Any]]

    # ===== 输出 =====
    final_response: str       # 最终回复
    need_human_transfer: bool # 是否需要转人工

    # ===== 控制 =====
    iterations: int           # 迭代次数（防止死循环）
    error: Optional[str]      # 错误信息