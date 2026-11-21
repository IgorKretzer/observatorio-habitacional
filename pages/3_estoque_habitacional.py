import streamlit as st

from src.indicators.housing import tenure_subtotals
from src.visualization.charts import housing_chart, occupancy_chart
from src.visualization.components import catalog_card, kpi_grid, limitations, load, setup, table
from src.visualization.layout import chart_section, note, section

setup(
    "Estoque habitacional",
    topic="Domicílios e ocupação",
    description="Condição de ocupação, tipos de domicílio e situação do estoque habitacional.",
    period="Censo 2022 / SIDRA 9928 e diagnóstico municipal · verificação documental pendente",
)
section(
    "Dois recortes do estoque",
    "Posse nas categorias analisadas e situação de ocupação "
    "no diagnóstico municipal são universos que ainda precisam de conferência conceitual.",
)
catalog = load("indicator_catalog")
kpi_grid(
    [
        catalog_card(
            catalog,
            "tenure_Próprio",
            label="Domicílios próprios · parcial",
            explanation="Subtotal das três categorias informadas; não é o total municipal.",
        ),
        catalog_card(
            catalog,
            "tenure_Alugado",
            label="Domicílios alugados · parcial",
            explanation="Casas, casas de vila/condomínio e apartamentos analisados.",
        ),
        catalog_card(
            catalog,
            "tenure_Cedido",
            label="Domicílios cedidos · parcial",
            explanation="Subtotal das categorias selecionadas, com fonte ainda por conferir.",
        ),
        catalog_card(
            catalog,
            "occupancy_Ocupados",
            explanation="Valor informado pelo diagnóstico municipal; abrangência por conferir.",
        ),
        catalog_card(
            catalog,
            "occupancy_Vagos",
            explanation="Vacância censitária não significa oferta imediata para locação.",
        ),
        catalog_card(
            catalog,
            "occupancy_Uso ocasional",
            explanation="Categoria do diagnóstico municipal; conceitos ainda por conferir.",
        ),
    ]
)
housing, occupancy = load("housing_stock"), load("occupancy_status")
chart_section(
    "Condição de ocupação por tipo de domicílio",
    housing_chart(housing),
    description="Comparação entre casas, casas de vila/condomínio e apartamentos.",
    interpretation="Próprios, alugados e cedidos são subtotais parciais. Em outra condição, "
    "há valores desconhecidos para duas categorias; eles não são convertidos em zero.",
    source="IBGE · Censo 2022 · SIDRA 9928",
    period="2022",
)
chart_section(
    "Ocupados, vagos e de uso ocasional",
    occupancy_chart(occupancy),
    description="Situação de ocupação registrada no diagnóstico municipal, sujeita à validação.",
    interpretation="As parcelas 34.318, 3.053 e 1.484 fecham o total informado de 38.855. "
    "O fechamento aritmético não valida a equivalência conceitual com o Censo.",
    source="Diagnóstico municipal · documento a identificar",
    period="2022",
)
note(
    "Vacância não é disponibilidade",
    "Vacância censitária não equivale à disponibilidade "
    "imediata de imóveis para locação. Não é possível inferir a propriedade ou a destinação "
    "dos imóveis vagos a partir desses dados.",
)
section("Tabelas detalhadas")
table(
    housing,
    "domicilios_condicao_tipo",
    columns=[
        "year",
        "dwelling_type",
        "tenure_status",
        "dwelling_count",
        "source_id",
        "source_status",
    ],
)
with st.expander("Subtotais parciais e situação de ocupação"):
    subtotals = tenure_subtotals(housing)
    subtotals["quality_status"] = "derived"
    subtotals["upstream_status"] = "pending_source_verification"
    subtotals["methodology"] = "Subtotal parcial; NULL se alguma categoria é desconhecida"
    table(subtotals, "subtotais_parciais")
    table(occupancy, "situacao_ocupacao")
section("Déficit habitacional e inadequação habitacional")
note(
    "Indicadores em preparação",
    "Indicadores em preparação — aguardando validação metodológica e dados complementares. "
    "Não se calcula déficit pela diferença entre domicílios vagos e alugados.",
    kind="unavailable",
)
limitations()
