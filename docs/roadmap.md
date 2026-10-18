# Roadmap de Evolução — HelpDesk IA

## Fase 1 — MVP Completo (Entregue)
- [x] API REST em FastAPI com tipagem Pydantic
- [x] Banco de dados relacional com SQLAlchemy e SQLite
- [x] Motor de IA plugável com sanitização e decisão baseada em confiança
- [x] Painel web interativo (HTML/CSS/JS) para abertura, triagem, auditoria e KPIs
- [x] Sistema de autenticação opcional com JWT e perfis de usuário
- [x] Suite de testes unitários e de integração com pytest
- [x] Dockerfile, docker-compose e pipeline de CI com GitHub Actions
- [x] Script de seed com 12 chamados realistas e usuário demo

## Fase 2 — Curto Prazo
- [ ] Migrações versionadas de esquema de banco com Alembic
- [ ] Exportação de relatórios gerenciais em PDF e CSV
- [ ] Suporte a anexos de arquivos e capturas de tela nos chamados
- [ ] Integração com Provedores Reais de LLM (Google Gemini API / OpenAI / Ollama)

## Fase 3 — Médio Prazo
- [ ] Base de conhecimento interna com busca semântica (RAG)
- [ ] Chatbot de triagem N1 conversacional
- [ ] Regras de SLA com alertas automáticos por e-mail e webhook
- [ ] Deploy conteinerizado com PostgreSQL e monitoramento OpenTelemetry
