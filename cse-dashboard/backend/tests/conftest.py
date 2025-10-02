from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("ENVIRONMENT", "test")

ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
for path in (str(ROOT_DIR), str(BACKEND_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

from backend.app import create_app
from backend.core.config import get_settings


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    get_settings().environment = "test"
    app = create_app()
    with TestClient(app) as c:
        yield c
