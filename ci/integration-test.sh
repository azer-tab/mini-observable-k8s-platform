#!/usr/bin/env bash
# ci/integration-test.sh
# ---------------------------------------------------------------------------
# Spin up the full stack via Docker Compose, wait for it to be healthy,
# then run a series of smoke tests against the API.
# ---------------------------------------------------------------------------
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
RETRIES=30
SLEEP=2

echo "==> Starting stack..."
docker compose up -d --build

echo "==> Waiting for API to become ready..."
for i in $(seq 1 "$RETRIES"); do
  if curl -sf "${API_URL}/healthz" > /dev/null 2>&1; then
    echo "    API is up after ${i} attempts."
    break
  fi
  if [ "$i" -eq "$RETRIES" ]; then
    echo "ERROR: API did not become healthy in time."
    docker compose logs api
    docker compose down -v
    exit 1
  fi
  sleep "$SLEEP"
done

echo "==> Running smoke tests..."

# --- /healthz ---
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/healthz")
[ "$STATUS" -eq 200 ] && echo "  [PASS] GET /healthz → 200" || { echo "  [FAIL] GET /healthz → $STATUS"; exit 1; }

# --- /readyz ---
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/readyz")
[ "$STATUS" -eq 200 ] && echo "  [PASS] GET /readyz → 200" || { echo "  [FAIL] GET /readyz → $STATUS"; exit 1; }

# --- /metrics ---
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/metrics")
[ "$STATUS" -eq 200 ] && echo "  [PASS] GET /metrics → 200" || { echo "  [FAIL] GET /metrics → $STATUS"; exit 1; }

# --- POST /items ---
ITEM=$(curl -sf -X POST "${API_URL}/items" \
  -H "Content-Type: application/json" \
  -d '{"name":"integration-test-item","description":"created by CI"}')
ITEM_ID=$(echo "$ITEM" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "  [PASS] POST /items → id=${ITEM_ID}"

# --- GET /items ---
COUNT=$(curl -sf "${API_URL}/items" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")
[ "$COUNT" -ge 1 ] && echo "  [PASS] GET /items → ${COUNT} item(s)" || { echo "  [FAIL] GET /items returned 0 items"; exit 1; }

# --- GET /items/{id} ---
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/items/${ITEM_ID}")
[ "$STATUS" -eq 200 ] && echo "  [PASS] GET /items/${ITEM_ID} → 200" || { echo "  [FAIL] GET /items/${ITEM_ID} → $STATUS"; exit 1; }

# --- GET /simulate-error ---
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}/simulate-error")
[ "$STATUS" -eq 500 ] && echo "  [PASS] GET /simulate-error → 500" || { echo "  [FAIL] GET /simulate-error → $STATUS"; exit 1; }

echo ""
echo "==> All integration tests passed."
echo "==> Tearing down stack..."
docker compose down -v
