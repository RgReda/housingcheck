from __future__ import annotations

from datetime import date
from typing import Optional

from sqlmodel import Field

from .base import TimeStampedModel


class SignalMomentum(TimeStampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ticker: str = Field(index=True)
    date: date
    momentum_3m: float | None = None
    momentum_6m: float | None = None
    reversal_1w: float | None = None
    adtv: float | None = None
    news_impact_score: float | None = None
    classement: str | None = None
