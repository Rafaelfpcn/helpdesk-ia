# Métricas e Indicadores do HelpDesk IA

O sistema expõe métricas técnicas, operacionais e de IA através do endpoint `/metrics` e do painel interativo.

## Métricas Operacionais de Suporte

| Métrica | Descrição |
|---|---|
| `tickets_total` | Volume total de chamados abertos no sistema |
| `tickets_by_status` | Distribuição da fila de atendimento (aberto, em análise, aguardando, resolvido, fechado) |
| `tickets_by_category` | Áreas mais demandadas no suporte de TI (Infraestrutura, Acesso, Hardware, Sistema, etc.) |
| `tickets_by_priority` | Proporção de criticidade dos incidentes (baixa, média, alta, crítica) |

## Métricas de Inteligência Artificial

| Métrica | Descrição |
|---|---|
| `ai_suggestions_total` | Total de sugestões de triagem geradas |
| `ai_reviews_total` | Total de sugestões auditadas e revisadas por humanos |
| `ai_accepted_rate` | Percentual de sugestões aceitas sem necessidade de alteração |
| `ai_corrected_rate` | Percentual de sugestões que precisaram de correção humana |
| `ai_avg_confidence` | Nível médio de certeza manifestado pela IA nas predições |
| `ai_avg_latency_ms` | Tempo médio de resposta do motor de IA em milissegundos |
| `ai_by_decision` | Quantidade de sugestões com preenchimento automático vs. revisão manual |

## Avaliação Offline do Modelo

O script `scripts/evaluate_ai.py` executa um benchmark contra o dataset padrão em `data/eval_dataset.json`:

```bash
python scripts/evaluate_ai.py
```

Calcula acurácia de categoria, acurácia de prioridade e acurácia completa (ambos corretos simultaneamente).
