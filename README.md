# HelpDesk IA 🎫🤖

> Sistema profissional de abertura, triagem e análise de chamados de TI com apoio de Inteligência Artificial responsável.

![CI](https://github.com/Rafaelfpcn/helpdesk-ia/actions/workflows/ci.yml/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 🎯 Proposta de Valor & Problema Real de TI

Em centrais de serviços de TI (Service Desk / Help Desk), a triagem inicial de chamados costuma ser um gargalo operacional:
- Chamados são abertos com descrições vagas ou categorias incorretas.
- Incidentes de alta prioridade ficam parados na mesma fila que solicitações rotineiras.
- Atendentes perdem tempo classificando chamados manualmente em vez de resolver incidentes.

O **HelpDesk IA** automatiza a triagem inicial analisando o texto do chamado em tempo real para inferir categoria, prioridade, resumo estruturado e ação recomendada, operando com **auditoria e supervisão humana obrigatória**.

---

## ✨ Destaques de Engenharia e IA Responsável

- **Human-in-the-Loop:** A IA não fecha nem resolve chamados sozinha. Toda sugestão pode ser aceita ou corrigida por um atendente.
- **Decisão baseada em confiança (Threshold):** Se a confiança for alta ($\ge 0.70$), o chamado é auto-preenchido. Se a confiança for baixa, aplica fallback seguro e requer revisão manual.
- **Tolerância a falhas:** Caso o serviço de IA falhe, o sistema não quebra: aplica fallback gracioso e registra a ocorrência.
- **Privacidade & Sanitização (LGPD):** Regex sanitiza CPFs, telefones e e-mails antes de enviar à camada de inteligência.
- **Auditoria completa:** Trilha de auditoria persistente de cada predição, tempo de resposta (latência) e correções humanas.
- **Avaliação com Dataset Sintético:** Script automatizado (`scripts/evaluate_ai.py`) para medir acurácia de classificação.
- **Autenticação JWT Opcional:** Suporte a login e proteção de rotas, configurável via flag `AUTH_REQUIRED=false` (ideal para recrutadores testarem instantaneamente).

---

## 🛠️ Tecnologias Utilizadas

| Componente | Tecnologia | Finalidade |
|---|---|---|
| **Backend** | Python 3.11+, FastAPI | API REST moderna de alta performance com OpenAPI/Swagger |
| **Validação** | Pydantic v2 | Modelagem e validação estrita de tipos |
| **Persistência** | SQLAlchemy ORM, SQLite | Camada de abstração de dados relacional |
| **Segurança** | PyJWT, PBKDF2-HMAC-SHA256 | Autenticação segura por token JWT e hashing com salt |
| **Frontend** | HTML5, CSS3, JavaScript Puro | Painel responsivo sem complexidade de bundles |
| **Qualidade & Testes** | Pytest, HTTPX, Ruff | Testes automatizados e linter de código moderno |
| **DevOps** | Docker, Docker Compose, GitHub Actions | Conteinerização completa e CI/CD automatizado |

---

## 🚀 Como Executar Localmente

### Pré-requisitos
- Python 3.11+ instalado
- Git

### 1. Clonar o repositório
```bash
git clone https://github.com/Rafaelfpcn/helpdesk-ia.git
cd helpdesk-ia
```

### 2. Criar e ativar o ambiente virtual
```bash
# Linux/macOS
python -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente
```bash
# Linux/macOS
cp .env.example .env

# Windows
copy .env.example .env
```

### 5. Popular o banco com dados de demonstração
```bash
python scripts/seed.py --reset
```
*Gera 12 chamados realistas com predições de IA, revisões simuladas e cria o usuário demo (`demo@example.com` / `demo123`).*

### 6. Iniciar a aplicação
```bash
uvicorn app.main:app --reload
```

Acesse no navegador:
- **Interface Web:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Swagger / OpenAPI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Métricas:** [http://127.0.0.1:8000/metrics](http://127.0.0.1:8000/metrics)

---

## 🐳 Executando com Docker

```bash
docker compose up --build
```
Para popular os dados dentro do container:
```bash
docker compose exec api python scripts/seed.py
```

---

## 🧪 Testes e Avaliação da IA

```bash
# Executar todos os testes automatizados
pytest -v

# Executar avaliação do modelo no dataset sintético
python scripts/evaluate_ai.py

# Verificar formatação e boas práticas
ruff check .
```

---

## 🔐 Autenticação

O sistema possui autenticação JWT opcional:
- Por padrão, `AUTH_REQUIRED=false` no `.env`, permitindo uso direto da interface sem login obrigatório.
- Para ativar proteção estrita em produção, altere no `.env`:
  ```env
  AUTH_REQUIRED=true
  ```
- **Credenciais demo:** `demo@example.com` | `demo123`

---

## 📂 Estrutura do Projeto

```text
helpdesk-ia/
├── app/
│   ├── api/             # Rotas REST e autenticação
│   ├── core/            # Configurações Pydantic e Logging
│   ├── db/              # Conexão e Sessão SQLAlchemy
│   ├── services/        # Regras de Negócio, Camada de IA e Segurança
│   ├── static/          # Frontend web (HTML, CSS, JS)
│   ├── models.py        # Modelos ORM relacionais
│   ├── schemas.py       # Schemas Pydantic de entrada/saída
│   └── main.py          # Ponto de entrada FastAPI
├── data/
│   └── eval_dataset.json # Dataset de benchmark para IA
├── docs/                # Documentação técnica e arquitetura
├── scripts/             # Scripts de seed e avaliação
├── tests/               # Testes unitários e de integração
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
└── README.md
```

---

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.
