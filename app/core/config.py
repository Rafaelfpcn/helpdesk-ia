from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "HelpDesk IA"
    env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    database_url: str = "sqlite:///./helpdesk.db"
    api_prefix: str = ""
    allowed_origins: str = "http://localhost:8000"

    ai_provider: str = "mock"
    ai_model_name: str = "mock-v1"
    ai_confidence_threshold: float = 0.70
    ai_fallback_category: str = "nao_classificado"
    ai_fallback_priority: str = "media"
    ai_max_latency_ms: int = 1500

    secret_key: str = "dev-secret-change-me-in-production-32chars"
    access_token_expire_minutes: int = 60
    auth_required: bool = False

    @property
    def app_env(self) -> str:
        return self.env

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
