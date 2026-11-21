from html.parser import HTMLParser
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from src.config import ROOT


class CardValues(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = []
        self.reading = False

    def handle_starttag(self, tag, attrs):
        self.reading = tag == "p" and "oh-kpi-value" in dict(attrs).get("class", "")

    def handle_data(self, data):
        if self.reading:
            self.values.append(data)

    def handle_endtag(self, tag):
        if tag == "p":
            self.reading = False


def rendered_values(app):
    parser = CardValues()
    for element in app.get("html"):
        parser.feed(element.proto.body)
    return parser.values


@pytest.mark.parametrize("page", [ROOT / "app.py", *sorted((ROOT / "pages").glob("*.py"))])
def test_pages_render_without_exceptions(page: Path):
    app = AppTest.from_file(str(page), default_timeout=30).run()
    assert not app.exception
    assert len(app.main.title) == 1


def test_overview_values():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    assert rendered_values(app) == [
        "R$ 4.075,06",
        "37.323",
        "10.656",
        "3.053",
        "R$ 2.300,00",
        "13",
    ]
    assert app.main.title[0].value == "Quanto custa morar em Pato Branco?"


def test_market_filters_are_disabled_without_metadata():
    app = AppTest.from_file(str(ROOT / "pages/2_mercado_alugueis.py"), default_timeout=30).run()
    assert len(app.multiselect) == 3
    assert all(widget.disabled for widget in app.multiselect)
    assert len(app.date_input) == 0


def test_policy_filter_updates_table():
    app = AppTest.from_file(str(ROOT / "pages/4_politica_urbana.py"), default_timeout=30).run()
    assert len(app.dataframe[0].value) == 9
    app.multiselect[0].set_value(["Analisado"]).run()
    assert not app.exception
    assert app.dataframe[0].value.empty


def test_market_calculated_statistics():
    app = AppTest.from_file(str(ROOT / "pages/2_mercado_alugueis.py"), default_timeout=30).run()
    assert rendered_values(app) == [
        "13",
        "R$ 2.572,31",
        "R$ 2.300,00",
        "R$ 1.400,00",
        "R$ 4.500,00",
    ]


def test_multipage_navigation():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    for page in sorted((ROOT / "pages").glob("*.py")):
        app.switch_page(f"pages/{page.name}").run()
        assert not app.exception
        assert len(app.main.title) == 1
