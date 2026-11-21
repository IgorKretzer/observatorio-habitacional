from html import escape
from urllib.parse import urlparse

import pandas as pd
import streamlit as st

from src.config import QUALITY, ROOT
from src.visualization.components import limitations, load, setup, table
from src.visualization.layout import html, note, section

setup(
    "Metodologia e fontes",
    topic="Transparência da pesquisa",
    description="De onde vêm os números, como são calculados e o que ainda não permitem concluir.",
    period="Pato Branco / PR · IBGE 4118501 · períodos identificados em cada fonte",
)
section("Sobre o projeto")
st.write(
    "O Observatório Habitacional de Pato Branco é uma iniciativa independente de pesquisa "
    "sobre as condições econômicas de acesso à moradia. Reúne dados públicos e levantamentos "
    "identificados, sem vínculo institucional com Prefeitura, IBGE ou IPARDES."
)
note(
    "Situação desta edição",
    "A versão 1.1 reorganiza a apresentação; não altera os valores "
    "nem valida automaticamente as fontes. Os dados numéricos continuam em verificação "
    "documental, e os anúncios permanecem exploratórios.",
)
section(
    "Fontes utilizadas",
    "Uma fonte identificada não é necessariamente uma fonte já conferida. "
    "Datas de acesso desconhecidas são mantidas como informação ausente.",
)
sources = load("sources")
catalog = load("indicator_catalog")
sources["associated_indicators"] = (
    sources["source_id"]
    .map(
        catalog.groupby("source_id")["indicator_name"].agg(
            lambda names: "; ".join(sorted(set(names)))
        )
    )
    .fillna("Nenhum indicador numérico associado")
)
for row in sources.to_dict("records"):
    reference = (
        str(int(row["reference_year"])) if pd.notna(row["reference_year"]) else "Não informado"
    )
    access = (
        pd.Timestamp(row["retrieved_at"]).strftime("%d/%m/%Y")
        if pd.notna(row["retrieved_at"])
        else "Não informada"
    )
    with st.expander(f"{row['institution']} · {row['dataset_name']}"):
        url = row["source_url"]
        link = (
            f'<a href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">'
            "Consultar fonte declarada ↗</a>"
            if pd.notna(url) and urlparse(url).scheme in {"http", "https"}
            else "<p>URL original ainda não informada.</p>"
        )
        html(
            f'<article class="oh-source"><h3>{escape(row["dataset_name"])}</h3>'
            f"<p>Instituição: {escape(row['institution'])}</p>"
            f"<p>Ano: {escape(reference)} · Acesso: {access}</p>"
            f"<p>Status: {escape(QUALITY[row['status']])}</p>"
            f"<p>Indicadores associados: {escape(row['associated_indicators'])}</p>"
            f"<p>{escape(row['notes'])}</p>{link}</article>"
        )
table(
    sources,
    "fontes",
    columns=[
        "institution",
        "dataset_name",
        "reference_year",
        "retrieved_at",
        "status",
        "source_url",
        "associated_indicators",
    ],
)
section("Metodologia de cálculo")
for title, text in [
    (
        "Remuneração, média e mediana",
        "A média é a soma das remunerações dividida pelo número de observações do universo "
        "informado. A mediana é o valor central ordenado. A mediana salarial exata é indisponível "
        "e não pode ser deduzida da média. Remuneração individual, de um "
        "vínculo e renda domiciliar "
        "são conceitos diferentes.",
    ),
    (
        "Variação nominal anual",
        "Variação (%) = (média do ano / média do ano imediatamente anterior − 1) × 100. "
        "Sem ano anterior consecutivo, base válida ou denominador "
        "positivo, não se calcula o resultado. "
        "Os valores são nominais, sem correção pela inflação.",
    ),
    (
        "Distribuição salarial acumulada",
        "Percentual = vínculos da faixa acumulada / total de vínculos do "
        "mesmo ano e município × 100. "
        "Os 20.818 vínculos até 2 salários mínimos estão contidos nos 28.384 até 3; "
        "o denominador é 37.323. Essas faixas não podem ser somadas.",
    ),
    (
        "Domicílios e subtotais",
        "Os subtotais por posse somam apenas as três categorias informadas da SIDRA 9928. "
        "São parciais, sem alegação de cobertura municipal completa. Uma "
        "soma que contém categorias "
        "desconhecidas permanece indisponível; traços e ausências não viram zero.",
    ),
    (
        "Anúncios, média e mediana",
        "A média soma os valores de aluguel conhecidos e divide pela "
        "quantidade de valores conhecidos. "
        "A mediana ordena esses valores e toma o centro. A contagem de "
        "anúncios inclui todos os registros, "
        "mesmo se o aluguel de algum registro for desconhecido. São preços pedidos, não contratos.",
    ),
    (
        "Classes dos gráficos de aluguel",
        "O histograma usa classes regulares de R$ 500, ancoradas em múltiplos de 500. "
        "O início é inclusivo, o fim é exclusivo. A linha tracejada marca a mediana. "
        "O gráfico separado de faixas mantém os cortes originais em R$ 1.500, 2.500 e 3.500, "
        "com limite superior inclusivo; seus grupos não têm a mesma "
        "amplitude e não representam densidade.",
    ),
    (
        "Custo total, ausências e duplicados",
        "Custo total = aluguel + condomínio + IPTU mensal, somente se os três forem conhecidos. "
        "URLs repetidas são candidatas a revisão; nenhuma exclusão é automática. IDs seed-* são "
        "técnicos. Nenhuma característica de imóvel foi inventada.",
    ),
]:
    with st.expander(title):
        st.write(text)
