import json

import pandas as pd
import streamlit as st

from src.config import DATABASE, QUALITY
from src.database import initialize_database, query, seed_fingerprint


@st.cache_resource
def prepare_database(fingerprint):
    report = DATABASE.with_suffix(".report.json")
    if (
        not DATABASE.exists()
        or not report.exists()
        or json.loads(report.read_text(encoding="utf-8"))["fingerprint"] != fingerprint
    ):
        initialize_database()
    return str(DATABASE)


@st.cache_data
def cached_query(sql, parameters, fingerprint):
    return query(sql, parameters)


def load(table):
    allowed = {
        "sources",
        "urban_policy_documents",
        "information_requests",
        "indicator_catalog",
        "formal_wages",
        "wage_distribution",
        "housing_stock",
        "occupancy_status",
        "rental_costs",
        "indicators",
    }
    if table not in allowed:
        raise ValueError("Tabela não permitida")
    fingerprint = seed_fingerprint()
    prepare_database(fingerprint)
    raw = {"sources", "urban_policy_documents", "information_requests", "indicator_catalog"}
    return cached_query(
        f"SELECT * FROM {table if table in raw else 'export_' + table}", None, fingerprint
    )


def setup(title):
    st.set_page_config(page_title=f"{title} | Observatório Habitacional", layout="wide")
    prepare_database(seed_fingerprint())
    st.sidebar.title("Observatório Habitacional")
    st.sidebar.caption("Pato Branco · Paraná · 4118501")
    st.sidebar.info("Pesquisa independente. Sem vínculo institucional com órgãos públicos.")
    st.title(title)
    st.caption("Renda, moradia e desenvolvimento urbano")
    st.write("Pesquisa independente baseada em dados públicos e metodologia documentada.")


def number(value, decimals=0):
    if pd.isna(value):
        return "Indisponível"
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def card(label, value, *, year, source, status, explanation):
    with st.container(border=True):
        st.metric(label, value)
        st.caption(f"Referência: {year} · Fonte: {source}")
        st.caption(f"Status: {QUALITY.get(status, status)}")
        st.write(explanation)


def table(frame, name):
    st.dataframe(frame, hide_index=True, width="stretch")
    st.download_button(
        "Exportar CSV",
        frame.to_csv(index=False).encode("utf-8-sig"),
        f"{name}.csv",
        mime="text/csv",
        key=f"download_{name}",
    )


def limitations():
    with st.expander("Limitações dos dados", expanded=True):
        st.write(
            "Fontes numéricas com verificação documental pendente. RAIS mede vínculos formais, "
            "não pessoas nem renda domiciliar. Valores salariais são nominais. "
            "As categorias censitárias selecionadas são parciais. "
            "Os anúncios são uma amostra de 13 valores de uma única imobiliária, sem "
            "data de coleta informada, e não representam o mercado municipal. "
            "Não há indicador oficial de acessibilidade calculado pelo cruzamento dessas bases."
        )
