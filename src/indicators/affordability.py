"""Somente simulações explícitas; não produz estimativa municipal."""

import pandas as pd

from src.indicators.income import safe_percentage


def simulate_burden(rent, income, *, rent_year, income_year, source_ids):
    if not source_ids:
        raise ValueError("Fontes obrigatórias")
    if any(pd.notna(v) and v < 0 for v in (rent, income)):
        raise ValueError("Valores negativos")
    return {
        "value": safe_percentage(rent, income),
        "quality_status": "derived",
        "methodology": "Simulação individual, sem inferência populacional",
        "reference_years": [rent_year, income_year],
        "source_ids": list(source_ids),
        "warning": "Anos distintos ou desconhecidos; não comparáveis diretamente"
        if rent_year is None or income_year is None or rent_year != income_year
        else "Simulação; não é indicador oficial",
    }
