import streamlit as st

from src.indicators.income import annual_changes, cumulative_shares
from src.visualization.charts import cumulative_chart, wages_chart
from src.visualization.components import (
    IndicatorCard,
    catalog_card,
    kpi_grid,
    limitations,
    load,
    number,
    setup,
    table,
)
from src.visualization.layout import chart_section, note, section

setup(
    "Renda e trabalho",
    topic="Trabalho formal",
    description="O que a remuneração dos vínculos formais permite observar sobre a renda local.",
    period="RAIS/IPARDES · 2022–2025 · reais correntes · verificação documental pendente",
)
note(
    "Um universo específico",
    "Os dados da RAIS referem-se a vínculos formais de trabalho e não "
    "representam diretamente a renda de todas as famílias do município.",
)
catalog = load("indicator_catalog")
section(
    "Retrato do trabalho formal", "Referência de 2025; vínculos não equivalem a pessoas distintas."
)
kpi_grid(
    [
        catalog_card(
            catalog,
            "average_monthly_wage_2025",
            explanation="Média nominal dos vínculos formais. Não representa renda domiciliar.",
        ),
        catalog_card(
            catalog,
            "employment_relationships_2025",
            explanation="Uma pessoa pode ter mais de um vínculo formal de emprego.",
        ),
        IndicatorCard(
            "Mediana salarial",
            "Indisponível",
            "reais por mês",
            "2025",
            "RAIS/IPARDES",
            "unavailable",
            "A média não permite inferir a mediana salarial exata.",
            "rais_2025",
            "unavailable",
            "pending_source_verification",
        ),
    ]
)
wages = annual_changes(load("formal_wages"))
chart_section(
    "Série histórica da remuneração",
    wages_chart(wages),
    description="Salários médios nominais mensais, sem correção inflacionária.",
    interpretation="A série descreve remuneração do trabalho formal. A variação nominal não "
    "é uma medida de mudança do poder de compra. Renda individual e renda domiciliar são "
    "conceitos distintos do salário de um vínculo.",
    source="RAIS/IPARDES",
    period="2022–2025",
)
distribution = cumulative_shares(load("wage_distribution"), wages)
chart_section(
    "Distribuição salarial acumulada",
    cumulative_chart(distribution),
    description="O mesmo total de vínculos é usado como denominador nas duas faixas.",
    interpretation=f"Até dois salários mínimos: {number(distribution.iloc[0]['percentage'], 1)}% "
    f"dos vínculos. Até três: {number(distribution.iloc[1]['percentage'], 1)}%. "
    "A primeira faixa está contida na segunda; não se somam as porcentagens.",
    source="RAIS/IPARDES",
    period="2025",
)
section("Dados para consulta e reprodução", "Os CSVs mantêm anos, fontes e valores desconhecidos.")
table(
    wages,
    "renda_anual",
    columns=[
        "year",
        "average_monthly_wage",
        "median_wage",
        "nominal_change_pct",
        "employment_relationships",
        "establishments",
        "source_id",
        "source_status",
    ],
)
with st.expander("Consultar os valores das faixas acumuladas"):
    table(
        distribution,
        "faixas_salariais_acumuladas",
        columns=[
            "year",
            "wage_band",
            "employment_relationships",
            "percentage",
            "total_relationships",
            "source_id",
            "source_status",
        ],
    )
if wages["median_wage"].notna().any():
    table(wages.dropna(subset=["average_monthly_wage", "median_wage"]), "media_mediana")
section("Notas metodológicas")
limitations()
