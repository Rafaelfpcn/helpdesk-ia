from app.main import app
from app.services.ai.base import AIProvider
from app.services.ai.factory import get_ai_provider

REVIEWER = {"reviewed_by": "Carlos Atendente Teste"}


def _create(client, payload, **overrides):
    response = client.post("/api/tickets", json={**payload, "initial_category": "outros", **overrides})
    assert response.status_code == 201
    return response.json()


def test_confirm_applies_ai_suggestion_to_ticket(client, payload):
    ticket = _create(client, payload)
    response = client.post(f"/api/tickets/{ticket['id']}/review/confirm", json=REVIEWER)
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "rede"  # sugestão da IA virou oficial
    assert body["suggestion"]["review_status"] == "confirmada"
    assert body["suggestion"]["final_category"] == "rede"
    assert body["suggestion"]["reviewed_by"] == REVIEWER["reviewed_by"]
    assert "revisão humana" in body["suggestion"]["notice"]


def test_change_overrides_ticket_but_preserves_original_suggestion(client, payload):
    ticket = _create(client, payload)
    response = client.post(
        f"/api/tickets/{ticket['id']}/review/change",
        json={**REVIEWER, "category": "hardware", "priority": "alta", "note": "Era problema no cabo."},
    )
    body = response.json()
    assert response.status_code == 200
    assert (body["category"], body["priority"]) == ("hardware", "alta")
    assert body["suggestion"]["review_status"] == "alterada"
    assert body["suggestion"]["suggested_category"] == "rede"  # a sugestão original é preservada
    assert body["suggestion"]["final_category"] == "hardware"
    logs = client.get(f"/api/tickets/{ticket['id']}/logs").json()
    assert [e["event_type"] for e in logs][-1] == "suggestion_changed"


def test_review_twice_returns_409(client, payload):
    ticket = _create(client, payload)
    url = f"/api/tickets/{ticket['id']}/review/confirm"
    client.post(url, json=REVIEWER)
    response = client.post(url, json=REVIEWER)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "review_already_done"


def test_change_with_same_values_as_suggestion_is_rejected(client, payload):
    ticket = _create(client, payload)
    suggestion = ticket["suggestion"]
    response = client.post(
        f"/api/tickets/{ticket['id']}/review/change",
        json={
            **REVIEWER,
            "category": suggestion["suggested_category"],
            "priority": suggestion["suggested_priority"],
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_review"


def test_review_ticket_without_suggestion_returns_409(client, payload):
    class FailingProvider(AIProvider):
        name = "falha"

        def analyze(self, title, description):
            raise RuntimeError("boom")

    app.dependency_overrides[get_ai_provider] = lambda: FailingProvider()
    ticket = _create(client, payload)
    response = client.post(f"/api/tickets/{ticket['id']}/review/confirm", json=REVIEWER)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "no_suggestion"


def test_review_unknown_ticket_returns_404(client):
    response = client.post("/api/tickets/999/review/confirm", json=REVIEWER)
    assert response.status_code == 404


def test_review_requires_reviewer_name(client, payload):
    ticket = _create(client, payload)
    response = client.post(f"/api/tickets/{ticket['id']}/review/confirm", json={"reviewed_by": "A"})
    assert response.status_code == 422
