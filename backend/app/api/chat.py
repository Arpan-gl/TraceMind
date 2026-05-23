from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_recent_messages, get_summary, increment_daily_quota, set_recent_messages
from app.core.config import get_settings
from app.core.db import get_db
from app.core.dependencies import get_current_user_id_dep
from app.models.conversation import Conversation
from app.models.enums import MessageRole
from app.models.message import Message
from app.schemas import ChatStreamRequest
from app.sdk.llm_wrapper import LLMWrapper

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{conversation_id}/stream")
async def stream_chat(
    conversation_id: UUID,
    payload: ChatStreamRequest,
    user_id: UUID = Depends(get_current_user_id_dep),
    session: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    conversation = await session.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
            Conversation.is_deleted.is_(False),
        )
    )
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="conversation not found")

    recent_messages = await get_recent_messages(conversation_id)
    summary = await get_summary(conversation_id)
    prompt_messages: list[dict[str, str]] = []
    if summary:
        prompt_messages.append({"role": "system", "content": summary})
    prompt_messages.extend(recent_messages)
    prompt_messages.append({"role": "user", "content": payload.message})

    user_message = Message(conversation_id=conversation_id, role=MessageRole.user, content=payload.message, token_count=max(1, len(payload.message) // 4))
    session.add(user_message)
    await session.commit()

    settings = get_settings()
    wrapper = LLMWrapper(provider=payload.provider, model=payload.model, api_key=settings.groq_api_key)

    async def event_stream() -> AsyncGenerator[str, None]:
        assistant_chunks: list[str] = []
        try:
            async for chunk in wrapper.generate_stream(prompt_messages, session_id=str(payload.session_id), conversation_id=str(conversation_id)):
                assistant_chunks.append(chunk)
                yield f"data: {chunk}\n\n"
        finally:
            assistant_text = "".join(assistant_chunks)
            assistant_message = Message(
                conversation_id=conversation_id,
                role=MessageRole.assistant,
                content=assistant_text,
                token_count=max(1, len(assistant_text) // 4),
            )
            session.add(assistant_message)
            await session.commit()
            await set_recent_messages(
                conversation_id,
                [*recent_messages, {"role": "user", "content": payload.message}, {"role": "assistant", "content": assistant_text}],
            )
            await increment_daily_quota(user_id, user_message.token_count + assistant_message.token_count)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
