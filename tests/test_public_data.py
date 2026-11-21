import hashlib
import json

from scripts.export_public_data import INDICATOR_FIELDS, SOURCE_FIELDS, export_public_data


def test_export_is_deterministic_and_does_not_write_database(database, tmp_path):
    output = tmp_path / "public"
    original_hash = hashlib.sha256(database.read_bytes()).hexdigest()
    export_public_data(database, output)
    first = {p.name: p.read_bytes() for p in output.glob("*.json")}
    export_public_data(database, output)
    assert {p.name: p.read_bytes() for p in output.glob("*.json")} == first
    assert hashlib.sha256(database.read_bytes()).hexdigest() == original_hash
    manifest = json.loads(first["manifest.json"])
    assert manifest["rows"] == {"indicators.json": 23, "sources.json": 8}
    for name, digest in manifest["files"].items():
        assert hashlib.sha256(first[name]).hexdigest() == digest


def test_export_preserves_values_years_and_quality(database, tmp_path):
    output = tmp_path / "public"
    export_public_data(database, output)
    indicators = json.loads((output / "indicators.json").read_text(encoding="utf-8"))
    indexed = {row["indicator_id"]: row for row in indicators}
    assert indexed["average_monthly_wage_2025"]["value"] == 4075.06
    assert indexed["average_monthly_wage_2025"]["reference_year"] == 2025
    assert indexed["average_monthly_wage_2025"]["source_id"] == "rais_2025"
    assert indexed["rental_amostra_informada_median"]["reference_year"] is None
    assert indexed["median_wage_2025"]["value"] is None
    assert indexed["median_wage_2025"]["quality_status"] == "unavailable"
    assert all(row["upstream_status"] == "pending_source_verification" for row in indicators)
    assert all(set(row) == set(INDICATOR_FIELDS) for row in indicators)
    sources = json.loads((output / "sources.json").read_text(encoding="utf-8"))
    assert all(set(row) == set(SOURCE_FIELDS) for row in sources)
    assert {row["source_id"] for row in indicators} <= {row["source_id"] for row in sources}
    assert [row["indicator_id"] for row in indicators] == sorted(indexed)
