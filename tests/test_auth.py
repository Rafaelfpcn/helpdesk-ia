def test_register_user(client):
    payload = {
        "name": "Usuário Teste",
        "email": "teste@example.com",
        "password": "senha123",
        "role": "requester",
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 201

    body = response.json()

    assert body["email"] == payload["email"]
    assert body["role"] == payload["role"]
    assert body["is_active"] is True


def test_login_and_token(client):
    register_payload = {
        "name": "Usuário Login",
        "email": "login@example.com",
        "password": "senha123",
        "role": "requester",
    }

    register_response = client.post("/auth/register", json=register_payload)

    assert register_response.status_code == 201

    login_payload = {
        "email": "login@example.com",
        "password": "senha123",
    }

    response = client.post("/auth/token", json=login_payload)

    assert response.status_code == 200

    body = response.json()

    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_me_without_auth_when_auth_not_required(client):
    response = client.get("/auth/me")

    assert response.status_code == 200

    body = response.json()

    assert body["email"] == "demo@example.com"
