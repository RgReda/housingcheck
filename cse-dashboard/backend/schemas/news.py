from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NewsRead(BaseModel):
    id: int
    source: str
    titre: str
    url: str
    resume: str | None = None
    published_at: datetime
    tickers: list[str]
    news_impact_score: float | None = None

    class Config:
        orm_mode = True
