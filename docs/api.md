# Especificação da API REST

A API do HelpDesk IA é construída com **FastAPI** e fornece documentação interativa OpenAPI/Swagger acessível em:
`http://127.0.0.1:8000/docs` (ou `/redoc`).

---

## Tabela Resumo dos Endpoints

| Método | Rota | Descrição | Status Sucesso | Status Erros |
|---|---|---|---|---|
| **POST** | `/api/tickets` | Abre chamado, sanitiza dados sensíveis e gera sugestão de IA | `201 Created` | `422 Unprocessable Entity` |
| **GET** | `/api/tickets` | Lista chamados com filtros opcionais (`status`, `category`, `priority`) | `200 OK` | `422 Unprocessable Entity` |
| **GET** | `/api/tickets/{id}` | Recupera detalhes de um chamado e sua sugestão de IA | `200 OK` | `404 Not Found` |
| **PATCH** | `/api/tickets/{id}/status` | Atualiza status operacional respeitando máquina de estados | `200 OK` | `404 Not Found`, `409 Conflict` |
| **POST** | `/api/tickets/{id}/review/confirm` | Confirma sugestão da IA (categoria e prioridade viram oficiais) | `200 OK` | `404 Not Found`, `409 Conflict` |
| **POST** | `/api/tickets/{id}/review/change` | Corrige manualmente categoria e prioridade | `200 OK` | `404 Not Found`, `409 Conflict`, `422 Validation Error` |
| **GET** | `/api/tickets/{id}/logs` | Retorna histórico imutável de auditoria do chamado | `200 OK` | `404 Not Found` |
| **GET** | `/api/metrics` | Consolida indicadores de negócio, governança de IA e impacto | `200 OK` | — |
| **GET** | `/health` | Health check da aplicação | `200 OK` | — |

---

## Formato Padronizado de Erros de Negócio

Erros operacionais e regras de negócio violadas retornam um envelope JSON unificado:

```json
{
  "error": {
    "code": "invalid_status_transition",
    "message": "Não é possível mudar de 'aberto' para 'resolvido'."
  }
}
```

### Códigos de Erro Mapeados:
- `ticket_not_found` (404): Chamado não existe no banco.
- `invalid_status_transition` (409): Transição de status proibida pelas regras de negócio.
- `review_already_done` (409): O chamado já teve sua triagem revisada anteriormente.
- `no_suggestion` (409): Tentativa de revisar chamado onde a IA falhou e não gerou sugestão.
- `invalid_review` (422): Tentativa de alteração com valores 100% idênticos aos sugeridos pela IA (deve-se usar a rota de confirmação).

---

## Máquina de Estados de Transição de Status

```
[aberto] ---------> [em_atendimento]
   |                      |
   v                      v
[fechado] <---------- [resolvido]
```

- De **`aberto`**: pode transitar para `em_atendimento` ou `fechado`.
- De **`em_atendimento`**: pode transitar para `resolvido` ou retornar para `aberto`.
- De **`resolvido`**: pode transitar para `fechado` ou reabrir para `em_atendimento`.
- De **`fechado`**: estado terminal, nenhuma transição permitida.
