from __future__ import annotations

from typing import Generator

from sqlmodel import Session

from .session import engine


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
