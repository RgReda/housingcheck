from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select

from db.deps import get_session
from models import Alerte
from schemas import AlerteCreate, AlerteRead

router = APIRouter()


@router.post("/alertes", response_model=AlerteRead)
def create_alerte(payload: AlerteCreate, session=Depends(get_session)):
    alerte = Alerte(**payload.dict())
    session.add(alerte)
    session.commit()
    session.refresh(alerte)
    return AlerteRead.from_orm(alerte)


@router.get("/alertes", response_model=list[AlerteRead])
def list_alertes(session=Depends(get_session)):
    alertes = session.exec(select(Alerte)).all()
    return [AlerteRead.from_orm(a) for a in alertes]


@router.delete("/alertes/{alerte_id}")
def delete_alerte(alerte_id: int, session=Depends(get_session)):
    alerte = session.get(Alerte, alerte_id)
    if not alerte:
        raise HTTPException(status_code=404, detail="Alerte introuvable")
    session.delete(alerte)
    session.commit()
    return {"status": "deleted"}
