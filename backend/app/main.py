from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from .cleaning import clean_quotes
from .config import ROUTES
from .data import ensure_seed_file
from .indexer import airline_breakdown, aggregate_index, daily_index, lead_time_curve, route_index
from .models import DailyIndex, PaginatedFares, Route

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "sample" / "fares.csv"
ensure_seed_file(DATA_PATH)
RAW = pd.read_csv(DATA_PATH)
FARES = clean_quotes(RAW)
FARES["travel_date"] = pd.to_datetime(FARES["travel_date"]).dt.date
FARES["booking_date"] = pd.to_datetime(FARES["booking_date"]).dt.date

def _index_response(frame: pd.DataFrame) -> list[dict]:
    return frame.to_dict(orient="records")

app = FastAPI(title="APIx — Real-time Airfare Price Index", version="1.0.0", description="Synthetic demo API for an automated Indian airfare price index.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/health")
def health():
    return {"status": "ok", "records": len(FARES), "data_mode": "synthetic"}

@app.get("/api/routes", response_model=list[Route])
def routes():
    return [Route(route=r.route, origin=r.origin, destination=r.destination, weight=r.weight, distance_km=r.distance_km) for r in ROUTES]

@app.get("/api/index/daily", response_model=list[DailyIndex])
def index_daily():
    return _index_response(daily_index(FARES))

@app.get("/api/index/weekly")
def index_weekly():
    return _index_response(aggregate_index(FARES, "W"))

@app.get("/api/index/monthly")
def index_monthly():
    return _index_response(aggregate_index(FARES, "M"))

@app.get("/api/index/route/{origin}/{destination}")
def index_route(origin: str, destination: str):
    route = f"{origin.upper()}-{destination.upper()}"
    return {"route": route, "items": _index_response(route_index(FARES, route))}

@app.get("/api/index/lead-time")
def index_lead_time(route: str | None = None):
    return _index_response(lead_time_curve(FARES, route))

@app.get("/api/index/airlines")
def index_airlines():
    return _index_response(airline_breakdown(FARES))

@app.get("/api/index/heatmap")
def index_heatmap():
    daily = FARES.groupby(["route", "booking_date"], as_index=False).agg(avg_fare=("total_fare", "mean"))
    daily["date"] = daily.pop("booking_date").astype(str)
    daily["avg_fare"] = daily["avg_fare"].round(0)
    return _index_response(daily)

@app.get("/api/fares/raw", response_model=PaginatedFares)
def fares_raw(page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200), route: str | None = None, airline: str | None = None, advance_window: int | None = None, date: str | None = None):
    work = FARES.copy()
    if route:
        work = work[work.route.str.upper() == route.upper()]
    if airline:
        work = work[work.airline.str.lower() == airline.lower()]
    if advance_window:
        work = work[work.advance_window_days == advance_window]
    if date:
        work = work[work.booking_date.astype(str) == date]
    total = len(work)
    items = work.iloc[(page - 1) * page_size: page * page_size].copy()
    items["timestamp_collected"] = pd.to_datetime(items["timestamp_collected"], utc=True)
    return {"items": items.to_dict(orient="records"), "total": total, "page": page, "page_size": page_size}
