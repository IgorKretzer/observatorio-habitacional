from pathlib import Path

import pandas as pd

from src.validation.quality import validate_frame


def read_wages(path: Path) -> pd.DataFrame:
    """CSV padronizado ou Excel; conversão de layouts originais é etapa externa."""
    frame = (
        pd.read_excel(path, dtype={"municipality_code": "string"})
        if path.suffix.lower() == ".xlsx"
        else pd.read_csv(path, dtype={"municipality_code": "string"})
    )
    validate_frame("formal_wages", frame)
    return frame
