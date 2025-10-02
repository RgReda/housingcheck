from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlmodel import select

from db.deps import get_session
from models import Palmares
from schemas import PalmaresItem

router = APIRouter()


@router.get("/palmares", response_model=list[PalmaresItem])
def list_palmares(limit: int = Query(default=5), session=Depends(get_session)):
    query = (
        select(Palmares)
        .order_by(Palmares.date.desc(), Palmares.variation_pct.desc())
        .limit(limit * 2)
    )
    items = session.exec(query).all()
    return [
        PalmaresItem(
            date=item.date,
            type=item.type,
            ticker=item.ticker,
            nom=item.nom,
            variation_pct=item.variation_pct,
            volume=item.volume,
        )
        for item in items
    ]
