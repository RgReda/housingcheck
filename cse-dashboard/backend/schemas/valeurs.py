from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class CoursSerie(BaseModel):
    date: date
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None
    variation_pct: float | None = None


class ValeurBase(BaseModel):
    ticker: str
    nom: str
    secteur: str | None = None
    flottant: float | None = None
    legal_delay: bool = True


class ValeurList(ValeurBase):
    momentum_score: float | None = None
    adtv: float | None = None
    news_impact_score: float | None = None


class ValeurDetail(ValeurBase):
    updated_at: datetime
    cours: List[CoursSerie]
    stats: dict[str, float | None]
    correlation_masi: float | None = None
    latest_news: List["NewsItem"]

    class Config:
        orm_mode = True


class NewsItem(BaseModel):
    titre: str
    source: str
    url: str
    published_at: datetime
    news_impact_score: float | None = None


ValeurDetail.update_forward_refs(NewsItem=NewsItem)
