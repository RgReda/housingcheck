from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlmodel import select

from db.deps import get_session
from models import OPCVM, ValeurLiquidative
from schemas import OPCVMRead, ValeurLiquidativeRead

router = APIRouter()


@router.get("/opcvm", response_model=list[OPCVMRead])
def list_opcvm(
    cat: str | None = Query(default=None),
    ytd_min: float | None = Query(default=None),
    session=Depends(get_session),
):
    query = select(OPCVM)
    if cat:
        query = query.where(OPCVM.categorie == cat)
    items = session.exec(query).all()
    results: list[OPCVMRead] = []
    for item in items:
        navs = session.exec(
            select(ValeurLiquidative)
            .where(ValeurLiquidative.opcvm_id == item.id)
            .order_by(ValeurLiquidative.date.desc())
        ).all()
        nav_read = [
            ValeurLiquidativeRead(
                date=nav.date,
                vl=nav.vl,
                frais_entree=nav.frais_entree,
                frais_sortie=nav.frais_sortie,
            )
            for nav in navs
        ]
        extra = item.extra_data or {}
        performances = {
            "ytd": extra.get("perf_ytd") or extra.get("ytd"),
            "1m": extra.get("perf_1m") or extra.get("1m"),
            "3m": extra.get("perf_3m") or extra.get("3m"),
        }
        if ytd_min and (performances.get("ytd") or 0) < ytd_min:
            continue
        results.append(
            OPCVMRead(
                id=item.id,
                code=item.code,
                nom=item.nom,
                categorie=item.categorie,
                societe_gestion=item.societe_gestion,
                periodicite_vl=item.periodicite_vl,
                performances=performances,
                valeurs_liquidatives=nav_read,
            )
        )
    return results
