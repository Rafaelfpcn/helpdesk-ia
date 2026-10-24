# Catálogo de Métricas e Indicadores de Impacto

O HelpDesk IA estrutura seus indicadores em três níveis estratégicos:
1. **Técnicos:** Saúde de código, confiabilidade e performance da infraestrutura.
2. **De Negócio:** Eficiência operacional da equipe de suporte e resolução de problemas.
3. **De IA e Governança:** Confiabilidade da triagem assistida e alinhamento humano-máquina.

---

## 1. Indicadores Técnicos

| Indicador | Como Medir | Endpoint / Ferramenta | Interpretação & Limitações |
|---|---|---|---|
| **Testes Automatizados** | `pytest -v` | Terminal / CI Actions | Quantidade de cenários de teste aprovados. |
| **Cobertura de Código** | `pytest --cov=app` | Terminal / Relatório HTML | Percentual de linhas executadas durante os testes automatizados. |
| **Integração Contínua (CI)** | GitHub Actions Badge | Repositório no GitHub | Validação automática da suíte em Python 3.11 e 3.12 em push/PR. |
| **Latência da API (p50 / p95)** | `python -m scripts.benchmark` | Terminal local | Mediana (p50) e percentil 95 (p95) de tempo de resposta em milissegundos. |
| **Taxa de Falha da IA** | Chamados sem sugestão ÷ Total | `/api/metrics` (`ai.failure_rate`) | Percentual de vezes que a IA falhou e o sistema acionou a falha segura. |

---

## 2. Indicadores de Negócio

| Indicador | Fórmula | Endpoint | Interpretação & Limitações |
|---|---|---|---|
| **Backlog Operacional** | `aberto` + `em_atendimento` | `/api/metrics` (`backlog_count`) | Foto do momento: volume de chamados demandando ação da equipe. |
| **Taxa de Resolução** | (`resolvido` + `fechado`) ÷ Total | `/api/metrics` (`resolution_rate`) | Percentual de chamados concluídos sobre o volume histórico. |
| **Tempo Médio de Resolução (MTTR)** | Média de (`resolved_at` − `created_at`) | `/api/metrics` (`avg_resolution_hours`) | Tempo médio em horas até a solução do chamado. |
| **Idade Média do Backlog** | Média de (`agora` − `created_at`) | `/api/metrics` (`avg_open_hours`) | Quanto tempo os chamados em aberto estão aguardando resolução. |
| **Tempo Economizado Estimado** | `confirmadas` × (`tempo_manual` − `tempo_revisao`) | `/api/metrics` (`impact`) | **Estimativa de ganho de produtividade**. Veja metodologia abaixo. |

---

## 3. Indicadores de IA e Governança

| Indicador | Fórmula | Endpoint | Interpretação & Limitações |
|---|---|---|---|
| **Cobertura de Triagem** | Sugestões geradas ÷ Total de chamados | `ai.triage_coverage` | Cobertura de classificação assistida por IA. |
| **Taxa de Confirmação Humana** | Sugestões confirmadas ÷ Total revisado | `ai.confirmation_rate` | Mede o quanto os atendentes concordam com a IA. Pode sofrer com *viés de automação*. |
| **Acurácia de Categoria** | Categorias mantidas ÷ Total revisado | `ai.category_accuracy` | Capacidade do modelo de direcionar o chamado para a fila técnica correta. |
| **Acurácia de Prioridade** | Prioridades mantidas ÷ Total revisado | `ai.priority_accuracy` | Capacidade do modelo de avaliar a criticidade real do incidente. |
| **Calibração de Confiança** | Média de confiança em confirmadas vs. alteradas | `ai.avg_confidence_*` | Se a confiança média for similar em ambos os grupos, a pontuação não prevê acerto com precisão. |
| **Matriz de Confusões Frequentes** | Pares (`sugerida` → `final`) mais comuns | `ai.top_corrections` | Mapeia os tópicos em que o modelo mais se confunde, norteando melhorias. |

---

## Protocolo de Medição do Tempo Economizado

Para garantir credibilidade técnica em entrevistas e na documentação do portfólio, **nunca divulgue estimativas sem explicitar as premissas**:

1. Execute o script de seed: `python -m scripts.seed --reset` para garantir uma base controlada e reprodutível.
2. **Cronometrar Triagem Manual:**
   - Selecione 10 a 20 chamados do arquivo `data/seed_tickets.json`.
   - Cronometre o tempo para ler a descrição, definir categoria, prioridade, resumo e ação inicial **sem consultar a IA**.
   - Anote os tempos e calcule a **mediana** (ex.: 5,0 minutos).
3. **Cronometrar Revisão com Apoio de IA:**
   - Em outros 10 a 20 chamados, utilize a tela de revisão web do HelpDesk IA.
   - Cronometre o tempo para ler a sugestão pronta e clicar em confirmar ou efetuar pequenos ajustes.
   - Calcule a **mediana** (ex.: 1,0 minuto).
4. Insira os valores calculados nas variáveis `MANUAL_TRIAGE_MINUTES` e `REVIEW_MINUTES` do arquivo `.env`.
5. O sistema recalcula dinamicamente a economia apenas para chamados **onde a sugestão foi confirmada**:
   $$\text{Tempo Economizado} = \text{Chamados Confirmados} \times (\text{Tempo Manual} - \text{Tempo Revisão})$$
