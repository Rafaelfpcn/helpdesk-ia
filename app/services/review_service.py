from sqlalchemy.orm import Session

from app.enums import EventType, ReviewStatus
from app.errors import InvalidReview, NoSuggestionAvailable, ReviewAlreadyDone
from app.models import AISuggestion, Ticket
from app.schemas.review import ReviewChange, ReviewConfirm
from app.services.audit_service import log_event
from app.services.ticket_service import get_ticket
from app.utils import utcnow


def _get_pending_suggestion(db: Session, ticket_id: int) -> tuple[Ticket, AISuggestion]:
    ticket = get_ticket(db, ticket_id)
    suggestion = ticket.suggestion
    if suggestion is None:
        raise NoSuggestionAvailable("Este chamado não tem sugestão da IA para revisar.")
    if suggestion.review_status != ReviewStatus.pendente.value:
        raise ReviewAlreadyDone("A sugestão deste chamado já foi revisada.")
    return ticket, suggestion


def _apply_review(
    ticket: Ticket,
    suggestion: AISuggestion,
    status: ReviewStatus,
    reviewed_by: str,
    category: str,
    priority: str,
    note: str | None,
) -> None:
    """Grava a decisão humana. A sugestão original (suggested_*) NUNCA é alterada."""
    suggestion.review_status = status.value
    suggestion.reviewed_by = reviewed_by
    suggestion.final_category = category
    suggestion.final_priority = priority
    suggestion.review_note = note
    suggestion.reviewed_at = utcnow()
    # Só agora a categoria e a prioridade OFICIAIS do chamado mudam.
    ticket.category = category
    ticket.priority = priority


def confirm_suggestion(db: Session, ticket_id: int, data: ReviewConfirm) -> Ticket:
    ticket, suggestion = _get_pending_suggestion(db, ticket_id)
    _apply_review(
        ticket,
        suggestion,
        ReviewStatus.confirmada,
        data.reviewed_by,
        suggestion.suggested_category,
        suggestion.suggested_priority,
        data.note,
    )
    log_event(
        db,
        ticket.id,
        EventType.suggestion_confirmed,
        data.reviewed_by,
        {
            "category": suggestion.suggested_category,
            "priority": suggestion.suggested_priority,
            "has_note": bool(data.note),
        },
    )
    db.commit()
    db.refresh(ticket)
    return ticket


def change_suggestion(db: Session, ticket_id: int, data: ReviewChange) -> Ticket:
    ticket, suggestion = _get_pending_suggestion(db, ticket_id)
    new_category, new_priority = data.category.value, data.priority.value
    # Se nada mudou, isso é uma confirmação. Aceitar como "alterada" contaminaria as métricas.
    if new_category == suggestion.suggested_category and new_priority == suggestion.suggested_priority:
        raise InvalidReview("Os valores são iguais aos da sugestão da IA; use a confirmação.")
    _apply_review(
        ticket,
        suggestion,
        ReviewStatus.alterada,
        data.reviewed_by,
        new_category,
        new_priority,
        data.note,
    )
    log_event(
        db,
        ticket.id,
        EventType.suggestion_changed,
        data.reviewed_by,
        {
            "suggested": {"category": suggestion.suggested_category, "priority": suggestion.suggested_priority},
            "final": {"category": new_category, "priority": new_priority},
            "has_note": bool(data.note),
        },
    )
    db.commit()
    db.refresh(ticket)
    return ticket
