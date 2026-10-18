# 🎤 Guia de Apresentação do Projeto & Roteiro de Entrevista

> **HelpDesk IA** — Sistema de Triagem e Análise de Chamados de TI com IA Responsável  
> **Autor:** Rafael  
> **Repositório:** [https://github.com/Rafaelfpcn/helpdesk-ia](https://github.com/Rafaelfpcn/helpdesk-ia)

---

## ⏱️ 1. Pitch de Elevador (30 Segundos)

> *"Desenvolvi o **HelpDesk IA**, uma plataforma completa de Help Desk e Service Desk que resolve um dos maiores gargalos operacionais de TI: a triagem manual e lenta de incidentes. O sistema utiliza uma camada de Inteligência Artificial para inferir categoria, prioridade e tempo estimado de resposta em tempo real, mas com um diferencial crítico: **supervisão humana obrigatória (Human-in-the-Loop)**, tolerância a falhas com fallback gracioso e sanitização de dados sensíveis em conformidade com a LGPD. O backend foi construído em FastAPI e SQLAlchemy, com testes automatizados e CI/CD no GitHub Actions."*

---

## 🎙️ 2. Apresentação Técnica Aprofundada (2 Minutos para Entrevistas)

### 📌 Contexto & Problema de Negócio
*"Em equipes de suporte de TI, filas de chamados frequentemente sofrem com descrições incompletas, prioridades erradas e chamados críticos misturados a pedidos comuns. Isso atrasa o tempo de primeira resposta (MTTA) e a resolução (MTTR).*

### 💡 A Solução de Engenharia
*Para resolver isso sem introduzir riscos de 'alucinação' de modelos de IA em produção, arquitetei um sistema baseado em 4 pilares:*

1. **Back-end de Alta Performance:** Desenvolvido em Python com **FastAPI** e **Pydantic v2**, garantindo validação estrita de esquemas em tempo de execução e documentação OpenAPI/Swagger automática.
2. **Engenharia de IA Responsável:**
   - **Confiança mínima parametrizável (Threshold $\ge 0.70$):** Se a certeza for alta, a sugestão é pré-preenchida; caso contrário, é marcado para revisão manual obrigatória.
   - **Privacidade & LGPD:** Os dados passam por sanitização por Regex (removendo CPFs, telefones e e-mails) antes de qualquer processamento de inteligência.
   - **Tolerância a Falhas:** Caso o provedor de IA oscile ou falhe, o sistema aplica um fallback silencioso e não impede a abertura do chamado pelo usuário.
3. **Trilha de Auditoria & Métricas de Negócio:**
   - Cada inferência de IA gera um registro persistente com latência, confiança, dados originais e status de validação humana (se o analista aceitou ou corrigiu a sugestão).
   - O painel exibe taxa de aceitação, acurácia e chamados por categoria e prioridade.
4. **DevOps & Qualidade de Código:**
   - 100% dos testes unitários e de integração implementados com **Pytest** e **HTTPX**.
   - Linting rigoroso com **Ruff**.
   - Integração Contínua (CI/CD) automatizada via **GitHub Actions** em cada push/pull request.
   - Pronto para contêiner com **Docker** e **Docker Compose**."*

---

## 🥊 3. Perguntas que Recrutadores & Tech Leads Vão Fazer (e Como Responder)

### ❓ P1: *"Por que você usou um Mock de IA por padrão em vez de exigir uma API paga como OpenAI ou Gemini?"*
> **Sua resposta:**  
> *"Eu desenhei a arquitetura seguindo o padrão de projeto Strategy / Factory. Ter um provedor Mock determinístico como padrão permite que qualquer recrutador ou colega da equipe clone o repositório e rode os testes e a aplicação localmente sem precisar cadastrar cartão de crédito ou gerar tokens. Além disso, garante que os testes de integração no GitHub Actions sejam rápidos, determinísticos e gratuitos. Para plugar uma LLM real como Gemini ou GPT, basta implementar a mesma interface abstrata no diretório `app/services/ai.py` e apontar a variável de ambiente `AI_PROVIDER`."*

### ❓ P2: *"Como você tratou a segurança e dados sensíveis (LGPD)?"*
> **Sua resposta:**  
> *"Implementei uma etapa de pré-processamento no `ai.py` que sanitiza padrões de dados sensíveis (CPFs, e-mails, telefones e números de cartões) antes de enviá-los para processamento. Na camada de autenticação, usei tokens JWT criptografados com PBKDF2 e salt para senhas, mantendo o sistema modular com uma flag que permite ativar ou desativar a autenticação estrita dependendo do ambiente."*

### ❓ P3: *"Como você avaliou se o modelo de IA é eficaz?"*
> **Sua resposta:**  
> *"Criei um dataset de benchmark sintético em `data/eval_dataset.json` com chamados típicos de TI e casos de borda (pedidos ambíguos ou com dados confusos). Desenvolvi o script `scripts/evaluate_ai.py` que calcula a acurácia de categorização e priorização, simulando o comportamento do modelo e validando a taxa de acerto antes de qualquer deploy."*

---

## 📱 4. Modelo de Post Pronto para o LinkedIn

```markdown
🚀 Acabo de finalizar e publicar o HelpDesk IA!

Trata-se de um sistema completo de gestão e triagem de chamados de TI (Service Desk) desenvolvido em Python e FastAPI, integrado a uma camada de Inteligência Artificial responsável.

Um dos maiores desafios no suporte de TI é o gargalo na triagem inicial: chamados mal categorizados, descrições vagas e incidentes críticos perdidos na fila. 

Principais destaques do projeto:
✅ Triagem inteligente de categoria, prioridade e tempo de resposta em tempo real.
✅ IA Responsável & Human-in-the-Loop: a IA apenas sugere; o analista valida ou corrige com trilha de auditoria completa.
✅ Privacidade por Design (LGPD): sanitização automática de CPFs, e-mails e telefones.
✅ Dashboard interativo com métricas de negócio, acurácia da IA e taxas de aceite.
✅ Qualidade e DevOps: testes automatizados com Pytest, linter Ruff, CI/CD no GitHub Actions e Docker Compose.

🔗 Repositório público no GitHub: https://github.com/Rafaelfpcn/helpdesk-ia

Feedback e sugestões são muito bem-vindos!

#Python #FastAPI #InteligenciaArtificial #HelpDesk #DevOps #EngenhariaDeSoftware #OpenSource #Portfolio
```

---

## 📋 5. Roteiro Prático para Apresentar ao Vivo (Demo de 3 Minutos)

1. **Abrir o Dashboard (`http://localhost:8001`)**:
   - Mostre os cartões de indicadores (chamados abertos, acurácia da IA, taxa de aceitação dos analistas).
2. **Criar um Chamado Crítico**:
   - Vá na aba "Novo chamado".
   - Digite: *"Servidor de banco de dados fora do ar e ninguém consegue faturar pedidos"*.
   - Deixe os campos de categoria e prioridade em branco e envie.
3. **Mostrar a Mágica da IA & Human-in-the-Loop**:
   - Vá para "Chamados", clique em "Detalhes" do chamado criado.
   - Mostre que a IA inferiu: Categoria: `Infraestrutura`, Prioridade: `Crítica`, com score de confiança e justificativa.
   - Mostre os botões de revisão humana (Aceitar / Corrigir) demonstrando governança de IA.
4. **Mostrar a Documentação da API**:
   - Abra o Swagger em `/docs` e mostre a arquitetura REST limpa e padronizada.
5. **Finalizar com os Testes**:
   - No terminal, rode `pytest -v` para provar a cobertura e confiabilidade do código.
