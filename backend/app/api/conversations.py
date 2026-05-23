from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user_id_dep
from app.core.db import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas import ConversationCreate, ConversationRead, MessageRead

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationRead])
async def list_conversations(
    user_id: UUID = Depends(get_current_user_id_dep),
    session: AsyncSession = Depends(get_db),
) -> list[ConversationRead]:
    result = await session.scalars(
        select(Conversation)
        .where(Conversation.user_id == user_id, Conversation.is_deleted.is_(False))
        .order_by(Conversation.updated_at.desc())
    )
    return [ConversationRead(id=row.id, title=row.title, updated_at=row.updated_at) for row in result.all()]


@router.post("", response_model=ConversationRead)
async def create_conversation(
    payload: ConversationCreate,
    user_id: UUID = Depends(get_current_user_id_dep),
    session: AsyncSession = Depends(get_db),
) -> ConversationRead:
    conversation = Conversation(user_id=user_id, title=payload.title)
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return ConversationRead(id=conversation.id, title=conversation.title, updated_at=conversation.updated_at)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    user_id: UUID = Depends(get_current_user_id_dep),
    session: AsyncSession = Depends(get_db),
) -> None:
    conversation = await session.scalar(
        select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id)
    )
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="conversation not found")
    conversation.is_deleted = True
    await session.commit()


@router.get("/{conversation_id}/messages")
async def get_messages(
    conversation_id: UUID,
    user_id: UUID = Depends(get_current_user_id_dep),
    session: AsyncSession = Depends(get_db),
) -> list[MessageRead]:
    conversation = await session.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
            Conversation.is_deleted.is_(False),
        )
    )
    if conversation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="conversation not found")

    result = await session.scalars(
        select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
    )
    return [
        MessageRead(
            id=row.id,
            conversation_id=row.conversation_id,
            role=row.role.value,
            content=row.content,
            token_count=row.token_count,
            created_at=row.created_at,
        )
        for row in result.all()
    ]
