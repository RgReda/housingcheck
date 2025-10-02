from __future__ import annotations

import logging
import random
from datetime import datetime

from sqlmodel import Session, select

from db.session import engine
from models import Cours, Valeur

logger = logging.getLogger(__name__)


class IntradaySimulator:
    """Simule des cours intraday différés lorsque les flux temps réel sont indisponibles."""

    def run(self) -> int:
        with Session(engine) as session:
            valeurs = session.exec(select(Valeur)).all()
            count = 0
            for valeur in valeurs:
                latest = session.exec(
                    select(Cours)
                    .where(Cours.valeur_id == valeur.id)
                    .order_by(Cours.date.desc())
                    .limit(1)
                ).first()
                if not latest or latest.close is None:
                    continue
                simulated_close = latest.close * (1 + random.uniform(-0.01, 0.01))
                latest.close = round(simulated_close, 2)
                latest.updated_at = datetime.utcnow()
                session.add(latest)
                count += 1
            session.commit()
        logger.info("Simulation intraday exécutée", extra={"count": count})
        return count
