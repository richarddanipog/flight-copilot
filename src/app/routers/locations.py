from fastapi import APIRouter, Query
from typing import List, Dict, Any
from src.infra.airports.airports_loader import search_airports

router = APIRouter()


@router.get("/locations")
def locations(q: str = Query(..., min_length=2)) -> List[Dict[str, Any]]:
    return search_airports(q)
