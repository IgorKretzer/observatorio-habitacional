import pandas as pd


def safe_percentage(numerator, denominator):
    if pd.isna(numerator) or pd.isna(denominator) or denominator <= 0:
        return None
    return float(numerator) / float(denominator) * 100


def annual_changes(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.sort_values(["municipality_code", "year"]).copy()
    grouped = result.groupby("municipality_code")
    previous = grouped["average_monthly_wage"].shift()
    previous_year = grouped["year"].shift()
    result["nominal_change_pct"] = [
        safe_percentage(current - prior, prior)
        if pd.notna(prior) and year - old_year == 1
        else None
        for current, prior, year, old_year in zip(
            result["average_monthly_wage"], previous, result["year"], previous_year
        )
    ]
    return result


def cumulative_shares(distribution, wages):
    result = distribution.merge(
        wages[["year", "municipality_code", "employment_relationships"]].rename(
            columns={"employment_relationships": "total_relationships"}
        ),
        on=["year", "municipality_code"],
        validate="many_to_one",
    )
    result["percentage"] = [
        safe_percentage(n, d)
        for n, d in zip(result["employment_relationships"], result["total_relationships"])
    ]
    return result
