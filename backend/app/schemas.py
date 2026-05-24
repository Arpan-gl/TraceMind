from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthCredentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime


class ConversationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)


class ConversationRead(BaseModel):
    id: UUID
    title: str
    updated_at: datetime | None = None


class ChatStreamRequest(BaseModel):
    message: str = Field(min_length=1)
    provider: str = Field(default="groq")
    model: str = Field(default="llama-3.1-8b-instant")
    session_id: UUID


class MessageRead(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    token_count: int
    created_at: datetime


class InferenceLogPayload(BaseModel):
    id: UUID
    conversation_id: UUID | None = None
    provider: str
    model: str
    latency_ms: float
    tokens_input: int
    tokens_output: int
    status: str
    error_message: str | None = None
    request_preview: str = Field(max_length=200)
    response_preview: str = Field(max_length=200)
    session_id: UUID | None = None
    created_at: datetime
