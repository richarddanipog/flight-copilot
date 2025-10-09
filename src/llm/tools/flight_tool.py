from __future__ import annotations
from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field, field_validator
from src.app.deps import get_search_service

from src.core.entities import Airport, FlightQuery
from src.core.services import SearchFlightsService

from langchain_core.tools import StructuredTool


class SearchFlightsInput(BaseModel):
    origin: str = Field(..., description="Origin IATA, e.g., TLV")
    destination: str = Field(..., description="Destination IATA, e.g., BCN")
    date_from: date = Field(..., description="Outbound date (YYYY-MM-DD)")
    date_to: Optional[date] = Field(None, description="Latest outbound date")
    return_date: Optional[date] = Field(None, description="Return date")
    nonstop: bool = Field(False, description="Require nonstop")
    max_price: Optional[int] = Field(None, description="Max price")
    limit: Optional[int] = Field(5, ge=1, le=20, description="Max results")

    @field_validator("origin", "destination")
    @classmethod
    def upper_iata(cls, v: str) -> str:
        return (v or "").upper()

    @field_validator("limit", mode="before")
    def _coerce_limit(cls, v):
        if v in (None, "", "null"):
            return 5
        try:
            v = int(v)
        except Exception:
            return 5
        return max(1, min(20, v))


def search_flights_tool() -> StructuredTool:
    """Return a LangChain StructuredTool bound to the given provider."""
    service = get_search_service()

    def _run(
        origin: str,
        destination: str,
        date_from: date,
        date_to: Optional[date] = None,
        return_date: Optional[date] = None,
        nonstop: bool = False,
        max_price: Optional[int] = None,
        limit: Optional[int] = 5,
    ) -> List[dict]:
        q = FlightQuery(
            origin=Airport(origin),
            destination=Airport(destination),
            date_from=date_from,
            date_to=date_to or date_from,
            return_date=return_date,
            nonstop=nonstop,
            max_price=max_price,
        )
        its = service.execute(q, limit=limit)
        return its

    return StructuredTool.from_function(
        func=_run,
        name="search_flights",
        description="Search flights and return itineraries.",
        args_schema=SearchFlightsInput,
    )
