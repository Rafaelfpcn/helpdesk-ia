from app.services.ai import MockAiProvider


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200

    body = response.json()

    assert body["database"] == "ok"
    assert body["ai_provider"] == "mock"


def test_create_ticket(client):
    payload = {
        "requester_name": "Maria Silva",
        "requester_email": "maria.silva@example.com",
        "title": "Sistema financeiro fora do ar",
        "description": (
            "O sistema financeiro está fora do ar para todos os usuários "
            "do setor financeiro. Não conseguimos emitir notas."
        ),
        "source": "portal",
    }

    response = client.post("/tickets", json=payload)

    assert response.status_code == 201

    body = response.json()

    assert body["ticket"]["title"] == payload["title"]
    assert body["ticket"]["status"] == "aberto"
    assert body["ticket"]["needs_review"] is True

    assert body["suggestion"]["provider"] == "mock"
    assert body["suggestion"]["suggested_category"] is not None
    assert body["suggestion"]["suggested_priority"] is not None


def test_list_tickets(client):
    payload = {
        "requester_name": "João Souza",
        "requester_email": "joao.souza@example.com",
        "title": "Problema com impressora",
        "description": (
            "A impressora do setor administrativo não está imprimindo."
        ),
        "source": "portal",
    }

    create_response = client.post("/tickets", json=payload)
    assert create_response.status_code == 201

    response = client.get("/tickets")

    assert response.status_code == 200

    body = response.json()

    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["title"] == payload["title"]


def test_mock_ai_provider_infra():
    provider = MockAiProvider()

    result = provider.analyze(
        title="Servidor fora do ar",
        description=(
            "O servidor principal está fora do ar e todos os usuários "
            "estão sem acesso ao sistema financeiro."
        ),
    )

    assert result.suggested_category == "Infraestrutura"
    assert result.suggested_priority in ["alta", "critica"]
    assert result.confidence > 0.5
