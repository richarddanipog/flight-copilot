from src.infra.airports.airports_loader import load_airports
from .routers import flights, agent, locations
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI


app = FastAPI(title="Flight Copilot API", version="1.0.0")


@app.on_event("startup")
def startup_event():
    load_airports()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flights.router,   prefix="/api", tags=["flights"])
app.include_router(agent.router,     prefix="/api", tags=["agent"])
app.include_router(locations.router, prefix="/api", tags=["locations"])


@app.get("/health")
def health():
    return {"ok": True}
