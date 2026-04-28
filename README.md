# Mini Observable Kubernetes Platform

A production-inspired, interview-ready DevOps project built around a simple FastAPI backend.  
It demonstrates Docker, Kubernetes, CI/CD, Prometheus monitoring, Grafana dashboards, alerting, and SRE documentation — all in one cohesive repository.

---

## Repository Structure

```
mini-observable-k8s-platform/
├── app/                        # FastAPI application
│   ├── main.py                 # Routes, middleware, Prometheus metrics
│   ├── database.py             # SQLAlchemy engine + session
│   ├── models.py               # ORM model + Pydantic schemas
│   ├── requirements.txt
│   └── tests/
│       ├── test_health.py      # Unit tests for health endpoints
│       └── test_items.py       # Unit tests for CRUD endpoints (SQLite)
├── docker/
│   └── Dockerfile              # Multi-stage, non-root runtime image
├── k8s/                        # Kubernetes plain YAML manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.example.yaml
│   ├── postgres-deployment.yaml
│   ├── postgres-service.yaml
│   ├── api-deployment.yaml
│   ├── api-service.yaml
│   ├── api-hpa.yaml
│   └── ingress.yaml
├── monitoring/
│   ├── prometheus.yaml         # Scrape config + rule_files reference
│   ├── alert-rules.yaml        # ApiDown / HighErrorRate / HighLatency
│   └── grafana-dashboard.json  # Importable dashboard
├── ci/
│   └── integration-test.sh     # Compose-based smoke tests
├── docs/
│   ├── architecture.md
│   ├── deployment.md
│   ├── observability.md
│   ├── incident-response.md
│   └── runbook.md
├── .github/workflows/ci.yml    # Test → Build → Validate K8s → Integration
├── docker-compose.yml          # API + PostgreSQL + Prometheus + Grafana
├── Makefile                    # Convenience targets
├── flake.nix                   # Optional Nix dev shell
└── LICENSE
```

---

## Quick Start (Docker Compose)

```bash
# Clone the repo
git clone https://github.com/azer-optim/mini-observable-k8s-platform.git
cd mini-observable-k8s-platform

# Start everything
make up

# Or directly:
docker compose up -d --build
```

| Service    | URL |
|------------|-----|
| API docs   | http://localhost:8000/docs |
| Healthz    | http://localhost:8000/healthz |
| Metrics    | http://localhost:8000/metrics |
| Prometheus | http://localhost:9090 |
| Grafana    | http://localhost:3000 (admin / admin) |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Liveness probe |
| GET | `/readyz` | Readiness probe (checks DB) |
| GET | `/metrics` | Prometheus metrics |
| POST | `/items` | Create an item |
| GET | `/items` | List all items |
| GET | `/items/{id}` | Get item by ID |
| GET | `/simulate-error` | Force a 500 (chaos testing) |
| GET | `/simulate-latency` | Add 2 s delay (latency testing) |

---

## Running Tests

```bash
# Unit tests (no DB required)
make test

# Integration tests (requires Docker)
make integration-test
```

---

## Kubernetes Deployment (kind / minikube)

```bash
# Create a local cluster
kind create cluster --name platform

# Apply all manifests
kubectl apply -f k8s/

# Check status
kubectl get all -n platform

# Access the API
kubectl port-forward svc/api 8080:80 -n platform
curl http://localhost:8080/healthz
```

See [docs/deployment.md](docs/deployment.md) for full instructions including rollbacks and Ingress setup.

---

## Monitoring

- **Prometheus** scrapes `/metrics` every 15 seconds.
- **Alert rules** in `monitoring/alert-rules.yaml`:
  - `ApiDown` – API unreachable for 1 minute
  - `HighErrorRate` – 5xx rate > 5% for 2 minutes
  - `HighLatency` – p95 latency > 1 s for 2 minutes
- **Grafana dashboard** – import `monitoring/grafana-dashboard.json`.

See [docs/observability.md](docs/observability.md) for PromQL queries and chaos testing steps.

