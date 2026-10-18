import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


def sanitize_text(text: str) -> str:
    """
    Sanitização simples para reduzir exposição de dados sensíveis.
    Não é uma solução completa de LGPD, mas demonstra preocupação com privacidade.
    """
    text = re.sub(
        r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b",
        "[CPF_REMOVIDO]",
        text,
    )

    text = re.sub(
        r"[\w\.-]+@[\w\.-]+\.\w+",
        "[EMAIL_REMOVIDO]",
        text,
    )

    text = re.sub(
        r"\b\d{2,5}[-\s]?\d{4}\b",
        "[TELEFONE_REMOVIDO]",
        text,
    )

    return " ".join(text.split())


@dataclass
class AiAnalysisResult:
    suggested_category: str
    suggested_priority: str
    summary: str
    suggested_action: str
    urgency_score: float
    confidence: float


@dataclass
class AiTicketAnalysis:
    provider: str
    prompt_version: str

    suggested_category: str
    suggested_priority: str

    summary: str
    suggested_action: str

    urgency_score: float
    confidence: float

    latency_ms: int

    decision: str = "manual_review"
    error_message: Optional[str] = None


class BaseAiProvider(ABC):
    @abstractmethod
    def analyze(self, title: str, description: str) -> AiAnalysisResult:
        raise NotImplementedError


class MockAiProvider(BaseAiProvider):
    """
    IA simulada usando palavras-chave.
    Permite rodar sem custos ou chave externa; totalmente plugável.
    """

    CATEGORY_RULES = {
        "Infraestrutura": [
            "fora do ar",
            "servidor",
            "rede",
            "internet",
            "lento",
            "lentidão",
            "indisponível",
            "instabilidade",
            "sem conexão",
        ],
        "Acesso": [
            "senha",
            "login",
            "acesso",
            "bloqueado",
            "permissão",
            "usuário",
        ],
        "Hardware": [
            "impressora",
            "teclado",
            "mouse",
            "notebook",
            "computador",
            "monitor",
        ],
        "Sistema": [
            "erp",
            "sistema financeiro",
            "erro no sistema",
            "bug",
            "falha no sistema",
        ],
        "Solicitação": [
            "dúvida",
            "como fazer",
            "instalação",
            "instalar",
            "novo acesso",
            "solicito",
        ],
    }

    URGENCY_TERMS = [
        "urgente",
        "não consigo trabalhar",
        "todos os usuários",
        "paralisado",
        "crítico",
        "critico",
        "imediato",
    ]

    def analyze(self, title: str, description: str) -> AiAnalysisResult:
        text = f"{title} {description}".lower()

        category, matches = self._detect_category(text)
        has_urgency = self._detect_urgency(text)

        confidence = self._calculate_confidence(matches)
        urgency_score = self._calculate_urgency_score(matches, has_urgency)
        priority = self._calculate_priority(category, has_urgency)

        summary = self._generate_summary(title, description)
        suggested_action = self._generate_action(category)

        return AiAnalysisResult(
            suggested_category=category,
            suggested_priority=priority,
            summary=summary,
            suggested_action=suggested_action,
            urgency_score=urgency_score,
            confidence=confidence,
        )

    def _detect_category(self, text: str) -> tuple[str, int]:
        best_category = "Outros"
        best_score = 0

        for category, keywords in self.CATEGORY_RULES.items():
            score = sum(1 for keyword in keywords if keyword in text)

            if score > best_score:
                best_score = score
                best_category = category

        return best_category, best_score

    def _detect_urgency(self, text: str) -> bool:
        return any(term in text for term in self.URGENCY_TERMS)

    def _calculate_confidence(self, matches: int) -> float:
        if matches <= 0:
            return 0.35

        if matches == 1:
            return 0.55

        if matches == 2:
            return 0.70

        return 0.85

    def _calculate_urgency_score(self, matches: int, has_urgency: bool) -> float:
        score = 0.45 + (0.10 * matches)

        if has_urgency:
            score += 0.25

        return min(score, 1.0)

    def _calculate_priority(self, category: str, has_urgency: bool) -> str:
        if has_urgency:
            if category == "Infraestrutura":
                return "critica"
            return "alta"

        if category == "Infraestrutura":
            return "alta"

        if category == "Sistema":
            return "alta"

        if category == "Acesso":
            return "media"

        if category == "Hardware":
            return "media"

        if category == "Solicitação":
            return "baixa"

        return "media"

    def _generate_summary(self, title: str, description: str) -> str:
        description_fragment = description.strip().replace("\n", " ")

        if len(description_fragment) > 180:
            description_fragment = description_fragment[:180] + "..."

        return f"{title}. {description_fragment}"

    def _generate_action(self, category: str) -> str:
        actions = {
            "Infraestrutura": (
                "Verificar conectividade, status do servidor, serviços afetados "
                "e impacto em outros usuários."
            ),
            "Acesso": (
                "Validar identidade do solicitante, verificar permissões, "
                "status da conta e política de senhas."
            ),
            "Hardware": (
                "Verificar condições físicas do equipamento, drivers, "
                "conexões e disponibilidade de reserva."
            ),
            "Sistema": (
                "Verificar logs da aplicação, versão do sistema, "
                "usuários afetados e possíveis erros recentes."
            ),
            "Solicitação": (
                "Registrar solicitação, verificar catálogo de serviços "
                "e orientar o usuário sobre o procedimento."
            ),
            "Outros": (
                "Realizar triagem manual para entender melhor o problema."
            ),
        }

        return actions.get(category, actions["Outros"])


class AiService:
    def __init__(
        self,
        provider: BaseAiProvider,
        provider_name: str = "mock",
        prompt_version: str = "v1.0-mock",
        confidence_threshold: float = 0.70,
        fallback_category: str = "nao_classificado",
        fallback_priority: str = "media",
    ):
        self.provider = provider
        self.provider_name = provider_name
        self.prompt_version = prompt_version
        self.confidence_threshold = confidence_threshold
        self.fallback_category = fallback_category
        self.fallback_priority = fallback_priority

    def analyze_ticket(self, title: str, description: str) -> AiTicketAnalysis:
        start = time.perf_counter()

        sanitized_text = sanitize_text(f"{title}\n{description}")

        try:
            result = self.provider.analyze(
                title=title,
                description=sanitized_text,
            )

            latency_ms = int((time.perf_counter() - start) * 1000)

            decision = (
                "auto_fill"
                if result.confidence >= self.confidence_threshold
                else "manual_review"
            )

            return AiTicketAnalysis(
                provider=self.provider_name,
                prompt_version=self.prompt_version,
                suggested_category=result.suggested_category,
                suggested_priority=result.suggested_priority,
                summary=result.summary,
                suggested_action=result.suggested_action,
                urgency_score=result.urgency_score,
                confidence=result.confidence,
                latency_ms=latency_ms,
                decision=decision,
                error_message=None,
            )

        except Exception as exc:
            latency_ms = int((time.perf_counter() - start) * 1000)

            return AiTicketAnalysis(
                provider=self.provider_name,
                prompt_version=self.prompt_version,
                suggested_category=self.fallback_category,
                suggested_priority=self.fallback_priority,
                summary=title,
                suggested_action="Revisar manualmente, pois a IA falhou.",
                urgency_score=0.5,
                confidence=0.0,
                latency_ms=latency_ms,
                decision="manual_review",
                error_message=str(exc),
            )
