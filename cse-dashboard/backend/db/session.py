from __future__ import annotations

from sqlmodel import SQLModel, create_engine

from core.config import get_settings

settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, echo=False, connect_args=connect_args)


def create_all() -> None:
    SQLModel.metadata.create_all(engine)
