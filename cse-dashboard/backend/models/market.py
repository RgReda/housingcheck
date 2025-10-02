from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from sqlmodel import Field, SQLModel

from .base import TimeStampedModel


class Indice(TimeStampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True)
    nom: str
    dernier_niveau: float | None = None
    variation_jour: float | None = None
    variation_hebdo: float | None = None
    variation_mois: float | None = None


class Valeur(TimeStampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ticker: str = Field(index=True, unique=True)
    nom: str
    secteur: str | None = None
    flottant: float | None = None
    legal_delay: bool = Field(default=True)


class Cours(TimeStampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    valeur_id: int = Field(foreign_key="valeur.id")
    date: date
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None
    variation_pct: float | None = None


class Palmares(TimeStampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: date = Field(index=True)
    type: str = Field(description="hausses|baisses")
    ticker: str
    nom: str
    variation_pct: float
    volume: float | None = None
