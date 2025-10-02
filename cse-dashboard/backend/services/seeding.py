from __future__ import annotations

import logging
from datetime import datetime

from sqlmodel import Session, select

from db.session import engine
from models import (
    Cours,
    Indice,
    News,
    OPCVM,
    SignalMomentum,
    Valeur,
    ValeurLiquidative,
)
from utils.normalization import parse_decimal
from .sample_loader import load_sample

logger = logging.getLogger(__name__)


def seed_from_samples() -> None:
    data_indices = load_sample("indices.json")
    data_quotes = load_sample("quotes.json")
    data_news = load_sample("news.json")
    data_opcvm = load_sample("opcvm.json")

    with Session(engine) as session:
        for indice in data_indices:
            existing_indice = session.exec(select(Indice).where(Indice.code == indice["code"])).first()
            if existing_indice:
                existing_indice.nom = indice["nom"]
                existing_indice.dernier_niveau = indice["niveau"]
                existing_indice.variation_jour = indice["var_jour"]
                existing_indice.variation_hebdo = indice["var_semaine"]
                existing_indice.variation_mois = indice["var_mois"]
                session.add(existing_indice)
            else:
                session.add(
                    Indice(
                        code=indice["code"],
                        nom=indice["nom"],
                        dernier_niveau=indice["niveau"],
                        variation_jour=indice["var_jour"],
                        variation_hebdo=indice["var_semaine"],
                        variation_mois=indice["var_mois"],
                    )
                )

        for quote in data_quotes:
            valeur = session.exec(select(Valeur).where(Valeur.ticker == quote["ticker"])).first()
            if not valeur:
                valeur = Valeur(
                    ticker=quote["ticker"],
                    nom=quote["nom"],
                    secteur=quote.get("secteur"),
                    flottant=parse_decimal(quote.get("flottant")),
                    legal_delay=True,
                )
                session.add(valeur)
                session.flush()
            cours = Cours(
                valeur_id=valeur.id,
                date=datetime.fromisoformat(quote["date"]).date(),
                open=parse_decimal(quote.get("open")),
                high=parse_decimal(quote.get("high")),
                low=parse_decimal(quote.get("low")),
                close=parse_decimal(quote.get("close")),
                volume=parse_decimal(quote.get("volume")),
                variation_pct=parse_decimal(quote.get("variation_pct")),
            )
            session.add(cours)

        for item in data_news:
            existing_news = session.exec(select(News).where(News.url == item["url"])).first()
            if existing_news:
                existing_news.source = item["source"]
                existing_news.titre = item["titre"]
                existing_news.resume = item.get("resume")
                existing_news.published_at = datetime.fromisoformat(item["published_at"])
                existing_news.tickers = ",".join(item.get("tickers", []))
                existing_news.news_impact_score = item.get("news_impact_score")
                session.add(existing_news)
            else:
                session.add(
                    News(
                        source=item["source"],
                        titre=item["titre"],
                        url=item["url"],
                        resume=item.get("resume"),
                        published_at=datetime.fromisoformat(item["published_at"]),
                        tickers=",".join(item.get("tickers", [])),
                        news_impact_score=item.get("news_impact_score"),
                    )
                )

        for fund in data_opcvm:
            opcvm = session.exec(select(OPCVM).where(OPCVM.code == fund["code"])).first()
            if not opcvm:
                opcvm = OPCVM(
                    code=fund["code"],
                    nom=fund["nom"],
                    categorie=fund["categorie"],
                    societe_gestion=fund.get("societe_gestion"),
                    periodicite_vl=fund.get("periodicite_vl"),
                    extra_data=fund.get("performances", {}),
                )
                session.add(opcvm)
                session.flush()
            else:
                opcvm.nom = fund["nom"]
                opcvm.categorie = fund["categorie"]
                opcvm.societe_gestion = fund.get("societe_gestion")
                opcvm.periodicite_vl = fund.get("periodicite_vl")
                opcvm.extra_data = fund.get("performances", {})
                session.add(opcvm)
            for nav in fund.get("valeurs_liquidatives", []):
                session.add(
                    ValeurLiquidative(
                        opcvm_id=opcvm.id,
                        date=datetime.fromisoformat(nav["date"]).date(),
                        vl=parse_decimal(nav["vl"]),
                        frais_entree=parse_decimal(nav.get("frais_entree")),
                        frais_sortie=parse_decimal(nav.get("frais_sortie")),
                    )
                )

        for signal in load_sample("signals.json"):
            session.merge(
                SignalMomentum(
                    ticker=signal["ticker"],
                    date=datetime.fromisoformat(signal["date"]).date(),
                    momentum_3m=signal.get("momentum_3m"),
                    momentum_6m=signal.get("momentum_6m"),
                    reversal_1w=signal.get("reversal_1w"),
                    adtv=signal.get("adtv"),
                    news_impact_score=signal.get("news_impact_score"),
                    classement=signal.get("classement"),
                )
            )

        session.commit()
        logger.info("Seed complété depuis les échantillons")


if __name__ == "__main__":
    seed_from_samples()
