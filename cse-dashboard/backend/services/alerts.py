from __future__ import annotations

import logging
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage

import httpx
from sqlmodel import Session, select

from core.config import get_settings
from db.session import engine
from models import Alerte, Cours, News, Valeur

logger = logging.getLogger(__name__)


class AlertDispatcher:
    def __init__(self) -> None:
        self.settings = get_settings()

    def run(self) -> int:
        with Session(engine) as session:
            alertes = session.exec(select(Alerte)).all()
            count = 0
            for alerte in alertes:
                if self._should_fire(alerte, session):
                    self._dispatch(alerte)
                    alerte.dernier_envoi = datetime.utcnow()
                    session.add(alerte)
                    count += 1
            session.commit()
        logger.info("Alertes envoyées", extra={"count": count})
        return count

    def _should_fire(self, alerte: Alerte, session: Session) -> bool:
        if alerte.dernier_envoi:
            delta = datetime.utcnow() - alerte.dernier_envoi
            if delta < timedelta(minutes=alerte.cooldown_minutes):
                return False
        if alerte.condition == "news":
            news = session.exec(
                select(News)
                .where(News.tickers.contains(alerte.cible))
                .order_by(News.published_at.desc())
                .limit(1)
            ).first()
            return bool(news and (not alerte.mot_cle or alerte.mot_cle.lower() in news.titre.lower()))
        cours = session.exec(
            select(Cours)
            .where(Cours.valeur.has(Valeur.ticker == alerte.cible))
            .order_by(Cours.date.desc())
            .limit(1)
        ).first()
        if not cours:
            return False
        if alerte.condition == "prix" and alerte.seuil and cours.close:
            return cours.close >= alerte.seuil
        if alerte.condition == "variation" and alerte.seuil and cours.variation_pct:
            return cours.variation_pct >= alerte.seuil
        if alerte.condition == "volume" and alerte.seuil and cours.volume:
            return cours.volume >= alerte.seuil
        return False

    def _dispatch(self, alerte: Alerte) -> None:
        if alerte.canal == "email":
            self._send_email(alerte)
        elif alerte.canal == "telegram":
            self._send_telegram(alerte)

    def _send_email(self, alerte: Alerte) -> None:
        if not self.settings.smtp_host:
            logger.warning("SMTP non configuré")
            return
        msg = EmailMessage()
        msg["Subject"] = f"Alerte {alerte.cible}"
        msg["From"] = self.settings.smtp_user or "noreply@example.com"
        msg["To"] = self.settings.smtp_user or "user@example.com"
        msg.set_content(f"Condition {alerte.condition} déclenchée pour {alerte.cible}")
        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as smtp:
            if self.settings.smtp_user and self.settings.smtp_password:
                smtp.starttls()
                smtp.login(self.settings.smtp_user, self.settings.smtp_password)
            smtp.send_message(msg)
        logger.info("Email envoyé", extra={"cible": alerte.cible})

    def _send_telegram(self, alerte: Alerte) -> None:
        if not self.settings.telegram_bot_token or not self.settings.telegram_chat_id:
            logger.warning("Telegram non configuré")
            return
        url = f"https://api.telegram.org/bot{self.settings.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": self.settings.telegram_chat_id,
            "text": f"Alerte {alerte.cible}: condition {alerte.condition}",
        }
        try:
            response = httpx.post(url, json=payload, timeout=10)
            response.raise_for_status()
        except httpx.HTTPError as exc:  # pragma: no cover - dépend du réseau
            logger.error("Envoi Telegram échoué", extra={"error": str(exc)})
        else:
            logger.info("Message Telegram envoyé", extra={"cible": alerte.cible})
