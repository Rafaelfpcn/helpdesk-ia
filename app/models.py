from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


def utcnow():
    return datetime.now(timezone.utc)


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)

    requester_name = Column(String(120), nullable=False)
    requester_email = Column(String(180), nullable=False)

    title = Column(String(180), nullable=False)
    description = Column(Text, nullable=False)

    category = Column(String(80), nullable=True)
    priority = Column(String(20), nullable=False, default="media")
    status = Column(String(20), nullable=False, default="aberto")
    source = Column(String(40), nullable=False, default="portal")

    needs_review = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)

    suggestions = relationship(
        "AiSuggestion",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )


class AiSuggestion(Base):
    __tablename__ = "ai_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)

    provider = Column(String(40), nullable=False, default="mock")
    prompt_version = Column(String(40), nullable=True)

    suggested_category = Column(String(80), nullable=True)
    suggested_priority = Column(String(20), nullable=True)

    summary = Column(Text, nullable=True)
    suggested_action = Column(Text, nullable=True)

    urgency_score = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)

    latency_ms = Column(Integer, nullable=True)
    decision = Column(String(20), nullable=False, default="manual_review")
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utcnow, nullable=False)

    ticket = relationship(
        "Ticket",
        back_populates="suggestions",
    )


class AiReview(Base):
    __tablename__ = "ai_reviews"

    id = Column(Integer, primary_key=True, index=True)
    suggestion_id = Column(Integer, ForeignKey("ai_suggestions.id"), nullable=False)

    reviewer_name = Column(String(120), nullable=False)

    accepted = Column(Boolean, nullable=False, default=False)

    corrected_category = Column(String(80), nullable=True)
    corrected_priority = Column(String(20), nullable=True)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=utcnow, nullable=False)

    suggestion = relationship("AiSuggestion")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    action = Column(String(80), nullable=False)
    entity = Column(String(80), nullable=False)
    entity_id = Column(Integer, nullable=True)

    payload = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=utcnow, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(120), nullable=False)
    email = Column(String(180), nullable=False, unique=True, index=True)

    hashed_password = Column(String(255), nullable=False)

    role = Column(String(30), nullable=False, default="requester")
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime, default=utcnow, nullable=False)
