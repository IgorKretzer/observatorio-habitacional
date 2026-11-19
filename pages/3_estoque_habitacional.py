import streamlit as st

from src.indicators.housing import tenure_subtotals
from src.visualization.charts import housing_chart, occupancy_chart
from src.visualization.components import limitations, load, setup, table

setup("Estoque habitacional")
st.caption("Censo 2022 / SIDRA 9928 e diagnóstico municipal · verificação documental pendente")
st.warning("Vacância censitária não equivale à disponibilidade imediata de imóveis para locação.")
housing = load("housing_stock")
occupancy = load("occupancy_status")
st.subheader("Condição de ocupação e tipo de domicílio")
st.plotly_chart(housing_chart(housing), width="stretch")
st.write(
    "Próprios, alugados e cedidos são subtotais das categorias informadas. "
    "Outra condição contém valores desconhecidos; não se completa a soma com zeros."
)
table(housing, "domicilios_condicao_tipo")
subtotals = tenure_subtotals(housing)
subtotals["quality_status"] = "derived"
subtotals["upstream_status"] = "pending_source_verification"
subtotals["methodology"] = "Subtotal parcial; NULL se alguma categoria informada é desconhecida"
table(subtotals, "subtotais_parciais")
st.subheader("Situação de ocupação")
st.plotly_chart(occupancy_chart(occupancy), width="stretch")
table(occupancy, "situacao_ocupacao")
st.write(
    "O total de 38.855 e as parcelas 34.318, 3.053 e 1.484 fecham aritmeticamente. "
    "A abrangência de domicílios particulares permanentes e as definições do diagnóstico "
    "ainda precisam ser confrontadas com o Censo; a soma não confirma os conceitos."
)
st.subheader("Déficit habitacional e inadequação habitacional")
st.info("Indicadores em preparação — aguardando validação metodológica e dados complementares.")
st.write(
    "Não se calcula déficit pela diferença entre domicílios vagos e alugados. "
    "A propriedade ou destinação dos domicílios vagos não pode ser inferida desses números."
)
limitations()
