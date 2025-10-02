from __future__ import annotations

import logging
from datetime import datetime
from typing import Iterable, List

import httpx
from bs4 import BeautifulSoup
from sqlmodel import Session

from core.config import get_settings
from db.session import engine
from models import News

logger = logging.getLogger(__name__)


class BaseNewsAdapter:
    source: str

    async def fetch(self) -> list[dict[str, str]]:
        raise NotImplementedError


class RSSAdapter(BaseNewsAdapter):
    def __init__(self, source: str, url: str) -> None:
        self.source = source
        self.url = url

    async def fetch(self) -> list[dict[str, str]]:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(self.url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "xml")
        items: list[dict[str, str]] = []
        for item in soup.find_all("item"):
            items.append(
                {
                    "titre": item.title.text if item.title else "",
                    "url": item.link.text if item.link else "",
                    "resume": item.description.text if item.description else "",
                    "published_at": item.pubDate.text if item.pubDate else datetime.utcnow().isoformat(),
                }
            )
        return items


class NewsIngestionService:
    def __init__(self, adapters: Iterable[BaseNewsAdapter]) -> None:
        self.adapters = list(adapters)
        self.settings = get_settings()

    async def run(self) -> int:
        if not self.settings.enable_scraping:
            logger.warning("Scraping désactivé")
            return 0
        stored = 0
        for adapter in self.adapters:
            try:
                items = await adapter.fetch()
            except Exception as exc:  # pragma: no cover - dépend du réseau
                logger.error("Ingestion news échouée", extra={"source": adapter.source, "error": str(exc)})
                continue
            stored += self._persist(adapter.source, items)
        return stored

    def _persist(self, source: str, items: List[dict[str, str]]) -> int:
        with Session(engine) as session:
            count = 0
            for item in items:
                published_at = self._parse_date(item.get("published_at"))
                news = News(
                    source=source,
                    titre=item.get("titre", ""),
                    url=item.get("url", ""),
                    resume=item.get("resume"),
                    published_at=published_at,
                    tickers=",".join(item.get("tickers", [])) if item.get("tickers") else None,
                    news_impact_score=item.get("news_impact_score"),
                )
                session.add(news)
                count += 1
            session.commit()
        return count

    @staticmethod
    def _parse_date(value: str | None) -> datetime:
        if not value:
            return datetime.utcnow()
        for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        return datetime.utcnow()
