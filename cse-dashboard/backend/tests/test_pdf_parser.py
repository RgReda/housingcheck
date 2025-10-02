from __future__ import annotations

from pathlib import Path

from services.pdf_parser import BulletinParser


def test_bulletin_parser_extracts_tables(tmp_path):
    sample_pdf = Path(__file__).resolve().parents[2] / "data" / "samples" / "bulletin_sample.pdf"
    parser = BulletinParser(sample_pdf)
    tables = parser.parse()
    assert "hausses" in tables
    assert any(row["ticker"].startswith("CSE") for row in tables["hausses"]) or tables["hausses"]
