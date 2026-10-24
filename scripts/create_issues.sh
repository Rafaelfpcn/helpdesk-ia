#!/usr/bin/env bash
# Uso: bash scripts/create_issues.sh (dentro do repositório, com o GitHub CLI logado)
set -e

for label in backend frontend ia docs testes bug melhoria; do
  gh label create "$label" --force >/dev/null || true
done

for m in "M1 - Fundação" "M2 - Backend" "M3 - IA responsável" "M4 - Frontend" \
         "M5 - Qualidade e publicação" "Roadmap - Melhorias futuras"; do
  gh api repos/:owner/:repo/milestones -f title="$m" >/dev/null || true
done

create() {
  gh issue create --title "$1" --label "$2" --milestone "$3" --body "$4" >/dev/null && echo "criada: $1";
}

M1="M1 - Fundação"; M2="M2 - Backend"; M3="M3 - IA responsável"
M4="M4 - Frontend"; M5="M5 - Qualidade e publicação"; MR="Roadmap - Melhorias futuras"

create "Criar estrutura de pastas e repositório" docs "$M1" "Critério de aceite: estrutura conforme docs/architecture.md, .gitignore e README inicial."
create "Configurar FastAPI, .gitignore e requirements" backend "$M1" "Critério de aceite: GET /health responde 200; dependências em requirements.txt e requirements-dev.txt."
create "Configurar SQLite e SQLAlchemy" backend "$M1" "Critério de aceite: sessão por requisição (get_db) e tabelas criadas na inicialização."
create "Criar modelos Ticket, AISuggestion e AuditLog" backend "$M1" "Critério de aceite: três tabelas com relacionamentos e valores controlados (enums)."
create "Implementar POST /api/tickets com validação" backend "$M2" "Critério de aceite: 201 com dados válidos; 422 com título curto, e-mail inválido ou categoria desconhecida."
create "Implementar listagem e detalhe de chamados" backend "$M2" "Critério de aceite: filtros por status, categoria e prioridade; 404 padronizado."
create "Implementar atualização de status" backend "$M2" "Critério de aceite: transições inválidas retornam 409; resolved_at preenchido ao resolver."
create "Tratamento padronizado de erros" backend "$M2" "Critério de aceite: erros de negócio em JSON {error: {code, message}}."
create "Criar AIProvider e MockAIProvider" ia "$M3" "Critério de aceite: interface única; mock determinístico com categoria, prioridade, urgência, resumo e ação."
create "Criar Sanitizer de dados sensíveis" ia "$M3" "Critério de aceite: mascara CPF, CNPJ, e-mail, telefone, cartão e senha; logs guardam só tipo e quantidade."
create "Implementar revisão humana (confirmar/corrigir)" ia "$M3" "Critério de aceite: sugestão original preservada; segunda revisão retorna 409; correção idêntica à sugestão é rejeitada."
create "Implementar logs de auditoria" backend "$M3" "Critério de aceite: eventos de criação, sugestão, revisão, status e falha da IA registrados na mesma transação."
create "Escrever docs/ai-responsible.md" docs "$M3" "Critério de aceite: princípios, limitações do mock e do sanitizer, riscos de um LLM real."
create "Tela de abertura de chamado" frontend "$M4" "Critério de aceite: formulário com validação e mensagens de erro da API."
create "Tela de listagem com filtros" frontend "$M4" "Critério de aceite: filtros por status, categoria e prioridade; estado vazio."
create "Tela de detalhe e revisão da IA" frontend "$M4" "Critério de aceite: aviso de limitação visível; confirmar/corrigir; botões de status válidos."
create "Dashboard de métricas" frontend "$M4" "Critério de aceite: totais, barras por categoria/prioridade/status, tempos médios e qualidade da IA."
create "Testes: criação, listagem, status e IA mock" testes "$M5" "Critério de aceite: pytest verde com banco em memória isolado."
create "Script de seed com dados fictícios" backend "$M5" "Critério de aceite: 30 chamados com histórico realista; reproduzível (semente fixa)."
create "Dockerfile e docker-compose" backend "$M5" "Critério de aceite: docker compose up sobe a aplicação com banco persistente."
create "README completo com prints" docs "$M5" "Critério de aceite: todas as seções preenchidas e prints em docs/images."
create "GitHub Actions rodando pytest" testes "$M5" "Critério de aceite: workflow verde em push e pull request."
create "Autenticação e papéis (usuário x atendente)" melhoria "$MR" "Hoje qualquer pessoa pode revisar chamados."
create "Integrar LLM real via novo AIProvider" ia "$MR" "Manter sanitizer, validar saída contra enums e tratar texto do chamado como dado (prompt injection)."
create "Paginação e busca na listagem" melhoria "$MR" "A lista carrega todos os chamados."
create "Migrar para PostgreSQL com Alembic" backend "$MR" "Substituir create_all por migrações versionadas."
create "Revisão manual de chamados sem sugestão da IA" melhoria "$MR" "Permitir triagem manual quando a IA falha."
create "SLA e alertas de prazo" melhoria "$MR" "Prazos por prioridade e destaque de chamados atrasados."
create "Sanitizer mais completo e mascaramento na entrada" ia "$MR" "Detectar nomes, endereços e IPs; avaliar mascarar também no banco."
create "Comparar versões da IA com as mesmas métricas" ia "$MR" "Registrar versão do provider e comparar taxa de confirmação."
