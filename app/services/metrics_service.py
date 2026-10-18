from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models


def get_metrics(db: Session) -> dict:
    tickets_total = db.query(func.count(models.Ticket.id)).scalar() or 0

    tickets_by_status = dict(
        db.query(models.Ticket.status, func.count(models.Ticket.id))
        .group_by(models.Ticket.status)
        .all()
    )

    tickets_by_category = dict(
        db.query(models.Ticket.category, func.count(models.Ticket.id))
        .group_by(models.Ticket.category)
        .all()
    )

    tickets_by_priority = dict(
        db.query(models.Ticket.priority, func.count(models.Ticket.id))
        .group_by(models.Ticket.priority)
        .all()
    )

    ai_suggestions_total = (
        db.query(func.count(models.AiSuggestion.id)).scalar() or 0
    )

    ai_reviews_total = db.query(func.count(models.AiReview.id)).scalar() or 0

    ai_accepted_total = (
        db.query(func.count(models.AiReview.id))
        .filter(models.AiReview.accepted.is_(True))
        .scalar()
        or 0
    )

    ai_corrected_total = (
        db.query(func.count(models.AiReview.id))
        .filter(models.AiReview.accepted.is_(False))
        .scalar()
        or 0
    )

    ai_accepted_rate = (
        ai_accepted_total / ai_reviews_total
        if ai_reviews_total
        else None
    )

    ai_corrected_rate = (
        ai_corrected_total / ai_reviews_total
        if ai_reviews_total
        else None
    )

    ai_avg_confidence = (
        db.query(func.avg(models.AiSuggestion.confidence)).scalar()
    )

    ai_avg_latency_ms = (
        db.query(func.avg(models.AiSuggestion.latency_ms)).scalar()
    )

    ai_avg_urgency_score = (
        db.query(func.avg(models.AiSuggestion.urgency_score)).scalar()
    )

    ai_by_decision = dict(
        db.query(models.AiSuggestion.decision, func.count(models.AiSuggestion.id))
        .group_by(models.AiSuggestion.decision)
        .all()
    )

    return {
        "tickets_total": tickets_total,
        "tickets_by_status": tickets_by_status,
        "tickets_by_category": tickets_by_category,
        "tickets_by_priority": tickets_by_priority,
        "ai_suggestions_total": ai_suggestions_total,
        "ai_reviews_total": ai_reviews_total,
        "ai_accepted_total": ai_accepted_total,
        "ai_corrected_total": ai_corrected_total,
        "ai_accepted_rate": ai_accepted_rate,
        "ai_corrected_rate": ai_corrected_rate,
        "ai_avg_confidence": ai_avg_confidence,
        "ai_avg_latency_ms": ai_avg_latency_ms,
        "ai_avg_urgency_score": ai_avg_urgency_score,
        "ai_by_decision": ai_by_decision,
    }
