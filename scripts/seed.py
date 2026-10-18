"""
Seed de dados fictícios para demonstração do HelpDesk IA.
Usa exclusivamente dados inventados. Não há dados reais de pessoas ou empresas.

Uso:
    python scripts/seed.py [--reset]
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from app import models  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.db.base import Base, SessionLocal, engine  # noqa: E402
from app.schemas import AiReviewCreate, TicketCreate, TicketUpdate  # noqa: E402
from app.services.ai import AiService, MockAiProvider  # noqa: E402
from app.services.metrics_service import get_metrics  # noqa: E402
from app.services.security import hash_password  # noqa: E402
from app.services.ticket_service import ReviewService, TicketService  # noqa: E402

FAKE_TICKETS = [
    {
        "requester_name": "Maria Alves",
        "requester_email": "maria.alves@example.com",
        "title": "Servidor principal fora do ar",
        "description": (
            "O servidor principal está fora do ar e todos os usuários do financeiro "
            "estão sem acesso ao sistema. Não conseguimos emitir notas."
        ),
        "source": "portal",
        "review": {"accepted": True, "notes": "Classificação correta."},
        "status": "em_analise",
    },
    {
        "requester_name": "João Pereira",
        "requester_email": "joao.pereira@example.com",
        "title": "Senha bloqueada no portal",
        "description": "Não consigo fazer login no portal corporativo. Minha senha foi bloqueada.",
        "source": "telefone",
        "review": {"accepted": True},
        "status": "resolvido",
    },
    {
        "requester_name": "Ana Costa",
        "requester_email": "ana.costa@example.com",
        "title": "Impressora do administrativo não imprime",
        "description": "A impressora do setor administrativo não imprime documentos desde a manhã.",
        "source": "portal",
        "review": {"accepted": True},
        "status": "resolvido",
    },
    {
        "requester_name": "Carlos Lima",
        "requester_email": "carlos.lima@example.com",
        "title": "Erro ao salvar pedido no ERP",
        "description": "O ERP apresenta erro ao salvar pedidos no módulo comercial. Bug recorrente.",
        "source": "email",
        "review": {
            "accepted": False,
            "corrected_priority": "critica",
            "notes": "Impacta faturamento, subir para crítica.",
        },
        "status": "em_analise",
    },
    {
        "requester_name": "Fernanda Souza",
        "requester_email": "fernanda.souza@example.com",
        "title": "Dúvida sobre instalação da VPN",
        "description": "Como fazer para instalar a VPN no notebook corporativo?",
        "source": "chat",
        "review": {"accepted": True},
    },
    {
        "requester_name": "Ricardo Nunes",
        "requester_email": "ricardo.nunes@example.com",
        "title": "Preciso de ajuda",
        "description": "Preciso de ajuda com uma coisa aqui no setor, mas não sei descrever direito o que houve.",
        "source": "portal",
        "review": {
            "accepted": False,
            "corrected_category": "Solicitação",
            "corrected_priority": "baixa",
            "notes": "Descrição insuficiente, IA não conseguiu classificar.",
        },
    },
    {
        "requester_name": "Beatriz Ramos",
        "requester_email": "beatriz.ramos@example.com",
        "title": "Internet lenta no setor de compras",
        "description": "A internet está lenta no setor de compras, a rede está instável desde ontem.",
        "source": "portal",
        "review": {"accepted": True},
        "status": "aguardando",
    },
    {
        "requester_name": "Diego Martins",
        "requester_email": "diego.martins@example.com",
        "title": "Mouse com defeito",
        "description": "O mouse do meu notebook está com defeito e não responde corretamente.",
        "source": "telefone",
        "review": {"accepted": True},
        "status": "fechado",
    },
    {
        "requester_name": "Patrícia Gomes",
        "requester_email": "patricia.gomes@example.com",
        "title": "Acesso bloqueado para todos os usuários",
        "description": "Todos os usuários estão sem acesso ao portal corporativo. Urgente, equipe paralisada.",
        "source": "portal",
        "review": {"accepted": True, "notes": "Confirmado como incidente geral."},
        "status": "em_analise",
    },
    {
        "requester_name": "Lucas Ferreira",
        "requester_email": "lucas.ferreira@example.com",
        "title": "Monitor sem sinal",
        "description": "O monitor do meu posto de trabalho está sem sinal e o teclado também não funciona.",
        "source": "chat",
        "review": {"accepted": True},
        "status": "aberto",
    },
    {
        "requester_name": "Sandra Melo",
        "requester_email": "sandra.melo@example.com",
        "title": "Solicitação de novo acesso ao sistema financeiro",
        "description": "Solicito acesso para a nova colaboradora do financeiro ao sistema de contas a pagar.",
        "source": "email",
        "review": {"accepted": True},
    },
    {
        "requester_name": "Otávio Ribeiro",
        "requester_email": "otavio.ribeiro@example.com",
        "title": "Barulho estranho na copa",
        "description": "Tem um barulho estranho na copa perto da geladeira, não parece ser de TI.",
        "source": "portal",
        "review": {
            "accepted": False,
            "corrected_category": "Infraestrutura",
            "corrected_priority": "baixa",
            "notes": "Redirecionado para facilities, registrado como Outros.",
        },
    },
]


def run(reset: bool = False) -> None:
    if reset:
        Base.metadata.drop_all(bind=engine)
        print("Banco de dados resetado com sucesso.")

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Criação do usuário demo
    demo_user = (
        db.query(models.User)
        .filter(models.User.email == "demo@example.com")
        .first()
    )

    if not demo_user:
        demo_user = models.User(
            name="Demo User",
            email="demo@example.com",
            hashed_password=hash_password("demo123"),
            role="admin",
            is_active=True,
        )
        db.add(demo_user)
        db.commit()
        print("Usuário demo criado: demo@example.com / demo123")

    ai_service = AiService(
        provider=MockAiProvider(),
        provider_name=settings.ai_provider,
        prompt_version="v1.0-mock",
        confidence_threshold=settings.ai_confidence_threshold,
        fallback_category=settings.ai_fallback_category,
        fallback_priority=settings.ai_fallback_priority,
    )

    ticket_service = TicketService(db=db, ai_service=ai_service)
    review_service = ReviewService(db=db)

    created = 0

    for item in FAKE_TICKETS:
        payload = TicketCreate(
            requester_name=item["requester_name"],
            requester_email=item["requester_email"],
            title=item["title"],
            description=item["description"],
            category=item.get("category"),
            priority=item.get("priority"),
            source=item.get("source", "portal"),
        )

        ticket, suggestion = ticket_service.create_ticket(payload)

        review = item.get("review")
        if review:
            review_service.review_suggestion(
                suggestion.id,
                AiReviewCreate(
                    reviewer_name=review.get("reviewer_name", "Atendente N1"),
                    accepted=review.get("accepted", True),
                    corrected_category=review.get("corrected_category"),
                    corrected_priority=review.get("corrected_priority"),
                    notes=review.get("notes"),
                ),
            )

        status = item.get("status")
        if status:
            ticket_service.update_ticket(ticket.id, TicketUpdate(status=status))

        created += 1

    metrics = get_metrics(db)
    db.close()

    print(f"Seed concluído: {created} chamados criados com sugestões de IA.")
    print()
    print("Métricas resultantes:")
    print(f"  Total de chamados ............ {metrics['tickets_total']}")
    print(f"  Sugestões de IA .............. {metrics['ai_suggestions_total']}")
    print(f"  Revisões humanas ............. {metrics['ai_reviews_total']}")
    print(f"  Sugestões aceitas ............ {metrics['ai_accepted_total']}")
    print(f"  Sugestões corrigidas ......... {metrics['ai_corrected_total']}")
    print(f"  Confiança média da IA ........ {metrics['ai_avg_confidence']}")
    print(f"  Latência média da IA (ms) .... {metrics['ai_avg_latency_ms']}")
    print(f"  Decisões por tipo ............ {metrics['ai_by_decision']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Popular banco com dados fictícios.")
    parser.add_argument("--reset", action="store_true", help="Recria as tabelas do zero.")
    args = parser.parse_args()

    run(reset=args.reset)