---

## CI/CD (GitHub Actions)

`.github/workflows/ci.yml` runs on every push and PR:

1. **Unit tests** – pytest with SQLite, no external dependencies.
2. **Docker build** – multi-stage build; pushed to GHCR on `main`.
3. **K8s validation** – `kubectl apply --dry-run=client` on all manifests.
4. **Integration tests** – full Docker Compose stack, smoke-tested with `curl`.

---

## Nix Development Shell (optional)

```bash
nix develop   # enters a shell with Python, kubectl, kind, Docker, make, curl, jq
```

---

## Documentation

| Document | Purpose |
|----------|---------|
| [architecture.md](docs/architecture.md) | System diagram, component overview, design decisions |
| [deployment.md](docs/deployment.md) | Local and Kubernetes deployment instructions |
| [observability.md](docs/observability.md) | Metrics, dashboards, alerts, chaos testing |
| [incident-response.md](docs/incident-response.md) | Severity levels, incident playbooks |
| [runbook.md](docs/runbook.md) | Day-2 operations: scale, rollback, logs, DB access |

---

## Design Decisions

| Choice | Reason |
|--------|--------|
| **FastAPI** | Async-native, automatic OpenAPI docs, fast to test with `TestClient` |
| **SQLAlchemy** | Clean ORM abstraction; SQLite override makes unit tests DB-free |
| **prometheus-client** | Zero-dependency, built-in histogram for latency percentiles |
| **Multi-stage Dockerfile** | Build deps excluded from runtime image; non-root user by default |
| **Plain Kubernetes YAML** | No Helm/Kustomize – every manifest is self-explanatory |
| **HPA on CPU** | Realistic autoscaling; can extend to custom metrics |
| **GitHub Actions** | Native to GitHub, no extra CI infrastructure needed |
| **Docker Compose for local dev** | Single command to start the full stack including monitoring |

---

## Interview Talking Points

> Use these to explain the project during a DevOps/SRE interview.

1. **Observability first** – Every request is measured by a Prometheus `Counter` and `Histogram`. The dashboard and alert rules are written before the application is "done".

2. **Health vs. readiness** – `/healthz` (liveness) checks only that the process is alive. `/readyz` (readiness) checks that the database connection works — preventing traffic from reaching a pod that cannot serve it.

3. **Non-root containers** – The Dockerfile uses a non-root user and a minimal `python:3.12-slim` base. This reduces the attack surface without any runtime complexity.

4. **Zero-downtime rollbacks** – `kubectl rollout undo` leverages the Deployment revision history. The HPA ensures multiple replicas are always running during a rollout.

5. **Testing pyramid** – Unit tests use SQLite to avoid any external dependency. Integration tests use Docker Compose to test the real stack end-to-end. Both run in CI.

6. **Alert fatigue awareness** – Three meaningful alerts (down, error rate, latency) with clear `for` windows to prevent flapping. Each alert has a corresponding runbook entry.

7. **Infrastructure as Code mindset** – Everything is in version control: manifests, alert rules, dashboard JSON, CI pipeline. Nothing is clicked in a UI.

---

## Local Testing Checklist

Before pushing to GitHub, verify:

- [ ] `make up` starts all four services without errors
- [ ] `curl http://localhost:8000/healthz` returns `{"status":"ok"}`
- [ ] `curl http://localhost:8000/readyz` returns `{"status":"ready"}`
- [ ] `curl -X POST http://localhost:8000/items -H "Content-Type: application/json" -d '{"name":"test"}'` returns a 201
- [ ] `curl http://localhost:8000/metrics` includes `http_requests_total`
- [ ] Prometheus at http://localhost:9090/targets shows the `api` target as UP
- [ ] Grafana dashboard shows data after a few requests
- [ ] `make test` passes all unit tests
- [ ] `kubectl apply --dry-run=client -f k8s/` produces no errors
- [ ] `make down` cleans up volumes

---

## License

[MIT](LICENSE)
