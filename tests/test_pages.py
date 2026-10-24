def test_pages_home_renders_form(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Abrir Novo Chamado de TI" in response.text
    assert "Aviso de Privacidade" in response.text


def test_pages_tickets_list_renders(client, payload):
    client.post("/api/tickets", json=payload)
    response = client.get("/tickets")
    assert response.status_code == 200
    assert "Central de Chamados de TI" in response.text
    assert payload["title"] in response.text


def test_pages_ticket_detail_renders_ai_notice(client, payload):
    ticket = client.post("/api/tickets", json=payload).json()
    response = client.get(f"/tickets/{ticket['id']}")
    assert response.status_code == 200
    assert "Sugestão da IA (Triagem)" in response.text
    assert "revisão humana" in response.text
    assert "Trilha de Auditoria" in response.text


def test_pages_dashboard_renders_metrics(client, payload):
    client.post("/api/tickets", json=payload)
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "Dashboard de Métricas" in response.text
    assert "Impacto Operacional Estimado" in response.text
    assert "Qualidade das Sugestões da IA" in response.text


def test_pages_escape_xss_content(client, payload):
    xss_title = "<script>alert('xss')</script>"
    xss_desc = "Tentativa de injeção <img src=x onerror=alert(1)>"
    ticket = client.post(
        "/api/tickets",
        json={**payload, "title": xss_title, "description": xss_desc},
    ).json()

    response = client.get(f"/tickets/{ticket['id']}")
    assert response.status_code == 200
    # O HTML não pode conter a tag bruta sem escape
    assert "<script>alert('xss')</script>" not in response.text
    assert "&lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;" in response.text or "&lt;script&gt;" in response.text
