from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.review import ReviewChange, ReviewConfirm
from app.schemas.ticket import TicketOut
from app.services import review_service

router = APIRouter(prefix="/api/tickets", tags=["review"])


@router.post("/{ticket_id}/review/confirm", response_model=TicketOut)
def confirm(ticket_id: int, body: ReviewConfirm, db: Session = Depends(get_db)):
    """O atendente concorda com a IA: categoria e prioridade sugeridas passam a ser as oficiais."""
    return review_service.confirm_suggestion(db, ticket_id, body)


@router.post("/{ticket_id}/review/change", response_model=TicketOut)
def change(ticket_id: int, body: ReviewChange, db: Session = Depends(get_db)):
    """O atendente discorda: os valores informados passam a ser os oficiais."""
    return review_service.change_suggestion(db, ticket_id, body)
