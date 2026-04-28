# Deployment Guide

## Local Development (Docker Compose)

### Prerequisites

- Docker 24+
- Docker Compose v2

### Start the full stack

```bash
# Build images and start all services in the background
docker compose up -d --build

# Tail logs
docker compose logs -f api

# Stop everything and remove volumes
docker compose down -v
```

### Useful URLs

| Service    | URL                        |
|------------|----------------------------|
| API docs   | http://localhost:8000/docs |
| Healthz    | http://localhost:8000/healthz |
| Metrics    | http://localhost:8000/metrics |
| Prometheus | http://localhost:9090      |
| Grafana    | http://localhost:3000 (admin / admin) |

---

## Kubernetes Deployment (kind or minikube)

### Prerequisites

- `kubectl`
- `kind` or `minikube`

### 1. Create a local cluster

```bash
# kind
kind create cluster --name platform

# minikube
minikube start
```

### 2. Create the namespace and apply manifests

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.example.yaml   # copy & customise before applying
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/api-service.yaml
kubectl apply -f k8s/api-hpa.yaml
```

Or apply the whole directory at once:

```bash
kubectl apply -f k8s/
```

### 3. Check pod status

```bash
kubectl get pods -n platform
kubectl describe pod <pod-name> -n platform
```

### 4. Access the API

```bash
# Port-forward the service
kubectl port-forward svc/api 8080:80 -n platform
curl http://localhost:8080/healthz
```

### 5. Enable the Ingress (kind)

```bash
# Install the nginx ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Apply the ingress resource
kubectl apply -f k8s/ingress.yaml

# Add to /etc/hosts
echo "127.0.0.1 api.local" | sudo tee -a /etc/hosts
curl http://api.local/healthz
```

### 6. View logs

```bash
kubectl logs -l app=api -n platform --tail=50 -f
```

### 7. Rollback a deployment

```bash
# See revision history
kubectl rollout history deployment/api -n platform

# Roll back to the previous revision
kubectl rollout undo deployment/api -n platform

# Roll back to a specific revision
kubectl rollout undo deployment/api -n platform --to-revision=2
```

---

## CI/CD

The GitHub Actions workflow at `.github/workflows/ci.yml`:

1. Runs unit tests on every push / PR.
2. Builds and pushes the Docker image to GHCR on pushes to `main`.
3. Validates Kubernetes manifests via `kubectl apply --dry-run=client`.
4. Runs integration tests (Docker Compose stack) on pushes to `main`.

The image is tagged `latest` and `sha-<short-sha>` on every merge.
