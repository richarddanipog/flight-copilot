import json
from pathlib import Path
from pydantic import BaseModel

AIRPORTS = []


class Airport(BaseModel):
    label: str
    iata: str
    icao: str
    name: str
    city: str
    country: str


def load_airports():
    global AIRPORTS
    path = Path(__file__).parent / "airports.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # the file is keyed by ICAO, so loop values
    AIRPORTS = [
        {
            "iata": a.get("iata"),
            "icao": a.get("icao"),
            "name": a.get("name"),
            "city": a.get("city"),
            "country": a.get("country"),
        }
        for a in data.values()
        if a.get("iata")  # skip entries with no IATA
    ]


def add_airport_label(airport):
    return {
        "label": f"{airport["city"]} — {airport["name"]} ({airport["iata"]}), {airport["country"]}",
        **airport
    }


def search_airports(query: str, limit: int = 10) -> list[Airport]:
    q = query.lower()
    results = [
        add_airport_label(a) for a in AIRPORTS
        if (a["iata"] and a["iata"].lower().startswith(q))
        or (a["city"] and a["city"].lower().startswith(q))
        or (a["name"] and a["name"].lower().startswith(q))
    ]
    return results[:limit]
