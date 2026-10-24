from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.ai_suggestion import AISuggestion
    from app.models.audit_log import AuditLog


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    requester_name: Mapped[str] = mapped_column(String(100))
    requester_email: Mapped[str] = mapped_column(String(150))
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    initial_category: Mapped[str] = mapped_column(String(20))
    category: Mapped[str] = mapped_column(String(20), index=True)
    priority: Mapped[str] = mapped_column(String(20), index=True)
    status: Mapped[str] = mapped_column(String(20), index=True)
    source: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    suggestion: Mapped[Optional["AISuggestion"]] = relationship(
        "AISuggestion", back_populates="ticket", uselist=False, cascade="all, delete-orphan"
    )
    logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog", back_populates="ticket", order_by="AuditLog.id", cascade="all, delete-orphan"
    )
