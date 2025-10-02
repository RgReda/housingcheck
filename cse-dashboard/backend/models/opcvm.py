from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field

from .base import TimeStampedModel


class OPCVM(TimeStampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True)
    nom: str
    categorie: str
    societe_gestion: str | None = None
    periodicite_vl: str | None = None
    extra_data: dict | None = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=True),
    )

class ValeurLiquidative(TimeStampedModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    opcvm_id: int = Field(foreign_key="opcvm.id")
    date: date
    vl: float
    frais_entree: float | None = None
    frais_sortie: float | None = None

