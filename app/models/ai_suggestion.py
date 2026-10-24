from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import ReviewStatus
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.ticket import Ticket


class AISuggestion(Base):
    __tablename__ = "ai_suggestions"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), unique=True)

    # O que a IA sugeriu (nunca é sobrescrito: é a base da métrica de acerto)
    suggested_category: Mapped[str] = mapped_column(String(20))
    suggested_priority: Mapped[str] = mapped_column(String(20))
    urgency_level: Mapped[str] = mapped_column(String(20))
    summary: Mapped[str] = mapped_column(Text)
    initial_action: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    provider: Mapped[str] = mapped_column(String(30))

    # O que o humano decidiu na revisão
    review_status: Mapped[str] = mapped_column(String(20), default=ReviewStatus.pendente.value)
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    final_category: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    final_priority: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    review_note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="suggestion")
