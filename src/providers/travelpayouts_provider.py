from typing import List
from src.core.entities import FlightQuery, Itinerary
from src.core.services import FlightProvider
from .travelpayouts_client import TravelpayoutsClient


class TravelpayoutsProvider(FlightProvider):
    def __init__(self, client: TravelpayoutsClient):
        self.client = client

    def search(self, query: FlightQuery, limit: int) -> List[Itinerary]:
        return self.client.search(query, limit=limit)
