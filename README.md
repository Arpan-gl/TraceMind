# TraceMind

Production-style LLM inference logging and ingestion system with real-time streaming, observability, telemetry pipelines, and short-term memory optimization.

---

# Overview

TraceMind is a lightweight AI infrastructure platform that combines:

* Real-time LLM chat streaming
* Inference telemetry logging
* Async ingestion pipelines
* Short-term memory optimization
* Monitoring and observability
* Token quota management
* Production-style backend architecture

The system is designed to simulate how modern AI products monitor, optimize, and scale LLM workloads in production environments.

---

# Features

## Chat Application

* Multi-turn conversations
* Real-time token streaming using SSE
* Conversation history
* Resume conversations
* Delete conversations
* Authentication and session management

## Inference Logging SDK

* Captures latency
* Tracks token usage
* Tracks request status and errors
* Stores timestamps and session metadata
* Supports provider abstraction

## Ingestion Pipeline

* Asynchronous telemetry ingestion
* Queue-based event processing
* Structured inference logs
* Background workers

## Observability

* Prometheus metrics
* Grafana dashboards
* Queue monitoring
* API latency tracking
* Token usage analytics

## Infrastructure

* Docker Compose setup
* GitHub Actions CI/CD
* Redis caching
* PostgreSQL persistence
* RabbitMQ event architecture

---

# Tech Stack

| Layer          | Technology                                      |
| -------------- | ----------------------------------------------- |
| Frontend       | React.js + TypeScript + TailwindCSS + shadcn/ui |
| Backend        | FastAPI                                         |
| Streaming      | Server-Sent Events (SSE)                        |
| LLM Provider   | Groq (Llama 3)                                  |
| Cache / Memory | Redis                                           |
| Database       | PostgreSQL                                      |
| Queue          | RabbitMQ                                        |
| Monitoring     | Prometheus + Grafana                            |
| Deployment     | Docker Compose + Render                         |
| CI/CD          | GitHub Actions                                  |

---

# System Design Architecture

```text
                        ┌────────────────────┐
                        │     React UI       │
                        │  Chat + Auth UI    │
                        └─────────┬──────────┘
                                  │
                                  ▼
                    ┌────────────────────────┐
                    │  Nginx Reverse Proxy   │
                    │   Rate Limiting Layer  │
                    └─────────┬──────────────┘
                              │
                              ▼
                    ┌────────────────────────┐
                    │      FastAPI API       │
                    │  Auth + Chat + SSE     │
                    └─────────┬──────────────┘
                              │
               ┌──────────────┴──────────────┐
               │                             │
               ▼                             ▼
      ┌────────────────┐           ┌────────────────┐
      │     Redis      │           │   LLM Wrapper  │
      │ Short Memory   │           │ Telemetry SDK  │
      └────────────────┘           └──────┬─────────┘
                                          │
                                          ▼
                              ┌────────────────────┐
                              │    Groq / Llama3   │
                              │   Streaming Model  │
                              └─────────┬──────────┘
                                        │
                                        ▼
                            ┌──────────────────────┐
                            │  RabbitMQ Telemetry  │
                            │      Event Queue     │
                            └─────────┬────────────┘
                                      │
                                      ▼
                            ┌──────────────────────┐
                            │   Ingestion Worker   │
                            │ Metadata Processing  │
                            └─────────┬────────────┘
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │      PostgreSQL        │
                          │ Chats + Logs + Tokens  │
                          └────────────────────────┘

                                      │
                                      ▼
                        ┌─────────────────────────┐
                        │ Prometheus + Grafana   │
                        │ Monitoring Dashboards  │
                        └─────────────────────────┘
```

---

# Chat Request Flow

```text
1. User logs into the application.
2. User sends a message from the frontend.
3. FastAPI validates JWT authentication.
4. Redis fetches recent conversation memory.
5. Prompt builder creates optimized context.
6. LLM Wrapper calls Groq model.
7. Tokens stream back using SSE.
8. Frontend renders response in real-time.
9. SDK captures inference metadata:
   - latency
   - token usage
   - timestamps
   - provider
   - errors
10. Telemetry event pushed to RabbitMQ.
11. Ingestion worker consumes event.
12. PostgreSQL stores logs and analytics.
13. Prometheus collects metrics.
14. Grafana visualizes dashboards.
```

---

# Lightweight LLM SDK

The SDK acts as a middleware layer around all model calls.

Instead of directly calling:

```python
client.chat.completions.create()
```

The system uses:

```python
llm_wrapper.generate()
```

The wrapper automatically:

* measures latency
* tracks tokens
* logs request metadata
* captures failures
* streams responses
* emits telemetry events

---

# Inference Metadata Captured

| Field            | Description              |
| ---------------- | ------------------------ |
| provider         | groq                     |
| model            | llama-3-8b               |
| latency_ms       | total inference duration |
| tokens_input     | prompt tokens            |
| tokens_output    | completion tokens        |
| request_id       | unique request ID        |
| session_id       | conversation identifier  |
| status           | success / failure        |
| error_message    | provider error           |
| request_preview  | truncated prompt         |
| response_preview | truncated completion     |
| timestamp        | request timestamp        |

