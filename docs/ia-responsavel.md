# IA Responsável no HelpDesk IA

Este projeto utiliza Inteligência Artificial para apoiar a triagem e o roteamento de chamados de suporte de TI, seguindo princípios éticos e de responsabilidade.

## Princípios Adotados

1. **A IA não resolve chamados sozinha:** Toda sugestão gerada pela IA requer supervisão ou pode ser revisada/corrigida por um atendente humano.
2. **Confiança controla automação:** O sistema calcula um score de confiança (`confidence`). Somente sugestões com confiança superior ao limiar configurado (`AI_CONFIDENCE_THRESHOLD`) preenchem campos automaticamente (`auto_fill`). Abaixo do limiar, o sistema adota valores seguros e sinaliza `manual_review`.
3. **Resiliência e tolerância a falhas:** Caso o provedor de IA fique indisponível ou lance exceção, a abertura do chamado não é bloqueada. O sistema aplica fallback gracioso e registra a ocorrência.
4. **Privacidade e minimização de dados:** Dados textuais passam por uma camada de sanitização antes de serem processados pela IA, mascarando padrões comuns de CPF, e-mail e telefone.
5. **Auditoria persistente:** Todas as predições geradas, tempo de resposta (latência em ms), versão do prompt/modelo e decisões de revisão humana são gravadas no banco de dados para rastreabilidade.
6. **Métricas de qualidade contínuas:** O sistema monitora a taxa de aceitação vs. taxa de correção humana, permitindo identificar necessidade de ajustes no modelo ou nas regras.

## Mecânica de Decisão da IA

```text
Entrada (Título + Descrição)
          |
          v
   Sanitização Regex (LGPD)
          |
          v
    Provedor de IA (Análise)
          |
   +------+------+
   |             |
Confiança     Confiança
 >= 0.70       < 0.70
   |             |
   v             v
Decisão:      Decisão:
auto_fill   manual_review
(sugere)    (fallback)
```

## Configuração

No arquivo `.env`:

```env
AI_PROVIDER=mock
AI_CONFIDENCE_THRESHOLD=0.70
AI_FALLBACK_CATEGORY=nao_classificado
AI_FALLBACK_PRIORITY=media
AI_MAX_LATENCY_MS=1500
```
