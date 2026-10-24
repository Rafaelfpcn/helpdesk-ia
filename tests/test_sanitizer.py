from app.services.ai.sanitizer import sanitize


def test_sanitize_masks_all_supported_types_and_counts_them():
    text = (
        "Meu CPF é 123.456.789-09, e-mail ana@exemplo.com, tel (11) 98765-4321, "
        "cartão 4111 1111 1111 1111 e senha: Abc@12345"
    )
    result = sanitize(text)
    for leaked in ["123.456.789-09", "ana@exemplo.com", "98765-4321", "4111 1111 1111 1111", "Abc@12345"]:
        assert leaked not in result.text
    assert result.redactions == {"senha": 1, "email": 1, "cpf": 1, "cartao": 1, "telefone": 1}


def test_sanitize_keeps_text_without_sensitive_data_unchanged():
    text = "A impressora do setor não imprime desde ontem."
    result = sanitize(text)
    assert result.text == text
    assert result.redactions == {}


def test_sanitize_does_not_erase_the_word_senha_without_a_value():
    result = sanitize("esqueci a senha do email")
    assert result.text == "esqueci a senha do email"
    assert result.redactions == {}


def test_ai_never_receives_raw_sensitive_data_end_to_end(client, payload):
    body = {
        **payload,
        "title": "Problema de login",
        "description": "Não consigo entrar, meu CPF é 123.456.789-09 e o telefone (11) 98765-4321.",
    }
    ticket = client.post("/api/tickets", json=body).json()
    summary = ticket["suggestion"]["summary"]
    assert "123.456.789-09" not in summary
    assert "[CPF]" in summary
    logs = client.get(f"/api/tickets/{ticket['id']}/logs").json()
    assert logs[1]["details"]["redactions"] == {"cpf": 1, "telefone": 1}
