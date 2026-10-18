from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Priority(str, Enum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class Status(str, Enum):
    ABERTO = "aberto"
    EM_ANALISE = "em_analise"
    AGUARDANDO = "aguardando"
    RESOLVIDO = "resolvido"
    FECHADO = "fechado"


class TicketCreate(BaseModel):
    requester_name: str = Field(min_length=3, max_length=120)
    requester_email: EmailStr
    title: str = Field(min_length=5, max_length=180)
    description: str = Field(min_length=10, max_length=4000)
    category: Optional[str] = Field(default=None, max_length=80)
    priority: Optional[Priority] = None
    source: str = Field(default="portal", max_length=40)


class TicketUpdate(BaseModel):
    status: Optional[Status] = None
    category: Optional[str] = Field(default=None, max_length=80)
    priority: Optional[Priority] = None
    needs_review: Optional[bool] = None


class AiSuggestionRead(BaseModel):
    id: int
    ticket_id: int
    provider: str
    prompt_version: Optional[str] = None

    suggested_category: Optional[str] = None
    suggested_priority: Optional[str] = None

    summary: Optional[str] = None
    suggested_action: Optional[str] = None

    urgency_score: Optional[float] = None
    confidence: Optional[float] = None

    latency_ms: Optional[int] = None
    decision: Optional[str] = None
    error_message: Optional[str] = None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketRead(BaseModel):
    id: int

    requester_name: str
    requester_email: str

    title: str
    description: str

    category: Optional[str] = None
    priority: str
    status: str
    source: str

    needs_review: bool

    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TicketDetail(TicketRead):
    suggestions: List[AiSuggestionRead] = []


class TicketCreateResponse(BaseModel):
    ticket: TicketRead
    suggestion: Optional[AiSuggestionRead] = None


class AiReviewCreate(BaseModel):
    reviewer_name: str = Field(min_length=3, max_length=120)
    accepted: bool

    corrected_category: Optional[str] = Field(default=None, max_length=80)
    corrected_priority: Optional[Priority] = None

    notes: Optional[str] = Field(default=None, max_length=1000)


class AiReviewRead(BaseModel):
    id: int
    suggestion_id: int

    reviewer_name: str
    accepted: bool

    corrected_category: Optional[str] = None
    corrected_priority: Optional[str] = None

    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
    role: Optional[str] = Field(default="requester", max_length=30)


class UserRead(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LoginCreate(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
