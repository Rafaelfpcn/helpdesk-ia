from typing import List, Optional

from sqlalchemy.orm import Session

from app import models, schemas
from app.core.config import settings
from app.models import utcnow
from app.services.ai import AiService


def audit_log(
    db: Session,
    action: str,
    entity: str,
    entity_id: Optional[int],
    payload: Optional[dict] = None,
):
    db.add(
        models.AuditLog(
            action=action,
            entity=entity,
            entity_id=entity_id,
            payload=payload or {},
        )
    )


class TicketService:
    def __init__(self, db: Session, ai_service: AiService):
        self.db = db
        self.ai_service = ai_service

    def create_ticket(
        self,
        payload: schemas.TicketCreate,
    ) -> tuple[models.Ticket, models.AiSuggestion]:
        data = payload.model_dump(mode="json", exclude_none=True)

        category_was_provided = payload.category is not None
        priority_was_provided = payload.priority is not None

        ticket = models.Ticket(**data)

        ticket.status = "aberto"
        ticket.needs_review = True

        self.db.add(ticket)
        self.db.flush()

        audit_log(
            db=self.db,
            action="ticket_created",
            entity="ticket",
            entity_id=ticket.id,
            payload={
                "title": ticket.title,
                "source": ticket.source,
            },
        )

        analysis = self.ai_service.analyze_ticket(
            title=ticket.title,
            description=ticket.description,
        )

        suggestion = models.AiSuggestion(
            ticket_id=ticket.id,
            provider=analysis.provider,
            prompt_version=analysis.prompt_version,
            suggested_category=analysis.suggested_category,
            suggested_priority=analysis.suggested_priority,
            summary=analysis.summary,
            suggested_action=analysis.suggested_action,
            urgency_score=analysis.urgency_score,
            confidence=analysis.confidence,
            latency_ms=analysis.latency_ms,
            error_message=analysis.error_message,
            decision=analysis.decision,
        )

        self.db.add(suggestion)
        self.db.flush()

        audit_log(
            db=self.db,
            action="ai_suggested",
            entity="ai_suggestion",
            entity_id=suggestion.id,
            payload={
                "ticket_id": ticket.id,
                "provider": analysis.provider,
                "confidence": analysis.confidence,
                "urgency_score": analysis.urgency_score,
                "decision": analysis.decision,
            },
        )

        if not category_was_provided:
            if analysis.decision == "auto_fill":
                ticket.category = analysis.suggested_category
            else:
                ticket.category = settings.ai_fallback_category

        if not priority_was_provided:
            if analysis.decision == "auto_fill":
                ticket.priority = analysis.suggested_priority
            else:
                ticket.priority = settings.ai_fallback_priority

        self.db.commit()
        self.db.refresh(ticket)
        self.db.refresh(suggestion)

        return ticket, suggestion

    def get_ticket(self, ticket_id: int) -> Optional[models.Ticket]:
        return self.db.get(models.Ticket, ticket_id)

    def list_tickets(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[models.Ticket]:
        query = self.db.query(models.Ticket)

        if status:
            query = query.filter(models.Ticket.status == status)

        if category:
            query = query.filter(models.Ticket.category == category)

        if priority:
            query = query.filter(models.Ticket.priority == priority)

        return (
            query.order_by(models.Ticket.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def update_ticket(
        self,
        ticket_id: int,
        payload: schemas.TicketUpdate,
    ) -> Optional[models.Ticket]:
        ticket = self.db.get(models.Ticket, ticket_id)

        if not ticket:
            return None

        data = payload.model_dump(
            mode="json",
            exclude_unset=True,
            exclude_none=True,
        )

        for field, value in data.items():
            setattr(ticket, field, value)

        if data.get("status") in ["resolvido", "fechado"]:
            if not ticket.closed_at:
                ticket.closed_at = utcnow()

        audit_log(
            db=self.db,
            action="ticket_updated",
            entity="ticket",
            entity_id=ticket.id,
            payload=data,
        )

        self.db.commit()
        self.db.refresh(ticket)

        return ticket


class ReviewService:
    def __init__(self, db: Session):
        self.db = db

    def review_suggestion(
        self,
        suggestion_id: int,
        payload: schemas.AiReviewCreate,
    ) -> Optional[models.AiReview]:
        suggestion = self.db.get(models.AiSuggestion, suggestion_id)

        if not suggestion:
            return None

        ticket = self.db.get(models.Ticket, suggestion.ticket_id)

        if not ticket:
            return None

        corrected_priority_val = None
        if payload.corrected_priority:
            corrected_priority_val = (
                payload.corrected_priority.value
                if hasattr(payload.corrected_priority, "value")
                else str(payload.corrected_priority)
            )

        review = models.AiReview(
            suggestion_id=suggestion_id,
            reviewer_name=payload.reviewer_name,
            accepted=payload.accepted,
            corrected_category=payload.corrected_category,
            corrected_priority=corrected_priority_val,
            notes=payload.notes,
        )

        self.db.add(review)

        if payload.accepted:
            if suggestion.suggested_category:
                ticket.category = suggestion.suggested_category

            if suggestion.suggested_priority:
                ticket.priority = suggestion.suggested_priority
        else:
            if payload.corrected_category:
                ticket.category = payload.corrected_category

            if corrected_priority_val:
                ticket.priority = corrected_priority_val

        ticket.needs_review = False

        self.db.flush()

        audit_log(
            db=self.db,
            action="ai_reviewed",
            entity="ai_review",
            entity_id=review.id,
            payload={
                "suggestion_id": suggestion_id,
                "ticket_id": ticket.id,
                "accepted": payload.accepted,
            },
        )

        self.db.commit()
        self.db.refresh(review)

        return review
