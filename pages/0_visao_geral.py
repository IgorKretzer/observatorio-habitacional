import streamlit as st

from src.indicators.income import annual_changes, cumulative_shares
from src.visualization.charts import (
    cumulative_chart,
    housing_chart,
    rent_histogram,
    wages_chart,
)
from src.visualization.components import (
    catalog_card,
    kpi_grid,
    limitations,
    load,
    number,
    setup,
    table,
)
from src.visualization.layout import chart_section, explore, html, note, section

setup("Quanto custa morar em Pato Branco?", topic="Observatório Habitacional · Pato Branco / PR")
html(
    '<div class="oh-intro"><div><p class="oh-deck">Um observatório independente sobre renda, '
    "habitação e desenvolvimento urbano.</p><p>O Observatório Habitacional de Pato Branco reúne "
    "dados públicos e levantamentos independentes para investigar as condições de acesso à "
    "moradia no município. O projeto busca compreender a relação entre renda, aluguéis, "
    "estoque habitacional e políticas urbanas.</p></div>"
    '<aside class="oh-context"><strong>Um município, diferentes evidências</strong><br>'
    "Pato Branco · Paraná · IBGE 4118501<br>Trabalho formal: 2022–2025<br>"
    "Domicílios: Censo 2022<br>Anúncios: coleta não informada<br>"
    "Pesquisa independente, sem vínculo institucional.</aside></div>"
)
section(
    "O que os dados permitem observar",
    "Cada indicador mantém seu período, universo e fonte. Os valores abaixo não formam "
    "um índice único de acessibilidade habitacional.",
    number="01",
)
catalog = load("indicator_catalog")
specifications = [
    (
        "average_monthly_wage_2025",
        "Remuneração formal média",
        "Média mensal nominal dos vínculos formais; não é renda familiar nem mediana.",
    ),
    (
        "employment_relationships_2025",
        "Vínculos formais",
        "Relações formais de trabalho. Uma mesma pessoa pode manter mais de um vínculo.",
    ),
    (
        "tenure_Alugado",
        "Domicílios alugados · parcial",
        "Casas, casas de vila/condomínio e apartamentos. Subtotal das categorias analisadas.",
    ),
    (
        "occupancy_Vagos",
        "Domicílios vagos",
        "Valor do diagnóstico municipal, com conceitos por conferir. Não indica oferta de aluguel.",
    ),
    (
        "rental_amostra_informada_median",
        "Aluguel mediano · amostra",
        "Valor central dos 13 anúncios de uma única imobiliária; sem representatividade municipal.",
    ),
    (
        "rental_amostra_informada_count",
        "Anúncios analisados",
        "Amostra exploratória com IDs internos. Data, bairros e tipos de imóvel não informados.",
    ),
]
kpi_grid(
    [
        catalog_card(catalog, identifier, label=label, explanation=explanation)
        for identifier, label, explanation in specifications
    ]
)
wages = load("formal_wages").sort_values("year")
changes = annual_changes(wages)
latest = changes.sort_values("year").iloc[-1]
first_wage = number(wages.iloc[0]["average_monthly_wage"], 2)
chart_section(
    "Panorama da renda",
    wages_chart(wages),
    description="A série acompanha a remuneração média mensal dos vínculos "
    "formais em reais correntes.",
    interpretation=f"A remuneração informada passa de R$ {first_wage} "
    f"em {int(wages.iloc[0]['year'])} para R$ {number(latest['average_monthly_wage'], 2)} "
    f"em {int(latest['year'])}. A variação do último ano é nominal: "
    f"{number(latest['nominal_change_pct'], 1)}%."
    " Sem deflação, não se conclui ganho real de poder de compra.",
    source="RAIS/IPARDES · levantamento previamente informado",
    period="2022–2025",
)
chart_section(
    "Como se distribuem os vínculos formais",
    cumulative_chart(cumulative_shares(load("wage_distribution"), wages)),
    description="As faixas mostram proporções acumuladas, com o mesmo total de vínculos como base.",
    interpretation="Os vínculos até dois salários mínimos estão incluídos na faixa até três. "
    "As duas proporções não devem ser somadas.",
    source="RAIS/IPARDES",
    period="2025",
)
chart_section(
    "Panorama da habitação",
    housing_chart(load("housing_stock")),
    description="Condição de ocupação por tipo de domicílio nas categorias informadas.",
    interpretation="Nas categorias analisadas, há 6.853 casas, 229 casas de vila/condomínio e "
    "3.574 apartamentos alugados. O subtotal de 10.656 não é um total municipal definitivo. "
    "Categorias desconhecidas permanecem ausentes, sem imputação de zero.",
    source="IBGE · Censo 2022 · SIDRA 9928",
    period="2022",
)
chart_section(
    "Preços anunciados, em uma primeira amostra",
    rent_histogram(load("rental_costs")),
    description="Histograma em intervalos regulares de R$ 500; a linha tracejada marca a mediana.",
    interpretation="Os 13 valores informados variam entre R$ 1.400,00 e R$ 4.500,00. A mediana "
    "é R$ 2.300,00. São preços pedidos por uma única imobiliária, sem data de coleta informada.",
    source="Amostra exploratória previamente informada",
    period="Coleta não informada",
    status="Exploratório · fonte pendente de conferência",
)
section(
    "Explore a pesquisa",
    "Percorra os temas e consulte as evidências que sustentam cada leitura.",
    number="02",
)
explore()
section(
    "Transparência faz parte da pesquisa",
    "As pendências de verificação e os limites das bases são apresentados junto aos resultados.",
    number="03",
)
note(
    "Situação da pesquisa",
    "Versão 1.1: dados numéricos em verificação documental. "
    "O catálogo legislativo foi identificado; o conteúdo jurídico ainda não foi analisado.",
)
limitations()
with st.expander("Consultar e exportar todos os indicadores"):
    table(catalog, "indicadores_visao_geral")
