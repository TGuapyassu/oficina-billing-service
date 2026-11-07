# oficina-billing-service

**GitHub:** https://github.com/TGuapyassu/oficina-billing-service

## Cobertura

```bash
pip install -e ".[dev]"   # requer oficina-contracts
pytest
```

Evidência local (≥80%): [`docs/evidencias/cobertura-local.txt`](docs/evidencias/cobertura-local.txt) · resumo visual [`cobertura-resumo.svg`](docs/evidencias/cobertura-resumo.svg) · HTML em `docs/evidencias/htmlcov/` após o `pytest`. CI: artefato **coverage-report**.

## API (Swagger)

Com a stack local no ar: **http://localhost:8003/docs** (OpenAPI / Redoc em `/redoc`).

Fluxo integrado Saga (Postman no repo OS): ver seção **Postman** abaixo.

## Documentação

[`docs/architecture/`](docs/architecture/)

Orçamentos, aprovação/recusa e pagamentos via **Mercado Pago**.

## Bancos

| Tipo | Uso |
|------|-----|
| PostgreSQL | `orcamentos`, `pagamentos` |
| MongoDB | Idempotência de webhooks MP |

## Fluxo

1. Consome `execution.diagnosis_completed` → chama OS `GET /internal/os/{id}/items` → publica `budget.created`
2. `POST /orcamentos/os/{id}/decisao` → preferência MP → `payment.pending`
3. `POST /webhooks/mercadopago` ou `POST .../pagamento/simular-aprovado` (testes) → `payment.confirmed`

## Mercado Pago

Documentação: https://www.mercadopago.com.br/developers/pt/docs

Variáveis: `MP_ACCESS_TOKEN`, `MP_WEBHOOK_SECRET`, `PUBLIC_BASE_URL`

Sem token, o cliente MP retorna **checkout mock** para desenvolvimento.

## Compensações

Falha ao buscar itens da OS → publica `budget.creation_failed` (OS libera estoque).

## Infraestrutura

- `infra-db/` — RDS `oficina_billing`
- `infra-k8s/manifests/app/` — Deploy Kubernetes

Stack local: [`../oficina-os-service/docker-compose.stack.yml`](../oficina-os-service/docker-compose.stack.yml)

## Postman

Collection mínima deste serviço: [`docs/postman/oficina-billing-service.postman_collection.json`](docs/postman/oficina-billing-service.postman_collection.json).  
Fluxo E2E Saga: [`../oficina-os-service/docs/postman/oficina-fase4-microservices.postman_collection.json`](../oficina-os-service/docs/postman/oficina-fase4-microservices.postman_collection.json).
