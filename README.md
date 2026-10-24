# HelpDesk IA

![tests](https://github.com/SEU_USUARIO/helpdesk-ia/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-009688)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)
![License](https://img.shields.io/badge/license-MIT-green)

Sistema de **abertura e triagem de chamados de TI com apoio de Inteligência Artificial e supervisão humana obrigatória (*Human-in-the-Loop*)**.

A IA analisa relatos em linguagem natural, sanitiza dados sensíveis e sugere categoria, prioridade, resumo e ação inicial de suporte — **o atendente técnico humano sempre revisa, confirma ou corrige a decisão**.

> ⚠️ **Projeto de Portfólio Acadêmico e Técnico:** Todos os dados utilizados são 100% sintéticos e fictícios (nomes "…Teste", e-mails `@exemplo.com`). Não utilize dados reais. A IA padrão incluída opera via motor determinístico simulado (mock heurístico), demonstrando arquitetura desacoplada pronta para integração com LLMs reais (OpenAI, Gemini ou Ollama).

---

## 📌 Problema que Resolve

Em centros de serviços e equipes de suporte de TI, os chamados chegam em texto livre e frequentemente com dados sensíveis (senhas, CPFs, e-mails). A triagem manual consome tempo excessivo da equipe, a priorização varia conforme o humor ou experiência de cada atendente e a governança é difícil de auditar.

Por outro lado, adotar IA autônoma sem controle introduz sérios riscos:
- Vazamento de dados confidenciais (LGPD) para APIs de terceiros;
- Decisões automáticas incorretas que fecham ou despriorizam incidentes graves (alucinações);
- Perda de rastreabilidade para auditorias corporativas.

O **HelpDesk IA** implementa um fluxo equilibrado: **agilizar a triagem preliminar com IA, garantir anonimização de dados pré-processamento, manter o ser humano no comando e auditar continuamente a acurácia do modelo**.

---

## ✨ Funcionalidades Principais

- **Abertura de Chamados com Validação:** Formulário web e endpoint REST com validações rigorosas (Pydantic v2).
- **Sanitização Automática de Dados Sensíveis:** Mascaramento pré-IA de CPFs, CNPJs, cartões de crédito, e-mails, telefones e senhas.
- **Triagem Assistida por IA:** Inferência de categoria recomendada, urgência, prioridade, resumo executivo e sugestão de ação de suporte.
- **Supervisão Humana Obrigatória (*Human-in-the-Loop*):** Rotas e telas dedicadas para confirmar a sugestão ou aplicar correção manual.
- **Auditoria Imutável:** Rastreamento ponta a ponta (`audit_logs`) com registro de ator (`system`, `ai`, `atendente`), data/hora e metadados.
- **Máquina de Estados de Chamados:** Ciclo de vida controlado (`aberto` → `em_atendimento` → `resolvido` → `fechado`).
- **Dashboard Operacional e de Governança:** Painel com indicadores em tempo real, acurácia da IA, matriz de confusões semânticas e estimativa de impacto financeiro/operacional.
- **Documentação e API Interativa:** Documentação OpenAPI/Swagger nativa em `/docs`.

---

## 📸 Telas do Sistema (Prints)

> *Para capturar e salvar seus prints, execute o seed localmente e armazene as imagens em `docs/images/`.*

| Abertura de Chamado | Central de Chamados & Filtros |
|:---:|:---:|
| ![Abrir chamado](docs/images/01-abrir-chamado.png) | ![Lista de chamados](docs/images/02-lista.png) |
| **Triagem & Revisão Humana de IA** | **Dashboard de Métricas & Impacto** |
| ![Detalhe e Revisão](docs/images/03-detalhe-revisao-ia.png) | ![Dashboard de Métricas](docs/images/04-dashboard.png) |

---

## 🏛️ Arquitetura do Sistema

O projeto adota uma arquitetura em camadas orientada a serviços com baixo acoplamento:

```
Navegador (Jinja2 + JS) ──> Routers (/api/* e páginas) ──> Services (Regras de Negócio) ──> SQLite (SQLAlchemy)
                                                               │
                                                               └──> Sanitizer ──> AIProvider (Mock | LLM)
```

- **Inversão de Controle & Interface de IA:** O sistema depende apenas do contrato abstrato `AIProvider`. A substituição do mock por um modelo real é feita apenas alterando a variável `AI_PROVIDER` no `.env`.
- **Persistência Atômica:** Chamado, parecer da IA e registros de log são commitados na mesma transação atômica.
- **Isolamento de Decisão:** Colunas `suggested_*` e `final_*` são mantidas separadamente na tabela `ai_suggestions`, viabilizando o cálculo de métricas de acerto e calibração de confiança.

Detalhes completos e diagramas de sequência: [docs/architecture.md](docs/architecture.md) • Contratos da API: [docs/api.md](docs/api.md).

---

## 🛠️ Stack Tecnológica

- **Backend:** Python 3.11+, FastAPI, Pydantic v2, Pydantic-Settings
- **Banco de Dados & ORM:** SQLite 3, SQLAlchemy 2.0
- **Frontend:** Jinja2 Templates, HTML5 Semântico, CSS3 Moderno (sem frameworks externos pesados), JavaScript Vanilla
- **Testes & Cobertura:** Pytest, HTTPX, Pytest-Cov
- **Containerização:** Docker, Docker Compose
- **CI/CD:** GitHub Actions (Ubuntu, Python 3.11 & 3.12)

---

## 🚀 Como Rodar o Projeto Localmente

### Pré-requisitos:
- Python 3.11 ou superior instalado.

### 1. Clonar o repositório e preparar o ambiente virtual:
```bash
git clone https://github.com/SEU_USUARIO/helpdesk-ia.git
cd helpdesk-ia

# Criar e ativar ambiente virtual
python -m venv .venv

# No Windows (PowerShell):
.venv\Scripts\activate
# No Linux / macOS:
# source .venv/bin/activate

# Instalar dependências completas (com ferramentas de desenvolvimento e testes)
pip install -r requirements-dev.txt
```

### 2. Configurar variáveis de ambiente:
```bash
# Windows:
copy .env.example .env
# Linux / macOS:
# cp .env.example .env
```

### 3. Popular o banco com dados sintéticos de demonstração:
```bash
python -m scripts.seed --reset
```
*Gera 30 chamados fictícios com histórico retroativo realista para preencher o dashboard e os gráficos.*

### 4. Executar o servidor de desenvolvimento:
```bash
uvicorn app.main:app --reload
```

Acesse no navegador:
- **Aplicação Web:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Central de Chamados:** [http://127.0.0.1:8000/tickets](http://127.0.0.1:8000/tickets)
- **Dashboard de Métricas:** [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard)
- **Documentação Swagger (API):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🐳 Como Rodar com Docker

```bash
# Construir e iniciar os containers com volume persistente
docker compose up --build -d

# Popular com dados de demonstração dentro do container
docker compose exec web python -m scripts.seed --reset
```
Acesse a aplicação em `http://localhost:8000`.

---

## 🧪 Execução de Testes Automatizados

A suíte de testes do projeto executa contra um banco SQLite em memória isolado (`poolclass=StaticPool`), garantindo testes determinísticos e rápidos sem poluir o banco local:

```bash
# Rodar todos os testes com relatório detalhado
pytest -v

# Rodar com análise de cobertura de código
pytest -v --cov=app --cov-report=term-missing
```

### O que os testes cobrem:
- Criação e validação estrita de chamados (código 201 e 422).
- Comportamento de falha segura quando o serviço de IA falha inesperadamente.
- Classificação heurística do motor de IA mock e insensibilidade a acentos/caixa.
- Sanitização ponta a ponta e mascaramento estrito de dados sensíveis.
- Revisão humana: confirmação, alteração e rejeição de estados inválidos (código 409 e 422).
- Consolidação de métricas, backlog, acurácia e estimativa de impacto.
- Script de seed e geração de histórico.

---

## 📊 Métricas e Impacto Medido

O HelpDesk IA rejeita estimativas vazias e adota um protocolo formal de medição documentado em [docs/metrics.md](docs/metrics.md).

### Resultados Obtidos na Demonstração Controlada (`seed` reprodutivo):

| Indicador | Valor Demonstrado | Descrição |
|---|:---:|---|
| **Chamados no Sistema** | `30` | Volume total de chamados gerados sinteticamente |
| **Cobertura de Triagem IA** | `100%` (30/30) | Percentual de chamados atendidos pelo motor de IA |
| **Taxa de Confirmação Humana** | `58,3%` (14/24) | Percentual de análises em que o humano manteve a sugestão |
| **Acurácia em Categoria** | `58,3%` (14/24) | Direcionamento preciso para a fila técnica correspondente |
| **Acurácia em Prioridade** | `83,3%` (20/24) | Avaliação correta de criticidade e urgência |
| **Tempo Médio de Resolução (MTTR)** | `52,6 h` | Tempo médio decorrido nos chamados resolvidos |
| **Tempo Estimado Economizado** | `56,0 min (~0,9 h)` | Economia conservadora computada sobre chamados confirmados |

> **Premissas da Estimativa de Tempo:** 5,0 minutos para triagem manual sem IA e 1,0 minuto para revisão assistida (medianas obtidas em amostragem cronometrada), computadas **apenas para chamados com sugestão confirmada**.

### Indicadores Técnicos de Confiabilidade:

| Indicador | Valor Medido | Observações |
|---|:---:|---|
| **Testes Automatizados** | `41 aprovados` | Suíte com Pytest cobrindo unitários, integração e E2E |
| **Cobertura de Código** | `98%` | Medido via `pytest-cov` sobre todo o pacote `app/` |
| **Latência `POST /api/tickets`** | `p50: 24,8 ms / p95: 28,0 ms` | Inclui validação Pydantic, sanitização regex e mock de IA |
| **Latência `GET /api/metrics`** | `p50: 19,5 ms / p95: 23,0 ms` | Agregações SQL e processamento estatístico em tempo real |

---

## 🛡️ Diretrizes de IA Responsável

O projeto foi concebido sob princípios de computação ética e conformidade com a LGPD:
1. **Transparência e Explicabilidade:** O solicitante e o atendente são informados de que o parecer é gerado por IA com limites operacionais explícitos.
2. **Minimização de Dados:** Remoção proativa de dados identificáveis antes de alimentar o motor cognitivo.
3. **Imutabilidade de Auditoria:** O registro histórico não permite apagar falhas de modelo nem decisões humanas tomadas.
4. **Prevenção de Viés:** Monitoramento explícito de confusões frequentes de categoria para evitar que determinados chamados fiquem negligenciados.

Leia a política completa em: [docs/ai-responsible.md](docs/ai-responsible.md).

---

## 🗺️ Roadmap de Evoluções Futuras

- [ ] Autenticação baseada em JWT e controle de papéis (usuário vs. atendente).
- [ ] Integração com LLMs reais (OpenAI GPT-4o-mini / Google Gemini Flash / Ollama local).
- [ ] Paginação e busca textual avançada na listagem de chamados.
- [ ] Migração orientada para PostgreSQL com versionamento de schema via Alembic.
- [ ] Gestão de SLA por criticidade com alertas visuais de prazo expirando.
- [ ] Pipeline CI/CD completo com deploy automático em ambiente de nuvem (ex.: Render ou Railway).

---

## 📄 Licença

Distribuído sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
