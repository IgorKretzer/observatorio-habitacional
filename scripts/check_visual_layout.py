"""Verificação visual opcional. Requer Playwright apenas no ambiente de desenvolvimento."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ROUTES = [
    ("", "Quanto custa morar em Pato Branco?"),
    ("renda-trabalho", "Renda e trabalho"),
    ("mercado-alugueis", "Mercado de aluguéis"),
    ("estoque-habitacional", "Estoque habitacional"),
    ("politica-urbana", "Política urbana"),
    ("metodologia-fontes", "Metodologia e fontes"),
]
VIEWPORTS = [(1440, 1100), (1024, 900), (768, 1024), (390, 844), (320, 800)]


def check_visual_layout(base_url, output, executable=None):
    from playwright.sync_api import sync_playwright

    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    results, errors = [], []
    with sync_playwright() as runtime:
        arguments = {"headless": True}
        if executable:
            arguments["executable_path"] = executable
        browser = runtime.chromium.launch(**arguments)
        page = browser.new_page(viewport={"width": 1440, "height": 1100}, device_scale_factor=1)
        page.on("pageerror", lambda error: errors.append(str(error)))
        for route, heading in ROUTES:
            page.goto(base_url.rstrip("/") + "/" + route, wait_until="domcontentloaded")
            page.get_by_role("heading", name=heading, exact=True).wait_for(timeout=45000)
            page.locator("footer.oh-footer").wait_for(state="attached", timeout=45000)
            page.evaluate("document.fonts.ready")
            assert page.get_by_test_id("stException").count() == 0, heading
            if route in {"", "renda-trabalho", "mercado-alugueis", "estoque-habitacional"}:
                page.locator(".js-plotly-plot").first.wait_for(state="attached", timeout=30000)
            for width, height in VIEWPORTS:
                page.set_viewport_size({"width": width, "height": height})
                page.wait_for_timeout(350)
                page.locator(".oh-brand").scroll_into_view_if_needed()
                page.screenshot(path=str(output / f"{route or 'overview'}-{width}.png"))
                data = page.evaluate("""() => ({
                    innerWidth: innerWidth, pageWidth: document.documentElement.scrollWidth,
                    font: getComputedStyle(document.querySelector('h1')).fontFamily,
                    cards: [...document.querySelectorAll('.oh-kpi')].map(e => ({
                        left: e.getBoundingClientRect().left, right: e.getBoundingClientRect().right
                    })),
                    charts: [...document.querySelectorAll('.js-plotly-plot')].map(e => ({
                        left: e.getBoundingClientRect().left, right: e.getBoundingClientRect().right
                    })),
                })""")
                assert data["pageWidth"] <= width, (route, width, data)
                assert all(
                    c["left"] >= 0 and c["right"] <= width + 1
                    for c in [*data["cards"], *data["charts"]]
                ), (route, width, data)
                if width in {1440, 390}:
                    for index, chart in enumerate(page.locator(".js-plotly-plot").all()):
                        chart.screenshot(
                            path=str(output / f"{route or 'overview'}-chart-{index}-{width}.png")
                        )
                results.append({"route": route, "width": width, "ok": True, **data})
            print(json.dumps({"page": route or "overview", "viewports": 5, "ok": True}), flush=True)
        assert not errors, errors
        browser.close()
    (output / "report.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8501")
    parser.add_argument("--output", type=Path, default=Path("artifacts/visual"))
    parser.add_argument("--browser-executable")
    args = parser.parse_args()
    result = check_visual_layout(args.base_url, args.output, args.browser_executable)
    print(f"{len(result)} combinações de página/largura verificadas")
