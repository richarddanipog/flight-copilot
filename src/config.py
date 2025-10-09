from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass
class Settings:
    amadeus_client_id: str | None = os.getenv("AMADEUS_CLIENT_ID")
    amadeus_client_secret: str | None = os.getenv("AMADEUS_CLIENT_SECRET")
    amadeus_auth_url: str | None = os.getenv("AMADEUS_AUTH_URL")
    amadeus_flights_url: str | None = os.getenv("AMADEUS_FLIGHTS_URL")

    model_name: str | None = os.getenv("MODEL_NAME")
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    use_verbose: bool = os.getenv("USE_VERBOSE", 'false') == 'true'
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ttl_sec: int = int(os.getenv("FLIGHT_CACHE_TTL_SEC", "1800"))


def get_settings() -> Settings:
    return Settings()
