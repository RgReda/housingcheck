from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class IndiceBase(BaseModel):
    code: str
    nom: str
    dernier_niveau: float | None = None
    variation_jour: float | None = None
    variation_hebdo: float | None = None
    variation_mois: float | None = None


class IndiceRead(IndiceBase):
    updated_at: datetime

    class Config:
        orm_mode = True
