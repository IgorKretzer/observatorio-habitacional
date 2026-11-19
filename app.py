import pandas as pd
import streamlit as st

from src.indicators.income import cumulative_shares
from src.visualization.charts import (
    cumulative_chart,
    rent_histogram,
    rented_chart,
    wages_chart,
)
from src.visualization.components import card, limitations, load, number, setup, table

setup("Observatório Habitacional de Pato Branco")
st.warning("MVP de pesquisa · dados numéricos aguardando conferência documental.")
catalog = load("indicator_catalog").set_index("indicator_id")
items = [
    (
        "employment_relationships_2025",
        "Vínculos formais",
        0,
        "Vínculos de trabalho; uma pessoa pode ter mais de um.",
    ),
    (
        "average_monthly_wage_2025",
        "Remuneração formal média",
        2,
        "Média mensal nominal; não é mediana nem renda familiar.",
    ),
    (
        "tenure_Alugado",
        "Domicílios alugados · parcial",
        0,
        "Casas, casas de vila/condomínio e apartamentos; não é total municipal definitivo.",
    ),
    (
        "occupancy_Vagos",
        "Domicílios vagos",
        0,
        "Conceitos do diagnóstico ainda por conferir; não indica oferta de aluguel.",
    ),
    (
        "rental_amostra_informada_median",
        "Aluguel mediano · amostra",
        2,
        "Amostra exploratória de uma única imobiliária; data de coleta não informada.",
    ),
    (
        "rental_amostra_informada_count",
        "Anúncios analisados",
        0,
        "Registros técnicos internos; amostra sem representatividade municipal.",
    ),
]
for start in (0, 3):
    for column, (key, label, decimals, explanation) in zip(st.columns(3), items[start : start + 3]):
        row = catalog.loc[key]
        with column:
            card(
                label,
                ("R$ " if decimals else "") + number(row["value"], decimals),
                year=number(row["reference_year"])
                if pd.notna(row["reference_year"])
                else "Não informado",
                source=row["source_name"],
                status=row["upstream_status"],
                explanation=explanation,
            )
            st.caption("Cálculo derivado; proveniência e ressalvas disponíveis na metodologia.")
wages = load("formal_wages")
housing = load("housing_stock")
distribution = cumulative_shares(load("wage_distribution"), wages)
rentals = load("rental_costs")
left, right = st.columns(2)
with left:
    st.plotly_chart(wages_chart(wages), width="stretch")
    st.plotly_chart(cumulative_chart(distribution), width="stretch")
with right:
    st.plotly_chart(rented_chart(housing), width="stretch")
    st.plotly_chart(rent_histogram(rentals), width="stretch")
st.caption(
    "Salários: 2022–2025 · Censo: 2022 · Anúncios: coleta desconhecida. "
    "Fontes pendentes; anúncios exploratórios. Não há cruzamento oficial de acessibilidade."
)
limitations()
with st.expander("Indicadores e proveniência para exportação"):
    table(catalog.reset_index(), "indicadores_visao_geral")
