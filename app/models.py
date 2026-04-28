"""SQLAlchemy ORM model and Pydantic schemas for items."""

import datetime

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, func

from app.database import Base


# ── ORM ──────────────────────────────────────────────────────────────────────

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1024), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class ItemCreate(BaseModel):
    name: str
    description: str | None = None


class ItemRead(BaseModel):
    id: int
    name: str
    description: str | None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}
