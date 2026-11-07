# oficina-billing-service

Microsserviço de **orçamento** e **pagamentos** (Mercado Pago). Reage a eventos da oficina, monta o valor da OS consultando o serviço OS e coordena aprovação, checkout e confirmação de pagamento via mensageria.

## O que este serviço faz

- Ao receber o diagnóstico concluído na Saga, busca itens da OS (`GET /internal/os/{id}/items` no OS) e cria orçamento; publica `budget.created` ou `budget.creation_failed` (compensação no OS).
- REST para consultar orçamento e registrar decisão do cliente (`aprovar` / `recusar`).
- Integração **Mercado Pago** (preferência de pagamento; sem token usa checkout **mock** em dev).
- Webhook `POST /webhooks/mercadopago` com idempotência em **MongoDB**.
- Endpoint de teste `POST /orcamentos/os/{id}/pagamento/simular-aprovado` para confirmar pagamento sem MP.

Persistência: **PostgreSQL** (`orcamentos`, `pagamentos`). **MongoDB** para deduplicação de webhooks. **RabbitMQ** para eventos `budget.*` e `payment.*`.

## Ecossistema

| Componente | Repositório | Porta (stack) |
|------------|-------------|---------------|
| OS | `oficina-os-service` | 8000 |
| Billing (este) | `oficina-billing-service` | 8003 |
| Execution | `oficina-execution-service` | 8002 |
| Contratos | `oficina-contracts` @ `v0.1.0` | — |

## Pré-requisitos

- Python **3.11+**; Docker Compose para stack completa.
- `oficina-contracts` instalável via GitHub (ou cópia local para desenvolvimento).

## Como rodar

### Stack completa

A partir do repositório OS (pastas irmãs obrigatórias):

```bash
cd ../oficina-os-service
docker compose -f docker-compose.stack.yml up --build
```

Swagger: **http://localhost:8003/docs**

O compose define `OS_SERVICE_URL=http://os-service:8000` e `INTERNAL_SERVICE_KEY` alinhados ao OS.

### Desenvolvimento local (só billing)

Suba PostgreSQL, MongoDB e RabbitMQ (ou use a stack e pare os outros serviços). Exemplo mínimo:

```bash
pip install "oficina-contracts @ git+https://github.com/TGuapyassu/oficina-contracts.git@v0.1.0"
pip install -e ".[dev]"
export DATABASE_URL=postgresql+psycopg2://oficina:oficina@localhost:5434/oficina_billing
export RABBITMQ_URL=amqp://guest:guest@localhost:5672/
export MONGODB_URL=mongodb://localhost:27017
export OS_SERVICE_URL=http://localhost:8000
export INTERNAL_SERVICE_KEY=dev-internal-key
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

| Variável | Uso |
|----------|-----|
| `DATABASE_URL` | PostgreSQL |
| `RABBITMQ_URL` | Publicação/consumo de eventos |
| `MONGODB_URL` | Idempotência de webhooks MP |
| `OS_SERVICE_URL` | Base URL do OS (**8000** na stack local) |
| `INTERNAL_SERVICE_KEY` | Mesmo valor configurado no OS |
| `MP_ACCESS_TOKEN` | Token MP; vazio → checkout mock |
| `MP_WEBHOOK_SECRET` | Validação de webhook (produção) |
| `PUBLIC_BASE_URL` | URL pública do serviço (links MP) |

Documentação MP: https://www.mercadopago.com.br/developers/pt/docs

## Fluxo de eventos (resumo)

1. Consome evento de diagnóstico → orçamento → `budget.created`.
2. `POST /orcamentos/os/{id}/decisao` (aprovado) → preferência MP → `payment.pending`.
3. Webhook MP ou `simular-aprovado` → `payment.confirmed` (execution e OS reagem na Saga).

Detalhes: [`docs/architecture/`](docs/architecture/).

## API e Postman

- OpenAPI: **http://localhost:8003/docs**
- Collection deste serviço: [`docs/postman/oficina-billing-service.postman_collection.json`](docs/postman/oficina-billing-service.postman_collection.json)
- Fluxo integrado Saga: [`../oficina-os-service/docs/postman/oficina-saga-microservices.postman_collection.json`](../oficina-os-service/docs/postman/oficina-saga-microservices.postman_collection.json)

## Testes

```bash
pip install -e ".[dev]"
pytest
```

Meta **≥80%** em `app/`. Evidências: [`docs/evidencias/`](docs/evidencias/) (`cobertura-local.txt`, `cobertura-resumo.svg`).

## Infraestrutura

- `infra-db/` — RDS `oficina_billing`
- `infra-k8s/manifests/app/` — deploy Kubernetes
- `scripts/k8s-deploy.sh` — aplica manifests no cluster
