from __future__ import annotations

import httpx
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from src.core.entities import Airport, Segment, Itinerary, Money, FlightQuery
from src.utils.flights import make_roundtrip
from src.utils.logger import get_logger

log = get_logger()


def _parse_offset_dt(s: str) -> datetime:
    """
    Parse '2025-12-20T11:10:00+02:00' or '...Z' into aware datetime (UTC or given offset).
    """
    if not s:
        raise ValueError("missing datetime string")
    s = s.strip()
    # python's fromisoformat understands +HH:MM offsets; for 'Z' we normalize
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        # assume UTC if no tz
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _add_minutes(dt: datetime, minutes: int) -> datetime:
    return dt + timedelta(minutes=int(minutes or 0))


def _build_deeplink(path: str, partner_id: str) -> str:
    """
    Aviasales returns relative path in 'link'. We add host and partner tracking.
    You can tweak the params to your preference.
    """
    base = "https://www.aviasales.com"
    joiner = "&" if "?" in path or "&" in path else "?"
    return f"{base}{path}{joiner}marker={partner_id}"


class TravelpayoutsClient:
    """
    Travelpayouts / Aviasales: prices_for_dates endpoint adapter that maps into your
    domain `Itinerary` (segments + price + total_duration_min + deeplink).

    Docs: https://api.travelpayouts.com/aviasales/v3/prices_for_dates
    """

    def __init__(self, token: str, partner_id: str, currency: str = "USD"):
        self.token = token
        self.partner_id = partner_id
        self.currency = currency
        self.base_url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"

    def _init_params(self, q: FlightQuery, limit: int) -> Dict[str, str]:
        # Aviasales expects YYYY-MM-DD (no time) for departure/return
        params: Dict[str, str] = {
            "origin": q.origin.iata,
            "destination": q.destination.iata,
            "departure_at": q.date_from.isoformat(),
            "return_at": (q.return_date or q.date_to or q.date_from).isoformat(),
            "currency": self.currency,
            "token": self.token,
            "direct": "false",
            "limit": limit
        }

        return params

    def search(self, query: FlightQuery, limit: int = 10) -> List[Itinerary]:
        params = self._init_params(query, limit)
        log.info("Calling Aviasales prices_for_dates params=%s", params)

        with httpx.Client(timeout=20) as client:
            r = client.get(self.base_url, params=params)
            r.raise_for_status()
            payload: Dict[str, Any] = r.json()

        if not payload.get("success"):
            return []

        rows: List[Dict] = payload.get("data", [])

        results: List[Itinerary] = []
        for row in rows:
            try:
                price_val = row.get("price")
                if price_val is None:
                    continue

                # --- outbound (synthesize arrival) ---
                dep_out = _parse_offset_dt(row["departure_at"])
                dur_out = int(row.get("duration_to") or 0)
                if dur_out <= 0:
                    # cannot satisfy Segment "arrival > departure"
                    continue
                arr_out = _add_minutes(dep_out, dur_out)

                out_seg = Segment(
                    origin=Airport(row["origin_airport"]),
                    destination=Airport(row["destination_airport"]),
                    departure_utc=dep_out,
                    arrival_utc=arr_out,
                    carrier=(row.get("airline") or "").upper(),
                    flight_number=str(row.get("flight_number") or ""),
                    stops=row.get("transfers", 0)
                )

                segments: List[Segment] = [out_seg]
                total_minutes = dur_out

                # --- inbound (optional; synthesize arrival) ---
                ret_str: Optional[str] = row.get("return_at")
                dur_back = int(row.get("duration_back") or 0)
                if ret_str and dur_back > 0:
                    dep_ret = _parse_offset_dt(ret_str)
                    arr_ret = _add_minutes(dep_ret, dur_back)
                    ret_seg = Segment(
                        origin=Airport(row["destination_airport"]),
                        destination=Airport(row["origin_airport"]),
                        departure_utc=dep_ret,
                        arrival_utc=arr_ret,
                        carrier=(row.get("airline") or "").upper(),
                        # API doesn't provide the return number here
                        flight_number="",
                        stops=row.get("return_transfers", 0)
                    )
                    segments.append(ret_seg)
                    total_minutes += dur_back

                itm = Itinerary(
                    segments=segments,
                    price=Money(amount=int(price_val), currency=params.get(
                        "currency", self.currency)),
                    total_duration_min=total_minutes,
                    bags_included=False,
                    deeplink=_build_deeplink(
                        row["link"], self.partner_id) if row.get("link") else None,
                )
                results.append(itm)

            except Exception as e:
                log.info("Skip row due to mapping error: %s", e)
                continue

        # simple max price filter
        if query.max_price is not None:
            results = [
                it for it in results if it.price.amount <= query.max_price]

        # slice to limit because endpoint doesn’t support it
        results = results[: max(1, min(10, limit))]

        return make_roundtrip(results)
