from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select

from db.deps import get_session
from models import Cours, News, Valeur, SignalMomentum
from schemas import ValeurDetail, ValeurList, CoursSerie, NewsItem

router = APIRouter()


@router.get("/valeurs", response_model=list[ValeurList])
def list_valeurs(
    secteur: str | None = Query(default=None),
    liq_min: float | None = Query(default=None, description="ADTV minimum"),
    session=Depends(get_session),
):
    query = select(Valeur)
    if secteur:
        query = query.where(Valeur.secteur == secteur)
    valeurs = session.exec(query).all()

    results: list[ValeurList] = []
    for valeur in valeurs:
        signal = session.exec(
            select(SignalMomentum)
            .where(SignalMomentum.ticker == valeur.ticker)
            .order_by(SignalMomentum.date.desc())
            .limit(1)
        ).first()
        adtv = signal.adtv if signal else None
        if liq_min and (adtv or 0) < liq_min:
            continue
        results.append(
            ValeurList(
                ticker=valeur.ticker,
                nom=valeur.nom,
                secteur=valeur.secteur,
                flottant=valeur.flottant,
                legal_delay=valeur.legal_delay,
                momentum_score=signal.momentum_3m if signal else None,
                adtv=adtv,
                news_impact_score=signal.news_impact_score if signal else None,
            )
        )
    return results


@router.get("/valeurs/{ticker}", response_model=ValeurDetail)
def get_valeur(ticker: str, session=Depends(get_session)):
    valeur = session.exec(select(Valeur).where(Valeur.ticker == ticker)).first()
    if not valeur:
        raise HTTPException(status_code=404, detail="Valeur introuvable")
    cours = (
        session.exec(select(Cours).where(Cours.valeur_id == valeur.id).order_by(Cours.date.desc()))
        .all()
    )
    cours_series = [
        CoursSerie(
            date=entry.date,
            open=entry.open,
            high=entry.high,
            low=entry.low,
            close=entry.close,
            volume=entry.volume,
            variation_pct=entry.variation_pct,
        )
        for entry in cours
    ]
    stats = {
        "momentum_3m": None,
        "momentum_6m": None,
        "reversal_1w": None,
        "adtv": None,
    }
    signal = (
        session.exec(
            select(SignalMomentum)
            .where(SignalMomentum.ticker == ticker)
            .order_by(SignalMomentum.date.desc())
        ).first()
    )
    if signal:
        stats |= {
            "momentum_3m": signal.momentum_3m,
            "momentum_6m": signal.momentum_6m,
            "reversal_1w": signal.reversal_1w,
            "adtv": signal.adtv,
        }

    latest_news_query = select(News).order_by(News.published_at.desc()).limit(5)
    if ticker:
        latest_news_query = latest_news_query.where(News.tickers.contains(ticker))
    latest_news = session.exec(latest_news_query).all()
    news_items = [
        NewsItem(
            titre=item.titre,
            source=item.source,
            url=item.url,
            published_at=item.published_at,
            news_impact_score=item.news_impact_score,
        )
        for item in latest_news
    ]
    return ValeurDetail(
        ticker=valeur.ticker,
        nom=valeur.nom,
        secteur=valeur.secteur,
        flottant=valeur.flottant,
        legal_delay=valeur.legal_delay,
        updated_at=valeur.updated_at,
        cours=cours_series,
        stats=stats,
        correlation_masi=signal.news_impact_score if signal else None,
        latest_news=news_items,
    )
