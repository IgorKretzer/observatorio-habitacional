import streamlit as st

from src.config import QUALITY
from src.visualization.components import limitations, load, setup, table

setup("Metodologia e fontes")
st.write(
    "O observatório é uma iniciativa independente de pesquisa sobre acesso à moradia "
    "em Pato Branco/PR (IBGE 4118501). Não possui vínculo com Prefeitura, IBGE ou IPARDES."
)
st.info(
    "Os 13 aluguéis somam R$ 33.440,00: média calculada R$ 2.572,31. "
    "A expectativa de R$ 2.587,69 na especificação diverge da lista original, "
    "que foi preservada. Mediana: R$ 2.300,00."
)
st.subheader("Conceitos e limites de comparação")
for title, text in [
    (
        "Renda individual e domiciliar",
        "Remuneração de um vínculo formal não é a renda de uma pessoa nem a soma dos rendimentos "
        "dos moradores de um domicílio. A RAIS não cobre diretamente toda a população.",
    ),
    (
        "Média e mediana",
        "A média é a soma dividida pelo número de observações. A mediana é o valor central "
        "ordenado. A mediana salarial exata não está disponível e não foi inferida.",
    ),
    (
        "Valores nominais e período",
        "Salários de 2022 a 2025 estão em reais correntes, sem deflação. As "
        "variações são nominais. "
        "Não se compara automaticamente com anúncios de outra data; a coleta "
        "inicial é desconhecida.",
    ),
    (
        "Faixas salariais acumuladas",
        "Os 20.818 vínculos até 2 salários mínimos estão incluídos nos 28.384 até 3. "
        "Percentuais usam 37.323 vínculos como denominador; as faixas não são somadas.",
    ),
    (
        "Aluguel anunciado e efetivamente pago",
        "Anúncios são preços pedidos, sujeitos a negociação e seleção. Não são contratos. "
        "Não se estima o aluguel médio municipal a partir da amostra de 13 registros.",
    ),
    (
        "Amostra de anúncios",
        "Uma única imobiliária, sem desenho probabilístico, data ou características informadas. "
        "Pode haver seleção e duplicação. IDs seed-* são técnicos. Nenhum "
        "bairro ou link foi inventado.",
    ),
    (
        "Vacância e disponibilidade",
        "Domicílio vago no Censo não implica oferta imediata de aluguel, condição de uso ou "
        "propriedade de investidores. Conceitos do diagnóstico aguardam validação.",
    ),
    (
        "Abrangência censitária",
        "Os totais por posse se limitam às categorias informadas da tabela 9928. Traços e "
        "ausências são NULL; os subtotais não são apresentados como totais municipais definitivos.",
    ),
    (
        "PNAD Contínua",
        "O desenho amostral e os domínios de divulgação devem ser respeitados. Não se assume "
        "representatividade para Pato Branco nem se produz estimativa municipal automática. "
        "Microdados deverão ser processados fora da interface com desenho e "
        "incerteza documentados.",
    ),
    (
        "Déficit e inadequação",
        "Déficit trata de necessidades de reposição ou acréscimo de moradias segundo metodologia "
        "específica; inadequação trata de condições das moradias existentes. "
        "Componentes, universos "
        "e sobreposições precisam ser avaliados conforme estudos da Fundação João Pinheiro. "
        "Nenhum dos dois foi calculado neste MVP.",
    ),
    (
        "Custos e valores ausentes",
        "Condomínio e IPTU desconhecidos não valem zero. Custo total só é apresentado quando "
        "os três componentes são conhecidos. Indicadores indisponíveis permanecem nulos.",
    ),
    (
        "Duplicação e processamento",
        "Chaves técnicas são únicas. Reprocessamento substitui o snapshot, sem acumular cópias. "
        "URLs repetidas são candidatas à revisão; nenhuma exclusão automática é realizada.",
    ),
]:
    with st.expander(title):
        st.write(text)
st.subheader("Qualidade e proveniência")
for key, description in QUALITY.items():
    st.write(f"**{key}** — {description}.")
st.write(
    "Indicadores calculados recebem derived e mantêm source_id, ano, metodologia e "
    "limitações. O catálogo junta também upstream_status, que preserva a pendência "
    "da fonte original. Anúncios mantêm validation_status exploratory. "
    "Derived não promove automaticamente a fonte a verified."
)
st.subheader("Fontes cadastradas")
table(load("sources"), "fontes")
st.caption(
    "Data de acesso vazia significa desconhecida; o índice legislativo foi consultado "
    "em 19/11/2026. Os valores numéricos foram fornecidos na pesquisa, sem documentação "
    "primária anexada. O acesso automatizado ao SIDRA retornou 403."
)
st.subheader("Catálogo de indicadores e rastreabilidade")
table(load("indicator_catalog"), "catalogo_indicadores")
st.subheader("Evolução planejada")
st.write(
    "Renda domiciliar, CadÚnico e registros municipais dependerão de autorização e "
    "tratamento adequado. PNAD Contínua e estudos da Fundação João Pinheiro exigirão "
    "validação de metodologia, cobertura geográfica e período. Nada disso é resultado atual."
)
limitations()
