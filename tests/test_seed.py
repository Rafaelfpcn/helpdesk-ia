from app.schemas.ticket import TicketCreate
from app.services.ai.mock_provider import MockAIProvider
from app.services.metrics_service import get_metrics
from scripts.seed import load_entries, run_seed


def test_seed_file_has_valid_fictional_tickets():
    entries = load_entries()
    assert len(entries) >= 30
    for entry in entries:
        TicketCreate(**entry, requester_email="teste.seed@exemplo.com")  # valida tamanhos e categorias
        assert entry["requester_name"].endswith("Teste")  # convenção: todo nome fictício termina em "Teste"


def test_seed_populates_database_with_consistent_metrics(db_session):
    total = run_seed(db_session, MockAIProvider(), load_entries())
    metrics = get_metrics(db_session)
    assert metrics["total_tickets"] == total
    assert metrics["ai"]["triage_coverage"] == 1.0
    assert metrics["ai"]["reviewed_count"] > 0
    assert metrics["avg_resolution_hours"] is not None
