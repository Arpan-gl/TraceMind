import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, GUID, TimestampMixin


class TokenUsage(Base, TimestampMixin):
    __tablename__ = "token_usage"
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_token_usage_user_date"),)

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    daily_tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    user = relationship("User", back_populates="token_usage")
