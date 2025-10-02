from __future__ import annotations

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.config import get_settings
from services.alerts import AlertDispatcher
from services.daily_close import DailyCloseService
from services.news_ingestion import NewsIngestionService, RSSAdapter
from services.signals import SignalService

logger = logging.getLogger(__name__)


def configure_jobs(scheduler: AsyncIOScheduler) -> None:
    settings = get_settings()

    # Daily close
    scheduler.add_job(
        lambda: DailyCloseService().run(),
        "cron",
        hour=17,
        minute=30,
        timezone=settings.scheduler_timezone,
        id="daily_close",
    )

    # News ingestion every 15 minutes
    async def news_job():
        adapters = [
            RSSAdapter("Medias24", "https://medias24.com/feed"),
            RSSAdapter("LeDesk", "https://ledesk.ma/feed"),
        ]
        await NewsIngestionService(adapters).run()

    scheduler.add_job(lambda: asyncio.create_task(news_job()), "interval", minutes=15, id="news")

    # Signal computation daily
    scheduler.add_job(lambda: SignalService().run(), "cron", hour=18, minute=0, id="signals")

    # Alerts every 5 minutes
    scheduler.add_job(lambda: AlertDispatcher().run(), "interval", minutes=5, id="alerts")

    logger.info("Jobs planifiés")
