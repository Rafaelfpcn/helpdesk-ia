# Arquitetura do HelpDesk IA

## Visão Geral

O projeto segue uma arquitetura em camadas simples e modular, adequada para sistemas internos de suporte técnico e portfólio profissional.

```text
Frontend estático (HTML/CSS/JS puro)
        |
        | HTTP / REST (JSON)
        v
    FastAPI (rotas + dependências)
        |
        v
   Services (regras de negócio)
        |
   +----+--------------------+
   |                         |
Repository / DB           AiService
(SQLAlchemy)              (provider plugável + fallback)
   |                         |
   v                         v
 SQLite               Mock / LLM real
```

## Camadas

### 1. API (`app/api/`)
Recebe requisições HTTP, valida dados de entrada e saída com schemas Pydantic e delega execução para os serviços.
- `routes.py`: rotas de chamados (`/tickets`), métricas (`/metrics`), saúde (`/health`) e revisões de IA.
- `auth.py`: rotas de registro (`/auth/register`), autenticação JWT (`/auth/token`) e perfil (`/auth/me`).

### 2. Services (`app/services/`)
Concentra toda a lógica de negócio do sistema:
- `TicketService`: criação e atualização de chamados, integração automática com a IA e auditoria de eventos.
- `ReviewService`: processamento da revisão humana de sugestões geradas pela IA.
- `MetricsService`: cálculo em tempo real de KPIs de atendimento e de qualidade das predições.
- `AiService`: camada isolada de inteligência artificial com sanitização de texto, medição de latência, tolerância a falhas e decisão por threshold.
- `security.py`: hashing seguro de senhas com PBKDF2-HMAC-SHA256 e emissão/validação de tokens JWT.

### 3. Modelos e Banco (`app/models.py`, `app/db/`)
Entidades relacionais mapeadas com SQLAlchemy ORM:
- `Ticket`: dados do chamado (título, descrição, categoria, prioridade, status, flags de revisão).
- `AiSuggestion`: predições geradas pela IA (categoria, prioridade, resumo, ação sugerida, confiança, latência, decisão).
- `AiReview`: auditoria das revisões humanas (aceite, correções de categoria/prioridade, anotações).
- `AuditLog`: rastreabilidade completa de eventos no sistema.
- `User`: usuários do sistema para autenticação JWT e controle de permissões.

## Decisões Técnicas

| Decisão | Motivo |
|---|---|
| FastAPI | Alta performance assíncrona, documentação Swagger/OpenAPI interativa e tipagem estrita com Pydantic |
| SQLite | Zero configuração de infraestrutura para executar localmente; facilmente migrante para PostgreSQL |
| Provedor de IA Plugável | Permite testes 100% offline sem custo e sem chaves de API, podendo ser substituído por OpenAI, Gemini ou Ollama |
| IA Responsável | Princípio fundamental: a IA sugere com confiança declarada, mas a decisão final é humana |
| Sanitização de Dados | Redução proativa da exposição de dados sensíveis (CPF, e-mails, telefones) antes do envio à IA |
| Autenticação Híbrida | JWT opcional configurável via `AUTH_REQUIRED` para facilitar testes de recrutadores |
| Frontend Estático | Sem dependências de build complexas (React/Vue/Webpack), focado em simplicidade e consumo de APIs |

## Limitações Conhecidas & Dívida Técnica

- Sem migrações automáticas (Alembic planejado para o roadmap).
- Métricas calculadas dinamicamente via consultas agregadas no banco SQLite.
- Sanitização regex básica voltada a ambiente demonstrativo.
