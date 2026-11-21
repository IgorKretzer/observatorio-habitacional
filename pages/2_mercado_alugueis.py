import pandas as pd
import streamlit as st

from src.config import ROOT
from src.indicators.housing import rental_statistics
from src.ingestion.listings import filter_listings, read_listings
from src.validation.quality import duplicate_candidates
from src.visualization.charts import rent_histogram, rental_bands
from src.visualization.components import (
    IndicatorCard,
    kpi_grid,
    limitations,
    load,
    number,
    setup,
    table,
)
from src.visualization.layout import chart_section, note, section

setup(
    "Mercado de aluguéis",
    topic="Preços anunciados",
    description="Uma leitura exploratória dos valores pedidos para locação e dos limites "
    "dessa primeira amostra.",
    period="Amostra de uma única imobiliária · coleta não informada · verificação pendente",
)
note(
    "Amostra exploratória",
    "Os anúncios não são contratos efetivamente realizados. "
    "Esta amostra não representa o mercado municipal; imobiliária, bairros, tipos e datas "
    "de coleta não foram informados.",
    kind="exploratory",
)
rentals = load("rental_costs")
selections = {}
section("Explore a amostra", "Filtros dependem das informações efetivamente disponíveis.")
with st.expander("Filtros dos anúncios", expanded=False):
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
            help="Sem informação disponível na amostra" if not values else None,
        )
    dates = pd.to_datetime(rentals["collected_at"]).dropna()
    period = None
    if not dates.empty:
        period = st.date_input("Período de coleta", value=(dates.min().date(), dates.max().date()))
        st.caption("O filtro de período exclui anúncios sem data de coleta.")
    else:
        st.caption("Período indisponível: nenhuma data de coleta foi informada.")
rentals = filter_listings(rentals, selections, period)
stats = rental_statistics(rentals)
cards = []
for key, label, decimals in [
    ("count", "Anúncios na seleção", 0),
    ("mean", "Média anunciada", 2),
    ("median", "Mediana anunciada", 2),
    ("min", "Menor valor anunciado", 2),
    ("max", "Maior valor anunciado", 2),
]:
    cards.append(
        IndicatorCard(
            label,
            ("R$ " if decimals and stats[key] is not None else "") + number(stats[key], decimals),
            "anúncios" if key == "count" else "reais por mês",
            "Coleta conforme registros; não informada",
            "Amostra exploratória previamente informada",
            "exploratory",
            "Estatística da seleção de anúncios; sem inferência sobre o município.",
            quality_status="derived",
            source_status="pending_source_verification",
        )
    )
kpi_grid(cards)
if rentals.empty:
    note("Nenhum anúncio na seleção", "Ajuste os filtros para consultar os registros disponíveis.")
else:
    chart_section(
        "Distribuição dos preços anunciados",
        rent_histogram(rentals),
        description="Intervalos regulares de R$ 500. A linha tracejada indica a "
        "mediana da seleção.",
        interpretation=f"A seleção reúne {stats['count']} anúncios, com "
        f"{stats['known_rents']} aluguéis conhecidos. Média: R$ {number(stats['mean'], 2)}; "
        f"mediana: R$ {number(stats['median'], 2)}. Os dois valores descrevem a amostra.",
        source="Amostra exploratória previamente informada",
        period="Coleta não informada",
        status="Exploratório · fonte pendente",
    )
    chart_section(
        "Anúncios por faixa de valor",
        rental_bands(rentals),
        description="Grupos descritivos mantidos da versão inicial, com limite superior inclusivo.",
        interpretation="As faixas têm amplitudes diferentes e não formam um histograma de "
        "densidade. O gráfico compara a quantidade de anúncios em cada grupo.",
        source="Amostra exploratória previamente informada",
        period="Coleta não informada",
        status="Exploratório · fonte pendente",
    )
section(
    "Anúncios e custo mensal da moradia",
    "Aluguel + condomínio + IPTU mensal. O total só é conhecido quando os três componentes "
    "estão disponíveis; informação ausente não vale zero.",
)
table(
    rentals,
    "anuncios_filtrados",
    columns=[
        "listing_id",
        "monthly_rent",
        "condominium_fee",
        "iptu_monthly",
        "total_monthly_cost",
        "cost_completeness",
        "collected_at",
        "source_id",
        "validation_status",
    ],
)
candidates = duplicate_candidates(rentals)
st.caption(
    f"Registros com URL repetida: {len(candidates)}. São candidatos à revisão, sem "
    "exclusão automática. URLs desconhecidas não são comparadas."
)
if not candidates.empty:
    table(candidates, "possiveis_duplicados")
section("Metodologia e ampliação da amostra")
note(
    "Média conferida aritmeticamente",
    "Na lista original, os 13 aluguéis somam R$ 33.440,00: "
    "média R$ 2.572,31 e mediana R$ 2.300,00. A expectativa inicial de R$ 2.587,69 "
    "não corresponde aos valores fornecidos, que foram preservados.",
)
limitations()
with st.expander("Validar novos anúncios · prévia sem persistência"):
    st.write(
        "Use o modelo padronizado. A prévia valida o arquivo, mas não grava alterações "
        "no banco público. Campos vazios permanecem desconhecidos."
    )
    st.download_button(
        "Baixar modelo CSV",
        (ROOT / "data/metadata/rental_listings_template.csv").read_bytes(),
        "rental_listings_template.csv",
        mime="text/csv",
    )
    upload = st.file_uploader("CSV padronizado de anúncios", type=["csv"])
    if upload is not None:
        try:
            preview = read_listings(upload)
            if not preview["source_id"].isin(load("sources")["source_id"]).all():
                raise ValueError("Fonte não cadastrada: registre a fonte no processamento local.")
            note(
                "Arquivo validado",
                f"{len(preview)} registros com schema válido. Nenhum dado foi persistido.",
            )
            table(preview, "previa_importacao")
        except (ValueError, TypeError, pd.errors.ParserError) as error:
            st.error(f"Arquivo inválido: {error}")
