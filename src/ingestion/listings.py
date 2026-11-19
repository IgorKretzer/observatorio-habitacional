import pandas as pd

from src.validation.quality import validate_frame


def read_listings(path_or_buffer) -> pd.DataFrame:
    frame = pd.read_csv(path_or_buffer, dtype={"listing_id": "string", "source_id": "string"})
    validate_frame("rental_listings", frame)
    return frame


def filter_listings(frame, selections, period=None):
    result = frame.copy()
    for column in ("agency", "property_type", "neighborhood"):
        selected = selections.get(column, [])
        if selected:
            result = result[result[column].isin(selected)]
    if period and isinstance(period, (tuple, list)) and len(period) == 2:
        dates = pd.to_datetime(result["collected_at"])
        result = result[dates.between(pd.Timestamp(period[0]), pd.Timestamp(period[1]))]
    return result
