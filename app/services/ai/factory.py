from app.config import settings
from app.services.ai.base import AIProvider
from app.services.ai.mock_provider import MockAIProvider


def get_ai_provider() -> AIProvider:
    """Escolhe o provider pelo .env. Para ligar um LLM real no futuro, é só adicionar um 'elif' aqui."""
    if settings.ai_provider == "mock":
        return MockAIProvider()
    raise ValueError(f"AI_PROVIDER desconhecido: {settings.ai_provider!r}")
