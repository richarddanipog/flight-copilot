from __future__ import annotations
import time
import requests
from typing import List, Dict
from datetime import datetime
from src.core.entities import FlightQuery, Airport, Segment, Itinerary, Money
from src.utils.logger import get_logger
from src.utils.date_guard import normalize_departure, ensure_future
from src.config import Settings
from src.utils.flights import make_roundtrip

log = get_logger()
settings = Settings()


class AmadeusClient:
    """
    Minimal Amadeus adapter:
    - OAuth2 client_credentials to get a token
    - Flight Offers Search to fetch options
    - Maps only the fields we need into domain objects
    """

    def __init__(self, client_id: str, client_secret: str, currency: str = "USD"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.currency = currency
        self._token: str | None = None
        self._token_exp: float = 0.0  # epoch seconds

    # --- auth ---
    def _get_token(self) -> str:
        # reuse if not expired (5s skew)
        log.info('Getting token.')
        if self._token and time.time() < self._token_exp - 5:
            return self._token

        resp = requests.post(
            settings.amadeus_auth_url,
            data={"grant_type": "client_credentials",
                  "client_id": self.client_id,
                  "client_secret": self.client_secret},
            headers={"Content-Type": "application/x-www-form-urlencoded",
                     "Accept": "application/json"},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        self._token = data["access_token"]

        self._token_exp = time.time() + int(data.get("expires_in", 0))
        return self._token

    def _init_query_params(self, query: FlightQuery, limit: int) -> Dict:
        # --- normalize departure ---
        dep_raw = str(query.date_from)  # could be 'april' or datetime
        if hasattr(query.date_from, "isoformat"):   # already a datetime/date
            dep_iso = query.date_from.isoformat()
        else:
            dep_iso = normalize_departure(dep_raw)

        # ensure not past
        dep_iso = ensure_future(dep_iso)

        params = {
            "originLocationCode": query.origin.iata,
            "destinationLocationCode": query.destination.iata,
            "departureDate": dep_iso,
            "adults": 1,                                       # keep simple for now
            "currencyCode": self.currency,
            "max": str(limit),
            "nonStop": "true" if query.nonstop else "false",
        }

        if query.return_date:
            if hasattr(query.return_date, "isoformat"):
                ret_iso = query.return_date.isoformat()
            else:
                ret_iso = normalize_departure(str(query.return_date))
            ret_iso = ensure_future(ret_iso)
            params["returnDate"] = ret_iso

        if query.return_date:
            params["returnDate"] = query.return_date.isoformat()

        return params

    # --- search ---
    def search(self, query: FlightQuery, limit: int = 10) -> List[Itinerary]:
        log.debug('Invoked request to amadeus api.')

        token = self._get_token()
        params = self._init_query_params(query, limit)
        # Amadeus doesn't support "price_to" directly in this endpoint; we’ll filter later if needed.
        headers = {"Authorization": f"Bearer {token}",
                   "Accept": "application/json"}
        resp = requests.get(settings.amadeus_flights_url, headers=headers,
                            params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()

        # Map JSON -> domain
        results: List[Itinerary] = []
        for offer in payload.get("data", []):
            price_total = offer.get("price", {}).get("grandTotal")
            if not price_total:
                continue

            itins = offer.get("itineraries", [])
            if not itins:
                continue

            # --- outbound (required) ---
            out_segments, out_min = _segments_and_minutes_from_itin(itins[0])
            if not out_segments or out_min <= 0:
                continue

            all_segments = list(out_segments)
            total_minutes = out_min

            # --- inbound (optional) ---
            if len(itins) > 1:
                in_segments, in_min = _segments_and_minutes_from_itin(itins[1])
                if in_segments and in_min > 0:
                    all_segments.extend(in_segments)
                    total_minutes += in_min

            results.append(
                Itinerary(
                    segments=all_segments,
                    price=Money(amount=int(float(price_total)),
                                currency=self.currency),
                    total_duration_min=total_minutes,
                    bags_included=False,
                    deeplink=None,
                )
            )

        # simple price filter if query.max_price set
        if query.max_price is not None:
            results = [
                it for it in results if it.price.amount <= query.max_price]

        results = make_roundtrip(results)
        return results


def _iso8601_to_minutes(s: str) -> int:
    # very small parser for strings like "PT5H10M", "PT3H", "PT45M"
    s = s.upper().replace("PT", "")
    hours, mins = 0, 0
    if "H" in s:
        h, s = s.split("H", 1)
        hours = int(h or 0)
    if "M" in s:
        m = s.split("M", 1)[0] if "M" in s else "0"
        try:
            mins = int(m)
        except ValueError:
            mins = 0
    return hours * 60 + mins


def _segments_and_minutes_from_itin(itin_json):
    """Return (segments: List[Segment], total_minutes: int) from one Amadeus itinerary JSON."""
    segs_json = itin_json.get("segments", [])
    if not segs_json:
        return [], 0

    segments = []
    for seg in segs_json:
        dep = seg["departure"]
        arr = seg["arrival"]
        carrier = seg.get("carrierCode", "")
        flight_num = seg.get("number", "")
        segments.append(
            Segment(
                origin=Airport(dep["iataCode"]),
                destination=Airport(arr["iataCode"]),
                departure_utc=datetime.fromisoformat(
                    dep["at"].replace("Z", "+00:00")),
                arrival_utc=datetime.fromisoformat(
                    arr["at"].replace("Z", "+00:00")),
                carrier=carrier,
                flight_number=str(flight_num),
            )
        )
    minutes = _iso8601_to_minutes(itin_json.get("duration", "PT0M"))
    return segments, minutes
