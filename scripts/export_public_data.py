"""Contrato JSON determinístico. Não cria, altera ou reconstrói o banco."""

import argparse
import hashlib
import json
import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import DATABASE, MUNICIPALITY, QUALITY, ROOT  # noqa: E402
from src.database import query  # noqa: E402

INDICATOR_FIELDS = [
    "indicator_id",
    "indicator_name",
    "category",
    "municipality_code",
    "reference_year",
    "value",
    "unit",
    "source_id",
    "methodology",
    "quality_status",
    "limitations",
    "upstream_status",
    "source_name",
    "source_url",
    "source_notes",
]
SOURCE_FIELDS = [
    "source_id",
    "institution",
    "dataset_name",
    "source_url",
    "reference_year",
    "retrieved_at",
    "methodology_url",
    "notes",
    "status",
]


def _scalar(value):
    if pd.isna(value):
        return None
    if isinstance(value, (datetime, date, pd.Timestamp)):
        return value.date().isoformat() if isinstance(value, datetime) else value.isoformat()
    return value.item() if hasattr(value, "item") else value


def _records(frame):
    return [{key: _scalar(value) for key, value in row.items()} for row in frame.to_dict("records")]


def _encoded(payload):
    return (
        json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def export_public_data(db_path=DATABASE, output_dir=ROOT / "public/data"):
    db_path, output_dir = Path(db_path), Path(output_dir)
    if not db_path.exists():
        raise FileNotFoundError("Banco ausente. Execute scripts/initialize_database.py antes.")
    indicators = query("SELECT * FROM indicator_catalog ORDER BY indicator_id", db_path=db_path)
    sources = query("SELECT * FROM sources ORDER BY source_id", db_path=db_path)
    if not indicators["quality_status"].isin(QUALITY).all():
        raise ValueError("Indicador sem classificação de qualidade conhecida")
    if (
        not indicators["upstream_status"].isin(QUALITY).all()
        or not sources["status"].isin(QUALITY).all()
    ):
        raise ValueError("Fonte sem classificação de qualidade conhecida")
    payloads = {
        "indicators.json": _records(indicators[INDICATOR_FIELDS]),
        "sources.json": _records(sources[SOURCE_FIELDS]),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for filename, payload in payloads.items():
        content = _encoded(payload)
        (output_dir / filename).write_bytes(content)
        hashes[filename] = hashlib.sha256(content).hexdigest()
    manifest = {
        "schema_version": "1.0",
        "application_version": "1.1",
        "municipality": {"code": MUNICIPALITY, "name": "Pato Branco", "state": "PR"},
        "files": hashes,
        "rows": {name: len(rows) for name, rows in payloads.items()},
        "quality_categories": QUALITY,
        "methodology_notes": [
            "Derived não implica fonte verified; preservar upstream_status.",
            "Valores e anos desconhecidos são null, nunca zero ou ano presumido.",
            "Anúncios são amostra exploratória; não estimam o mercado municipal.",
            "Indicadores censitários por posse são subtotais parciais.",
            "Nenhuma informação de autenticação ou registro pessoal é exportada.",
        ],
    }
    (output_dir / "manifest.json").write_bytes(_encoded(manifest))
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DATABASE)
    parser.add_argument("--output", type=Path, default=ROOT / "public/data")
    args = parser.parse_args()
    print(json.dumps(export_public_data(args.database, args.output), ensure_ascii=False, indent=2))
