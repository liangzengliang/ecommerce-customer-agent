"""
对话服务
编排整个对话流程：加载记忆 → 调用 Agent → 持久化 → 返回结果。
"""

import uuid
import logging
from langchain_core.messages import HumanMessage, AIMessage
from sqlalchemy import select
from app.agents.graph.workflow import agent_graph
from app.services.memory_service import memory_service
from app.core.database import AsyncSessionLocal
from app.models.session import Session as SessionModel
from app.models.message import Message

logger = logging.getLogger(__name__)

class ChatService:
    """对话服务类"""

    @staticmethod
    async def get_or_create_session(session_id: str | None, user_id: int) -> str:
        """
        获取或创建会话
        参数：session_id - 会话ID（可为空）
              user_id - 用户ID
        返回：会话ID
        """
        async with AsyncSessionLocal() as db:
            if session_id:
                result = await db.execute(
                    select(SessionModel).where(SessionModel.session_id == session_id)
                )
                session = result.scalar_one_or_none()
                if session:
                    return session.session_id

            # 创建新会话
            new_id = f"sess_{uuid.uuid4().hex[:16]}"
            session = SessionModel(
                session_id=new_id,
                user_id=user_id,
                status="active",
                channel="web",
            )
            db.add(session)
            await db.commit()
            return new_id

    @staticmethod
    async def process(user_message: str, session_id: str | None = None,
                      user_id: int = 1) -> dict:
        """
        处理一条用户消息的完整流程
        参数：user_message - 用户消息
              session_id - 会话ID（首次为空）
              user_id - 用户ID
        返回：dict，含 session_id / content / intent_code / sentiment
        """
        # 1. 获取或创建会话
        session_id = await ChatService.get_or_create_session(session_id, user_id)
        # ↑ 如果传入的 session_id 存在，就复用它；否则创建新的

        # 2. 加载历史记忆，转为 LangChain 消息对象
        history = await memory_service.get_history(session_id, limit=10)
        messages = []
        for h in history:
            if h["role"] == "user":
                messages.append(HumanMessage(content=h["content"]))
            else:
                messages.append(AIMessage(content=h["content"]))

        # 3. 写入用户消息到记忆
        await memory_service.add_message(session_id, "user", user_message)

        # 4. 构造初始状态，调用 Agent
        initial_state = {
            "session_id": session_id,
            "user_id": user_id,
            "user_message": user_message,
            "messages": messages,
            "intent_code": "",
            "intent_name": "",
            "intent_confidence": 0.0,
            "sentiment": "neutral",
            "sentiment_score": 0.5,
            "entities": [],
            "slots": {},
            "missing_slots": [],
            "rag_context": "",
            "tool_results": [],
            "final_response": "",
            "need_human_transfer": False,
            "iterations": 0,
            "error": None,
        }

        try:
            final_state = await agent_graph.ainvoke(initial_state)
        except Exception as e:
            logger.error(f"Agent 执行失败: {e}", exc_info=True)
            final_state = {**initial_state, "final_response": "抱歉，系统繁忙，请稍后再试。"}

        response_text = final_state.get("final_response") or "抱歉，我暂时无法回答，请换个问法试试。"

        # 5. 写入 bot 回复到记忆
        await memory_service.add_message(session_id, "bot", response_text)

        # 6. 持久化到 MySQL
        async with AsyncSessionLocal() as db:
            user_msg = Message(
                session_id=session_id,
                sender_type="user",
                sender_id=user_id,
                content=user_message,
            )
            bot_msg = Message(
                session_id=session_id,
                sender_type="bot",
                content=response_text,
                intent_confidence=final_state.get("intent_confidence"),
                sentiment=final_state.get("sentiment"),
                sentiment_score=final_state.get("sentiment_score"),
                is_generated=True,
            )
            db.add(user_msg)
            db.add(bot_msg)

            # 更新会话统计
            result = await db.execute(
                select(SessionModel).where(SessionModel.session_id == session_id)
            )
            session = result.scalar_one_or_none()
            if session:
                session.message_count = (session.message_count or 0) + 2
            await db.commit()

        return {
            "session_id": session_id,        # ← 必须返回这个 session_id
            "content": response_text,
            "intent_code": final_state.get("intent_code"),
            "sentiment": final_state.get("sentiment"),
            "need_human_transfer": final_state.get("need_human_transfer", False),
        }

# 全局单例
chat_service = ChatService()