from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlmodel import select

from db.deps import get_session
from models import Indice
from schemas import IndiceRead

router = APIRouter()


@router.get("/indices", response_model=list[IndiceRead])
def list_indices(session=Depends(get_session)):
    result = session.exec(select(Indice)).all()
    return result
