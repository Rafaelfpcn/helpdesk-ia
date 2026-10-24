import re
from dataclasses import dataclass, field
from typing import Callable, Union


@dataclass(frozen=True)
class SanitizeResult:
    text: str
    redactions: dict[str, int] = field(default_factory=dict)  # ex.: {"cpf": 1}. Só o TIPO e a quantidade, nunca o valor.


Replacement = Union[str, Callable[[re.Match], str]]

# A ORDEM IMPORTA: regras mais específicas primeiro.
# Depois que "123.456.789-09" vira "[CPF]", as regras seguintes não o veem mais.
RULES: list[tuple[str, re.Pattern, Replacement]] = [
    # "senha: abc123", "senha é abc123", "token = xyz". Exige separador para não apagar "senha do email".
    (
        "senha",
        re.compile(r"(?i)\b(senha|password|pwd|token)\s*(?::|=|\bé\b|\beh\b|\bis\b)\s*\S+"),
        lambda m: f"{m.group(1)}: [SENHA]",
    ),
    ("email", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"), "[EMAIL]"),
    ("cnpj", re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b"), "[CNPJ]"),
    ("cpf", re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"), "[CPF]"),
    ("cartao", re.compile(r"\b\d(?:[ -]?\d){12,15}\b"), "[CARTAO]"),
    ("telefone", re.compile(r"(?<!\d)(?:\+?55[\s-]?)?(?:\(?\d{2}\)?[\s-]?)?9?\d{4}[\s-]?\d{4}(?!\d)"), "[TELEFONE]"),
]


def sanitize(text: str) -> SanitizeResult:
    """Mascara dados sensíveis. Prefere errar para o lado de mascarar demais (privacidade primeiro)."""
    redactions: dict[str, int] = {}
    for name, pattern, replacement in RULES:
        text, count = pattern.subn(replacement, text)
        if count:
            redactions[name] = count
    return SanitizeResult(text=text, redactions=redactions)
