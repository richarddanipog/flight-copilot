from fastapi import APIRouter, HTTPException, Depends
from src.app.deps import get_amadeus_client, get_search_service
from src.schemas.flight import FlightRequest, FlightResponse
from src.infra.cache import cache_get, cache_set, make_key
from src.utils.logger import get_logger
from src.config import get_settings

router = APIRouter()
log = get_logger()
settings = get_settings()


@router.post("/flights", response_model=FlightResponse)
def search_flights(req: FlightRequest,
                   provider=Depends(get_amadeus_client),
                   flight_service=Depends(get_search_service)) -> FlightResponse:
    key = make_key(provider, req)
    cached = cache_get(key)
    if cached is not None:
        log.info("Cache hit for %s", key)
        return FlightResponse(**cached)

    try:
        options = flight_service.execute(req)
    except Exception as e:
        log.error("Provider error: %s", e)
        raise HTTPException(status_code=502, detail="Upstream search failed")

    result = FlightResponse(options=options).model_dump()
    cache_set(key, result)
    return FlightResponse(**result)
