from __future__ import annotations
import pandas as pd
from .config import ROUTE_WEIGHTS

def _route_baselines(df: pd.DataFrame) -> pd.Series:
    return df.groupby("route")["total_fare"].transform("median")

def daily_index(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    work["period"] = pd.to_datetime(work["booking_date"]).dt.strftime("%Y-%m-%d")
    work["route_index"] = work["total_fare"] / work.groupby("route")["total_fare"].transform("median") * 100
    grouped = work.groupby(["period", "route"], as_index=False)["route_index"].mean()
    grouped["weight"] = grouped["route"].map(ROUTE_WEIGHTS).fillna(0)
    output = grouped.groupby("period").apply(lambda g: pd.Series({"index_value": (g.route_index * g.weight).sum() / g.weight.sum(), "route_indices": dict(zip(g.route, g.route_index.round(1)))}), include_groups=False).reset_index()
    output = output.sort_values("period").reset_index(drop=True)
    output["change_pct"] = output["index_value"].pct_change().fillna(0).mul(100).round(2)
    output["index_value"] = output["index_value"].round(2)
    return output

def aggregate_index(df: pd.DataFrame, frequency: str) -> pd.DataFrame:
    daily = daily_index(df)
    dates = pd.to_datetime(daily["period"])
    if frequency == "W":
        daily["period"] = dates.dt.to_period("W").apply(lambda x: x.start_time.strftime("%Y-%m-%d"))
    elif frequency == "M":
        daily["period"] = dates.dt.to_period("M").astype(str)
    output = daily.groupby("period", as_index=False).agg(index_value=("index_value", "mean"), change_pct=("change_pct", "sum"))
    output["index_value"] = output["index_value"].round(2)
    output["change_pct"] = output["change_pct"].round(2)
    return output

def route_index(df: pd.DataFrame, route: str) -> pd.DataFrame:
    work = df[df["route"] == route].copy()
    if work.empty:
        return pd.DataFrame(columns=["period", "index_value", "change_pct"])
    work["period"] = pd.to_datetime(work["booking_date"]).dt.strftime("%Y-%m-%d")
    baseline = work["total_fare"].median()
    out = work.groupby("period", as_index=False)["total_fare"].mean().rename(columns={"total_fare": "index_value"})
    out["index_value"] = (out["index_value"] / baseline * 100).round(2)
    out["change_pct"] = out["index_value"].pct_change().fillna(0).mul(100).round(2)
    return out

def lead_time_curve(df: pd.DataFrame, route: str | None = None) -> pd.DataFrame:
    work = df if route is None else df[df["route"] == route]
    return work.groupby("advance_window_days", as_index=False).agg(avg_fare=("total_fare", "mean")).round(2)

def airline_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("airline", as_index=False).agg(base_fare=("base_fare", "mean"), taxes=("taxes", "mean"), fees=("udf", "mean"), convenience_fee=("convenience_fee", "mean")).round(2)
