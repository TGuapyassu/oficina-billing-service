# Eventos Saga — Billing Service

## Consome

- `execution.diagnosis_completed` → busca `GET /internal/os/{id}/items` → publica `budget.created`
- Falha na busca → `budget.creation_failed`

## Publica

- `budget.created`, `budget.approved`, `budget.rejected`
- `payment.pending`, `payment.confirmed`, `payment.failed`

## REST

- `POST /orcamentos/os/{id}/decisao`
- `POST /webhooks/mercadopago`
- `POST /orcamentos/os/{id}/pagamento/simular-aprovado` (testes)
