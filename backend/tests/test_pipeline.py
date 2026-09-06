import pandas as pd
from app.cleaning import clean_quotes, deduplicate_quotes, remove_iqr_outliers
from app.indexer import daily_index, lead_time_curve

def sample():
    return pd.DataFrame([
        {"route":"DEL-BOM", "airline":"IndiGo", "travel_date":"2025-01-08", "booking_date":"2025-01-01", "advance_window_days":7, "fare_class":"Economy", "base_fare":100, "taxes":18, "udf":50, "convenience_fee":30, "total_fare":198, "source":"OTA"},
        {"route":"DEL-BOM", "airline":"IndiGo", "travel_date":"2025-01-08", "booking_date":"2025-01-01", "advance_window_days":7, "fare_class":"Economy", "base_fare":100, "taxes":18, "udf":50, "convenience_fee":30, "total_fare":198, "source":"OTA"},
        {"route":"DEL-BLR", "airline":"Air India", "travel_date":"2025-01-08", "booking_date":"2025-01-01", "advance_window_days":7, "fare_class":"Economy", "base_fare":120, "taxes":21, "udf":50, "convenience_fee":30, "total_fare":221, "source":"OTA"},
    ])

def test_deduplicate_quotes_keeps_one_record():
    assert len(deduplicate_quotes(sample())) == 2

def test_iqr_removes_extreme_value():
    df = pd.DataFrame({"total_fare": [100, 101, 99, 102, 1000]})
    assert len(remove_iqr_outliers(df)) == 4

def test_clean_quotes_fills_missing_and_deduplicates():
    df = sample()
    df.loc[0, "taxes"] = None
    result = clean_quotes(df)
    assert len(result) == 2 and result["taxes"].isna().sum() == 0

def test_daily_index_has_route_indices_and_base_100_scale():
    result = daily_index(sample())
    assert result.iloc[0]["period"] == "2025-01-01"
    assert "DEL-BOM" in result.iloc[0]["route_indices"]
    assert result.iloc[0]["index_value"] > 0

def test_lead_time_curve_groups_windows():
    result = lead_time_curve(sample())
    assert list(result.columns) == ["advance_window_days", "avg_fare"]
