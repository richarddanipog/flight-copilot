from typing import List, Optional, Tuple
from fastapi import HTTPException
from src.core.entities import Itinerary, Segment, FlightQuery, Airport
from src.schemas.flight import FlightRequest
from src.utils.date_guard import get_time_minutes
from src.utils.date_guard import coerce_future_iso


def _find_turnaround_split(segs: List[Segment]) -> Optional[int]:
    """
    Return index i such that outbound = segs[:i+1], return = segs[i+1:].
    We pick the pair (a=segs[i], b=segs[i+1]) with the LARGEST positive gap
    where a.destination == b.origin (i.e., same airport continuity).
    This corresponds to the 'stay' at the destination (turnaround).
    """
    if len(segs) < 2:
        return None

    # compute eligible gaps
    gaps: List[Tuple[int, int]] = []  # (i, gap_minutes)
    for i in range(len(segs) - 1):
        a, b = segs[i], segs[i + 1]
        if a.destination.iata != b.origin.iata:
            continue  # segments are not contiguous at the same airport
        gap = get_time_minutes(b.departure_utc) - \
            get_time_minutes(a.arrival_utc)
        if gap > 0:
            gaps.append((i, gap))

    if not gaps:
        return None

    # pick the largest gap (turnaround)
    gaps.sort(key=lambda t: t[1], reverse=True)
    return gaps[0][0]


def _build_leg(leg_segs: List[Segment]) -> dict:
    """Build a single leg (summary + segments + layovers) from contiguous segments."""
    origin = leg_segs[0].origin.iata
    destination = leg_segs[-1].destination.iata
    depart_utc = leg_segs[0].departure_utc
    arrive_utc = leg_segs[-1].arrival_utc

    # per-segment durations
    seg_total = 0
    seg_views = []
    for s in leg_segs:
        dur = get_time_minutes(s.arrival_utc) - \
            get_time_minutes(s.departure_utc)
        seg_views.append({
            "origin": s.origin.iata,
            "destination": s.destination.iata,
            "depart_utc": s.departure_utc.isoformat(),
            "arrive_utc": s.arrival_utc.isoformat(),
            "carrier": s.carrier,
            "flight_number": getattr(s, "flight_number", None),
            "duration_min": dur,
        })
        seg_total += dur

    # layovers within the leg only
    lay_total = 0
    layovers = []
    for i in range(len(leg_segs) - 1):
        a, b = leg_segs[i], leg_segs[i + 1]
        # only valid if same airport continuity
        if a.destination.iata == b.origin.iata:
            gap = get_time_minutes(b.departure_utc) - \
                get_time_minutes(a.arrival_utc)
            if gap > 0:
                layovers.append(
                    {"at": a.destination.iata, "duration_min": gap})
                lay_total += gap

    return {
        "origin": origin,
        "destination": destination,
        "depart_utc": depart_utc.isoformat(),
        "arrive_utc": arrive_utc.isoformat(),
        "duration_min": seg_total + lay_total,
        "stops": max(0, len(leg_segs) - 1),
        "segments": seg_views,
        "layovers": layovers,
    }


def itinerary_to_roundtrip(it: Itinerary) -> dict:
    """
    Transform a raw Itinerary into a UI-friendly dict:
    - Detect turnaround (outbound vs return) using the largest gap at a contiguous airport
    - Build legs with proper origin/destination, segments, layovers, and durations
    - Never count the multi-day 'stay' between legs as a layover
    """
    segs = it.segments[:]  # assume already chronological; copy if you want to sort
    home = segs[0].origin.iata
    carriers = list(dict.fromkeys(s.carrier for s in segs))
    price = {"amount": it.price.amount, "currency": it.price.currency}
    deeplink = it.deeplink

    # one-way if final dest != home
    if segs[-1].destination.iata != home:
        return {
            "price": price,
            "deeplink": deeplink,
            "carriers": carriers,
            "outbound": _build_leg(segs),
            "return_": None,
        }

    # find best split by turnaround (largest gap at same-airport boundary)
    split = _find_turnaround_split(segs)
    if split is None:
        # fallback: try simple heuristic—first point where remaining ends at home
        for i in range(len(segs) - 1):
            left, right = segs[: i + 1], segs[i + 1:]
            if left[0].origin.iata == home and left[-1].destination.iata != home and right[-1].destination.iata == home:
                split = i
                break

    # if still not found, treat as one-way to avoid nonsense
    if split is None or split >= len(segs) - 1:
        return {
            "price": price,
            "deeplink": deeplink,
            "carriers": carriers,
            "outbound": _build_leg(segs),
            "return_": None,
        }

    outbound_segs = segs[: split + 1]
    return_segs = segs[split + 1:]

    # validations to avoid “looping” legs
    if (
        outbound_segs[0].origin.iata != home or
        return_segs[-1].destination.iata != home or
        outbound_segs[-1].destination.iata != return_segs[0].origin.iata or
        get_time_minutes(return_segs[0].departure_utc) <= get_time_minutes(
            outbound_segs[-1].arrival_utc)
    ):
        # Fallback to safer one-way if validations fail
        return {
            "price": price,
            "deeplink": deeplink,
            "carriers": carriers,
            "outbound": _build_leg(segs),
            "return_": None,
        }

    outbound_leg = _build_leg(outbound_segs)
    return_leg = _build_leg(return_segs)

    return {
        "price": price,
        "deeplink": deeplink,
        "carriers": carriers,
        "outbound": outbound_leg,
        "return_": return_leg,
    }


def make_roundtrip(itineraries: list[Itinerary]):
    return [itinerary_to_roundtrip(it) for it in itineraries]


def init_flight_query(req: FlightRequest) -> FlightQuery:
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

    return flight_query
