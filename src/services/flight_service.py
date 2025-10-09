from typing import List
from fastapi import HTTPException
from src.schemas.flight import FlightRequest
from src.utils.logger import get_logger
from src.core.entities import FlightQuery, Airport, Itinerary
from src.utils.date_guard import coerce_future_iso


class FlightService:
    def __init__(self, provider):
        self.log = get_logger()
        self.provider = provider

    def search_flights(self, req: FlightRequest):
        # 1) Coerce dates into future-safe ISO
        try:
            dep_iso = coerce_future_iso(req.departureDate)
            ret_iso = coerce_future_iso(
                req.returnDate) if req.returnDate else None
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

        flight_query = FlightQuery(
            origin=Airport(req.origin),
            destination=Airport(req.destination),
            date_from=dep_iso,
            date_to=dep_iso,
            return_date=ret_iso,
            nonstop=bool(req.nonStop),
            max_price=req.maxPrice,
        )

        try:
            data: List[Itinerary] = self.provider.search(flight_query, 10)
        except Exception as e:
            self.log.error(f"Provider error: {e}")
            raise HTTPException(
                status_code=502, detail="Upstream search failed")

        # Normalize to API response
        options = data
        return options
