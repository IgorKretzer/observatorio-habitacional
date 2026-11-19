import streamlit as st

from src.indicators.income import annual_changes, cumulative_shares
from src.visualization.charts import cumulative_chart, wages_chart
from src.visualization.components import limitations, load, setup, table

setup("Renda e trabalho")
st.info(
    "Os dados da RAIS referem-se a vínculos formais de trabalho e não representam "
    "diretamente a renda de todas as famílias do município."
)
st.caption("RAIS/IPARDES · 2022–2025 · verificação documental pendente · R$/mês nominais")
wages = annual_changes(load("formal_wages"))
st.plotly_chart(wages_chart(wages), width="stretch")
st.subheader("Série anual e variação nominal")
st.write("Variação em relação ao ano imediatamente anterior; sem correção inflacionária.")
table(wages, "renda_anual")
if wages["median_wage"].notna().any():
    comparison = wages.dropna(subset=["average_monthly_wage", "median_wage"])
    st.subheader("Média e mediana · apenas anos com ambas disponíveis")
    table(comparison, "media_mediana")
else:
    st.info("Mediana salarial exata indisponível. A média não permite deduzi-la.")
st.subheader("Distribuição acumulada de vínculos · 2025")
distribution = cumulative_shares(load("wage_distribution"), wages)
st.plotly_chart(cumulative_chart(distribution), width="stretch")
st.warning("Até 2 e até 3 salários mínimos são faixas acumuladas e não devem ser somadas.")
table(distribution, "faixas_salariais_acumuladas")
limitations()
