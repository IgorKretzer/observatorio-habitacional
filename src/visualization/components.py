import json
from dataclasses import dataclass
from html import escape

import pandas as pd
import streamlit as st

from src.config import DATABASE
from src.database import initialize_database, query, seed_fingerprint
from src.visualization.layout import html, note, page_heading
from src.visualization.theme import STATUS_LABELS


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


def setup(title, *, description="", period="", topic=""):
    prepare_database(seed_fingerprint())
    page_heading(title, topic=topic, description=description, period=period)


def number(value, decimals=0):
    if pd.isna(value):
        return "Indisponível"
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


@dataclass(frozen=True)
class IndicatorCard:
    label: str
    value: str
    unit: str
    year: str
    source: str
    status: str
    explanation: str
    source_id: str = ""
    quality_status: str = ""
    source_status: str = ""


def catalog_card(catalog, indicator_id, *, label=None, explanation=None):
    indexed = catalog.set_index("indicator_id") if "indicator_id" in catalog else catalog
    row = indexed.loc[indicator_id]
    is_money = row["unit"] == "BRL/mês"
    is_rental = row["category"] == "Mercado de aluguéis"
    value = number(row["value"], 2 if is_money else 0)
    return IndicatorCard(
        label=label or row["indicator_name"],
        value=("R$ " + value) if is_money and pd.notna(row["value"]) else value,
        unit="reais por mês" if is_money else row["unit"],
        year=str(int(row["reference_year"]))
        if pd.notna(row["reference_year"])
        else "Coleta não informada",
        source=row["source_name"],
        status="exploratory" if is_rental else row["upstream_status"],
        explanation=explanation or row["limitations"],
        source_id=row["source_id"],
        quality_status=row["quality_status"],
        source_status=row["upstream_status"],
    )


def kpi_markup(cards):
    items = []
    for card in cards:
        label = STATUS_LABELS.get(card.status, card.status)
        status_class = card.status if card.status in STATUS_LABELS else "information"
        # Inclusive textos fornecidos no banco passam por escape antes da interpolação.
        items.append(
            f'<article class="oh-kpi" data-source-id="{escape(card.source_id)}" '
            f'data-quality="{escape(card.quality_status)}">'
            f"<h3>{escape(card.label)}</h3>"
            f'<p class="oh-kpi-value">{escape(card.value)}</p>'
            f'<p class="oh-kpi-unit">{escape(card.unit)} · {escape(card.year)}</p>'
            f'<p class="oh-kpi-context">{escape(card.explanation)}</p>'
            f'<div class="oh-kpi-meta">Fonte: {escape(card.source)}'
            f'<br><span class="oh-status oh-status-{status_class}">{escape(label)}</span>'
            f"<br>{escape(STATUS_LABELS.get(card.quality_status, card.quality_status))}"
            f" · fonte: {escape(STATUS_LABELS.get(card.source_status, card.source_status))}"
            "</div></article>"
        )
    return '<section class="oh-kpi-grid" aria-label="Indicadores e suas referências">' + (
        "".join(items) + "</section>"
    )


def kpi_grid(cards):
    html(kpi_markup(cards))


def card(label, value, *, year, source, status, explanation, unit=""):
    """Compatibilidade para componentes anteriores; cards novos usam kpi_grid."""
    kpi_grid([IndicatorCard(label, value, unit, str(year), source, status, explanation)])


