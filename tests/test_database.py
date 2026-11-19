import json
import shutil

import pandas as pd
import pytest

from src.config import SEEDS
from src.database import initialize_database, query
from src.schemas import SCHEMAS


def test_idempotent_snapshot(database):
    before = {table: query(f"SELECT * FROM {table}", db_path=database) for table in SCHEMAS}
    initialize_database(database)
    for table in SCHEMAS:
        pd.testing.assert_frame_equal(
            before[table], query(f"SELECT * FROM {table}", db_path=database)
        )
    assert len(before["rental_listings"]) == 13
    assert before["information_requests"].empty
    assert (
        json.loads(database.with_suffix(".report.json").read_text(encoding="utf-8"))["rows"][
            "formal_wages"
        ]
        == 4
    )


def test_catalog_and_sql_costs(database):
    catalog = query("SELECT * FROM indicator_catalog", db_path=database).set_index("indicator_id")
    assert catalog.loc["tenure_Alugado", "value"] == 10656
    assert catalog.loc["employment_relationships_2025", "value"] == 37323
    assert catalog.loc["rental_amostra_informada_median", "value"] == 2300
    assert catalog.loc["rental_amostra_informada_count", "value"] == 13
    assert catalog.loc["rental_amostra_informada_mean", "value"] == pytest.approx(2572.30769231)
    assert catalog.loc["occupancy_Vagos", "value"] == 3053
    assert catalog.loc["average_monthly_wage_2025", "value"] == 4075.06
    assert catalog.loc["median_wage_2025", "quality_status"] == "unavailable"
    assert pd.isna(catalog.loc["median_wage_2025", "value"])
    assert pd.isna(catalog.loc["rental_amostra_informada_median", "reference_year"])
    assert catalog["upstream_status"].eq("pending_source_verification").all()
    assert query("SELECT * FROM rental_costs", db_path=database)["total_monthly_cost"].isna().all()


def test_parquet_and_export_provenance(database):
    wages = pd.read_parquet(database.parent / "formal_wages.parquet")
    assert wages["year"].tolist() == [2022, 2023, 2024, 2025]
    export = query("SELECT * FROM export_formal_wages", db_path=database)
    assert export["source_id"].tolist() == [f"rais_{year}" for year in range(2022, 2026)]
    assert export["municipality_code"].eq("4118501").all()
    assert export["source_status"].eq("pending_source_verification").all()
    assert query("SELECT * FROM sources", db_path=database)["retrieved_at"].notna().sum() == 1


@pytest.mark.parametrize("mutation", ["source", "year", "negative", "cumulative", "occupancy"])
def test_rejected_snapshot_preserves_database(database, tmp_path, mutation):
    directory = tmp_path / "bad-seeds"
    shutil.copytree(SEEDS, directory)
    table = {
        "source": "formal_wages",
        "year": "formal_wages",
        "negative": "rental_listings",
        "cumulative": "wage_distribution",
        "occupancy": "occupancy_status",
    }[mutation]
    frame = pd.read_csv(directory / f"{table}.csv")
    if mutation == "source":
        frame.loc[0, "source_id"] = "unknown"
    elif mutation == "year":
        frame.loc[0, "year"] = 2000
    elif mutation == "negative":
        frame.loc[0, "monthly_rent"] = -100
    elif mutation == "cumulative":
        frame.loc[0, "employment_relationships"] = 37000
    else:
        frame.loc[0, "dwelling_count"] = 99999
    frame.to_csv(directory / f"{table}.csv", index=False)
    with pytest.raises(ValueError):
        initialize_database(database, directory)
    assert len(query("SELECT * FROM rental_listings", db_path=database)) == 13
