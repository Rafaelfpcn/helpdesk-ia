import re
import unicodedata

from app.enums import Category, Priority, Urgency
from app.services.ai.base import AIAnalysis, AIProvider

# Ordem importa: em caso de empate, a primeira categoria vence.
# "seguranca" vem primeiro para ser tratada com mais cuidado.
CATEGORY_KEYWORDS: dict[Category, list[str]] = {
    Category.seguranca: ["virus", "malware", "phishing", "ransomware", "invadido", "suspeito", "vazamento", "golpe"],
    Category.acesso_senha: ["senha", "login", "acesso", "bloqueado", "conta", "redefinir", "autenticacao"],
    Category.email: ["e-mail", "email", "outlook", "caixa de entrada", "spam", "anexo"],
    Category.impressora: ["impressora", "imprimir", "impressao", "toner", "scanner"],
    Category.rede: ["wifi", "wi-fi", "internet", "rede", "vpn", "lenta", "sem conexao", "roteador", "dns"],
    Category.hardware: ["computador", "notebook", "monitor", "teclado", "mouse", "nao liga", "tela azul", "ssd", "bateria"],
    Category.software: ["programa", "aplicativo", "instalar", "instalacao", "erro", "travando", "atualizacao", "licenca", "excel"],
}

PRIORITY_CRITICAL = [
    "fora do ar",
    "ninguem consegue",
    "todos os usuarios",
    "ransomware",
    "invadido",
    "vazamento",
    "parou de funcionar",
]
PRIORITY_HIGH = ["urgente", "nao consigo trabalhar", "impossivel trabalhar", "bloqueado", "travou", "prazo"]
PRIORITY_LOW = ["duvida", "sugestao", "quando puder", "sem pressa", "melhoria"]

PRIORITY_TO_URGENCY = {
    Priority.critica: Urgency.imediata,
    Priority.alta: Urgency.alta,
    Priority.media: Urgency.moderada,
    Priority.baixa: Urgency.baixa,
}

INITIAL_ACTIONS = {
    Category.rede: "Verificar se o problema afeta só este usuário ou outros; testar cabo/Wi-Fi e reiniciar o equipamento de rede local.",
    Category.hardware: "Checar alimentação e conexões do equipamento; se persistir, encaminhar para bancada de manutenção.",
    Category.software: "Reproduzir o erro, anotar a mensagem exibida e verificar versão e licença do programa.",
    Category.acesso_senha: "Confirmar a identidade do solicitante por canal oficial antes de redefinir qualquer credencial.",
    Category.email: "Verificar se o acesso ao webmail funciona e se a caixa está cheia ou bloqueada.",
    Category.impressora: "Conferir papel, toner e fila de impressão; reiniciar o spooler se necessário.",
    Category.seguranca: "Isolar o equipamento da rede, não apagar evidências e acionar o responsável de segurança.",
    Category.outros: "Pedir mais detalhes ao solicitante para classificar corretamente o chamado.",
}


def _normalize(text: str) -> str:
    """Minúsculas e sem acentos, para 'Impressão' e 'impressao' serem iguais."""
    text = unicodedata.normalize("NFD", text.lower())
    return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")


def _count_hits(text: str, keywords: list[str]) -> int:
    # \b = limite de palavra: evita que "rede" case dentro de "arredondado".
    return sum(1 for kw in keywords if re.search(rf"\b{re.escape(kw)}\b", text))


def _summarize(title: str, description: str, max_len: int = 200) -> str:
    first_sentence = re.split(r"(?<=[.!?])\s+", description.strip())[0]
    summary = f"{title.strip()} — {first_sentence}"
    return summary if len(summary) <= max_len else summary[: max_len - 1] + "…"


class MockAIProvider(AIProvider):
    """IA simulada baseada em palavras-chave. Determinística: mesma entrada, mesma saída.

    Limitações conhecidas (vão para docs/ai-responsible.md):
    - Não entende contexto nem negação: "não é urgente" ainda contém "urgente".
    - Só reconhece as palavras da lista; descrições incomuns viram "outros".
    - A confiança é uma estimativa simples (nº de palavras encontradas), não uma probabilidade real.
    """

    name = "mock"

    def analyze(self, title: str, description: str) -> AIAnalysis:
        # Ignora marcadores do sanitizer ([CPF], [EMAIL]...) para não distorcer a classificação.
        cleaned = re.sub(r"\[[A-Z_]+\]", " ", f"{title} {description}")
        text = _normalize(cleaned)
        category, hits = self._classify(text)
        priority = self._prioritize(text, category)
        confidence = 0.3 if hits == 0 else min(0.5 + 0.1 * hits, 0.9)

        return AIAnalysis(
            category=category,
            priority=priority,
            urgency=PRIORITY_TO_URGENCY[priority],
            summary=_summarize(title, description),
            initial_action=INITIAL_ACTIONS[category],
            confidence=round(confidence, 2),
        )

    @staticmethod
    def _classify(text: str) -> tuple[Category, int]:
        scores = {cat: _count_hits(text, kws) for cat, kws in CATEGORY_KEYWORDS.items()}
        best = max(scores, key=scores.get)
        if scores[best] == 0:
            return Category.outros, 0
        return best, scores[best]

    @staticmethod
    def _prioritize(text: str, category: Category) -> Priority:
        if _count_hits(text, PRIORITY_CRITICAL):
            priority = Priority.critica
        elif _count_hits(text, PRIORITY_HIGH):
            priority = Priority.alta
        elif _count_hits(text, PRIORITY_LOW):
            priority = Priority.baixa
        else:
            priority = Priority.media

        # Regra de negócio: segurança nunca fica abaixo de "alta".
        if category == Category.seguranca and priority in (Priority.baixa, Priority.media):
            priority = Priority.alta

        return priority
