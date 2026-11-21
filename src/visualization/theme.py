"""Tokens da identidade visual, compartilhados por CSS e Plotly."""

COLORS = {
    "background": "#F3F0E9",
    "surface": "#FFFFFF",
    "text": "#171717",
    "muted": "#626262",
    "primary": "#8B342F",
    "secondary": "#47635C",
    "border": "#DDD8D0",
    "alternate": "#EAE5DC",
}
FONT = "Inter, Arial, sans-serif"
HEADING_FONT = "'Source Serif 4', Georgia, serif"
STATUS_LABELS = {
    "verified": "Conferido",
    "pending_source_verification": "Verificação pendente",
    "exploratory": "Amostra exploratória",
    "derived": "Calculado",
    "unavailable": "Em preparação",
}
PAGES = [
    ("pages/0_visao_geral.py", "Visão Geral", ""),
    ("pages/1_renda_trabalho.py", "Renda e Trabalho", "renda-trabalho"),
    ("pages/2_mercado_alugueis.py", "Mercado de Aluguéis", "mercado-alugueis"),
    ("pages/3_estoque_habitacional.py", "Estoque Habitacional", "estoque-habitacional"),
    ("pages/4_politica_urbana.py", "Política Urbana", "politica-urbana"),
    ("pages/5_metodologia_fontes.py", "Metodologia e Fontes", "metodologia-fontes"),
]
