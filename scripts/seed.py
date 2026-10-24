"""Popula o banco com chamados FICTÍCIOS para demonstração.

Uso:
  python -m scripts.seed         # só se o banco estiver vazio
  python -m scripts.seed --reset # apaga os chamados e recria
"""

import argparse
import json
import random
import unicodedata
from datetime import timedelta
from pathlib import Path

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.enums import Category, EventType, Priority, Source, Status
from app.models import AISuggestion, AuditLog, Ticket
from app.schemas.review import ReviewChange, ReviewConfirm
from app.schemas.ticket import TicketCreate
from app.services import review_service, ticket_service
from app.services.ai.base import AIProvider
from app.services.ai.factory import get_ai_provider
from app.utils import utcnow

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "seed_tickets.json"
REVIEWERS = ["Carlos Atendente Teste", "Marina Suporte Teste"]
MIN_AGE_HOURS, MAX_AGE_HOURS = 2, 14 * 24  # chamados abertos entre 2 horas e 14 dias atrás

# (limite sorteado, caminho de status): define quanto cada chamado "avança" na fila
STATUS_PATHS = [
    (0.35, []),
    (0.60, [Status.em_atendimento]),
    (0.90, [Status.em_atendimento, Status.resolvido]),
    (1.00, [Status.em_atendimento, Status.resolvido, Status.fechado]),
]


def load_entries() -> list[dict]:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def _email_from_name(name: str) -> str:
    """'Ana Souza Teste' -> 'ana.souza@exemplo.com' (domínio reservado a exemplos)."""
    ascii_name = "".join(
        ch for ch in unicodedata.normalize("NFD", name.lower()) if unicodedata.category(ch) != "Mn"
    )
    return ".".join(ascii_name.split()[:2]) + "@exemplo.com"


def _simulate_review(db: Session, ticket: Ticket, reviewer: str, rng: random.Random) -> None:
    suggestion = ticket.suggestion
    if suggestion is None:
        return
    roll = rng.random()
    if roll < 0.25:
        return  # 25% ficam pendentes
    if roll < 0.70:
        review_service.confirm_suggestion(db, ticket.id, ReviewConfirm(reviewed_by=reviewer))
        return

    # 30%: o atendente discorda da IA (a categoria SEMPRE muda, então a revisão é válida)
    category = rng.choice([c for c in Category if c.value != suggestion.suggested_category])
    priority = (
        Priority(suggestion.suggested_priority)
        if rng.random() < 0.5
        else rng.choice(list(Priority))
    )
    review_service.change_suggestion(
        db,
        ticket.id,
        ReviewChange(
            reviewed_by=reviewer,
            category=category,
            priority=priority,
            note="Ajuste feito na triagem (dado de demonstração).",
        ),
    )


def _simulate_status(db: Session, ticket: Ticket, reviewer: str, rng: random.Random) -> None:
    roll = rng.random()
    for limit, path in STATUS_PATHS:
        if roll < limit:
            for status in path:
                ticket_service.update_status(db, ticket.id, status, reviewer)
            return


def _backdate(db: Session, ticket: Ticket, age_hours: int, rng: random.Random) -> None:
    """Move o histórico do chamado para o passado, mantendo a ordem dos eventos.

    Sem isso, todos os chamados teriam 'agora' como data e as métricas de tempo ficariam zeradas.
    """
    ticket.created_at = utcnow() - timedelta(hours=age_hours)
    logs = list(ticket.logs)
    step_max = max(2, int(age_hours * 60 / (len(logs) + 1)))  # garante que nada cai no futuro
    cursor = ticket.created_at
    for position, log in enumerate(logs):
        if position > 0:
            cursor += timedelta(minutes=rng.randint(1, step_max))
        log.created_at = cursor
        details = json.loads(log.details)
        if log.event_type == EventType.status_changed.value and details.get("to") == Status.resolvido.value:
            ticket.resolved_at = cursor
        if ticket.suggestion and log.event_type in (
            EventType.suggestion_confirmed.value,
            EventType.suggestion_changed.value,
        ):
            ticket.suggestion.reviewed_at = cursor

    if ticket.suggestion:
        ticket.suggestion.created_at = ticket.created_at
    ticket.updated_at = cursor
    db.commit()


def run_seed(db: Session, provider: AIProvider, entries: list[dict], seed: int = 42) -> int:
    """Cria os chamados passando pelo fluxo REAL (validação, sanitizer, IA, revisão, status)."""
    rng = random.Random(seed)  # semente fixa: todo mundo gera o mesmo dashboard
    for index, entry in enumerate(entries):
        data = TicketCreate(
            **entry,
            requester_email=_email_from_name(entry["requester_name"]),
            source=Source.seed,
        )
        ticket = ticket_service.create_ticket(db, data, provider)
        reviewer = REVIEWERS[index % len(REVIEWERS)]
        _simulate_review(db, ticket, reviewer, rng)
        _simulate_status(db, ticket, reviewer, rng)
        _backdate(db, ticket, rng.randint(MIN_AGE_HOURS, MAX_AGE_HOURS), rng)
    return len(entries)


def _wipe(db: Session) -> None:
    for model in (AuditLog, AISuggestion, Ticket):  # filhos antes do pai
        db.execute(delete(model))
    db.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Popula o banco com chamados fictícios.")
    parser.add_argument("--reset", action="store_true", help="apaga todos os chamados antes de popular")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if args.reset:
            _wipe(db)
        elif db.scalar(select(func.count()).select_from(Ticket)):
            print("O banco já tem chamados. Use --reset para recriar.")
            return

        total = run_seed(db, get_ai_provider(), load_entries())
        print(f"{total} chamados fictícios criados com sucesso. Abra /dashboard para ver as métricas!")


if __name__ == "__main__":
    main()
