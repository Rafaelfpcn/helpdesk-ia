from app.main import app
from app.services.ai.base import AIProvider
from app.services.ai.factory import get_ai_provider


def _create(client, payload, **overrides):
    response = client.post("/api/tickets", json={**payload, **overrides})
    assert response.status_code == 201
    return response.json()


# ---------- criação ----------
def test_create_ticket_returns_201_with_pending_ai_suggestion(client, payload):
    response = client.post("/api/tickets", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "aberto"
    assert body["source"] == "web"
    assert body["category"] == "rede"  # oficial = inicial até a revisão
    assert body["suggestion"]["review_status"] == "pendente"
    assert body["suggestion"]["provider"] == "mock"


def test_create_ticket_rejects_invalid_data(client, payload):
    assert client.post("/api/tickets", json={**payload, "title": "abc"}).status_code == 422
    assert client.post("/api/tickets", json={**payload, "requester_email": "sem-arroba"}).status_code == 422
    assert client.post("/api/tickets", json={**payload, "initial_category": "xyz"}).status_code == 422


def test_ticket_is_saved_even_if_ai_fails(client, payload):
    class FailingProvider(AIProvider):
        name = "falha"

        def analyze(self, title, description):
            raise RuntimeError("boom")

    app.dependency_overrides[get_ai_provider] = lambda: FailingProvider()
    response = client.post("/api/tickets", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["suggestion"] is None
    assert body["priority"] == "media"  # prioridade padrão (falha segura)
    logs = client.get(f"/api/tickets/{body['id']}/logs").json()
    assert [e["event_type"] for e in logs] == ["ticket_created", "suggestion_failed"]


# ---------- listagem e detalhe ----------
def test_list_tickets_and_filter_by_status(client, payload):
    first = _create(client, payload)
    _create(client, payload, title="Outro chamado de teste")
    client.patch(f"/api/tickets/{first['id']}/status", json={"status": "em_atendimento"})

    all_tickets = client.get("/api/tickets").json()
    in_progress = client.get("/api/tickets", params={"status": "em_atendimento"}).json()
    assert len(all_tickets) == 2
    assert [t["id"] for t in in_progress] == [first["id"]]


def test_get_unknown_ticket_returns_404_with_standard_error(client):
    response = client.get("/api/tickets/999")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "ticket_not_found"


# ---------- status ----------
def test_update_status_sets_resolved_at(client, payload):
    ticket = _create(client, payload)
    url = f"/api/tickets/{ticket['id']}/status"
    assert client.patch(url, json={"status": "em_atendimento"}).status_code == 200
    resolved = client.patch(url, json={"status": "resolvido"}).json()
    assert resolved["status"] == "resolvido"
    assert resolved["resolved_at"] is not None


def test_invalid_status_transition_returns_409(client, payload):
    ticket = _create(client, payload)
    response = client.patch(f"/api/tickets/{ticket['id']}/status", json={"status": "resolvido"})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "invalid_status_transition"


# ---------- logs ----------
def test_logs_record_creation_and_suggestion(client, payload):
    ticket = _create(client, payload)
    logs = client.get(f"/api/tickets/{ticket['id']}/logs").json()
    assert [e["event_type"] for e in logs] == ["ticket_created", "suggestion_generated"]
