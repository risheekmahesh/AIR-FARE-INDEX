from __future__ import annotations
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import numpy as np
import pandas as pd
from .config import ADVANCE_WINDOWS, AIRLINES, FARE_CLASSES, ROUTES, SOURCES

COLUMNS = ["route", "airline", "travel_date", "booking_date", "advance_window_days", "fare_class", "base_fare", "taxes", "udf", "convenience_fee", "total_fare", "source", "timestamp_collected"]

def generate_sample_data(days: int = 75, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    start = date.today() - timedelta(days=days - 1)
    rows = []
    for day_offset in range(days):
        booking_date = start + timedelta(days=day_offset)
        for route_idx, route in enumerate(ROUTES):
            for window in ADVANCE_WINDOWS:
                travel_date = booking_date + timedelta(days=window)
                weekend = travel_date.weekday() >= 4
                festival = travel_date.month in (10, 11) and travel_date.day >= 15
                for airline_idx, airline in enumerate(AIRLINES):
                    distance_factor = route.distance_km / 1000
                    lead_factor = 1 + (45 - window) / 45 * 1.25
                    demand_factor = 1.12 if weekend else 1.0
                    festival_factor = 1.3 if festival else 1.0
                    airline_factor = 0.92 + airline_idx * 0.045
                    noise = rng.normal(1.0, 0.055)
                    base = 215 + distance_factor * 260 * lead_factor * demand_factor * festival_factor * airline_factor * noise
                    base = round(max(150, base), 2)
                    taxes = round(base * 0.18, 2)
                    udf = round(50 + distance_factor * 18, 2)
                    convenience_fee = round(35 + (airline_idx % 3) * 7, 2)
                    rows.append({"route": route.route, "airline": airline, "travel_date": travel_date.isoformat(), "booking_date": booking_date.isoformat(), "advance_window_days": window, "fare_class": FARE_CLASSES[(day_offset + airline_idx) % len(FARE_CLASSES)], "base_fare": base, "taxes": taxes, "udf": udf, "convenience_fee": convenience_fee, "total_fare": round(base + taxes + udf + convenience_fee, 2), "source": SOURCES[(route_idx + airline_idx) % len(SOURCES)], "timestamp_collected": datetime.combine(booking_date, datetime.min.time(), tzinfo=timezone.utc).isoformat()})
    return pd.DataFrame(rows, columns=COLUMNS)

def ensure_seed_file(path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        generate_sample_data().to_csv(target, index=False)
    return target
