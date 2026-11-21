from html import escape
from urllib.parse import urlparse

import pandas as pd
import streamlit as st

from src.visualization.components import load, setup, table
from src.visualization.layout import html, note, section

setup(
    "Política urbana",
    topic="Território, instrumentos e documentos",
    description="Um catálogo para acompanhar a pesquisa sobre planejamento e políticas urbanas.",
    period="Documentos de 2023–2024 · índice consultado em 19/11/2026 · conteúdo não analisado",
)
note(
    "Identificação não é análise jurídica",
    "Os documentos foram identificados no índice "
    "municipal. Vigência, alterações, artigos e efeitos das políticas ainda não foram analisados.",
)
documents = load("urban_policy_documents")
groups = {
    "Planejamento territorial": ["plano_diretor", "perimetro", "viario", "calcadas"],
    "Zoneamento": ["lupa"],
    "Instrumentos urbanísticos": ["outorga", "eiv", "preempcao"],
    "Financiamento urbano": ["fundurb"],
    "Habitação de interesse social": [],
    "Estudos e documentos": [],
}
status = st.multiselect(
    "Situação da análise documental",
    ["Identificado", "Em análise", "Analisado", "Verificação pendente"],
)
selected = documents[documents["analysis_status"].isin(status)] if status else documents
section(
    "Documentos por tema",
    "Agrupamento editorial para facilitar a consulta; não constitui "
    "uma classificação jurídica nem valida o conteúdo das normas.",
)
for group, identifiers in groups.items():
    rows = selected[selected["document_id"].isin(identifiers)]
    with st.expander(f"{group} · {len(rows)} documento(s)", expanded=bool(len(rows))):
        if rows.empty:
            st.write(
                "Nenhum documento neste grupo para a seleção atual. "
                "O catálogo poderá receber novas evidências verificadas."
            )
        for row in rows.to_dict("records"):
            url = row["source_url"]
            link = (
                f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">'
                "Consultar índice oficial de legislação ↗</a>"
                if pd.notna(url) and urlparse(url).scheme in {"https", "http"}
                else "<p>Link oficial ainda não informado.</p>"
            )
            html(
                f'<article class="oh-document"><div class="oh-document-meta">'
                f"{escape(row['document_type'])} {escape(row['law_number'])} · "
                f"{int(row['publication_year'])}</div><h3>{escape(row['document_name'])}</h3>"
                f'<span class="oh-status">{escape(row["analysis_status"])}</span>'
                "<p>Descrição jurídica não publicada: análise documental pendente.</p>"
                f"{link}</article>"
            )
section("Catálogo para consulta e exportação")
table(
    selected,
    "catalogo_legislacao",
    columns=[
        "document_name",
        "law_number",
        "publication_year",
        "analysis_status",
        "source_url",
        "notes",
    ],
)
section("Execução das políticas e financiamento")
note(
    "Agenda de pesquisa",
    "Indicadores de execução orçamentária, FUNDURB, outorga onerosa "
    "e políticas habitacionais estão em preparação. Nenhum valor de arrecadação ou resultado "
    "de política foi presumido.",
    kind="unavailable",
)
section("Solicitações oficiais de informação")
requests = load("information_requests")
if requests.empty:
    note(
        "Nenhum envio confirmado cadastrado",
        "Solicitações à Prefeitura ou ao IBGE só serão exibidas com registro confirmado "
        "de envio. Não há protocolos nem datas presumidos.",
    )
else:
    table(requests, "solicitacoes_confirmadas")
