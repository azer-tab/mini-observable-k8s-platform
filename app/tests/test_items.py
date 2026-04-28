"""Tests for /items CRUD endpoints using an in-memory SQLite database."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# ── In-memory SQLite override ─────────────────────────────────────────────────
SQLITE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_create_item():
    response = client.post("/items", json={"name": "widget", "description": "a test item"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "widget"
    assert data["description"] == "a test item"
    assert "id" in data


def test_list_items_empty():
    response = client.get("/items")
    assert response.status_code == 200
    assert response.json() == []


def test_list_items_after_create():
    client.post("/items", json={"name": "foo"})
    client.post("/items", json={"name": "bar"})
    response = client.get("/items")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_item_by_id():
    create = client.post("/items", json={"name": "thing"})
    item_id = create.json()["id"]
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "thing"


def test_get_item_not_found():
    response = client.get("/items/99999")
    assert response.status_code == 404


def test_simulate_error():
    response = client.get("/simulate-error")
    assert response.status_code == 500


def test_simulate_latency():
    response = client.get("/simulate-latency")
    assert response.status_code == 200
