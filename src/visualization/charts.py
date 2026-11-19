import pandas as pd
import plotly.express as px

PRIMARY = "#8B342F"
SECONDARY = "#47635C"


def style(figure):
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "#171717"},
        margin={"l": 10, "r": 10, "t": 45, "b": 10},
        separators=",.",
        legend_title_text="",
    )
    return figure


def wages_chart(frame):
    return style(
        px.line(
            frame,
            x="year",
            y="average_monthly_wage",
            markers=True,
            labels={"year": "Ano", "average_monthly_wage": "Remuneração nominal (R$/mês)"},
            color_discrete_sequence=[PRIMARY],
            title="Remuneração formal média • nominal",
        ).update_xaxes(dtick=1)
    )


def rented_chart(frame):
    rented = frame[frame["tenure_status"] == "Alugado"]
    return style(
        px.bar(
            rented,
            x="dwelling_type",
            y="dwelling_count",
            labels={"dwelling_type": "Tipo de domicílio", "dwelling_count": "Domicílios alugados"},
            color_discrete_sequence=[SECONDARY],
            title="Alugados • categorias analisadas • 2022",
        )
    )


def cumulative_chart(frame):
    return style(
        px.bar(
            frame.sort_values("wage_band_order"),
            x="percentage",
            y="wage_band",
            orientation="h",
            text="employment_relationships",
            range_x=[0, 100],
            labels={
                "percentage": "Percentual dos vínculos (%)",
                "wage_band": "Faixa acumulada",
                "employment_relationships": "Vínculos",
            },
            color_discrete_sequence=[PRIMARY],
            title="Faixas acumuladas • 2025 • não somar",
        )
    )


def rent_histogram(frame):
    return style(
        px.histogram(
            frame,
            x="monthly_rent",
            nbins=8,
            color_discrete_sequence=[PRIMARY],
            labels={"monthly_rent": "Aluguel anunciado (R$/mês)"},
            title="Distribuição da amostra exploratória",
        ).update_yaxes(title="Anúncios")
    )


def rental_bands(frame):
    bands = pd.cut(
        frame["monthly_rent"],
        bins=[0, 1500, 2500, 3500, float("inf")],
        labels=["Até R$ 1.500", "R$ 1.500–2.500", "R$ 2.500–3.500", "Acima de R$ 3.500"],
        include_lowest=True,
    )
    counts = bands.value_counts(sort=False).rename_axis("Faixa").reset_index(name="Anúncios")
    return style(
        px.bar(
            counts,
            x="Faixa",
            y="Anúncios",
            color_discrete_sequence=[SECONDARY],
            title="Faixas de aluguel • limites superiores inclusivos",
        )
    )


def housing_chart(frame):
    return style(
        px.bar(
            frame,
            x="dwelling_type",
            y="dwelling_count",
            color="tenure_status",
            barmode="group",
            color_discrete_sequence=[SECONDARY, PRIMARY, "#70665A", "#ACA59A"],
            labels={
                "dwelling_type": "Tipo",
                "dwelling_count": "Domicílios",
                "tenure_status": "Condição",
            },
            title="Condição de ocupação • categorias analisadas",
        )
    )


def occupancy_chart(frame):
    return style(
        px.bar(
            frame[frame["status"] != "Total informado"],
            x="status",
            y="dwelling_count",
            labels={"status": "Situação", "dwelling_count": "Domicílios"},
            color_discrete_sequence=[SECONDARY],
            title="Situação de ocupação • 2022 • fonte pendente",
        )
    )
