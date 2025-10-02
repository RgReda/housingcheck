from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field

from .base import TimeStampedModel


class Alerte(TimeStampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    utilisateur: str = Field(default="default")
    cible: str = Field(description="ticker ou indice")
    condition: str = Field(description="prix|variation|volume|news|momentum")
    seuil: float | None = None
    mot_cle: str | None = None
    canal: str = Field(description="email|telegram")
    cooldown_minutes: int = Field(default=60)
    dernier_envoi: datetime | None = None
