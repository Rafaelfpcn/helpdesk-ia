from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.enums import Category, Priority, Status
from app.services import metrics_service, ticket_service

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Dicionário de tradução de labels de enums para exibição amigável
LABELS: dict[str, str] = {
    # Categorias
    "rede": "Rede / Conectividade",
    "hardware": "Hardware / Equipamento",
    "software": "Software / Sistema",
    "acesso_senha": "Acesso e Senha",
    "email": "E-mail / Comunicação",
    "impressora": "Impressora / Periférico",
    "seguranca": "Segurança da Informação",
    "outros": "Outros Assuntos",
    # Prioridades
    "baixa": "Baixa",
    "media": "Média",
    "alta": "Alta",
    "critica": "Crítica",
    # Status
    "aberto": "Aberto",
    "em_atendimento": "Em Atendimento",
    "resolvido": "Resolvido",
    "fechado": "Fechado",
    # Urgência
    "moderada": "Moderada",
    "imediata": "Imediata",
    # Revisão
    "pendente": "Pendente",
    "confirmada": "Confirmada",
    "alterada": "Alterada",
    # Eventos de auditoria
    "ticket_created": "Chamado Aberto",
    "suggestion_generated": "Sugestão da IA Gerada",
    "suggestion_failed": "Falha na IA (Falha Segura)",
    "suggestion_confirmed": "Sugestão Confirmada pelo Atendente",
    "suggestion_changed": "Sugestão Corrigida pelo Atendente",
    "status_changed": "Status do Chamado Alterado",
}


def label_filter(value: Optional[str]) -> str:
    if not value:
        return "—"
    return LABELS.get(str(value), str(value).replace("_", " ").title())


def pct_filter(value: Optional[float]) -> str:
    if value is None:
        return "—"
    return f"{round(value * 100, 1)}%".replace(".", ",")


def hours_filter(value: Optional[float]) -> str:
    if value is None:
        return "—"
    return f"{round(value, 1)} h".replace(".", ",")


def datetime_filter(value: Optional[datetime]) -> str:
    if not value:
        return "—"
    return value.strftime("%d/%m/%Y às %H:%M")


templates.env.filters["label"] = label_filter
templates.env.filters["pct"] = pct_filter
templates.env.filters["hours"] = hours_filter
templates.env.filters["datetime"] = datetime_filter

router = APIRouter(include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
def page_new_ticket(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="new_ticket.html",
        context={
            "categories": list(Category),
            "page_title": "Abrir Chamado de TI",
        },
    )


@router.get("/tickets", response_class=HTMLResponse)
def page_list_tickets(
    request: Request,
    status: Optional[Status] = None,
    category: Optional[Category] = None,
    priority: Optional[Priority] = None,
    db: Session = Depends(get_db),
):
    tickets = ticket_service.list_tickets(db, status, category, priority)
    return templates.TemplateResponse(
        request=request,
        name="tickets.html",
        context={
            "tickets": tickets,
            "statuses": list(Status),
            "categories": list(Category),
            "priorities": list(Priority),
            "selected_status": status.value if status else "",
            "selected_category": category.value if category else "",
            "selected_priority": priority.value if priority else "",
            "page_title": "Lista de Chamados",
        },
    )


@router.get("/tickets/{ticket_id}", response_class=HTMLResponse)
def page_ticket_detail(
    request: Request,
    ticket_id: int,
    db: Session = Depends(get_db),
):
    ticket = ticket_service.get_ticket(db, ticket_id)
    return templates.TemplateResponse(
        request=request,
        name="review.html",
        context={
            "ticket": ticket,
            "categories": list(Category),
            "priorities": list(Priority),
            "page_title": f"Chamado #{ticket.id} - {ticket.title}",
        },
    )


@router.get("/dashboard", response_class=HTMLResponse)
def page_dashboard(
    request: Request,
    db: Session = Depends(get_db),
):
    metrics = metrics_service.get_metrics(db)
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "metrics": metrics,
            "page_title": "Dashboard de Métricas & Impacto",
        },
    )
