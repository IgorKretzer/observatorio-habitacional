import pandas as pd
import streamlit as st

from src.indicators.housing import rental_statistics
from src.ingestion.listings import filter_listings, read_listings
from src.validation.quality import duplicate_candidates
from src.visualization.charts import rent_histogram, rental_bands
from src.visualization.components import card, limitations, load, number, setup, table

setup("Mercado de aluguéis")
st.warning(
    "Amostra exploratória previamente informada: 13 anúncios de uma única imobiliária. "
    "Não representa o mercado municipal. Imobiliária e data da coleta não informadas."
)
rentals = load("rental_costs")
selections = {}
with st.expander("Filtros", expanded=True):
    for column, label in [
        ("agency", "Imobiliária"),
        ("property_type", "Tipo de imóvel"),
        ("neighborhood", "Bairro"),
    ]:
        values = sorted(rentals[column].dropna().unique().tolist())
        selections[column] = st.multiselect(
            label,
            values,
            disabled=not values,
            help="Sem informação na amostra" if not values else None,
        )
    dates = pd.to_datetime(rentals["collected_at"]).dropna()
    period = None
    if not dates.empty:
        period = st.date_input("Período de coleta", value=(dates.min().date(), dates.max().date()))
        st.caption("Ao filtrar por período, anúncios sem data ficam fora do resultado.")
    else:
        st.caption("Filtro de período indisponível: datas de coleta desconhecidas.")
rentals = filter_listings(rentals, selections, period)
stats = rental_statistics(rentals)
labels = [
    ("count", "Anúncios", 0),
    ("mean", "Média anunciada", 2),
    ("median", "Mediana anunciada", 2),
    ("min", "Mínimo", 2),
    ("max", "Máximo", 2),
]
for col, (key, label, decimals) in zip(st.columns(5), labels):
    with col:
        card(
            label,
            ("R$ " if decimals and stats[key] is not None else "") + number(stats[key], decimals),
            year="Coleta não informada / conforme filtro",
            source="Amostra exploratória previamente informada",
            status="exploratory",
            explanation="Estatística descritiva dos anúncios filtrados; não de contratos.",
        )
if rentals.empty:
    st.info("Nenhum anúncio para os filtros selecionados.")
else:
    left, right = st.columns(2)
    with left:
        st.plotly_chart(rent_histogram(rentals), width="stretch")
    with right:
        st.plotly_chart(rental_bands(rentals), width="stretch")
st.caption(
    "Conferência da amostra original: soma de R$ 33.440,00; média de R$ 2.572,31. "
    "O valor esperado de R$ 2.587,69 na especificação não corresponde à lista."
)
st.subheader("Anúncios e componentes de custo")
st.write(
    "Custo total mensal = aluguel + condomínio + IPTU mensal. "
    "O total permanece indisponível se qualquer componente for desconhecido."
)
table(rentals, "anuncios_filtrados")
candidates = duplicate_candidates(rentals)
st.caption(
    f"Possíveis duplicados por URL repetida: {len(candidates)}. "
    "Nenhum registro é removido automaticamente; URLs ausentes não são comparadas."
)
if not candidates.empty:
    table(candidates, "possiveis_duplicados")
with st.expander("Preparar importação CSV · prévia sem persistência"):
    st.write(
        "Use as colunas do modelo; células vazias são desconhecidas. "
        "Cadastre a fonte no pipeline antes de incorporá-la. A aplicação pública não grava uploads."
    )
    from src.config import ROOT

    st.download_button(
        "Baixar modelo CSV",
        (ROOT / "data/metadata/rental_listings_template.csv").read_bytes(),
        "rental_listings_template.csv",
        mime="text/csv",
    )
    upload = st.file_uploader("CSV padronizado", type=["csv"])
    if upload is not None:
        try:
            preview = read_listings(upload)
            if not preview["source_id"].isin(load("sources")["source_id"]).all():
                raise ValueError(
                    "Fonte não cadastrada: atualize sources.csv no processamento local."
                )
            st.success(f"Schema válido: {len(preview)} registros. Nenhum dado foi persistido.")
            table(preview, "previa_importacao")
        except (ValueError, TypeError, pd.errors.ParserError) as error:
            st.error(f"Arquivo inválido: {error}")
limitations()
