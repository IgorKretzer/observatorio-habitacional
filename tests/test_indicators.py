import pandas as pd
import pytest

from src.indicators.affordability import simulate_burden
from src.indicators.housing import rental_statistics, tenure_subtotals, total_monthly_cost
from src.indicators.income import annual_changes, cumulative_shares, safe_percentage


@pytest.mark.parametrize("tenure,total", [("Alugado", 10656), ("Próprio", 22290), ("Cedido", 1184)])
def test_partial_tenure_totals(seeds, tenure, total):
    result = tenure_subtotals(seeds("housing_stock"))
    assert result.set_index("tenure_status").loc[tenure, "dwelling_count"] == total
    assert result["year"].eq(2022).all()
    assert result["source_id"].eq("sidra_9928").all()


def test_rental_mean_median(seeds):
    stats = rental_statistics(seeds("rental_listings"))
    assert stats["count"] == 13
    assert stats["mean"] == pytest.approx(2572.3076923076924)
    assert stats["median"] == 2300
    assert stats["min"] == 1400
    assert stats["max"] == 4500


def test_cumulative_percentages(seeds):
    result = cumulative_shares(seeds("wage_distribution"), seeds("formal_wages"))
    assert result["percentage"].tolist() == pytest.approx(
        [20818 / 37323 * 100, 28384 / 37323 * 100]
    )
    assert result["year"].eq(2025).all()
    assert result["source_id"].eq("rais_2025").all()


def test_annual_nominal_changes(seeds):
    frame = annual_changes(seeds("formal_wages"))
    assert pd.isna(frame.iloc[0]["nominal_change_pct"])
    assert frame["nominal_change_pct"].iloc[1:].tolist() == pytest.approx(
        [
            (3692.10 / 3397.25 - 1) * 100,
            (3924.92 / 3692.10 - 1) * 100,
            (4075.06 / 3924.92 - 1) * 100,
        ]
    )
    assert frame["median_wage"].isna().all()
    assert frame["source_id"].tolist() == [f"rais_{year}" for year in range(2022, 2026)]


def test_missing_cost_is_not_zero(seeds):
    result = total_monthly_cost(seeds("rental_listings"))
    assert result["total_monthly_cost"].isna().all()
    complete = pd.DataFrame({"monthly_rent": [1000], "condominium_fee": [0], "iptu_monthly": [50]})
    assert total_monthly_cost(complete)["total_monthly_cost"].iloc[0] == 1050


@pytest.mark.parametrize("numerator,denominator", [(1, 0), (1, None), (None, 1), (1, -1)])
def test_safe_division(numerator, denominator):
    assert safe_percentage(numerator, denominator) is None


def test_missing_tenure_and_empty_rentals(seeds):
    subtotals = tenure_subtotals(seeds("housing_stock")).set_index("tenure_status")
    assert pd.isna(subtotals.loc["Outra condição", "dwelling_count"])
    assert rental_statistics(seeds("rental_listings").iloc[:0])["median"] is None


def test_no_change_across_gap_or_missing(seeds):
    frame = seeds("formal_wages").iloc[[0, 2]].copy()
    assert annual_changes(frame)["nominal_change_pct"].isna().all()
    frame = seeds("formal_wages")
    frame.loc[1, "average_monthly_wage"] = None
    assert annual_changes(frame)["nominal_change_pct"].iloc[:3].isna().all()


def test_simulation_preserves_years_and_warning():
    result = simulate_burden(
        2300,
        4075.06,
        rent_year=None,
        income_year=2025,
        source_ids=["amostra_informada", "rais_2025"],
    )
    assert result["reference_years"] == [None, 2025]
    assert result["source_ids"] == ["amostra_informada", "rais_2025"]
    assert "Anos distintos" in result["warning"]
    assert "Simulação" in result["methodology"]
