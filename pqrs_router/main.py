"""pqrs-router HTTP API."""

from __future__ import annotations

from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .service import PQRSService

app = FastAPI(
    title="pqrs-router",
    version="1.0.0",
    summary="Classify and route citizen requests (PQRS) with statutory deadlines.",
)

_service: PQRSService | None = None


def get_service() -> PQRSService:
    global _service
    if _service is None:
        _service = PQRSService()
    return _service


class RouteRequest(BaseModel):
    text: str = Field(min_length=1)
    received_date: str | None = None  # ISO date; defaults to today


@app.get("/health", tags=["ops"])
def health() -> dict:
    return {"status": "ok"}


@app.post("/route", tags=["routing"])
def route(request: RouteRequest) -> dict:
    received = None
    if request.received_date:
        try:
            received = date.fromisoformat(request.received_date)
        except ValueError as exc:
            raise HTTPException(
                status_code=422, detail="received_date must be ISO (YYYY-MM-DD)"
            ) from exc
    return get_service().route(request.text, received=received)
