from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEEDS = ROOT / "data" / "seeds"
PROCESSED = ROOT / "data" / "processed"
DATABASE = PROCESSED / "observatorio.duckdb"
MUNICIPALITY = "4118501"
QUALITY = {
    "verified": "Fonte primária e valor conferidos",
    "pending_source_verification": "Verificação documental pendente",
    "exploratory": "Levantamento exploratório",
    "derived": "Calculado a partir de dados identificados",
    "unavailable": "Dado indisponível",
}
