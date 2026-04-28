# Incident Response Guide

## Severity Levels

| Level | Definition | Example |
|-------|-----------|---------|
| SEV-1 | Complete service outage | All API pods crash-looping |
| SEV-2 | Partial degradation | High error rate on one endpoint |
| SEV-3 | Performance issue | Elevated latency, no errors |

---

## Runbook Triggers

| Alert | Runbook |
|-------|---------|
| `ApiDown` | [API is unreachable](#api-is-unreachable) |
| `HighErrorRate` | [High 5xx error rate](#high-5xx-error-rate) |
| `HighLatency` | [High latency](#high-latency) |

---

## API is Unreachable

### Symptoms
- `ApiDown` alert fires.
- `kubectl get pods -n platform` shows pods in `CrashLoopBackOff` or `Error`.

### Steps

1. **Check pod status**
   ```bash
   kubectl get pods -n platform
   kubectl describe pod <pod-name> -n platform
   ```

2. **Check logs**
   ```bash
   kubectl logs -l app=api -n platform --previous
   ```

3. **Check database connectivity**
   ```bash
   kubectl exec -it <api-pod> -n platform -- curl http://localhost:8000/readyz
   ```

4. **Rollback if caused by a recent deployment**
   ```bash
   kubectl rollout undo deployment/api -n platform
   ```

5. **Scale up if needed**
   ```bash
   kubectl scale deployment/api --replicas=3 -n platform
   ```

---

## High 5xx Error Rate

### Symptoms
- `HighErrorRate` alert fires.
- Grafana error-rate panel shows > 5%.

### Steps

1. **Identify failing endpoints**
   ```promql
   rate(http_requests_total{status=~"5.."}[5m]) by (endpoint)
   ```

2. **Check API logs for stack traces**
   ```bash
   kubectl logs -l app=api -n platform --tail=200
   ```

3. **Check database health**
   ```bash
   kubectl exec -it <postgres-pod> -n platform -- psql -U appuser -d appdb -c "SELECT 1"
   ```

4. **If database is the cause**, consider restarting the postgres pod:
   ```bash
   kubectl rollout restart deployment/postgres -n platform
   ```

5. **Rollback API if a recent code change is suspect**
   ```bash
   kubectl rollout undo deployment/api -n platform
   ```

---

## High Latency

### Symptoms
- `HighLatency` alert fires.
- p95 latency > 1 second.

### Steps

1. **Check current replica count and HPA status**
   ```bash
   kubectl get hpa -n platform
   kubectl get pods -n platform
   ```

2. **Check resource saturation**
   ```bash
   kubectl top pods -n platform
   ```

3. **Scale up manually if HPA hasn't acted yet**
   ```bash
   kubectl scale deployment/api --replicas=4 -n platform
   ```

4. **Identify slow queries** – check PostgreSQL slow query log or add `EXPLAIN ANALYZE`.

5. **Review recent changes** – a new query or migration may have introduced a regression.

---

## Post-Incident

After resolving:

1. Document the timeline in a brief incident report.
2. Add/improve alert rules if gaps were found.
3. Add a test to prevent regression.
4. Update this runbook if steps were inaccurate.
