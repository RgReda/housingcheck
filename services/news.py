"""News aggregation utilities for Moroccan financial media."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List

import feedparser

DEFAULT_FEEDS = {
    "Médias24": "https://medias24.com/feed/",
    "L'Economiste": "https://www.leconomiste.com/rss-leconomiste/4173",
    "Boursenews": "https://boursenews.ma/rss",
    "Le Desk": "https://ledesk.ma/feed/",
}


@dataclass
class NewsItem:
    source: str
    title: str
    link: str
    published: datetime | None


class NewsAggregator:
    """Aggregates a curated list of RSS feeds."""

    def __init__(self, feeds: Iterable[tuple[str, str]] | None = None) -> None:
        self.feeds = list(feeds) if feeds else list(DEFAULT_FEEDS.items())

    def fetch(self, limit: int = 20) -> List[NewsItem]:
        items: List[NewsItem] = []
        for source, url in self.feeds:
            parsed = feedparser.parse(url)
            for entry in parsed.entries[: limit // max(len(self.feeds), 1) + 1]:
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                items.append(
                    NewsItem(
                        source=source,
                        title=getattr(entry, "title", ""),
                        link=getattr(entry, "link", ""),
                        published=published,
                    )
                )
        # Sort by publication date descending when available.
        items.sort(key=lambda item: item.published or datetime.min, reverse=True)
        return items[:limit]


news_aggregator = NewsAggregator()
