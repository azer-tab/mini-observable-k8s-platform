"""Database engine and session factory."""

import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://appuser:apppassword@localhost:5432/appdb",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Yield a database session and close it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def is_db_alive() -> bool:
    """Return True when a simple query succeeds."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
