import pytest

from src.visualization.charts import cumulative_chart, housing_chart, rent_histogram
from src.visualization.components import (
    IndicatorCard,
    catalog_card,
    display_formatter,
    kpi_markup,
)
from src.visualization.theme import COLORS


def test_cards_preserve_reference_and_source(database):
    from src.database import query

    catalog = query("SELECT * FROM indicator_catalog", db_path=database)
    card = catalog_card(catalog, "average_monthly_wage_2025")
    assert card.value == "R$ 4.075,06"
    assert card.year == "2025"
    assert card.source_id == "rais_2025"
    assert card.quality_status == "derived"
    assert card.source_status == "pending_source_verification"
    rental = catalog_card(catalog, "rental_amostra_informada_median")
    assert rental.year == "Coleta não informada"
    assert rental.status == "exploratory"


def test_card_content_is_escaped():
    card = IndicatorCard(
        "<script>test</script>",
        "13",
        "anúncios",
        "Não informado",
        "Pesquisa",
        "exploratory",
        "<img src=x onerror=alert(1)>",
    )
    markup = kpi_markup([card])
    assert "<script>" not in markup
    assert "<img " not in markup
    assert "&lt;script&gt;" in markup


@pytest.mark.parametrize(
    "column,value,expected",
    [
        ("year", 2025, "2025"),
        ("monthly_rent", 2300, "R$ 2.300,00"),
        ("percentage", 55.7774, "55,8%"),
        ("employment_relationships", 37323, "37.323"),
    ],
)
def test_brazilian_display(column, value, expected):
    assert display_formatter(column)(value) == expected


def test_charts_preserve_unknowns_and_histogram_intervals(seeds):
    figure = housing_chart(seeds("housing_stock"))
    other = next(trace for trace in figure.data if trace.name == "Outra condição")
    assert list(other.x) == [159, None, None]
    histogram = rent_histogram(seeds("rental_listings"))
    assert histogram.data[0].xbins.size == 500
    assert len(histogram.data[0].x) == 13
    assert histogram.layout.shapes[0].x0 == 2300


def test_accumulated_distribution_is_not_stacked(seeds):
    from src.indicators.income import cumulative_shares

    frame = cumulative_shares(seeds("wage_distribution"), seeds("formal_wages"))
    figure = cumulative_chart(frame)
    assert all(trace.type == "scatter" for trace in figure.data)
    assert list(figure.data[-1].x) == frame["percentage"].tolist()
    assert all("acumulado" in label for label in figure.data[-1].y)


def luminance(color):
    components = [int(color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in components]
    return sum(a * b for a, b in zip(linear, [0.2126, 0.7152, 0.0722]))


@pytest.mark.parametrize(
    "foreground,background",
    [
        (COLORS["text"], COLORS["background"]),
        (COLORS["muted"], COLORS["background"]),
        (COLORS["muted"], COLORS["surface"]),
        (COLORS["primary"], COLORS["background"]),
        ("#6B2825", "#F3E7DD"),
        ("#355449", "#EAF0EA"),
        ("#56524B", "#EAE5DC"),
    ],
)
def test_text_tokens_meet_aa_contrast(foreground, background):
    light, dark = sorted([luminance(foreground), luminance(background)], reverse=True)
    assert (light + 0.05) / (dark + 0.05) >= 4.5
