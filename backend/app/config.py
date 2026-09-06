from dataclasses import dataclass

@dataclass(frozen=True)
class RouteConfig:
    route: str
    origin: str
    destination: str
    weight: float
    distance_km: int

ROUTES = [
    RouteConfig("DEL-BOM", "DEL", "BOM", 0.24, 1138),
    RouteConfig("DEL-BLR", "DEL", "BLR", 0.23, 1740),
    RouteConfig("BOM-BLR", "BOM", "BLR", 0.18, 842),
    RouteConfig("DEL-CCU", "DEL", "CCU", 0.14, 1305),
    RouteConfig("BLR-HYD", "BLR", "HYD", 0.11, 459),
    RouteConfig("MAA-DEL", "MAA", "DEL", 0.10, 1760),
]
ROUTE_WEIGHTS = {r.route: r.weight for r in ROUTES}
AIRLINES = ["IndiGo", "Air India", "Air India Express", "Akasa Air", "SpiceJet"]
ADVANCE_WINDOWS = [1, 7, 15, 30, 45]
FARE_CLASSES = ["Economy Saver", "Economy Flex", "Premium Economy"]
SOURCES = ["airline site", "MakeMyTrip", "Cleartrip", "ixigo"]

# Fixed weights mirror relative passenger-traffic proportions across major domestic sectors.
# In production these would be refreshed against the latest DGCA traffic tables.
