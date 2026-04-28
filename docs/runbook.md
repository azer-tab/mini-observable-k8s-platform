# Operations Runbook

## Deploying a New Version

```bash
# 1. Build and push the image (done by CI on merge to main)
docker build -t ghcr.io/<org>/mini-observable-k8s-platform:v1.2.3 \
  -f docker/Dockerfile .
docker push ghcr.io/<org>/mini-observable-k8s-platform:v1.2.3

# 2. Update the image tag in k8s/api-deployment.yaml, then apply
kubectl set image deployment/api api=ghcr.io/<org>/mini-observable-k8s-platform:v1.2.3 -n platform

# 3. Monitor the rollout
kubectl rollout status deployment/api -n platform
```

---

## Rolling Back

```bash
# Undo the last deployment
kubectl rollout undo deployment/api -n platform

# Check rollout history
kubectl rollout history deployment/api -n platform

# Roll back to a specific revision
kubectl rollout undo deployment/api --to-revision=3 -n platform
```

---

## Scaling

```bash
# Manual scale
kubectl scale deployment/api --replicas=3 -n platform

# View HPA status
kubectl get hpa -n platform

# Disable HPA temporarily
kubectl delete hpa api-hpa -n platform
```

---

## Restarting Services

```bash
# Rolling restart (zero downtime)
kubectl rollout restart deployment/api -n platform
kubectl rollout restart deployment/postgres -n platform
```

---

## Viewing Logs

```bash
# Live logs from all API pods
kubectl logs -l app=api -n platform -f

# Previous container logs (after crash)
kubectl logs <pod-name> -n platform --previous

# Filter for errors
kubectl logs -l app=api -n platform | grep -i error
```

---

## Database Operations

```bash
# Connect to Postgres
kubectl exec -it $(kubectl get pod -l app=postgres -n platform -o jsonpath='{.items[0].metadata.name}') \
  -n platform -- psql -U appuser -d appdb

# Backup (example; use proper tooling in production)
kubectl exec -it <postgres-pod> -n platform -- \
  pg_dump -U appuser appdb > backup-$(date +%Y%m%d).sql
```

---

## Checking Cluster Health

```bash
# Nodes
kubectl get nodes

# All resources in namespace
kubectl get all -n platform

# Events (useful for debugging)
kubectl get events -n platform --sort-by='.lastTimestamp'

# Resource usage
kubectl top pods -n platform
kubectl top nodes
```

---

## Prometheus / Grafana Access (Kubernetes)

```bash
# Port-forward Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n monitoring

# Port-forward Grafana
kubectl port-forward svc/grafana 3000:3000 -n monitoring
```

---

## Verifying Alerts

```bash
# Trigger the HighErrorRate alert
for i in $(seq 1 50); do curl -s http://localhost:8000/simulate-error > /dev/null; done

# Trigger the HighLatency alert
curl http://localhost:8000/simulate-latency

# Check active alerts in Prometheus
open http://localhost:9090/alerts
```