note(
    "Conferência da amostra original",
    "Os 13 aluguéis somam R$ 33.440,00, com média R$ 2.572,31 "
    "e mediana R$ 2.300,00. O valor esperado de R$ 2.587,69 na especificação inicial "
    "não corresponde à lista fornecida. Os dados originais foram preservados.",
)
section("Limitações e universos de interpretação")
limitations()
for title, text in [
    (
        "Renda individual, familiar e cobertura da RAIS",
        "Vínculos não são pessoas distintas nem todas as pessoas ocupadas. A RAIS não representa "
        "diretamente a renda de todas as famílias nem a população municipal.",
    ),
    (
        "Vacância, déficit e inadequação",
        "Vacância censitária não é oferta imediata de locação e não informa a propriedade por "
        "investidores. Déficit envolve necessidades de reposição ou acréscimo de moradias segundo "
        "metodologia específica; inadequação envolve condições de moradias existentes. "
        "Não se calcula déficit subtraindo alugados de vagos. A aplicação de metodologias da "
        "Fundação João Pinheiro depende de dados, universos e sobreposições validados.",
    ),
    (
        "PNAD Contínua e estimativas municipais",
        "Devem ser respeitados desenho amostral e domínios de divulgação. Não se assume "
        "representatividade municipal para Pato Branco nem se geram estimativas automaticamente. "
        "Microdados serão processados fora da interface, com incerteza e cobertura documentadas.",
    ),
    (
        "Temporalidade e amostra de anúncios",
        "A coleta dos 13 anúncios de uma única imobiliária não tem data informada. "
        "Não há amostragem probabilística e pode haver seleção e duplicação. Não se cruza "
        "automaticamente essa amostra com RAIS de outro período para criar um índice oficial.",
    ),
]:
    with st.expander(title):
        st.write(text)
section("Qualidade dos dados", "Cálculo derivado não promove a fonte original a validada.")
for key, description in QUALITY.items():
    st.write(f"**{key}** — {description}.")
st.write(
    "O catálogo preserva source_id, reference_year, unit, methodology e limitations. "
    "O campo upstream_status registra a situação da fonte utilizada. Anúncios conservam "
    "validation_status exploratory. Dado indisponível permanece nulo."
)
section("Atualizações e agenda de pesquisa")
st.write(
    "O índice legislativo foi consultado em 19/11/2026. Os números foram informados pela "
    "pesquisa sem documentos primários anexados; a tentativa automatizada de acesso ao SIDRA "
    "retornou 403. A mudança visual da versão 1.1 não é uma atualização dessas fontes."
)
st.write(
    "Próximas integrações: renda domiciliar, CadÚnico, registros administrativos municipais, "
    "PNAD Contínua e estudos da Fundação João Pinheiro, condicionadas à validação "
    "metodológica e ao tratamento adequado dos dados."
)
section(
    "Exportação e reprodução",
    "Os CSVs completos mantêm a estrutura original; JSONs públicos "
    "oferecem um contrato separado para uma futura interface.",
)
table(
    catalog,
    "catalogo_indicadores",
    columns=[
        "indicator_name",
        "reference_year",
        "value",
        "unit",
        "quality_status",
        "source_id",
        "upstream_status",
        "methodology",
        "limitations",
    ],
)
public = ROOT / "public/data"
for name, label in [
    ("indicators.json", "Indicadores e proveniência · JSON"),
    ("sources.json", "Fontes públicas · JSON"),
    ("manifest.json", "Manifesto · JSON"),
]:
    if (public / name).exists():
        st.download_button(
            label, (public / name).read_bytes(), name, mime="application/json", key=f"json_{name}"
        )
