from typing import Optional

from pydantic import BaseModel


class Correction(BaseModel):
    suggested: str
    final: str
    count: int


class AIMetrics(BaseModel):
    suggestions_total: int
    triage_coverage: Optional[float]  # sugestões / chamados
    pending_count: int
    reviewed_count: int
    confirmed_count: int
    changed_count: int
    confirmation_rate: Optional[float]  # confirmadas / revisadas
    category_accuracy: Optional[float]
    priority_accuracy: Optional[float]
    avg_confidence: Optional[float]
    avg_confidence_confirmed: Optional[float]  # calibração: confiança quando a IA acertou...
    avg_confidence_changed: Optional[float]  # ...versus quando o humano corrigiu
    failure_count: int  # chamados sem sugestão (a IA falhou)
    failure_rate: Optional[float]
    top_corrections: list[Correction]  # onde a IA mais erra a categoria


class ImpactAssumptions(BaseModel):
    manual_triage_minutes: float
    review_minutes: float
    counted_tickets: str


class ImpactEstimate(BaseModel):
    estimated_minutes_saved: float
    assumptions: ImpactAssumptions  # a estimativa NUNCA sai sem as premissas


class MetricsOut(BaseModel):
    total_tickets: int
    by_category: dict[str, int]
    by_priority: dict[str, int]
    by_status: dict[str, int]
    backlog_count: int  # aberto + em_atendimento
    resolution_rate: Optional[float]  # (resolvido + fechado) / total
    avg_resolution_hours: Optional[float]
    avg_open_hours: Optional[float]
    ai: AIMetrics
    impact: ImpactEstimate
