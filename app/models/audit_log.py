from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils import utcnow

if TYPE_CHECKING:
    from app.models.ticket import Ticket


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(40))
    actor: Mapped[str] = mapped_column(String(100))  # system, ai ou nome do atendente
    details: Mapped[str] = mapped_column(Text, default="{}")  # JSON em texto
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="logs")
