from functools import lru_cache
from src.config import get_settings
from src.providers.amadeus_client import AmadeusClient
from src.core.services import SearchFlightsService
from src.providers.travelpayouts_client import TravelpayoutsClient
from src.providers.travelpayouts_provider import TravelpayoutsProvider


@lru_cache(maxsize=1)
def get_amadeus_client() -> AmadeusClient:
    settings = get_settings()
    return AmadeusClient(
        client_id=settings.amadeus_client_id,
        client_secret=settings.amadeus_client_secret,
        currency="USD",
    )


@lru_cache(maxsize=1)
def get_travelpayouts_client() -> TravelpayoutsClient:
    s = get_settings()
    return TravelpayoutsClient(
        token=s.travelpayouts_api_token,
        partner_id=s.travelpayouts_partner_id,
        currency="USD",
    )


@lru_cache(maxsize=1)
def get_travelpayouts_provider():
    return TravelpayoutsProvider(get_travelpayouts_client())


@lru_cache(maxsize=1)
def get_flight_provider():
    # If you have a provider wrapper:
    # return AmadeusProvider(get_amadeus_client())

    # # If your routers directly accept the client as "provider", return the client:
    # return get_amadeus_client()

    return get_travelpayouts_provider()


@lru_cache(maxsize=1)
def get_search_service() -> SearchFlightsService:
    return SearchFlightsService(provider=get_flight_provider())
