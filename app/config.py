from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Lê variáveis de ambiente / .env. Valores padrão servem para rodar sem configurar nada."""

    app_name: str = "HelpDesk IA"
    database_url: str = "sqlite:///./helpdesk.db"
    ai_provider: str = "mock"
    manual_triage_minutes: float = 5.0
    review_minutes: float = 1.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
