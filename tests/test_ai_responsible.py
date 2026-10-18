from app.services.ai import AiService, MockAiProvider


def test_ai_service_low_confidence_manual_review():
    provider = MockAiProvider()

    service = AiService(
        provider=provider,
        provider_name="mock",
        prompt_version="v1.0-mock",
        confidence_threshold=0.70,
    )

    analysis = service.analyze_ticket(
        title="Preciso de ajuda",
        description="Preciso de ajuda com uma coisa aqui no setor.",
    )

    assert analysis.decision == "manual_review"
    assert analysis.confidence < 0.70


def test_ai_service_high_confidence_auto_fill():
    provider = MockAiProvider()

    service = AiService(
        provider=provider,
        provider_name="mock",
        prompt_version="v1.0-mock",
        confidence_threshold=0.70,
    )

    analysis = service.analyze_ticket(
        title="Servidor fora do ar",
        description=(
            "O servidor principal está fora do ar e todos os usuários "
            "estão sem acesso ao sistema financeiro."
        ),
    )

    assert analysis.decision == "auto_fill"
    assert analysis.confidence >= 0.70


def test_ai_service_error_fallback():
    class BrokenProvider:
        def analyze(self, title, description):
            raise RuntimeError("Falha simulada na IA")

    service = AiService(
        provider=BrokenProvider(),
        provider_name="broken",
        prompt_version="v1.0-mock",
        confidence_threshold=0.70,
        fallback_category="nao_classificado",
        fallback_priority="media",
    )

    analysis = service.analyze_ticket(
        title="Chamado importante",
        description="O sistema está com problema sério.",
    )

    assert analysis.decision == "manual_review"
    assert analysis.error_message == "Falha simulada na IA"
    assert analysis.suggested_category == "nao_classificado"
    assert analysis.suggested_priority == "media"
    assert analysis.confidence == 0.0
