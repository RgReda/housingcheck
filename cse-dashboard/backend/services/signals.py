from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date
from statistics import mean

from sqlmodel import Session, select

from db.session import engine
from models import Cours, News, SignalMomentum, Valeur

logger = logging.getLogger(__name__)


class SignalService:
    def run(self) -> int:
        with Session(engine) as session:
            tickers = [valeur.ticker for valeur in session.exec(select(Valeur)).all()]
            count = 0
            for ticker in tickers:
                count += self._compute_for_ticker(session, ticker)
            session.commit()
        logger.info("Signal momentum calculé", extra={"count": count})
        return count

    def _compute_for_ticker(self, session: Session, ticker: str) -> int:
        cours = session.exec(
            select(Cours).where(Cours.valeur.has(Valeur.ticker == ticker)).order_by(Cours.date.desc())
        ).all()
        if not cours:
            return 0
        closes = [c.close for c in cours if c.close]
        if len(closes) < 2:
            return 0
        momentum_3m = self._relative_change(closes, 63)
        momentum_6m = self._relative_change(closes, 126)
        reversal_1w = self._relative_change(closes, 5, inverse=True)
        adtv = mean([c.volume for c in cours[:20] if c.volume]) if cours else None

        news_items = session.exec(
            select(News).where(News.tickers.contains(ticker)).order_by(News.published_at.desc())
        ).all()
        news_impact = min(len(news_items) / 10, 1.0)

        signal = SignalMomentum(
            ticker=ticker,
            date=date.today(),
            momentum_3m=momentum_3m,
            momentum_6m=momentum_6m,
            reversal_1w=reversal_1w,
            adtv=adtv,
            news_impact_score=news_impact,
            classement="top" if (momentum_3m or 0) > 0 and (adtv or 0) > 10000 else "faible",
        )
        session.add(signal)
        return 1

    @staticmethod
    def _relative_change(closes: list[float], window: int, inverse: bool = False) -> float | None:
        if len(closes) <= window:
            return None
        reference = closes[window]
        if not reference:
            return None
        change = (closes[0] - reference) / reference
        return -change if inverse else change
