"""Entrada única: st.navigation substitui a descoberta automática de pages/."""

import streamlit as st

from src.visualization.layout import footer
from src.visualization.theme import PAGES

st.set_page_config(
    page_title="Observatório Habitacional de Pato Branco",
    layout="wide",
    initial_sidebar_state="collapsed",
)
navigation = st.navigation(
    [
        st.Page(path, title=title, default=index == 0, url_path=route or None)
        for index, (path, title, route) in enumerate(PAGES)
    ],
    position="top",
)
navigation.run()
footer()
