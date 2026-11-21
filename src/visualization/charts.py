"""Apresentação Plotly: não modifica as bases nem as fórmulas de indicadores."""

import math

import pandas as pd
import plotly.graph_objects as go

from src.visualization.theme import COLORS, FONT

PRIMARY = COLORS["primary"]
SECONDARY = COLORS["secondary"]


def _br(value, decimals=0):
    if pd.isna(value):
        return "Não informado"
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def style(figure, *, height=360):
    figure.update_layout(
        template="none",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": FONT, "color": COLORS["text"], "size": 13},
        height=height,
        autosize=True,
        margin={"l": 8, "r": 20, "t": 30, "b": 12},
        separators=",.",
        bargap=0.3,
        bargroupgap=0.08,
        hoverlabel={"bgcolor": "#FFFFFF", "font": {"family": FONT, "size": 13}},
        legend={"title": None, "orientation": "h", "y": 1.12, "x": 0, "font": {"size": 12}},
    )
    figure.update_xaxes(
        showline=True,
        linecolor=COLORS["border"],
        zeroline=False,
        automargin=True,
        tickfont={"size": 12},
        title_font={"size": 12},
    )
    figure.update_yaxes(
        gridcolor=COLORS["alternate"],
        zeroline=False,
        automargin=True,
        tickfont={"size": 12},
        title_font={"size": 12},
    )
    return figure


def wages_chart(frame):
    data = frame.sort_values("year")
    figure = go.Figure(
        go.Scatter(
            x=data["year"],
            y=data["average_monthly_wage"],
            mode="lines+markers",
            line={"color": PRIMARY, "width": 2.5},
            marker={"size": 8, "color": PRIMARY},
            customdata=[[f"R$ {_br(v, 2)}"] for v in data["average_monthly_wage"]],
            hovertemplate="Ano: %{x}<br>Remuneração média nominal: %{customdata[0]}<extra></extra>",
            name="Média nominal",
        )
    )
    style(figure)
    figure.update_xaxes(title="Ano de referência", dtick=1, tickformat="d", showgrid=False)
    figure.update_yaxes(title="Remuneração mensal (R$)", tickformat=",.0f", rangemode="tozero")
    return figure


def _dwelling_label(value):
    return value.replace("Casa de vila ou condomínio", "Casa de vila<br>ou condomínio")


def rented_chart(frame):
    data = frame[frame["tenure_status"] == "Alugado"].sort_values("dwelling_count")
    figure = go.Figure(
        go.Bar(
            x=data["dwelling_count"],
            y=[_dwelling_label(v) for v in data["dwelling_type"]],
            orientation="h",
            marker_color=SECONDARY,
            text=[_br(v) for v in data["dwelling_count"]],
            textposition="auto",
            hovertemplate="%{y}<br>Domicílios alugados: %{text}<extra></extra>",
        )
    )
    style(figure)
    figure.update_xaxes(title="Domicílios alugados · subtotal parcial", tickformat=",.0f")
    figure.update_yaxes(title=None, showgrid=False)
    return figure


def cumulative_chart(frame):
    figure = go.Figure()
    data = frame.sort_values("wage_band_order")
    labels = [
        f"Até {int(order) + 1} salários mínimos<br>(acumulado)" for order in data["wage_band_order"]
    ]
    for label, percentage in zip(labels, data["percentage"]):
        figure.add_trace(
            go.Scatter(
                x=[0, percentage],
                y=[label, label],
                mode="lines",
                line={"color": COLORS["border"], "width": 2},
                showlegend=False,
                hoverinfo="skip",
            )
        )
    figure.add_trace(
        go.Scatter(
            x=data["percentage"],
            y=labels,
            mode="markers+text",
            marker={"color": PRIMARY, "size": 12},
            text=[f"{_br(v, 1)}%" for v in data["percentage"]],
            textposition="middle right",
            customdata=[[_br(n)] for n in data["employment_relationships"]],
            hovertemplate="%{y}<br>%{customdata[0]} vínculos · %{text}<extra></extra>",
            showlegend=False,
            cliponaxis=False,
        )
    )
    style(figure, height=300)
    figure.update_xaxes(
        title="Percentual dos vínculos formais (%)", range=[0, 105], tickvals=[0, 25, 50, 75, 100]
    )
    figure.update_yaxes(title=None, showgrid=False)
    return figure


