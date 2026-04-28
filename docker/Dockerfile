# ── Build stage ───────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install dependencies into a local prefix so we can copy only what we need
COPY app/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim

# Non-root user for security
RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY app/ .

# Drop to non-root
USER app

EXPOSE 8000

# Uvicorn with a single worker is fine for a demo; adjust in production
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
