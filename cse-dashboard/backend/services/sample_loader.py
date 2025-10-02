from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "samples"


def load_sample(name: str) -> Any:
    path = DATA_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Sample {name} introuvable")
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)
