from __future__ import annotations

from datetime import date
from typing import List

from pydantic import BaseModel


class ValeurLiquidativeRead(BaseModel):
    date: date
    vl: float
    frais_entree: float | None = None
    frais_sortie: float | None = None


class OPCVMRead(BaseModel):
    id: int
    code: str
    nom: str
    categorie: str
    societe_gestion: str | None = None
    periodicite_vl: str | None = None
    performances: dict[str, float | None]
    valeurs_liquidatives: List[ValeurLiquidativeRead]

    class Config:
        orm_mode = True
