.PHONY: help up down build test integration-test logs \
        k8s-apply k8s-delete k8s-status port-forward lint

# Default target
help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Local development:"
	@echo "  up                  Start full stack (Docker Compose)"
	@echo "  down                Stop and remove containers and volumes"
	@echo "  build               Rebuild Docker images"
	@echo "  logs                Tail API logs"
	@echo ""
	@echo "Testing:"
	@echo "  test                Run unit tests"
	@echo "  integration-test    Run integration tests (requires Docker)"
	@echo ""
	@echo "Kubernetes:"
	@echo "  k8s-apply           Apply all manifests to current kubectl context"
	@echo "  k8s-delete          Delete all manifests from current kubectl context"
	@echo "  k8s-status          Show pod / service status in platform namespace"
	@echo "  port-forward        Port-forward API to localhost:8080"

# ── Docker Compose ────────────────────────────────────────────────────────────
up:
	docker compose up -d --build

down:
	docker compose down -v

build:
	docker compose build

logs:
	docker compose logs -f api

# ── Testing ───────────────────────────────────────────────────────────────────
test:
	pip install -q -r app/requirements.txt
	python -m pytest app/tests/ -v

integration-test:
	bash ci/integration-test.sh

# ── Kubernetes ────────────────────────────────────────────────────────────────
k8s-apply:
	kubectl apply -f k8s/

k8s-delete:
	kubectl delete -f k8s/

k8s-status:
	kubectl get all -n platform

port-forward:
	kubectl port-forward svc/api 8080:80 -n platform
