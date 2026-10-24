import json
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator

from app.enums import Category, Priority, Source, Status, Urgency

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
AI_NOTICE = (
    "Sugestão gerada por IA (simulada). Pode conter erros e só passa a valer "
    "depois da revisão humana."
)


class TicketCreate(BaseModel):
    """Dados que o usuário envia ao abrir um chamado."""

    model_config = ConfigDict(str_strip_whitespace=True)

    requester_name: str = Field(min_length=2, max_length=100, examples=["Ana Souza Teste"])
    requester_email: str = Field(pattern=EMAIL_PATTERN, max_length=150, examples=["ana.teste@exemplo.com"])
    initial_category: Category = Category.outros
    title: str = Field(min_length=5, max_length=120)
    description: str = Field(min_length=10, max_length=2000)
    source: Source = Source.web


class StatusUpdate(BaseModel):
    status: Status
    changed_by: str = Field(default="atendente", min_length=2, max_length=100)


class AISuggestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    suggested_category: Category
    suggested_priority: Priority
    urgency_level: Urgency
    summary: str
    initial_action: str
    confidence: float
    provider: str
    review_status: str
    reviewed_by: Optional[str] = None
    final_category: Optional[Category] = None
    final_priority: Optional[Priority] = None
    review_note: Optional[str] = None
    created_at: datetime
    reviewed_at: Optional[datetime] = None

    @computed_field
    @property
    def notice(self) -> str:
        """Aviso enviado em TODA resposta com sugestão, para o frontend sempre poder exibir."""
        return AI_NOTICE


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    requester_name: str
    requester_email: str
    title: str
    description: str
    initial_category: Category
    category: Category
    priority: Priority
    status: Status
    source: Source
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    suggestion: Optional[AISuggestionOut] = None


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_type: str
    actor: str
    details: dict
    created_at: datetime

    @field_validator("details", mode="before")
    @classmethod
    def parse_details(cls, value):
        # No banco o JSON é guardado como texto; na API devolvemos como objeto.
        return json.loads(value) if isinstance(value, str) else value