COLUMN_LABELS = {
    "year": "Ano",
    "reference_year": "Ano de referência",
    "reference_year_export": "Ano da base",
    "municipality_code": "Município (IBGE)",
    "municipality_code_export": "Município da base",
    "average_monthly_wage": "Remuneração média nominal",
    "median_wage": "Mediana salarial",
    "employment_relationships": "Vínculos",
    "establishments": "Estabelecimentos",
    "nominal_change_pct": "Variação nominal anual",
    "wage_band": "Faixa acumulada",
    "wage_band_order": "Ordem da faixa",
    "total_relationships": "Total de vínculos",
    "percentage": "Percentual de vínculos",
    "dwelling_type": "Tipo de domicílio",
    "tenure_status": "Condição de ocupação",
    "dwelling_count": "Domicílios",
    "monthly_rent": "Aluguel anunciado",
    "condominium_fee": "Condomínio",
    "iptu_monthly": "IPTU/mês",
    "total_monthly_cost": "Custo mensal total",
    "cost_completeness": "Componentes do custo",
    "agency": "Imobiliária",
    "property_type": "Tipo de imóvel",
    "neighborhood": "Bairro",
    "listing_id": "ID técnico",
    "listing_url": "Link do anúncio",
    "collected_at": "Data de coleta",
    "area_sqm": "Área (m²)",
    "bedrooms": "Quartos",
    "parking_spaces": "Vagas",
    "source_id": "ID da fonte",
    "source_institution": "Instituição",
    "source_dataset": "Base",
    "source_url": "URL da fonte",
    "source_status": "Verificação da fonte",
    "source_limitations": "Ressalvas da fonte",
    "unit_export": "Unidades",
    "methodology_export": "Metodologia da base",
    "indicator_id": "ID do indicador",
    "indicator_name": "Indicador",
    "category": "Tema",
    "value": "Valor",
    "unit": "Unidade",
    "methodology": "Metodologia",
    "quality_status": "Qualidade do indicador",
    "upstream_status": "Qualidade da fonte",
    "source_name": "Nome da fonte",
    "source_notes": "Notas da fonte",
    "limitations": "Limitações",
    "institution": "Instituição",
    "dataset_name": "Base de dados",
    "retrieved_at": "Acesso",
    "methodology_url": "URL metodológica",
    "notes": "Observações",
    "status": "Situação",
    "validation_status": "Qualidade do registro",
    "document_id": "ID do documento",
    "document_name": "Documento",
    "document_type": "Tipo",
    "law_number": "Número",
    "publication_year": "Ano",
    "analysis_status": "Análise documental",
    "request_id": "ID da solicitação",
    "subject": "Assunto",
    "submitted_at": "Envio confirmado",
    "protocol_number": "Protocolo",
    "response_date": "Data da resposta",
    "associated_indicators": "Indicadores associados",
}
MONEY = {
    "average_monthly_wage",
    "median_wage",
    "monthly_rent",
    "condominium_fee",
    "iptu_monthly",
    "total_monthly_cost",
}
INTEGER = {
    "year",
    "reference_year",
    "reference_year_export",
    "employment_relationships",
    "establishments",
    "total_relationships",
    "dwelling_count",
    "bedrooms",
    "parking_spaces",
    "publication_year",
}
PERCENTAGE = {"nominal_change_pct", "percentage"}


def display_formatter(column):
    if column in MONEY:
        return lambda value: f"R$ {number(value, 2)}"
    if column in PERCENTAGE:
        return lambda value: f"{number(value, 1)}%"
    if column in INTEGER:
        return lambda value: str(int(value)) if "year" in column else number(value)
    if column in {"quality_status", "upstream_status", "source_status", "validation_status"}:
        return lambda value: STATUS_LABELS.get(value, value)
    return None


def table(frame, name, *, columns=None, caption=None):
    formatters = {
        column: formatter
        for column in frame.columns
        if (formatter := display_formatter(column)) is not None
    }
    styled = frame.style.format(formatters, na_rep="—")
    st.dataframe(
        styled,
        hide_index=True,
        width="stretch",
        column_order=columns,
        column_config={column: label for column, label in COLUMN_LABELS.items() if column in frame},
    )
    if caption:
        st.caption(caption)
    st.download_button(
        "Exportar tabela completa · CSV",
        frame.to_csv(index=False).encode("utf-8-sig"),
        f"{name}.csv",
        mime="text/csv",
        key=f"download_{name}",
    )
    st.caption(
        "CSV em UTF-8: mantém campos originais e proveniência. Célula vazia significa "
        "informação desconhecida; a formatação brasileira se aplica à visualização."
    )


def limitations():
    note(
        "Como interpretar estes dados",
        "Fontes numéricas aguardam conferência documental. RAIS mede vínculos formais, não "
        "renda domiciliar. Valores salariais são nominais. Os subtotais censitários são parciais. "
        "A amostra de uma única imobiliária, sem data de coleta informada, não representa o "
        "mercado municipal. Não há indicador oficial de acessibilidade calculado pelo cruzamento "
        "dessas bases.",
    )
