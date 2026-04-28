"""Tests for /healthz and /readyz endpoints."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz_returns_200():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz_returns_200_when_db_alive():
    with patch("app.main.is_db_alive", return_value=True):
        response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readyz_returns_503_when_db_down():
    with patch("app.main.is_db_alive", return_value=False):
        response = client.get("/readyz")
    assert response.status_code == 503


def test_metrics_endpoint_returns_prometheus_text():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
