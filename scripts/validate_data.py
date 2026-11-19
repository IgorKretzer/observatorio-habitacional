import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.database import initialize_database  # noqa: E402

if __name__ == "__main__":
    with TemporaryDirectory() as directory:
        report = initialize_database(Path(directory) / "validation.duckdb")
    print(json.dumps(report, indent=2, ensure_ascii=False))
