from collections import Counter
from enum import Enum
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.enums import Category, Priority, ReviewStatus, Status
from app.models import AISuggestion, Ticket
from app.utils import utcnow


def _ratio(part: int, whole: int) -> Optional[float]:
    """Divisão segura: sem dados, devolve None (e não 0%, que enganaria)."""
    return round(part / whole, 4) if whole else None


def _avg(values: list[float]) -> Optional[float]:
    return round(sum(values) / len(values), 4) if values else None


def _count_by(db: Session, column, enum_cls: type[Enum]) -> dict[str, int]:
    rows = db.execute(select(column, func.count()).group_by(column)).all()
    counts = {value: count for value, count in rows}
    # Inclui valores com zero chamados, para o dashboard ter sempre as mesmas barras.
    return {item.value: counts.get(item.value, 0) for item in enum_cls}


def _avg_hours(deltas) -> Optional[float]:
    hours = [d.total_seconds() / 3600 for d in deltas]
    return round(sum(hours) / len(hours), 2) if hours else None


def estimate_impact(confirmed_count: int, manual_minutes: float, review_minutes: float) -> dict:
    """Estimativa CONSERVADORA de tempo economizado.

    Conta apenas sugestões confirmadas: quando o atendente corrige a IA, assumimos que não houve ganho.
    Em cada chamado confirmado, o ganho é (triagem manual - tempo de revisão).
    É uma estimativa baseada em premissas configuráveis, não uma medição.
    """
    saved_per_ticket = max(manual_minutes - review_minutes, 0.0)
    return {
        "estimated_minutes_saved": round(confirmed_count * saved_per_ticket, 1),
        "assumptions": {
            "manual_triage_minutes": manual_minutes,
            "review_minutes": review_minutes,
            "counted_tickets": "apenas sugestões confirmadas",
        },
    }


def _top_corrections(reviewed: list[AISuggestion], limit: int = 3) -> list[dict]:
    pairs = Counter(
        (s.suggested_category, s.final_category)
        for s in reviewed
        if s.final_category is not None and s.final_category != s.suggested_category
    )
    return [{"suggested": a, "final": b, "count": n} for (a, b), n in pairs.most_common(limit)]


def _ai_metrics(db: Session, total_tickets: int) -> dict:
    suggestions = list(db.scalars(select(AISuggestion)))
    reviewed = [s for s in suggestions if s.review_status != ReviewStatus.pendente.value]
    confirmed = [s for s in reviewed if s.review_status == ReviewStatus.confirmada.value]
    changed = [s for s in reviewed if s.review_status == ReviewStatus.alterada.value]
    without_suggestion = total_tickets - len(suggestions)  # no MVP, só a falha da IA causa isso

    return {
        "suggestions_total": len(suggestions),
        "triage_coverage": _ratio(len(suggestions), total_tickets),
        "pending_count": len(suggestions) - len(reviewed),
        "reviewed_count": len(reviewed),
        "confirmed_count": len(confirmed),
        "changed_count": len(changed),
        # Pendentes ficam FORA do denominador: "ainda não revisado" não é "errado".
        "confirmation_rate": _ratio(len(confirmed), len(reviewed)),
        "category_accuracy": _ratio(
            sum(s.final_category == s.suggested_category for s in reviewed), len(reviewed)
        ),
        "priority_accuracy": _ratio(
            sum(s.final_priority == s.suggested_priority for s in reviewed), len(reviewed)
        ),
        "avg_confidence": _avg([s.confidence for s in suggestions]),
        "avg_confidence_confirmed": _avg([s.confidence for s in confirmed]),
        "avg_confidence_changed": _avg([s.confidence for s in changed]),
        "failure_count": without_suggestion,
        "failure_rate": _ratio(without_suggestion, total_tickets),
        "top_corrections": _top_corrections(reviewed),
    }


def get_metrics(db: Session) -> dict:
    total = db.scalar(select(func.count()).select_from(Ticket)) or 0
    by_status = _count_by(db, Ticket.status, Status)
    ai = _ai_metrics(db, total)

    resolved = db.execute(
        select(Ticket.created_at, Ticket.resolved_at).where(Ticket.resolved_at.is_not(None))
    ).all()
    still_open = db.scalars(
        select(Ticket.created_at).where(
            Ticket.status.in_([Status.aberto.value, Status.em_atendimento.value])
        )
    ).all()
    now = utcnow()

    return {
        "total_tickets": total,
        "by_category": _count_by(db, Ticket.category, Category),
        "by_priority": _count_by(db, Ticket.priority, Priority),
        "by_status": by_status,
        "backlog_count": by_status[Status.aberto.value] + by_status[Status.em_atendimento.value],
        "resolution_rate": _ratio(
            by_status[Status.resolvido.value] + by_status[Status.fechado.value], total
        ),
        "avg_resolution_hours": _avg_hours(resolved_at - created_at for created_at, resolved_at in resolved),
        "avg_open_hours": _avg_hours(now - created_at for created_at in still_open),
        "ai": ai,
        "impact": estimate_impact(
            ai["confirmed_count"], settings.manual_triage_minutes, settings.review_minutes
        ),
    }
