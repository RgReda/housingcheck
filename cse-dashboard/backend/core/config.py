from __future__ import annotations

import functools
import os
from typing import List

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    environment: str = Field("development", env="ENVIRONMENT")
    database_url: str = Field("sqlite:///./cse_dashboard.db", env="DATABASE_URL")
    cors_allow_origins: List[str] = Field(default_factory=lambda: ["*"])
    scheduler_timezone: str = "Europe/Paris"
    smtp_host: str | None = Field(default=None, env="SMTP_HOST")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_user: str | None = Field(default=None, env="SMTP_USER")
    smtp_password: str | None = Field(default=None, env="SMTP_PASSWORD")
    telegram_bot_token: str | None = Field(default=None, env="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str | None = Field(default=None, env="TELEGRAM_CHAT_ID")
    enable_scraping: bool = Field(default=True, env="ENABLE_SCRAPING")
    legal_delay_banner: bool = Field(default=True, env="LEGAL_DELAY_BANNER")
    tradingview_symbols_mapping_file: str = Field(
        default="data/samples/tradingview_symbols.json",
        env="TRADINGVIEW_SYMBOLS_MAPPING_FILE",
    )
    daily_close_pdf_path: str = Field(
        default="data/samples/bulletin_sample.pdf",
        env="DAILY_CLOSE_PDF_PATH",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@functools.lru_cache()
def get_settings() -> Settings:
    return Settings()
