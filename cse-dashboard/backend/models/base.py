from __future__ import annotations

from datetime import datetime

from sqlmodel import SQLModel, Field


class TimeStampedModel(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
