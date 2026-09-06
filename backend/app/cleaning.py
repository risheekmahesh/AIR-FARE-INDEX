from __future__ import annotations
import pandas as pd

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    numeric = [c for c in ["base_fare", "taxes", "udf", "convenience_fee", "total_fare"] if c in result]
    for col in numeric:
        result[col] = result[col].fillna(result[col].median())
    for col in ["fare_class", "source"]:
        if col in result:
            result[col] = result[col].fillna("Unknown")
    return result

def deduplicate_quotes(df: pd.DataFrame) -> pd.DataFrame:
    keys = [c for c in ["route", "airline", "travel_date", "booking_date", "advance_window_days", "fare_class"] if c in df]
    return df.drop_duplicates(subset=keys, keep="last").reset_index(drop=True)

def remove_iqr_outliers(df: pd.DataFrame, column: str = "total_fare", multiplier: float = 1.5) -> pd.DataFrame:
    if df.empty or column not in df:
        return df.copy()
    q1, q3 = df[column].quantile([0.25, 0.75])
    iqr = q3 - q1
    if iqr == 0:
        return df.copy()
    low, high = q1 - multiplier * iqr, q3 + multiplier * iqr
    return df[df[column].between(low, high)].reset_index(drop=True)

def clean_quotes(df: pd.DataFrame) -> pd.DataFrame:
    return remove_iqr_outliers(deduplicate_quotes(handle_missing_values(df)))
