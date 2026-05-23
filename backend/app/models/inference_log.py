import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, GUID, TimestampMixin


class InferenceLog(Base, TimestampMixin):
    __tablename__ = "inference_logs"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False)
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    tokens_input: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tokens_output: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_preview: Mapped[str] = mapped_column(String(200), nullable=False)
    response_preview: Mapped[str] = mapped_column(String(200), nullable=False)
    session_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), nullable=True)
    conversation = relationship("Conversation", back_populates="inference_logs")
