import logging
from collections import Counter
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.enums import Category, EventType, Priority, Status
from app.errors import InvalidStatusTransition, TicketNotFound
from app.models import AISuggestion, Ticket
from app.schemas.ticket import TicketCreate
from app.services.ai.base import AIProvider
from app.services.ai.sanitizer import sanitize
from app.services.audit_service import log_event
from app.utils import utcnow

logger = logging.getLogger(__name__)

# Transições permitidas: de onde o chamado pode ir.
ALLOWED_TRANSITIONS: dict[Status, set[Status]] = {
    Status.aberto: {Status.em_atendimento, Status.fechado},
    Status.em_atendimento: {Status.aberto, Status.resolvido},
    Status.resolvido: {Status.em_atendimento, Status.fechado},
    Status.fechado: set(),
}


def create_ticket(db: Session, data: TicketCreate, provider: AIProvider) -> Ticket:
    ticket = Ticket(
        requester_name=data.requester_name,
        requester_email=data.requester_email,
        title=data.title,
        description=data.description,
        initial_category=data.initial_category.value,
        category=data.initial_category.value,  # oficial = inicial até a revisão humana
        priority=Priority.media.value,  # prioridade padrão até a revisão humana
        status=Status.aberto.value,
        source=data.source.value,
    )
    db.add(ticket)
    db.flush()  # envia ao banco sem finalizar, só para gerar ticket.id
    log_event(db, ticket.id, EventType.ticket_created, "system", {"source": ticket.source})
    _generate_suggestion(db, ticket, provider)
    db.commit()  # um único commit atômico: chamado + sugestão + logs
    db.refresh(ticket)
    return ticket


def _generate_suggestion(db: Session, ticket: Ticket, provider: AIProvider) -> None:
    try:
        # Minimização de dados: a IA só enxerga o texto com dados sensíveis mascarados.
        clean_title = sanitize(ticket.title)
        clean_description = sanitize(ticket.description)
        redactions = dict(Counter(clean_title.redactions) + Counter(clean_description.redactions))
        analysis = provider.analyze(clean_title.text, clean_description.text)
    except Exception as exc:  # noqa: BLE001
        # Falha segura: a IA nunca pode impedir a abertura do chamado.
        logger.exception("Falha ao gerar sugestão da IA (ticket %s)", ticket.id)
        log_event(
            db,
            ticket.id,
            EventType.suggestion_failed,
            "ai",
            {"provider": provider.name, "error": type(exc).__name__},
        )
        return

    db.add(
        AISuggestion(
            ticket_id=ticket.id,
            suggested_category=analysis.category.value,
            suggested_priority=analysis.priority.value,
            urgency_level=analysis.urgency.value,
            summary=analysis.summary,
            initial_action=analysis.initial_action,
            confidence=analysis.confidence,
            provider=provider.name,
        )
    )
    log_event(
        db,
        ticket.id,
        EventType.suggestion_generated,
        "ai",
        {
            "provider": provider.name,
            "category": analysis.category.value,
            "priority": analysis.priority.value,
            "confidence": analysis.confidence,
            "redactions": redactions,  # tipos e quantidades, nunca os valores
        },
    )


def get_ticket(db: Session, ticket_id: int) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise TicketNotFound(f"Chamado {ticket_id} não encontrado.")
    return ticket


def list_tickets(
    db: Session,
    status: Optional[Status] = None,
    category: Optional[Category] = None,
    priority: Optional[Priority] = None,
) -> list[Ticket]:
    stmt = (
        select(Ticket)
        .options(selectinload(Ticket.suggestion))  # carrega as sugestões de uma vez (evita N+1)
        .order_by(Ticket.created_at.desc(), Ticket.id.desc())
    )
    if status:
        stmt = stmt.where(Ticket.status == status.value)
    if category:
        stmt = stmt.where(Ticket.category == category.value)
    if priority:
        stmt = stmt.where(Ticket.priority == priority.value)
    return list(db.scalars(stmt))


def update_status(db: Session, ticket_id: int, new_status: Status, changed_by: str) -> Ticket:
    ticket = get_ticket(db, ticket_id)
    current = Status(ticket.status)
    if new_status not in ALLOWED_TRANSITIONS[current]:
        raise InvalidStatusTransition(
            f"Não é possível mudar de '{current.value}' para '{new_status.value}'."
        )
    ticket.status = new_status.value
    if new_status == Status.resolvido:
        ticket.resolved_at = utcnow()  # base da métrica de tempo de resolução
    elif new_status in (Status.aberto, Status.em_atendimento):
        ticket.resolved_at = None  # chamado reaberto
    # Em "fechado" mantemos o resolved_at original.
    log_event(
        db,
        ticket.id,
        EventType.status_changed,
        changed_by,
        {"from": current.value, "to": new_status.value},
    )
    db.commit()
    db.refresh(ticket)
    return ticket
