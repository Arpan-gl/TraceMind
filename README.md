# TraceMind

Production-style LLM inference logging and ingestion system.

## Setup

### Prerequisites
- Docker
- Docker Compose

### Run
1. Copy `.env.example` to `.env` and fill in the API keys and secrets.
2. Start the stack:

```bash
docker compose up --build
```

### Access
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Grafana: http://localhost:3001
- RabbitMQ management: http://localhost:15672
- Prometheus: http://localhost:9090

## Architecture Overview

| Component | Role | Notes |
| --- | --- | --- |
| Frontend | React + TypeScript + TailwindCSS + shadcn/ui | Auth, conversation list, and streamed chat UI |
| Backend | FastAPI + async SQLAlchemy + Alembic | JWT auth, conversation APIs, chat streaming, ingestion, and metrics |
| LLM SDK | Groq-first provider wrapper | Structured for multi-provider routing |
| Redis | Short-term context cache | Recent messages, summaries, and quota counters |
| PostgreSQL | Durable persistence | Users, conversations, messages, token usage, and inference logs |
| RabbitMQ | Telemetry decoupling | Offloads inference log delivery from chat requests |
| Prometheus | Metrics collection | Scrapes FastAPI and RabbitMQ exporter |
| Grafana | Dashboards | Pre-provisioned observability views |

## Schema Design Decisions

- Conversations are soft-deleted with `is_deleted` instead of hard deleted so history can be recovered and analytics remain stable.
- UUID primary keys are used instead of serial integers to avoid enumeration and to stay portable across services.
- `inference_logs` is separate from `messages` so telemetry can be queried, retained, and indexed independently from chat content.
- `token_usage` is tracked per day rather than per message because the main use case is quota management, not per-message billing.

## Tradeoffs Made

- SSE-style streaming over WebSockets because the use case is one-way server-to-client delivery and HTTP compatibility is simpler.
- Redis TTL memory instead of storing all history in cache because the system benefits from a hybrid cost/performance balance.
- RabbitMQ over Kafka because the requested scale does not need Kafka’s added operational complexity.
- Regex-based PII redaction for the first version because it is pragmatic and fast to ship; a dedicated redaction service would be better later.

## Future Improvements

- Deploy on Kubernetes with horizontal worker scaling.
- Add a vector database such as pgvector or Qdrant for semantic memory.
- Replace the regex PII scrubber with Microsoft Presidio.
- Add model routing so simple requests use cheaper models.
- Add multi-provider fallback if Groq fails.
- Add rate limiting per user.
- Add conversation search with PostgreSQL full-text search.
- Add export to markdown or PDF.