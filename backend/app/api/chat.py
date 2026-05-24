from collections.abc import AsyncGenerator
from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_daily_quota, get_recent_messages, get_summary, increment_daily_quota, set_recent_messages
from app.core.config import get_settings
from app.core.db import get_db
from app.core.dependencies import get_current_user_id_dep
from app.models.conversation import Conversation
from app.models.enums import MessageRole
from app.models.message import Message
from app.models.token_usage import TokenUsage
from app.schemas import ChatStreamRequest
from app.sdk.llm_wrapper import LLMWrapper

router = APIRouter(prefix="/chat", tags=["chat"])

DEPRECATED_GROQ_MODELS = {
    "llama-3-8b-8192",
    "llama3-8b-8192",
}


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _sse_data(chunk: str) -> str:
    return "".join(f"data: {line}\n" for line in chunk.splitlines() or [""]) + "\n"


def _sse_error(message: str) -> str:
    return "event: error\n" + "".join(f"data: {line}\n" for line in message.splitlines() or [""]) + "\n"


def _select_model(provider: str, requested_model: str) -> str:
    settings = get_settings()
    if provider == "groq" and requested_model in DEPRECATED_GROQ_MODELS:
        return settings.default_groq_model
    return requested_model or settings.default_groq_model


async def _get_persisted_daily_usage(session: AsyncSession, user_id: UUID) -> int:
    usage = await session.scalar(
        select(TokenUsage.daily_tokens_used).where(TokenUsage.user_id == user_id, TokenUsage.date == date.today())
    )
    return usage or 0


async def _persist_daily_usage(session: AsyncSession, user_id: UUID, tokens: int) -> None:
    usage = await session.scalar(select(TokenUsage).where(TokenUsage.user_id == user_id, TokenUsage.date == date.today()))
    if usage is None:
        session.add(TokenUsage(user_id=user_id, date=date.today(), daily_tokens_used=tokens))
    else:
        usage.daily_tokens_used += tokens
    await session.commit()


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

    estimated_input_tokens = sum(_estimate_tokens(message.get("content", "")) for message in prompt_messages)
    settings = get_settings()
    tokens_used = max(await get_daily_quota(user_id), await _get_persisted_daily_usage(session, user_id))
    remaining_tokens = settings.daily_token_limit - tokens_used
    if remaining_tokens <= 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"daily token limit of {settings.daily_token_limit} reached",
        )
    if estimated_input_tokens >= remaining_tokens:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"message needs about {estimated_input_tokens} tokens, but only {remaining_tokens} remain today",
        )

    max_output_tokens = min(remaining_tokens - estimated_input_tokens, settings.max_completion_tokens)
    user_message = Message(conversation_id=conversation_id, role=MessageRole.user, content=payload.message, token_count=_estimate_tokens(payload.message))
    session.add(user_message)
    await session.commit()

    selected_model = _select_model(payload.provider, payload.model)
    wrapper = LLMWrapper(provider=payload.provider, model=selected_model, api_key=settings.groq_api_key)

    async def event_stream() -> AsyncGenerator[str, None]:
        assistant_chunks: list[str] = []
        completed = False
        try:
            async for chunk in wrapper.generate_stream(
                prompt_messages,
                session_id=str(payload.session_id),
                conversation_id=str(conversation_id),
                max_output_tokens=max_output_tokens,
            ):
                assistant_chunks.append(chunk)
                yield _sse_data(chunk)
            completed = True
        except Exception as exc:
            yield _sse_error(f"LLM request failed: {exc}")
        finally:
            assistant_text = "".join(assistant_chunks)
            assistant_token_count = _estimate_tokens(assistant_text) if assistant_text else 0
            if assistant_text:
                assistant_message = Message(
                    conversation_id=conversation_id,
                    role=MessageRole.assistant,
                    content=assistant_text,
                    token_count=assistant_token_count,
                )
                session.add(assistant_message)
                await session.commit()
            await set_recent_messages(
                conversation_id,
                [*recent_messages, {"role": "user", "content": payload.message}]
                + ([{"role": "assistant", "content": assistant_text}] if completed and assistant_text else []),
            )
            token_delta = estimated_input_tokens + assistant_token_count
            await increment_daily_quota(user_id, token_delta)
            await _persist_daily_usage(session, user_id, token_delta)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
