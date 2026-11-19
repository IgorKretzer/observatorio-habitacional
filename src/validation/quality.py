"""Validações de domínio, integridade e interpretação."""

import math

import pandas as pd

from src.config import QUALITY
from src.schemas import KEYS, SCHEMAS

NONNEGATIVE = {
    "value",
    "employment_relationships",
    "establishments",
    "average_monthly_wage",
    "median_wage",
    "dwelling_count",
    "monthly_rent",
    "condominium_fee",
    "iptu_monthly",
    "area_sqm",
    "bedrooms",
    "parking_spaces",
}


def validate_frame(table: str, frame: pd.DataFrame) -> None:
    if set(frame.columns) != set(SCHEMAS[table]):
        raise ValueError(f"{table}: colunas diferentes do schema")
    keys = KEYS[table]
    if frame[keys].isna().any().any() or frame.duplicated(keys).any():
        raise ValueError(f"{table}: chave ausente ou duplicada")
    for column, sql_type in SCHEMAS[table].items():
        values = frame[column].dropna()
        if sql_type.startswith(("INTEGER", "BIGINT", "DOUBLE")):
            numeric = pd.to_numeric(values, errors="raise")
            if not numeric.map(math.isfinite).all():
                raise ValueError(f"{table}.{column}: valor não finito")
            if sql_type.startswith(("INTEGER", "BIGINT")) and (numeric % 1 != 0).any():
                raise ValueError(f"{table}.{column}: contagem/ano não inteiro")
            if column in NONNEGATIVE and (numeric < 0).any():
                raise ValueError(f"{table}.{column}: valor negativo")
        if sql_type == "DATE":
            pd.to_datetime(values, errors="raise", format="%Y-%m-%d")
    for column in ("quality_status", "validation_status"):
        if column in frame and not frame[column].isin(QUALITY).all():
            raise ValueError(f"{table}: status de qualidade inválido")
    if table == "sources" and not frame["status"].isin(QUALITY).all():
        raise ValueError("sources: status inválido")
    if table == "information_requests" and frame["submitted_at"].isna().any():
        raise ValueError("Solicitação sem envio confirmado")
    if (
        table == "urban_policy_documents"
        and not frame["analysis_status"]
        .isin(["Identificado", "Em análise", "Analisado", "Verificação pendente"])
        .all()
    ):
        raise ValueError("Situação de análise documental inválida")


def validate_relations(frames: dict[str, pd.DataFrame]) -> None:
    sources = frames["sources"].set_index("source_id")
    for table, frame in frames.items():
        if table != "sources" and "source_id" in frame:
            if frame["source_id"].isna().any() or not frame["source_id"].isin(sources.index).all():
                raise ValueError(f"{table}: fonte ausente ou desconhecida")
            year_column = "year" if "year" in frame else "reference_year"
            if year_column in frame:
                for row in frame.to_dict("records"):
                    source_year = sources.loc[row["source_id"], "reference_year"]
                    year = row[year_column]
                    if pd.notna(source_year) and pd.notna(year) and int(year) != int(source_year):
                        raise ValueError(f"{table}: ano divergente da fonte")
    wages = frames["formal_wages"]
    for _, group in frames["wage_distribution"].groupby(["year", "municipality_code"]):
        ordered = group.sort_values("wage_band_order")["employment_relationships"].dropna()
        if not ordered.is_monotonic_increasing:
            raise ValueError("Faixas acumuladas devem ser crescentes")
        matching = wages[
            (wages["year"] == group.iloc[0]["year"])
            & (wages["municipality_code"] == group.iloc[0]["municipality_code"])
        ]
        if not matching.empty and not ordered.empty:
            total = matching.iloc[0]["employment_relationships"]
            if pd.notna(total) and ordered.max() > total:
                raise ValueError("Faixa acumulada excede o total de vínculos")
    for _, group in frames["occupancy_status"].groupby(["year", "municipality_code"]):
        values = group.set_index("status")["dwelling_count"]
        components = values.reindex(["Ocupados", "Vagos", "Uso ocasional"])
        total = values.get("Total informado")
        if pd.notna(total) and components.notna().all() and components.sum() != total:
            raise ValueError("Ocupação: soma incompatível com total informado")


def interpretation_guard(
    *, population_claim=False, cumulative_sum=False, wage_statistic="mean", available=True
):
    if population_claim:
        raise ValueError("Amostra exploratória não estima a população municipal")
    if cumulative_sum:
        raise ValueError("Faixas acumuladas não podem ser somadas")
    if wage_statistic == "median" and not available:
        raise ValueError("Mediana salarial indisponível")


def duplicate_candidates(frame: pd.DataFrame) -> pd.DataFrame:
    """URLs repetidas são indícios; não exclui registros nem compara NULLs."""
    urls = frame["listing_url"]
    return frame[urls.notna() & urls.duplicated(keep=False)].copy()
