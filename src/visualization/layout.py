"""Estrutura editorial e navegação; nenhum acesso ou transformação dos dados."""

from html import escape

import streamlit as st

from src.visualization.styles import CSS
from src.visualization.theme import PAGES


def html(text):
    st.html(text)


def brand():
    html(CSS)
    html(
        '<header class="oh-brand"><span class="oh-brand-name">'
        "Observatório Habitacional<br>de Pato Branco</span>"
        '<span class="oh-brand-meta">Renda, moradia e desenvolvimento urbano<br>'
        "Pesquisa independente · versão 1.1</span></header>"
    )


def page_heading(title, *, topic="", description="", period=""):
    brand()
    if topic:
        html(f'<p class="oh-kicker">{escape(topic)}</p>')
    with st.container(key="page_heading"):
        st.title(title)
    if description:
        html(f'<p class="oh-section-description">{escape(description)}</p>')
    if period:
        st.caption(period)


def section(title, description="", *, number=None):
    if number:
        html(f'<p class="oh-kicker">{escape(str(number))} / {escape(title)}</p>')
    html(f'<h2 class="oh-section-title">{escape(title)}</h2>')
    if description:
        html(f'<p class="oh-section-description">{escape(description)}</p>')


def note(title, body, *, kind="information"):
    # Estilos permitidos; nenhum texto de fonte é interpretado como HTML.
    kind = kind if kind in {"information", "exploratory", "unavailable"} else "information"
    html(
        f'<aside class="oh-note oh-note-{kind}" aria-label="{escape(title)}">'
        f"<strong>{escape(title)}</strong>{escape(body)}</aside>"
    )


def chart_section(
    title,
    figure,
    *,
    description="",
    interpretation="",
    source="",
    period="",
    status="Verificação documental pendente",
):
    section(title, description)
    with st.container(border=True):
        st.plotly_chart(
            figure, width="stretch", config={"displayModeBar": False, "responsive": True}
        )
        if interpretation:
            html(
                '<p class="oh-reading"><strong>Leitura dos dados.</strong> '
                f"{escape(interpretation)}</p>"
            )
        st.caption(f"Fonte: {source} · Referência: {period} · {status}")


def explore():
    descriptions = [
        "Remuneração nominal, vínculos formais e faixas salariais.",
        "Preços anunciados e limites da amostra exploratória.",
        "Posse, tipos de domicílio e situação de ocupação.",
        "Documentos identificados e análise das políticas urbanas.",
        "Fontes, cálculos, limitações e qualidade de cada dado.",
    ]
    # URLs relativas à aplicação, compatíveis com o baseUrlPath do Streamlit.
    cards = [
        f'<a class="oh-explore" href="./{route}" target="_self"><h3>{escape(title)}</h3>'
        f"<p>{escape(description)}</p><span>Explorar tema →</span></a>"
        for (_, title, route), description in zip(PAGES[1:], descriptions)
    ]
    html(
        '<nav class="oh-explore-grid" aria-label="Explore a pesquisa">' + "".join(cards) + "</nav>"
    )


def footer():
    html(
        '<footer class="oh-footer">Observatório Habitacional de Pato Branco · Paraná · '
        "IBGE 4118501<br>Pesquisa independente baseada em dados públicos e metodologia "
        "documentada. Sem vínculo institucional com Prefeitura, IBGE ou IPARDES.</footer>"
    )
