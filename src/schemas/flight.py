from pydantic import BaseModel, Field
from typing import Optional, List


class FlightRequest(BaseModel):
    origin: str = Field(...,
                        description="IATA code or city text (TLV or 'Tel Aviv')")
    destination: str = Field(...,
                             description="IATA code or city text (PRG or 'Prague')")
    departureDate: str = Field(...,
                               description="YYYY-MM-DD or month word like 'april'")
    returnDate: Optional[str] = Field(
        None, description="YYYY-MM-DD or month word")
    maxPrice: Optional[int] = Field(None, ge=1)
    nonStop: Optional[bool] = False
    currency: Optional[str] = "USD"
    max: Optional[int] = 10


class AgentRequest(BaseModel):
    query: str


class Price(BaseModel):
    amount: int
    currency: str


class SegmentView(BaseModel):
    origin: str            # IATA
    destination: str       # IATA
    depart_utc: str        # ISO string
    arrive_utc: str        # ISO string
    carrier: str
    flight_number: Optional[str] = None
    duration_min: int


class LayoverView(BaseModel):
    at: str                # IATA
    duration_min: int


class Leg(BaseModel):
    origin: str            # leg start IATA
    destination: str       # leg end IATA
    depart_utc: str
    arrive_utc: str
    duration_min: int
    stops: int
    segments: List[SegmentView]
    layovers: List[LayoverView]


class FlightOption(BaseModel):
    price: Price
    deeplink: Optional[str] = None
    carriers: List[str]
    outbound: Optional[Leg] = None
    return_: Optional[Leg] = None

    class Config:
        populate_by_name = True


class FlightResponse(BaseModel):
    options: List[FlightOption]


class AgentResponse(BaseModel):
    options: List[FlightOption]
    output: Optional[str]