def rent_histogram(frame):
    known = frame["monthly_rent"].dropna()
    # Intervalos regulares de R$ 500, ancorados em múltiplos de 500.
    start = math.floor(float(known.min()) / 500) * 500 if len(known) else 0
    end = (math.floor(float(known.max()) / 500) + 1) * 500 if len(known) else 500
    figure = go.Figure(
        go.Histogram(
            x=known,
            xbins={"start": start, "end": end, "size": 500},
            marker={"color": SECONDARY, "line": {"color": "#FFFFFF", "width": 1}},
            hovertemplate="Intervalo de aluguel (R$): %{x}<br>Anúncios: %{y}<extra></extra>",
            name="Anúncios",
        )
    )
    if len(known):
        figure.add_vline(
            x=float(known.median()), line_color=PRIMARY, line_dash="dash", line_width=2
        )
    style(figure)
    figure.update_xaxes(title="Aluguel anunciado (R$/mês)", tickformat=",.0f", nticks=5)
    figure.update_yaxes(title="Quantidade de anúncios", dtick=1)
    return figure


def rental_bands(frame):
    # Mesmos cortes da versão 1.0; grupos descritivos, não classes de um histograma.
    bands = pd.cut(
        frame["monthly_rent"],
        bins=[0, 1500, 2500, 3500, float("inf")],
        labels=["Até R$ 1.500", "> R$ 1.500 a 2.500", "> R$ 2.500 a 3.500", "Acima de R$ 3.500"],
        include_lowest=True,
    )
    counts = bands.value_counts(sort=False)
    figure = go.Figure(
        go.Bar(
            x=counts.values,
            y=counts.index.astype(str),
            orientation="h",
            marker_color=SECONDARY,
            text=counts.values,
            textposition="auto",
            hovertemplate="%{y}<br>Anúncios: %{x}<extra></extra>",
        )
    )
    style(figure)
    figure.update_xaxes(title="Anúncios por faixa · limite superior inclusivo", dtick=1)
    figure.update_yaxes(title=None, showgrid=False, autorange="reversed")
    return figure


def housing_chart(frame):
    figure = go.Figure()
    colors = {
        "Próprio": SECONDARY,
        "Alugado": PRIMARY,
        "Cedido": "#70665A",
        "Outra condição": "#777777",
    }
    for tenure, color in colors.items():
        data = frame[frame["tenure_status"] == tenure]
        figure.add_trace(
            go.Bar(
                x=[None if pd.isna(v) else v for v in data["dwelling_count"]],
                y=[_dwelling_label(v) for v in data["dwelling_type"]],
                orientation="h",
                name=tenure,
                marker_color=color,
                customdata=[[_br(v)] for v in data["dwelling_count"]],
                hovertemplate=f"{tenure}<br>" + "%{y}: %{customdata[0]} domicílios<extra></extra>",
            )
        )
    style(figure, height=440)
    figure.update_layout(barmode="group", legend={"y": 1.22}, margin={"t": 70})
    figure.update_xaxes(title="Domicílios · categorias informadas", tickformat=",.0f", nticks=4)
    figure.update_yaxes(title=None, showgrid=False)
    return figure


def occupancy_chart(frame):
    data = frame[frame["status"] != "Total informado"].sort_values("dwelling_count")
    figure = go.Figure(
        go.Bar(
            x=data["dwelling_count"],
            y=data["status"],
            orientation="h",
            marker_color=SECONDARY,
            text=[_br(v) for v in data["dwelling_count"]],
            textposition="auto",
            hovertemplate="%{y}<br>Domicílios: %{text}<extra></extra>",
        )
    )
    style(figure)
    figure.update_xaxes(title="Domicílios · diagnóstico a conferir", tickformat=",.0f", nticks=4)
    figure.update_yaxes(title=None, showgrid=False)
    return figure
