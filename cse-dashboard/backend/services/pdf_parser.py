from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

import pdfplumber

logger = logging.getLogger(__name__)


class BulletinParser:
    """Parse les bulletins PDF de la cote de la CSE."""

    def __init__(self, pdf_path: str | Path) -> None:
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"Bulletin introuvable: {self.pdf_path}")

    def extract_tables(self) -> dict[str, list[dict[str, str]]]:
        tables: dict[str, list[dict[str, str]]] = {"hausses": [], "baisses": [], "indices": []}
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_table()
                if extracted:
                    header, *rows = extracted
                    header = [h.strip().lower() for h in header]
                    for row in rows:
                        if not row or not row[0]:
                            continue
                        data = {header[i]: (row[i].strip() if row[i] else "") for i in range(len(header))}
                        label = "hausses" if "hausse" in data.get("type", "") else "baisses"
                        if "indice" in data.get("type", "").lower():
                            label = "indices"
                        tables.setdefault(label, []).append(data)
                else:
                    text = page.extract_text() or ""
                    for line in text.splitlines():
                        if ";" not in line:
                            continue
                        parts = [segment.strip() for segment in line.split(";")]
                        if len(parts) < 5:
                            continue
                        data = {
                            "type": parts[0].lower(),
                            "ticker": parts[1],
                            "nom": parts[2],
                            "variation": parts[3],
                            "volume": parts[4],
                        }
                        label = "indices" if "indice" in data["type"] else ("hausses" if "hausse" in data["type"] else "baisses")
                        tables.setdefault(label, []).append(data)
        logger.info("Tables extraites", extra={"tables": list(tables.keys())})
        return tables

    def parse(self) -> dict[str, list[dict[str, str]]]:
        return self.extract_tables()