---

# Redis Memory Strategy

## Problem

Sending the entire chat history to the LLM increases:

* token cost
* latency
* context size

## Solution

TraceMind uses a hybrid memory architecture.

```text
Redis:
- recent messages
- temporary summaries
- active sessions

PostgreSQL:
- full conversation history
- persistent storage
```

---

# Memory Optimization Flow

```text
Prompt =
System Prompt
+ Conversation Summary
+ Last 6-10 Messages
+ Current User Message
```

## Optimization Rules

* Keep only recent messages in active context
* Summarize older messages every 10-15 turns
* Store summaries in Redis
* Use Redis TTL for inactive sessions
* Restore history from PostgreSQL if needed

---

# Database Schema Design

## users

```sql
id UUID PRIMARY KEY
email TEXT UNIQUE
password_hash TEXT
created_at TIMESTAMP
```

## conversations

```sql
id UUID PRIMARY KEY
user_id UUID
title TEXT
is_deleted BOOLEAN
created_at TIMESTAMP
```

## messages

```sql
id UUID PRIMARY KEY
conversation_id UUID
role TEXT
content TEXT
token_count INTEGER
created_at TIMESTAMP
```

## token_usage

```sql
id UUID PRIMARY KEY
user_id UUID
daily_tokens_used INTEGER
updated_at TIMESTAMP
```

## inference_logs

```sql
id UUID PRIMARY KEY
conversation_id UUID
provider TEXT
model TEXT
latency_ms INTEGER
tokens_input INTEGER
tokens_output INTEGER
status TEXT
error_message TEXT
request_preview TEXT
response_preview TEXT
created_at TIMESTAMP
```

---

# Queue-Based Ingestion Architecture

TraceMind uses RabbitMQ to decouple telemetry processing from chat requests.

## Without Queue

```text
API → Database
```

Problems:

* blocking writes
* slower responses
* reduced scalability

## With Queue

```text
API → RabbitMQ → Worker → PostgreSQL
```

Benefits:

* async ingestion
* retry handling
* smoother burst traffic
* fault isolation
* scalable worker architecture

---

# Monitoring and Observability

## Prometheus Metrics

* API request latency
* inference duration
* queue depth
* token consumption
* worker throughput
* request rate
* error rate

## Grafana Dashboards

* LLM latency dashboard
* token analytics
* API health dashboard
* queue monitoring
* ingestion pipeline status

---

# Security and Rate Limiting

## Authentication

* JWT-based authentication
* Password hashing with bcrypt

## Rate Limiting

Implemented using Nginx:

* request throttling
* abuse prevention
* API protection

Example:

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

---

# Docker Compose Setup

## Services

```yaml
frontend
backend
postgres
redis
rabbitmq
prometheus
grafana
nginx
```

Run the full stack:

```bash
docker compose up --build
```

---

# Setup Instructions

## Prerequisites

* Docker
* Docker Compose

## Installation

### 1. Clone Repository

```bash
git clone <repo-url>
cd tracemind
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Add:

* Groq API key
* JWT secrets
* database credentials

### 3. Start Services

```bash
docker compose up --build
```

---

# Access URLs

| Service    | URL                    |
| ---------- | ---------------------- |
| Frontend   | http://localhost:3000  |
| Backend    | http://localhost:8000  |
| Grafana    | http://localhost:3001  |
| RabbitMQ   | http://localhost:15672 |
| Prometheus | http://localhost:9090  |

---

# Engineering Tradeoffs

| Decision                     | Reason                        |
| ---------------------------- | ----------------------------- |
| SSE over WebSockets          | simpler one-way streaming     |
| RabbitMQ over Kafka          | lower operational complexity  |
| Redis TTL caching            | balances cost and performance |
| PostgreSQL relational schema | structured analytics queries  |
| Regex PII redaction          | fast MVP implementation       |
| UUIDs over integers          | safer public identifiers      |

---

# Scaling Considerations

Future improvements:

* Kubernetes deployment
* Horizontal worker scaling
* Distributed Redis cluster
* Multi-provider model routing
* Vector database memory
* Semantic search
* Advanced PII redaction
* Autoscaling queue consumers

---

# Future Improvements

* Multi-provider fallback support
* Dynamic model routing
* Semantic memory with pgvector
* Conversation export to PDF
* Full-text conversation search
* Advanced analytics dashboards
* Cost estimation per request
* User-level billing

---

# Final Summary

TraceMind demonstrates a production-style AI infrastructure platform focused on:

* scalable LLM integrations
* observability and telemetry
* streaming inference systems
* memory optimization
* async ingestion pipelines
* token usage tracking
* monitoring and analytics

The architecture is intentionally designed to balance:

* scalability
* cost efficiency
* developer experience
* operational simplicity
* production readiness
