from dataclasses import dataclass
from typing import Protocol, List
from .entities import FlightQuery, Itinerary
from src.schemas.flight import FlightRequest


class FlightProvider(Protocol):
    def search(self, query: FlightQuery,
               limit: int = 10) -> List[Itinerary]: ...


@dataclass
class SearchFlightsService:
    provider: FlightProvider

    def execute(self, query_or_req: FlightQuery | FlightRequest, limit: int = 10) -> List[Itinerary]:
        if isinstance(query_or_req, FlightRequest):
            from src.utils.flights import init_flight_query
            query = init_flight_query(query_or_req)
        else:
            query = query_or_req

        return self.provider.search(query, limit=limit)
