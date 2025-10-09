from dataclasses import dataclass
from datetime import date, datetime
from .exceptions import InvalidIATAError, ValidationError
from typing import List, Optional


@dataclass(frozen=True)
class Airport:  # one airport, validated (e.g., "TLV")
    """IATA airport code, e.g., 'TLV' or 'BCN'."""
    iata: str

    def __post_init__(self):
        code = (self.iata or "").upper()
        if len(code) != 3 or not code.isalpha():
            raise InvalidIATAError(
                f"IATA code must be 3 letters (got '{self.iata}')")
        object.__setattr__(self, "iata", code)  # normalize to uppercase


@dataclass(frozen=True)
class FlightQuery:  # the user’s request (from, to, dates, etc.).
    """A structured flight search request."""
    origin: Airport
    destination: Airport
    date_from: date
    date_to: date
    return_date: date | None = None
    nonstop: bool = True
    max_price: int | None = None  # whole units, e.g., USD

    def __post_init__(self):
        if self.origin.iata == self.destination.iata:
            raise ValidationError("origin and destination must differ")
        if self.date_to < self.date_from:
            raise ValidationError("date_to must be on or after date_from")
        if self.return_date and self.return_date < self.date_from:
            raise ValidationError("return_date must be after departure date")
        if self.max_price is not None and self.max_price <= 0:
            raise ValidationError("max_price must be > 0")


@dataclass(frozen=True)
class Money:  # price container.
    amount: int           # whole units (e.g., USD dollars) for simplicity
    currency: str = "USD"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("amount must be >= 0")
        if len(self.currency) != 3:
            raise ValueError("currency must be a 3-letter code")


@dataclass(frozen=True)
class Segment:  # one flight leg
    origin: Airport
    destination: Airport
    departure_utc: datetime
    arrival_utc: datetime
    carrier: str          # e.g., "LY"
    flight_number: str    # e.g., "LY393"

    def __post_init__(self):
        if self.arrival_utc <= self.departure_utc:
            raise ValueError("arrival must be after departure")
        if not self.carrier or not self.flight_number:
            raise ValueError("carrier and flight_number are required")


@dataclass(frozen=True)
class Itinerary:  # a trip (one or more segments) + price.
    segments: List[Segment]
    price: Money
    total_duration_min: int
    bags_included: bool = False
    deeplink: Optional[str] = None

    def __post_init__(self):
        if not self.segments:
            raise ValueError("itinerary must include at least one segment")
        if self.total_duration_min <= 0:
            raise ValueError("total_duration_min must be > 0")
