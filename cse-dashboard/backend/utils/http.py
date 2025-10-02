from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable

import httpx

logger = logging.getLogger(__name__)


async def fetch_json(url: str, *, timeout: int = 10) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        logger.info("Fetch JSON", extra={"url": url})
        return data


def backoff(retries: int = 3, delay: float = 1.0):
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:  # pragma: no cover - network failures
                    logger.warning("Retry", extra={"attempt": attempt + 1, "error": str(exc)})
                    await asyncio.sleep(current_delay)
                    current_delay *= 2
            raise RuntimeError(f"Echec après {retries} tentatives")

        return wrapper

    return decorator
