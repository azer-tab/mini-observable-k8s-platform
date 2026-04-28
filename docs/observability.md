# Observability Guide

## Metrics

The API exposes a Prometheus-compatible `/metrics` endpoint (text/plain format).

### Exported metrics

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total requests, labelled by `method`, `endpoint`, `status` |
| `http_request_duration_seconds` | Histogram | Per-request latency |

### Scrape configuration

`monitoring/prometheus.yaml` configures Prometheus to scrape `api:8000/metrics` every 15 seconds.

In Kubernetes, the pod annotations enable auto-discovery:

```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"
```

---

## Alert Rules

Defined in `monitoring/alert-rules.yaml`.

| Alert | Condition | Severity |
|-------|-----------|----------|
| `ApiDown` | `up{job="api"} == 0` for 1 min | critical |
| `HighErrorRate` | 5xx rate > 5% for 2 min | warning |
| `HighLatency` | p95 latency > 1 s for 2 min | warning |

---

## Grafana Dashboard

Import `monitoring/grafana-dashboard.json` via **Dashboards → Import**:

1. Open Grafana at http://localhost:3000
2. Go to **Dashboards → Import**
3. Upload `monitoring/grafana-dashboard.json`
4. Select the Prometheus datasource

The dashboard shows:
- Request rate per endpoint
- P95 latency per endpoint
- Error rate (5xx / total)
- API up/down status

---

## Querying Prometheus

Open http://localhost:9090 and try:

```promql
# Request rate
rate(http_requests_total[1m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error ratio
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

---

## Chaos Testing

Trigger the alert conditions intentionally:

```bash
# Generate 500 errors
for i in $(seq 1 20); do curl -s http://localhost:8000/simulate-error; done

# Generate high latency
curl http://localhost:8000/simulate-latency
```

Watch Prometheus fire the `HighErrorRate` and `HighLatency` alerts within the `for` window.
