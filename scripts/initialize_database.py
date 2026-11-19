import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.database import initialize_database  # noqa: E402

if __name__ == "__main__":
    print(json.dumps(initialize_database(), indent=2, ensure_ascii=False))
