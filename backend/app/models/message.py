import uuid

from sqlalchemy import Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, GUID, TimestampMixin
from app.models.enums import MessageRole


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    conversation_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole, name="message_role"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    conversation = relationship("Conversation", back_populates="messages")
