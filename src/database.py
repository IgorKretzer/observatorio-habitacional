"""Snapshots reproduzíveis; consultas com conexões curtas e somente leitura."""

import hashlib
import json
from pathlib import Path

import duckdb
import pandas as pd

from src.config import DATABASE, MUNICIPALITY, SEEDS
from src.indicators.housing import rental_statistics, tenure_subtotals
from src.schemas import SCHEMAS
from src.validation.quality import validate_frame, validate_relations


def seed_fingerprint(seed_dir=SEEDS):
    digest = hashlib.sha256(b"pipeline-v3")
    for path in sorted(Path(seed_dir).glob("*.csv")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def derived_indicators(frames):
    rows = []

    def add(key, name, category, year, value, unit, source, method, limitation):
        rows.append(
            {
                "indicator_id": key,
                "indicator_name": name,
                "category": category,
                "municipality_code": MUNICIPALITY,
                "reference_year": year,
                "value": value,
                "unit": unit,
                "source_id": source,
                "methodology": method,
                "quality_status": "unavailable" if pd.isna(value) else "derived",
                "limitations": limitation,
            }
        )

    for row in frames["formal_wages"].to_dict("records"):
        for field, name, unit in [
            ("employment_relationships", "Vínculos formais", "vínculos"),
            ("average_monthly_wage", "Remuneração formal média nominal", "BRL/mês"),
            ("median_wage", "Mediana salarial", "BRL/mês"),
        ]:
            add(
                f"{field}_{row['year']}",
                name,
                "Renda e trabalho",
                row["year"],
                row[field],
                unit,
                row["source_id"],
                f"Campo {field} da base formal",
                "Fonte pendente; vínculos não são pessoas; valores nominais. "
                "Mediana exata não informada.",
            )
    for row in tenure_subtotals(frames["housing_stock"]).to_dict("records"):
        add(
            f"tenure_{row['tenure_status']}",
            f"Domicílios: {row['tenure_status']}",
            "Estoque habitacional",
            row["year"],
            row["dwelling_count"],
            "domicílios",
            row["source_id"],
            "Soma das categorias informadas somente se todas conhecidas",
            "Subtotal parcial; fonte pendente; não é total municipal definitivo.",
        )
    for row in frames["occupancy_status"].to_dict("records"):
        add(
            f"occupancy_{row['status']}",
            row["status"],
            "Estoque habitacional",
            row["year"],
            row["dwelling_count"],
            "domicílios",
            row["source_id"],
            "Valor informado pelo diagnóstico; conceitos ainda por conferir",
            "Fonte pendente. Vacância não é disponibilidade para locação.",
        )
    for source, group in frames["rental_listings"].groupby("source_id"):
        statistics = rental_statistics(group)
        years = pd.to_datetime(group["collected_at"], errors="raise").dt.year
        year = int(years.iloc[0]) if years.notna().all() and years.nunique() == 1 else None
        for field, name in [
            ("count", "Anúncios analisados"),
            ("mean", "Aluguel médio anunciado"),
            ("median", "Aluguel mediano anunciado"),
        ]:
            add(
                f"rental_{source}_{field}",
                name,
                "Mercado de aluguéis",
                year,
                statistics[field],
                "anúncios" if field == "count" else "BRL/mês",
                source,
                f"{field} dos aluguéis conhecidos; contagem inclui todos os registros",
                "Amostra exploratória; coleta pode ser desconhecida; "
                "não estima aluguel municipal; fonte pendente de conferência.",
            )
    return pd.DataFrame(rows, columns=SCHEMAS["indicators"])


def initialize_database(db_path=DATABASE, seed_dir=SEEDS):
    db_path, seed_dir = Path(db_path), Path(seed_dir)
    frames = {}
    for table, columns in SCHEMAS.items():
        frame = pd.read_csv(
            seed_dir / f"{table}.csv",
            dtype={name: "string" for name, kind in columns.items() if kind.startswith("VARCHAR")},
        )
        validate_frame(table, frame)
        frames[table] = frame[list(columns)]
    validate_relations(frames)
    calculated = derived_indicators(frames)
    frames["indicators"] = (
        calculated
        if frames["indicators"].empty
        else pd.concat([frames["indicators"], calculated], ignore_index=True)
    )
    validate_frame("indicators", frames["indicators"])
    validate_relations(frames)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    staged = db_path.with_suffix(".staging.duckdb")
    try:
        with duckdb.connect(str(staged)) as connection:
            connection.execute("BEGIN TRANSACTION")
            for table, columns in SCHEMAS.items():
                definition = ", ".join(f'"{name}" {kind}' for name, kind in columns.items())
                connection.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
                connection.execute(f'CREATE TABLE "{table}" ({definition})')
                connection.register("incoming", frames[table])
                connection.execute(f'INSERT INTO "{table}" SELECT * FROM incoming')
                connection.unregister("incoming")
            connection.execute("""
                CREATE OR REPLACE VIEW rental_costs AS
                SELECT *, monthly_rent + condominium_fee + iptu_monthly AS total_monthly_cost,
                    CASE WHEN monthly_rent IS NOT NULL AND condominium_fee IS NOT NULL
                              AND iptu_monthly IS NOT NULL THEN 'Completo'
                         ELSE 'Incompleto — componentes desconhecidos' END AS cost_completeness
                FROM rental_listings
            """)
            for table in (
                "formal_wages",
                "wage_distribution",
                "housing_stock",
                "occupancy_status",
                "rental_costs",
                "indicators",
            ):
                year = (
                    "d.reference_year"
                    if table == "indicators"
                    else "EXTRACT(YEAR FROM d.collected_at)::INTEGER"
                    if table == "rental_costs"
                    else "d.year"
                )
                municipality = (
                    f"'{MUNICIPALITY}'" if table == "rental_costs" else "d.municipality_code"
                )
                unit = {
                    "formal_wages": "BRL/mês; vínculos; estabelecimentos",
                    "wage_distribution": "vínculos",
                    "housing_stock": "domicílios",
                    "occupancy_status": "domicílios",
                    "rental_costs": "BRL/mês; m²",
                    "indicators": "conforme coluna unit",
                }[table]
                method = {
                    "formal_wages": "Série nominal de vínculos formais",
                    "wage_distribution": "Faixas acumuladas; não somar",
                    "housing_stock": "Categorias parciais da SIDRA 9928",
                    "occupancy_status": "Diagnóstico; conceitos por conferir",
                    "rental_costs": "Anúncios; não são contratos; total exige 3 componentes",
                    "indicators": "Conforme coluna methodology",
                }[table]
                connection.execute(f"""
                    CREATE OR REPLACE VIEW export_{table} AS
                    SELECT d.*, s.institution AS source_institution,
                        s.dataset_name AS source_dataset, s.source_url,
                        s.status AS source_status, {year} AS reference_year_export,
                        {municipality} AS municipality_code_export,
                        s.notes AS source_limitations, '{unit}' AS unit_export,
                        '{method}' AS methodology_export
                    FROM {table} d JOIN sources s USING(source_id)
                """)
            connection.execute("""
                CREATE OR REPLACE VIEW indicator_catalog AS
                SELECT i.*, s.status AS upstream_status, s.dataset_name AS source_name,
                    s.source_url, s.notes AS source_notes
                FROM indicators i JOIN sources s USING(source_id)
            """)
            connection.execute("COMMIT")
            report = {
                "fingerprint": seed_fingerprint(seed_dir),
                "rows": {table: len(frame) for table, frame in frames.items()},
                "warnings": [
                    "Fontes numéricas pendentes de conferência documental",
                    "Amostra exploratória com data de coleta desconhecida",
                    "Coerência aritmética do estoque não valida conceitos censitários",
                ],
            }
            for table in SCHEMAS:
                connection.execute(f'SELECT * FROM "{table}"').df().to_parquet(
                    db_path.parent / f"{table}.parquet", engine="pyarrow", index=False
                )
        staged.replace(db_path)
        db_path.with_suffix(".report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        return report
    finally:
        if staged.exists():
            staged.unlink()


def query(sql, parameters=None, db_path=DATABASE):
    with duckdb.connect(str(db_path), read_only=True) as connection:
        return connection.execute(sql, parameters or []).df()
