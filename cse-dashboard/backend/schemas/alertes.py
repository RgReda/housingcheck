from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class AlerteCreate(BaseModel):
    cible: str
    condition: str
    seuil: float | None = None
    mot_cle: str | None = None
    canal: str = Field(regex="^(email|telegram)$")
    cooldown_minutes: int = 60


class AlerteRead(AlerteCreate):
    id: int
    utilisateur: str
    dernier_envoi: datetime | None = None

    class Config:
        orm_mode = True
