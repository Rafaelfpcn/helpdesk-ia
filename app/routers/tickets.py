from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.enums import Category, Priority, Status
from app.schemas.ticket import AuditLogOut, StatusUpdate, TicketCreate, TicketOut
from app.services import ticket_service
from app.services.ai.base import AIProvider
from app.services.ai.factory import get_ai_provider

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.post("", response_model=TicketOut, status_code=201)
def create_ticket(
    data: TicketCreate,
    db: Session = Depends(get_db),
    provider: AIProvider = Depends(get_ai_provider),
):
    """Abre um chamado e gera a sugestão da IA (que ainda precisa de revisão humana)."""
    return ticket_service.create_ticket(db, data, provider)


@router.get("", response_model=list[TicketOut])
def list_tickets(
    status: Optional[Status] = None,
    category: Optional[Category] = None,
    priority: Optional[Priority] = None,
    db: Session = Depends(get_db),
):
    return ticket_service.list_tickets(db, status, category, priority)


@router.get("/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    return ticket_service.get_ticket(db, ticket_id)


@router.patch("/{ticket_id}/status", response_model=TicketOut)
def update_status(ticket_id: int, body: StatusUpdate, db: Session = Depends(get_db)):
    return ticket_service.update_status(db, ticket_id, body.status, body.changed_by)


@router.get("/{ticket_id}/logs", response_model=list[AuditLogOut])
def get_logs(ticket_id: int, db: Session = Depends(get_db)):
    return ticket_service.get_ticket(db, ticket_id).logs
