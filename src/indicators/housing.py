import pandas as pd


def tenure_subtotals(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.groupby(
        ["year", "municipality_code", "tenure_status", "source_id"], as_index=False
    )["dwelling_count"].agg(lambda values: values.sum(min_count=len(values)))


def rental_statistics(frame: pd.DataFrame) -> dict:
    values = frame["monthly_rent"].dropna()
    return {
        "count": len(frame),
        "known_rents": len(values),
        "mean": values.mean() if len(values) else None,
        "median": values.median() if len(values) else None,
        "min": values.min() if len(values) else None,
        "max": values.max() if len(values) else None,
    }


def total_monthly_cost(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    columns = ["monthly_rent", "condominium_fee", "iptu_monthly"]
    result["total_monthly_cost"] = result[columns].sum(axis=1, min_count=3)
    result["cost_completeness"] = (
        result[columns]
        .notna()
        .all(axis=1)
        .map({True: "Completo", False: "Incompleto — componentes desconhecidos"})
    )
    return result
