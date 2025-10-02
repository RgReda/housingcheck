from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class PalmaresItem(BaseModel):
    date: date
    type: str
    ticker: str
    nom: str
    variation_pct: float
    volume: float | None = None

    class Config:
        orm_mode = True
