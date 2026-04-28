# Architecture Overview

## System Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                         Kubernetes Cluster                        │
│  namespace: platform                                              │
│                                                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐    │
│  │   Ingress    │───▶│  API Service │───▶│  API Deployment  │    │
│  │ (nginx)      │    │  (ClusterIP) │    │  (2–5 replicas)  │    │
│  └──────────────┘    └──────────────┘    └──────┬───────────┘    │
│                                                  │                │
│                                          ┌───────▼───────────┐   │
│                                          │ Postgres Service   │   │
│                                          │ Postgres Deployment│   │
│                                          └───────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Monitoring (separate namespace or Docker Compose)           │  │
│  │  Prometheus ──scrapes──▶ /metrics on each API pod           │  │
│  │  Grafana ──reads──▶ Prometheus                              │  │
│  └─────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| API       | FastAPI (Python 3.12) | Business logic + health/metrics endpoints |
| Database  | PostgreSQL 16 | Persistent item storage |
| Container | Docker (multi-stage) | Reproducible, minimal image |
| Orchestration | Kubernetes plain YAML | Deployment, scaling, self-healing |
| CI/CD     | GitHub Actions | Test, build, push, validate |
| Metrics   | Prometheus | Time-series scraping and alerting |
| Dashboard | Grafana | Visualization |
| Local dev | Docker Compose | One-command local stack |

## Data Flow

1. Client → Ingress → API Service → API Pod
2. API Pod → PostgreSQL (items CRUD)
3. Prometheus → API Pod `/metrics` (15-second scrape interval)
4. Grafana → Prometheus (dashboard queries)

## Key Design Decisions

- **FastAPI** – async-friendly, built-in OpenAPI docs, easy to test with `TestClient`.
- **SQLAlchemy ORM** – clean separation of DB logic, easy to swap DB engines in tests.
- **prometheus-client** – zero-dependency Prometheus integration; histogram gives latency percentiles.
- **Multi-stage Dockerfile** – build deps do not leak into the runtime image; runs as non-root.
- **Plain Kubernetes YAML** – no Helm or Kustomize; each file is human-readable and self-explanatory.
- **HPA** – scales on CPU utilization; a natural next step is custom metrics.
