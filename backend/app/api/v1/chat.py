"""
对话接口
提供同步和 SSE 流式两种对话方式。
"""

import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import chat_service

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: User = Depends(get_current_user)):
    """同步对话接口"""
    result = await chat_service.process(
        user_message=request.message,
        session_id=request.session_id,
        user_id=current_user.id,
    )
    return ChatResponse(
        session_id=result["session_id"],
        content=result["content"],
        intent_code=result.get("intent_code"),
        sentiment=result.get("sentiment"),
    )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, current_user: User = Depends(get_current_user)):
    """SSE 流式对话接口"""

    async def event_generator():
        result = await chat_service.process(
            user_message=request.message,
            session_id=request.session_id,      # ← 关键：把前端的 session_id 传下去
            user_id=current_user.id,
        )

        # ★★★ 第一块必须返回 session_id ★★★
        yield f"data: {json.dumps({'session_id': result['session_id']}, ensure_ascii=False)}\n\n"

        # 逐字返回
        text = result["content"]
        for i in range(0, len(text), 5):
            yield f"data: {json.dumps({'delta': text[i:i+5]}, ensure_ascii=False)}\n\n"

        # 结束标记
        yield f"data: {json.dumps({'done': True, 'intent_code': result.get('intent_code')}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")