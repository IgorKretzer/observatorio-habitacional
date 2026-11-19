import streamlit as st

from src.visualization.components import load, setup, table

setup("Política urbana")
st.write(
    "Catálogo inicial de documentos municipais. Identificação no índice público "
    "não constitui análise jurídica nem avaliação dos resultados das políticas."
)
st.link_button(
    "Consultar catálogo municipal", "https://patobranco.pr.gov.br/legislacao-planejamento-urbano/"
)
documents = load("urban_policy_documents")
status = st.multiselect(
    "Situação da análise documental",
    ["Identificado", "Em análise", "Analisado", "Verificação pendente"],
)
if status:
    documents = documents[documents["analysis_status"].isin(status)]
table(documents, "catalogo_legislacao")
st.caption(
    "Índice consultado em 19/11/2026. Vigência, alterações, artigos e aplicação "
    "prática ainda não analisados. Referências iniciais não garantem consolidação normativa."
)
st.subheader("Solicitações oficiais de informação")
requests = load("information_requests")
if requests.empty:
    st.info("Nenhum envio confirmado cadastrado. Não há protocolos ou datas presumidos.")
else:
    table(requests, "solicitacoes_confirmadas")
