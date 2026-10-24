import json
from typing import Optional

from sqlalchemy.orm import Session

from app.enums import EventType
from app.models import AuditLog


def log_event(
    db: Session,
    ticket_id: int,
    event_type: EventType,
    actor: str,
    details: Optional[dict] = None,
) -> None:
    """Registra um evento de auditoria.

    NÃO faz commit: quem chama decide, para que o chamado e seus logs sejam
    salvos juntos em uma transação atômica (tudo ou nada).
    """
    db.add(
        AuditLog(
            ticket_id=ticket_id,
            event_type=event_type.value,
            actor=actor,
            details=json.dumps(details or {}, ensure_ascii=False),
        )
    )
