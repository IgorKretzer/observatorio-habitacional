import pandas as pd
import pytest

from src.config import SEEDS
from src.database import initialize_database


@pytest.fixture
def seeds():
    def read(table):
        return pd.read_csv(SEEDS / f"{table}.csv", dtype={"municipality_code": "string"})

    return read


@pytest.fixture
def database(tmp_path):
    path = tmp_path / "test.duckdb"
    initialize_database(path)
    return path
