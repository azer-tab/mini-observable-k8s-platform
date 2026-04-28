"""
Mini Observable K8s Platform – FastAPI backend.

Endpoints
---------
GET  /healthz            – liveness probe (process alive)
GET  /readyz             – readiness probe (DB reachable)
GET  /metrics            – Prometheus metrics
POST /items              – create an item
GET  /items              – list all items
GET  /items/{id}         – get single item
GET  /simulate-error     – force a 500 (chaos testing)
GET  /simulate-latency   – add artificial delay (latency testing)
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db, is_db_alive
from app.models import Item, ItemCreate, ItemRead

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── Lifespan: create tables on startup ───────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ensured.")
    yield


# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(title="Mini Observable K8s Platform", version="1.0.0", lifespan=lifespan)

# ── Prometheus metrics ────────────────────────────────────────────────────────
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
)

# ── Middleware: record every request ─────────────────────────────────────────
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start

    endpoint = request.url.path
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status=response.status_code,
    ).inc()
    REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(duration)
    return response


# ── Health endpoints ──────────────────────────────────────────────────────────
@app.get("/healthz", tags=["health"])
def healthz():
    """Liveness probe – returns 200 as long as the process is running."""
    return {"status": "ok"}


@app.get("/readyz", tags=["health"])
def readyz():
    """Readiness probe – returns 200 only when the DB is reachable."""
    if not is_db_alive():
        raise HTTPException(status_code=503, detail="database unreachable")
    return {"status": "ready"}


# ── Metrics endpoint ──────────────────────────────────────────────────────────
@app.get("/metrics", tags=["observability"])
def metrics():
    """Expose Prometheus metrics in text format."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ── Items endpoints ───────────────────────────────────────────────────────────
@app.post("/items", response_model=ItemRead, status_code=201, tags=["items"])
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    """Create a new item and persist it to PostgreSQL."""
    item = Item(name=payload.name, description=payload.description)
    db.add(item)
    db.commit()
    db.refresh(item)
    logger.info("Created item id=%s name=%s", item.id, item.name)
    return item


@app.get("/items", response_model=list[ItemRead], tags=["items"])
def list_items(db: Session = Depends(get_db)):
    """Return all items."""
    return db.query(Item).all()


@app.get("/items/{item_id}", response_model=ItemRead, tags=["items"])
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Return a single item by ID."""
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="item not found")
    return item


# ── Chaos / testing helpers ───────────────────────────────────────────────────
@app.get("/simulate-error", tags=["chaos"])
def simulate_error():
    """Always returns HTTP 500 – useful for testing alert rules."""
    raise HTTPException(status_code=500, detail="simulated error")


@app.get("/simulate-latency", tags=["chaos"])
def simulate_latency():
    """Sleeps for 2 seconds – useful for testing latency alerts."""
    time.sleep(2)
    return {"status": "slow response"}
