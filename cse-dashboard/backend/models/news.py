from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field

from .base import TimeStampedModel


class News(TimeStampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source: str
    titre: str
    url: str
    resume: str | None = None
    published_at: datetime
    tickers: str | None = Field(default=None, description="Liste séparée par des virgules")
    news_impact_score: float | None = None
