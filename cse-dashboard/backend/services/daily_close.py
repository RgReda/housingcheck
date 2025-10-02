from __future__ import annotations

import logging
from datetime import date

from sqlmodel import Session, select

from core.config import get_settings
from db.session import engine
from models import Palmares, Indice
from utils.normalization import parse_decimal
from .pdf_parser import BulletinParser

logger = logging.getLogger(__name__)


class DailyCloseService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def run(self) -> dict[str, int]:
        parser = BulletinParser(self.settings.daily_close_pdf_path)
        tables = parser.parse()
        with Session(engine) as session:
            inserted_palmares = self._save_palmares(session, tables)
            updated_indices = self._update_indices(session, tables)
            session.commit()
        logger.info(
            "Daily close import terminé",
            extra={"palmares": inserted_palmares, "indices": updated_indices},
        )
        return {"palmares": inserted_palmares, "indices": updated_indices}

    def _save_palmares(self, session: Session, tables: dict[str, list[dict[str, str]]]) -> int:
        count = 0
        for label in ("hausses", "baisses"):
            for row in tables.get(label, []):
                palmares = Palmares(
                    date=date.today(),
                    type=label,
                    ticker=row.get("ticker", row.get("symbole", "")).upper(),
                    nom=row.get("nom", row.get("titre", "")),
                    variation_pct=parse_decimal(row.get("variation", row.get("variation %", "0"))),
                    volume=parse_decimal(row.get("volume", "0")),
                )
                session.add(palmares)
                count += 1
        return count

    def _update_indices(self, session: Session, tables: dict[str, list[dict[str, str]]]) -> int:
        count = 0
        for row in tables.get("indices", []):
            code = row.get("ticker", row.get("indice", "")).upper()
            indice = session.exec(select(Indice).where(Indice.code == code)).first()
            if not indice:
                indice = Indice(code=code, nom=row.get("nom", code))
            indice.dernier_niveau = parse_decimal(row.get("niveau", row.get("cours", "0")))
            indice.variation_jour = parse_decimal(row.get("variation", row.get("var%", "0")))
            session.add(indice)
            count += 1
        return count
