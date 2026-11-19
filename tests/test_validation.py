from datetime import date
from io import StringIO

import pandas as pd
import pytest

from src.ingestion.listings import filter_listings, read_listings
from src.validation.quality import duplicate_candidates, interpretation_guard, validate_frame


@pytest.mark.parametrize(
    "table,column",
    [
        ("rental_listings", "monthly_rent"),
        ("rental_listings", "condominium_fee"),
        ("rental_listings", "iptu_monthly"),
        ("housing_stock", "dwelling_count"),
        ("formal_wages", "employment_relationships"),
        ("wage_distribution", "employment_relationships"),
    ],
)
def test_reject_negatives(seeds, table, column):
    frame = seeds(table)
    frame.loc[0, column] = -1
    with pytest.raises(ValueError):
        validate_frame(table, frame)


def test_unknown_values_remain_null(seeds):
    frame = seeds("rental_listings")
    parsed = read_listings(StringIO(frame.to_csv(index=False)))
    assert parsed["monthly_rent"].notna().all()
    for column in ("agency", "neighborhood", "collected_at", "iptu_monthly"):
        assert parsed[column].isna().all()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"population_claim": True},
        {"cumulative_sum": True},
        {"wage_statistic": "median", "available": False},
    ],
)
def test_interpretation_guard(kwargs):
    with pytest.raises(ValueError):
        interpretation_guard(**kwargs)


def test_duplicate_candidates_do_not_delete(seeds):
    frame = seeds("rental_listings")
    assert duplicate_candidates(frame).empty
    frame["listing_url"] = frame["listing_url"].astype("string")
    frame.loc[:1, "listing_url"] = "https://example.org/repeated"
    assert len(duplicate_candidates(frame)) == 2
    assert len(frame) == 13


def test_duplicate_ids_and_missing_schema(seeds):
    frame = seeds("rental_listings")
    frame.loc[1, "listing_id"] = frame.loc[0, "listing_id"]
    with pytest.raises(ValueError):
        validate_frame("rental_listings", frame)
    with pytest.raises(ValueError):
        validate_frame("rental_listings", frame.drop(columns=["monthly_rent"]))


def test_filters():
    frame = pd.DataFrame(
        {
            "agency": ["A", "A", "B"],
            "property_type": ["Casa", "Apartamento", "Casa"],
            "neighborhood": ["N1", "N2", None],
            "collected_at": ["2025-01-01", "2025-02-01", None],
        }
    )
    assert len(filter_listings(frame, {"agency": ["A"]})) == 2
    assert len(filter_listings(frame, {"property_type": ["Casa"]})) == 2
    assert len(filter_listings(frame, {"neighborhood": ["N2"]})) == 1
    assert len(filter_listings(frame, {}, (date(2025, 1, 1), date(2025, 1, 31)))) == 1
    assert filter_listings(frame, {"agency": ["C"]}).empty


@pytest.mark.parametrize("value", [float("inf"), 1.5])
def test_invalid_counts(seeds, value):
    frame = seeds("housing_stock")
    frame["dwelling_count"] = frame["dwelling_count"].astype(float)
    frame.loc[0, "dwelling_count"] = value
    with pytest.raises(ValueError):
        validate_frame("housing_stock", frame)


def test_request_without_confirmed_submission(seeds):
    frame = seeds("information_requests")
    frame.loc[0] = ["internal", "IBGE", "Teste", None, None, "Rascunho", None, None]
    with pytest.raises(ValueError):
        validate_frame("information_requests", frame)
