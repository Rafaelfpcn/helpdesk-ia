from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.metrics import MetricsOut
from app.services import metrics_service

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("", response_model=MetricsOut)
def get_metrics(db: Session = Depends(get_db)):
    return metrics_service.get_metrics(db)
