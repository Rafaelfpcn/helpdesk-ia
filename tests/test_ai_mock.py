import pytest

from app.enums import Category, Priority, Urgency
from app.services.ai.mock_provider import MockAIProvider

provider = MockAIProvider()


@pytest.mark.parametrize(
    "title, description, expected",
    [
        ("VPN caiu", "A internet está lenta e a VPN não conecta.", Category.rede),
        ("Esqueci a senha", "Preciso redefinir minha senha de login.", Category.acesso_senha),
        ("Impressão falhando", "A impressora não imprime e o toner acabou.", Category.impressora),
        ("Notebook", "O notebook não liga e a bateria parece morta.", Category.hardware),
    ],
)
def test_mock_classifies_by_keywords(title, description, expected):
    assert provider.analyze(title, description).category == expected


def test_mock_ignores_accents_and_case():
    result = provider.analyze("IMPRESSÃO", "A IMPRESSORA parou")
    assert result.category == Category.impressora


def test_mock_detects_critical_priority_and_maps_urgency():
    result = provider.analyze("Servidor", "O sistema está fora do ar e ninguém consegue acessar.")
    assert result.priority == Priority.critica
    assert result.urgency == Urgency.imediata


def test_mock_security_never_below_high():
    result = provider.analyze("E-mail estranho", "Recebi um phishing, só uma dúvida quando puder.")
    assert result.category == Category.seguranca
    assert result.priority in (Priority.alta, Priority.critica)


def test_mock_unknown_text_falls_back_to_outros_with_low_confidence():
    result = provider.analyze("Pedido", "Gostaria de conversar sobre um assunto diferente.")
    assert result.category == Category.outros
    assert result.priority == Priority.media
    assert result.confidence == 0.3


def test_mock_is_deterministic_and_confidence_in_range():
    first = provider.analyze("VPN", "A VPN não conecta e a internet está lenta.")
    second = provider.analyze("VPN", "A VPN não conecta e a internet está lenta.")
    assert first == second
    assert 0.0 <= first.confidence <= 1.0


def test_mock_ignores_sanitizer_markers():
    # "[EMAIL]" não pode empurrar o chamado para a categoria "email".
    result = provider.analyze("Falha", "O sistema do financeiro dá erro. Contato: [EMAIL]")
    assert result.category == Category.software
