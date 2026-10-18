from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import models, schemas
from app.core.config import settings
from app.db.base import get_db
from app.services.ai import AiService, MockAiProvider
from app.services.metrics_service import get_metrics
from app.services.security import get_current_user
from app.services.ticket_service import ReviewService, TicketService

router = APIRouter()

_ai_service: Optional[AiService] = None


def get_ai_service() -> AiService:
    global _ai_service

    if _ai_service is None:
        provider = MockAiProvider()

        _ai_service = AiService(
            provider=provider,
            provider_name=settings.ai_provider,
            prompt_version="v1.0-mock",
            confidence_threshold=settings.ai_confidence_threshold,
            fallback_category=settings.ai_fallback_category,
            fallback_priority=settings.ai_fallback_priority,
        )

    return _ai_service


@router.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        database_status = "ok"
    except Exception:
        database_status = "error"

    return {
        "status": "ok" if database_status == "ok" else "degraded",
        "database": database_status,
        "ai_provider": settings.ai_provider,
        "app_env": settings.app_env,
    }


@router.post(
    "/tickets",
    response_model=schemas.TicketCreateResponse,
    status_code=201,
)
def create_ticket(
    payload: schemas.TicketCreate,
    db: Session = Depends(get_db),
    ai_service: AiService = Depends(get_ai_service),
    current_user: models.User = Depends(get_current_user),
):
    service = TicketService(db=db, ai_service=ai_service)

    ticket, suggestion = service.create_ticket(payload)

    return schemas.TicketCreateResponse(
        ticket=schemas.TicketRead.model_validate(ticket),
        suggestion=schemas.AiSuggestionRead.model_validate(suggestion),
    )


@router.get(
    "/tickets",
    response_model=List[schemas.TicketRead],
)
def list_tickets(
    status: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    ai_service: AiService = Depends(get_ai_service),
):
    service = TicketService(db=db, ai_service=ai_service)

    return service.list_tickets(
        status=status,
        category=category,
        priority=priority,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/tickets/{ticket_id}",
    response_model=schemas.TicketDetail,
)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    ai_service: AiService = Depends(get_ai_service),
):
    service = TicketService(db=db, ai_service=ai_service)

    ticket = service.get_ticket(ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Chamado não encontrado.",
        )

    return schemas.TicketDetail.model_validate(ticket)


@router.patch(
    "/tickets/{ticket_id}",
    response_model=schemas.TicketRead,
)
def update_ticket(
    ticket_id: int,
    payload: schemas.TicketUpdate,
    db: Session = Depends(get_db),
    ai_service: AiService = Depends(get_ai_service),
    current_user: models.User = Depends(get_current_user),
):
    service = TicketService(db=db, ai_service=ai_service)

    ticket = service.update_ticket(ticket_id, payload)

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Chamado não encontrado.",
        )

    return ticket


@router.post(
    "/suggestions/{suggestion_id}/review",
    response_model=schemas.AiReviewRead,
    status_code=201,
)
def review_suggestion(
    suggestion_id: int,
    payload: schemas.AiReviewCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    service = ReviewService(db=db)

    review = service.review_suggestion(suggestion_id, payload)

    if not review:
        raise HTTPException(
            status_code=404,
            detail="Sugestão não encontrada.",
        )

    return review


@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    return get_metrics(db)
