from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.enums import Category, Priority, Urgency


@dataclass(frozen=True)
class AIAnalysis:
    """Resultado padronizado de qualquer provider de IA."""

    category: Category
    priority: Priority
    urgency: Urgency
    summary: str
    initial_action: str
    confidence: float  # 0.0 a 1.0


class AIProvider(ABC):
    """Contrato que todo provider deve seguir. O sistema só conhece esta interface."""

    name: str

    @abstractmethod
    def analyze(self, title: str, description: str) -> AIAnalysis:
        pass
