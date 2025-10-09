import hashlib
import orjson
import time
from datetime import timedelta
from redis import Redis, exceptions
from src.config import get_settings
from src.schemas.flight import FlightRequest
from src.utils.logger import get_logger

settings = get_settings()
log = get_logger()


def _connect_redis(required: bool = True, retries: int = 5, delay: float = 0.8):
    url = settings.redis_url

    for i in range(1, retries+1):
        try:
            redis = Redis.from_url(url, decode_responses=False)
            redis.ping()
            log.info(f"[Redis] Connected OK: {url}")
            return redis
        except exceptions.ConnectionError as e:
            log.warning(f"[Redis] Attempt {i}/{retries} failed: {e}")
            time.sleep(delay)

    msg = (
        "[Redis] Unable to connect after retries.\n"
        "Try starting Redis:\n"
        "  docker start redis\n"
        "Then re-run the server."
    )
    if required:
        log.error(msg)
        raise SystemExit(1)
    log.warning(msg)
    return None


redis = _connect_redis(required=True)


def _stable_dict(d: dict) -> bytes:
    # stable JSON (sorted keys) so the same request -> same key
    return orjson.dumps(d, option=orjson.OPT_SORT_KEYS)


def make_key(provider, req: FlightRequest) -> str:
    payload = {
        "origin": req.origin.upper(),
        "destination": req.destination.upper(),
        "departureDate": str(req.departureDate),
        "returnDate": str(req.returnDate or ""),
        "maxPrice": str(req.maxPrice or ""),
        "nonStop": "1" if bool(req.nonStop) else "0",
        "currency": (req.currency or "USD").upper(),
        "max": str(req.max or 10),
        "provider": provider.__class__.__name__.lower(),
    }
    prefix = "flights"
    # include a version “salt” so you can invalidate format changes by bumping it
    version = "v1"
    h = hashlib.sha256(_stable_dict(payload)).hexdigest()[:32]
    return f"{prefix}:{version}:{h}"


def cache_get(key: str):
    raw = redis.get(key)
    return None if raw is None else orjson.loads(raw)


def cache_set(key: str, value) -> None:
    redis.setex(key, timedelta(seconds=settings.ttl_sec), orjson.dumps(value))
