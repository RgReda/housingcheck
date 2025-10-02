from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.config import get_settings
from core.logging import configure_logging
from db.session import create_all, engine
from jobs.scheduler import configure_jobs
from services.seeding import seed_from_samples
from routers import indices, news, opcvm, valeurs, alertes, palmares, maintenance

configure_logging()
logger = logging.getLogger(__name__)
settings = get_settings()

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
scheduler = AsyncIOScheduler(timezone=settings.scheduler_timezone)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application lifespan")
    create_all()
    seed_from_samples()
    if settings.environment != "test":
        configure_jobs(scheduler)
        scheduler.start()
    try:
        yield
    finally:
        if settings.environment != "test":
            logger.info("Shutting down scheduler")
            scheduler.shutdown(wait=False)


def create_app() -> FastAPI:
    app = FastAPI(
        title="CSE Dashboard API",
        description="API pour le tableau de bord personnel Bourse de Casablanca",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/data", StaticFiles(directory=DATA_DIR, html=False), name="data")

    app.include_router(indices.router, prefix="/api", tags=["indices"])
    app.include_router(valeurs.router, prefix="/api", tags=["valeurs"])
    app.include_router(news.router, prefix="/api", tags=["news"])
    app.include_router(opcvm.router, prefix="/api", tags=["opcvm"])
    app.include_router(alertes.router, prefix="/api", tags=["alertes"])
    app.include_router(palmares.router, prefix="/api", tags=["palmares"])
    app.include_router(maintenance.router, prefix="/api", tags=["maintenance"])

    return app


app = create_app()
