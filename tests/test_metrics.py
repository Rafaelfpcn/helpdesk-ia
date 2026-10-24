from app.main import app
from app.services.ai.base import AIProvider
from app.services.ai.factory import get_ai_provider
from app.services.metrics_service import estimate_impact

REVIEWER = {"reviewed_by": "Carlos Atendente Teste"}


def test_estimate_impact_counts_only_confirmed_and_uses_assumptions():
    result = estimate_impact(confirmed_count=10, manual_minutes=5.0, review_minutes=1.0)
    assert result["estimated_minutes_saved"] == 40.0
    assert result["assumptions"]["manual_triage_minutes"] == 5.0
    assert result["assumptions"]["counted_tickets"] == "apenas sugestões confirmadas"


def test_estimate_impact_is_never_negative():
    # Se a revisão levar mais tempo que a triagem manual, a estimativa é 0, nunca negativa.
    assert estimate_impact(10, manual_minutes=1.0, review_minutes=3.0)["estimated_minutes_saved"] == 0.0


def test_metrics_with_empty_database(client):
    body = client.get("/api/metrics").json()
    assert body["total_tickets"] == 0
    assert set(body["by_status"].values()) == {0}
    assert body["avg_resolution_hours"] is None
    assert body["ai"]["suggestions_total"] == 0
    assert body["ai"]["confirmation_rate"] is None  # sem dados: None, não 0%


def test_metrics_reflect_reviews_and_ai_quality(client, payload):
    t1 = client.post("/api/tickets", json=payload).json()
    t2 = client.post(
        "/api/tickets",
        json={**payload, "title": "Impressora sem toner", "description": "A impressora não imprime e o toner acabou."},
    ).json()
    client.post("/api/tickets", json=payload)  # t3 fica pendente

    client.post(f"/api/tickets/{t1['id']}/review/confirm", json=REVIEWER)
    # t2: o humano corrige só a CATEGORIA e mantém a prioridade sugerida
    client.post(
        f"/api/tickets/{t2['id']}/review/change",
        json={**REVIEWER, "category": "hardware", "priority": t2["suggestion"]["suggested_priority"]},
    )
    # t1 é resolvido, o que gera tempo de resolução
    client.patch(f"/api/tickets/{t1['id']}/status", json={"status": "em_atendimento"})
    client.patch(f"/api/tickets/{t1['id']}/status", json={"status": "resolvido"})

    body = client.get("/api/metrics").json()
    ai = body["ai"]
    assert body["total_tickets"] == 3
    assert body["by_category"]["rede"] == 2 and body["by_category"]["hardware"] == 1
    assert body["by_status"]["resolvido"] == 1 and body["by_status"]["aberto"] == 2
    assert body["avg_resolution_hours"] is not None
    assert body["avg_open_hours"] is not None
    assert ai["suggestions_total"] == 3 and ai["triage_coverage"] == 1.0
    assert (ai["pending_count"], ai["reviewed_count"]) == (1, 2)
    assert (ai["confirmed_count"], ai["changed_count"]) == (1, 1)
    assert ai["confirmation_rate"] == 0.5
    assert ai["category_accuracy"] == 0.5
    assert ai["priority_accuracy"] == 1.0


def test_metrics_top_corrections_backlog_failure_rate_and_calibration(client, payload):
    tickets = [client.post("/api/tickets", json=payload).json() for _ in range(3)]
    for ticket in tickets[:2]:
        # duas correções iguais: rede -> hardware
        client.post(
            f"/api/tickets/{ticket['id']}/review/change",
            json={**REVIEWER, "category": "hardware", "priority": ticket["suggestion"]["suggested_priority"]},
        )
    client.post(f"/api/tickets/{tickets[2]['id']}/review/confirm", json=REVIEWER)

    class FailingProvider(AIProvider):
        name = "falha"

        def analyze(self, title, description):
            raise RuntimeError("boom")

    app.dependency_overrides[get_ai_provider] = lambda: FailingProvider()
    client.post("/api/tickets", json=payload)  # este chamado fica sem sugestão

    body = client.get("/api/metrics").json()
    ai = body["ai"]
    assert ai["top_corrections"] == [{"suggested": "rede", "final": "hardware", "count": 2}]
    assert body["backlog_count"] == 4
    assert body["resolution_rate"] == 0.0
    assert (ai["failure_count"], ai["failure_rate"]) == (1, 0.25)
    assert ai["triage_coverage"] == 0.75
    assert ai["avg_confidence_confirmed"] is not None
    assert ai["avg_confidence_changed"] is not None
    assert body["impact"]["estimated_minutes_saved"] >= 0
    assert body["impact"]["assumptions"]["counted_tickets"] == "apenas sugestões confirmadas"
