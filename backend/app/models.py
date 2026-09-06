from datetime import date, datetime
from pydantic import BaseModel, Field

class Route(BaseModel):
    route: str
    origin: str
    destination: str
    weight: float
    distance_km: int

class FareQuote(BaseModel):
    route: str
    airline: str
    travel_date: date
    booking_date: date
    advance_window: int = Field(alias="advance_window_days")
    fare_class: str
    base_fare: float
    taxes: float
    udf: float
    convenience_fee: float
    total_fare: float
    source: str
    timestamp_collected: datetime

class DailyIndex(BaseModel):
    period: str
    index_value: float
    change_pct: float
    route_indices: dict[str, float]

class PaginatedFares(BaseModel):
    items: list[FareQuote]
    total: int
    page: int
    page_size: int
