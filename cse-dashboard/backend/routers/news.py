from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlmodel import select

from db.deps import get_session
from models import News
from schemas import NewsRead

router = APIRouter()


@router.get("/news", response_model=list[NewsRead])
def list_news(
    source: str | None = Query(default=None),
    ticker: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    session=Depends(get_session),
):
    query = select(News)
    if source:
        query = query.where(News.source == source)
    if ticker:
        query = query.where(News.tickers.contains(ticker))
    if date_from:
        query = query.where(News.published_at >= date_from)
    query = query.order_by(News.published_at.desc())
    items = session.exec(query).all()
    return [
        NewsRead(
            id=item.id,
            source=item.source,
            titre=item.titre,
            url=item.url,
            resume=item.resume,
            published_at=item.published_at,
            tickers=item.tickers.split(",") if item.tickers else [],
            news_impact_score=item.news_impact_score,
        )
        for item in items
    ]
