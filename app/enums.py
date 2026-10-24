from enum import Enum


class Category(str, Enum):
    rede = "rede"
    hardware = "hardware"
    software = "software"
    acesso_senha = "acesso_senha"
    email = "email"
    impressora = "impressora"
    seguranca = "seguranca"
    outros = "outros"


class Priority(str, Enum):
    baixa = "baixa"
    media = "media"
    alta = "alta"
    critica = "critica"


class Status(str, Enum):
    aberto = "aberto"
    em_atendimento = "em_atendimento"
    resolvido = "resolvido"
    fechado = "fechado"


class Urgency(str, Enum):
    baixa = "baixa"
    moderada = "moderada"
    alta = "alta"
    imediata = "imediata"


class Source(str, Enum):
    web = "web"
    email = "email"
    telefone = "telefone"
    seed = "seed"


class ReviewStatus(str, Enum):
    pendente = "pendente"
    confirmada = "confirmada"
    alterada = "alterada"


class EventType(str, Enum):
    ticket_created = "ticket_created"
    suggestion_generated = "suggestion_generated"
    suggestion_failed = "suggestion_failed"
    suggestion_confirmed = "suggestion_confirmed"
    suggestion_changed = "suggestion_changed"
    status_changed = "status_changed"
