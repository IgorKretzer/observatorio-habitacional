import pandas as pd

from src.validation.quality import validate_frame


def read_housing(path) -> pd.DataFrame:
    # Traços são desconhecidos, nunca zeros.
    frame = pd.read_csv(path, dtype={"municipality_code": "string"}, na_values=["-", "..."])
    validate_frame("housing_stock", frame)
    return frame
